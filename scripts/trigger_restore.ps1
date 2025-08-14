# Script de PowerShell para activar restauración automática desde GitHub Actions
# Requiere PowerShell 5.1 o superior

param(
    [Parameter(Mandatory=$false)]
    [string]$GitHubToken = $env:GITHUB_TOKEN,
    
    [Parameter(Mandatory=$false)]
    [string]$RepoOwner = "simonkey1", # Tu usuario de GitHub
    
    [Parameter(Mandatory=$false)]
    [string]$RepoName = "crud_noli",
    
    [Parameter(Mandatory=$false)]
    [string]$ArtifactName,
    
    [Parameter(Mandatory=$false)]
    [switch]$ForceRestore,
    
    [Parameter(Mandatory=$false)]
    [switch]$ListArtifacts
)

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Get-AvailableArtifacts {
    param(
        [string]$Token,
        [string]$Owner,
        [string]$Repo
    )
    
    $url = "https://api.github.com/repos/$Owner/$Repo/actions/artifacts"
    $headers = @{
        "Accept" = "application/vnd.github.v3+json"
        "Authorization" = "token $Token"
    }
    
    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Get
        $backupArtifacts = $response.artifacts | Where-Object { $_.name -like "*backup*" }
        
        Write-ColoredOutput "📦 Se encontraron $($backupArtifacts.Count) artifacts de backup:" "Green"
        
        for ($i = 0; $i -lt [Math]::Min(10, $backupArtifacts.Count); $i++) {
            $artifact = $backupArtifacts[$i]
            $createdDate = [DateTime]::Parse($artifact.created_at).ToString("yyyy-MM-dd HH:mm:ss")
            Write-Host "  $($i+1). $($artifact.name) - $createdDate UTC"
        }
        
        return $backupArtifacts
    }
    catch {
        Write-ColoredOutput "❌ Error al obtener artifacts: $($_.Exception.Message)" "Red"
        return @()
    }
}

function Invoke-RestoreWorkflow {
    param(
        [string]$Token,
        [string]$Owner,
        [string]$Repo,
        [string]$Artifact = $null,
        [bool]$Force = $false
    )
    
    $url = "https://api.github.com/repos/$Owner/$Repo/actions/workflows/auto-restore.yml/dispatches"
    $headers = @{
        "Accept" = "application/vnd.github.v3+json"
        "Authorization" = "token $Token"
        "Content-Type" = "application/json"
    }
    
    $payload = @{
        "ref" = "main"
        "inputs" = @{}
    }
    
    if ($Artifact) {
        $payload.inputs.backup_artifact_name = $Artifact
    }
    
    if ($Force) {
        $payload.inputs.force_restore = "true"
    }
    
    $jsonPayload = $payload | ConvertTo-Json -Depth 3
    
    Write-ColoredOutput "🚀 Activando workflow de restauración..." "Cyan"
    Write-Host "📂 Repositorio: $Owner/$Repo"
    Write-Host "🗂️ Artifact: $($Artifact -or 'pre-deploy-backup (default)')"
    Write-Host "⚡ Forzar restauración: $(if ($Force) { 'Sí' } else { 'No' })"
    
    try {
        $response = Invoke-RestMethod -Uri $url -Headers $headers -Method Post -Body $jsonPayload
        
        Write-ColoredOutput "✅ ¡Workflow activado exitosamente!" "Green"
        Write-ColoredOutput "🌐 Monitorea el progreso en: https://github.com/$Owner/$Repo/actions" "Yellow"
        return $true
    }
    catch {
        Write-ColoredOutput "❌ Error al activar el workflow: $($_.Exception.Message)" "Red"
        if ($_.Exception.Response) {
            $statusCode = $_.Exception.Response.StatusCode
            Write-Host "📋 Código de estado: $statusCode"
        }
        return $false
    }
}

function Show-Menu {
    Write-ColoredOutput "🔄 Activador de Restauración Automática" "Cyan"
    Write-Host "=" * 40
    Write-Host ""
    Write-Host "¿Qué deseas hacer?"
    Write-Host "1. Ver artifacts disponibles"
    Write-Host "2. Restaurar usando el backup más reciente"
    Write-Host "3. Restaurar usando un artifact específico"
    Write-Host "4. Forzar restauración (aunque la DB tenga datos)"
    Write-Host "5. Salir"
    Write-Host ""
}

# Función principal
function Main {
    # Verificar token
    if (-not $GitHubToken) {
        Write-ColoredOutput "❌ No se encontró GITHUB_TOKEN" "Red"
        Write-ColoredOutput "💡 Crea un token en: https://github.com/settings/tokens" "Yellow"
        Write-ColoredOutput "💡 Necesita permisos: repo, workflow" "Yellow"
        Write-ColoredOutput "💡 Luego ejecuta: `$env:GITHUB_TOKEN='tu_token_aqui'" "Yellow"
        return
    }
    
    Write-Host "📂 Repositorio: $RepoOwner/$RepoName"
    Write-Host ""
    
    # Verificar parámetros de línea de comandos
    if ($ListArtifacts) {
        Write-Host "📦 Obteniendo lista de artifacts..."
        Get-AvailableArtifacts -Token $GitHubToken -Owner $RepoOwner -Repo $RepoName
        return
    }
    
    if ($ArtifactName -or $ForceRestore) {
        $force = $ForceRestore.IsPresent
        Invoke-RestoreWorkflow -Token $GitHubToken -Owner $RepoOwner -Repo $RepoName -Artifact $ArtifactName -Force $force
        return
    }
    
    # Mostrar menú interactivo
    do {
        Show-Menu
        $opcion = Read-Host "Elige una opción (1-5)"
        
        switch ($opcion) {
            "1" {
                Write-Host "`n📦 Obteniendo lista de artifacts..."
                Get-AvailableArtifacts -Token $GitHubToken -Owner $RepoOwner -Repo $RepoName
                Write-Host ""
            }
            "2" {
                Write-Host "`n🔄 Activando restauración con backup más reciente..."
                Invoke-RestoreWorkflow -Token $GitHubToken -Owner $RepoOwner -Repo $RepoName
                Write-Host ""
            }
            "3" {
                $artifact = Read-Host "`nNombre del artifact"
                if ($artifact) {
                    Write-Host "`n🔄 Activando restauración con artifact '$artifact'..."
                    Invoke-RestoreWorkflow -Token $GitHubToken -Owner $RepoOwner -Repo $RepoName -Artifact $artifact
                } else {
                    Write-ColoredOutput "❌ Nombre de artifact no puede estar vacío" "Red"
                }
                Write-Host ""
            }
            "4" {
                $artifact = Read-Host "`nNombre del artifact (opcional, presiona Enter para usar el default)"
                $artifactToUse = if ($artifact) { $artifact } else { $null }
                Write-Host "`n⚡ Activando restauración FORZADA..."
                Invoke-RestoreWorkflow -Token $GitHubToken -Owner $RepoOwner -Repo $RepoName -Artifact $artifactToUse -Force $true
                Write-Host ""
            }
            "5" {
                Write-ColoredOutput "👋 ¡Hasta luego!" "Green"
                break
            }
            default {
                Write-ColoredOutput "❌ Opción no válida" "Red"
                Write-Host ""
            }
        }
    } while ($opcion -ne "5")
}

# Ejecutar función principal
try {
    Main
}
catch {
    Write-ColoredOutput "❌ Error inesperado: $($_.Exception.Message)" "Red"
}
