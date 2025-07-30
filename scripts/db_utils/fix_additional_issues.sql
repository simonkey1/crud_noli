-- Script para completar la corrección de problemas de seguridad y rendimiento en Supabase
-- Este script complementa el fix_security_issues.sql existente para corregir
-- problemas adicionales detectados por el script check_security_status.py

-- 1. Corregir RLS en tabla cierrecaja 
ALTER TABLE public.cierrecaja ENABLE ROW LEVEL SECURITY;

-- 2. Crear políticas faltantes para alembic_version
CREATE POLICY IF NOT EXISTS "Solo admins pueden ver alembic_version" 
ON public.alembic_version FOR SELECT 
USING (auth.uid() IN (SELECT id FROM auth.users WHERE role = 'admin'));

-- 3. Crear índices faltantes para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_ordenitem_orden_id ON public.ordenitem(orden_id);

-- 4. Corregir permisos de función get_auth_user_id
CREATE OR REPLACE FUNCTION public.get_auth_user_id() 
RETURNS UUID 
LANGUAGE sql STABLE 
SECURITY INVOKER 
AS $$
    SELECT auth.uid()
$$;

-- 5. Verificar permisos en funciones
REVOKE ALL ON FUNCTION public.uuid_to_int FROM PUBLIC;
REVOKE ALL ON FUNCTION public.get_auth_user_id FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.uuid_to_int TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_auth_user_id TO authenticated;
