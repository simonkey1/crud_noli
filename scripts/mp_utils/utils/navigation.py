from fastapi import status
from starlette.responses import RedirectResponse

def redirect_with_cache_control(url, status_code=status.HTTP_302_FOUND):
    """
    Crea una redirección con cabeceras adicionales para mejorar la navegación.
    Especialmente útil para evitar problemas con el botón de retroceso del navegador.
    
    Args:
        url: URL a la que redirigir
        status_code: Código de estado HTTP (por defecto 302 Found)
        
    Returns:
        RedirectResponse con cabeceras adicionales
    """
    response = RedirectResponse(url=url, status_code=status_code)
    
    # Aseguramos que no se cachee la redirección para evitar problemas de navegación
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response
