-- Script SQL para habilitar RLS en Supabase
-- Este script puedes ejecutarlo directamente en el Editor SQL de Supabase

-- Habilitar RLS en todas las tablas
ALTER TABLE public.categoria ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.producto ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orden ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ordenitem ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user ENABLE ROW LEVEL SECURITY;

-- Eliminar políticas existentes para evitar conflictos
DROP POLICY IF EXISTS "Autenticados pueden ver categorías" ON public.categoria;
DROP POLICY IF EXISTS "Admins pueden gestionar categorías" ON public.categoria;

DROP POLICY IF EXISTS "Autenticados pueden ver productos" ON public.producto;
DROP POLICY IF EXISTS "Admins pueden gestionar productos" ON public.producto;

DROP POLICY IF EXISTS "Autenticados pueden ver sus órdenes" ON public.orden;
DROP POLICY IF EXISTS "Admins pueden ver todas las órdenes" ON public.orden;

DROP POLICY IF EXISTS "Autenticados pueden ver sus items de orden" ON public.ordenitem;
DROP POLICY IF EXISTS "Admins pueden ver todos los items de orden" ON public.ordenitem;

DROP POLICY IF EXISTS "Usuarios pueden ver y editar su propio perfil" ON public.user;
DROP POLICY IF EXISTS "Admins pueden ver y editar todos los usuarios" ON public.user;

-- Crear nuevas políticas

-- Categorías
CREATE POLICY "Autenticados pueden ver categorías" 
ON public.categoria FOR SELECT 
TO authenticated
USING (true);

CREATE POLICY "Admins pueden gestionar categorías" 
ON public.categoria FOR ALL 
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public."user"
    WHERE id::text = auth.uid()::text
    AND is_superuser = true
  )
);

-- Productos
CREATE POLICY "Autenticados pueden ver productos" 
ON public.producto FOR SELECT 
TO authenticated
USING (true);

CREATE POLICY "Admins pueden gestionar productos" 
ON public.producto FOR ALL 
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public."user"
    WHERE id::text = auth.uid()::text
    AND is_superuser = true
  )
);

-- Órdenes
CREATE POLICY "Autenticados pueden ver sus órdenes" 
ON public.orden FOR ALL 
TO authenticated
USING (
  usuario_id::text = auth.uid()::text OR
  EXISTS (
    SELECT 1 FROM public."user"
    WHERE id::text = auth.uid()::text
    AND is_superuser = true
  )
);

-- Items de orden
CREATE POLICY "Autenticados pueden ver sus items de orden" 
ON public.ordenitem FOR ALL 
TO authenticated
USING (
  EXISTS (
    SELECT 1 FROM public.orden
    WHERE id = orden_id
    AND usuario_id::text = auth.uid()::text
  ) OR
  EXISTS (
    SELECT 1 FROM public."user"
    WHERE id::text = auth.uid()::text
    AND is_superuser = true
  )
);

-- Usuarios
CREATE POLICY "Usuarios pueden ver y editar su propio perfil" 
ON public."user" FOR ALL 
TO authenticated
USING (
  id::text = auth.uid()::text OR
  EXISTS (
    SELECT 1 FROM public."user"
    WHERE id::text = auth.uid()::text
    AND is_superuser = true
  )
);
