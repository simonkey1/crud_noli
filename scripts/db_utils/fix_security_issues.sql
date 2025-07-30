-- Script para solucionar problemas de seguridad y rendimiento en Supabase
-- Ejecutar como SQL query en la consola de Supabase

-- 1. Habilitar RLS en las tablas que no lo tienen
ALTER TABLE public.cierrecaja ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;

-- 2. Crear políticas RLS para cierrecaja
CREATE POLICY "Administradores pueden ver todos los cierres" 
ON public.cierrecaja FOR SELECT 
USING (auth.uid() IN (SELECT id FROM auth.users WHERE role = 'admin'));

CREATE POLICY "Administradores pueden insertar cierres" 
ON public.cierrecaja FOR INSERT 
WITH CHECK (auth.uid() IN (SELECT id FROM auth.users WHERE role = 'admin'));

CREATE POLICY "Administradores pueden modificar cierres" 
ON public.cierrecaja FOR UPDATE 
USING (auth.uid() IN (SELECT id FROM auth.users WHERE role = 'admin'));

-- 3. Crear política RLS para alembic_version (sólo acceso de lectura)
CREATE POLICY "Solo administradores pueden ver alembic_version" 
ON public.alembic_version FOR SELECT 
USING (auth.uid() IN (SELECT id FROM auth.users WHERE role = 'admin'));

-- 4. Restringir acceso a las funciones
REVOKE ALL ON FUNCTION public.uuid_to_int FROM PUBLIC;
REVOKE ALL ON FUNCTION public.get_auth_user_id FROM PUBLIC;

-- Dar permisos solo a los roles que necesitan usar estas funciones
GRANT EXECUTE ON FUNCTION public.uuid_to_int TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_auth_user_id TO authenticated;

-- 5. Crear índices para las claves foráneas sin índices
-- Índices para public.orden
CREATE INDEX IF NOT EXISTS idx_orden_usuario_id ON public.orden(usuario_id);
CREATE INDEX IF NOT EXISTS idx_orden_cierre_id ON public.orden(cierre_id);

-- Índices para public.ordenitem
CREATE INDEX IF NOT EXISTS idx_ordenitem_orden_id ON public.ordenitem(orden_id);
CREATE INDEX IF NOT EXISTS idx_ordenitem_producto_id ON public.ordenitem(producto_id);

-- Índices para public.producto
CREATE INDEX IF NOT EXISTS idx_producto_categoria_id ON public.producto(categoria_id);

-- 6. Verificación final
-- Ejecutar estas consultas para verificar que se aplicaron los cambios correctamente
-- SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';
-- SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';
