-- Script SQL para activar RLS y hacer compatibles los IDs de usuarios con Supabase Auth
-- Ejecutar directamente en el Editor SQL de Supabase

-- 1. Crear funciones auxiliares para manejar la conversión UUID <-> INT
CREATE OR REPLACE FUNCTION uuid_to_int(uuid UUID)
RETURNS INTEGER AS $$
BEGIN
    -- Convertir UUID a número usando la parte numérica del UUID (método simplificado)
    RETURN ('x' || substring(uuid::text, 1, 8))::bit(32)::integer;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_auth_user_id()
RETURNS INTEGER AS $$
DECLARE
    auth_id UUID;
    user_id INTEGER;
BEGIN
    -- Obtener UUID del usuario autenticado
    auth_id := auth.uid();
    
    -- Si no hay usuario autenticado, devolver NULL
    IF auth_id IS NULL THEN
        RETURN NULL;
    END IF;
    
    -- Intentar encontrar el usuario por nombre de usuario
    -- Esto asume que los usernames en tu tabla user coinciden con los emails en auth.users
    SELECT u.id INTO user_id
    FROM public."user" u
    JOIN auth.users au ON u.username = au.email
    WHERE au.id = auth_id;
    
    RETURN user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Habilitar RLS en todas las tablas
ALTER TABLE public.categoria ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.producto ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orden ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ordenitem ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."user" ENABLE ROW LEVEL SECURITY;

-- 3. Crear políticas de RLS que usan la función get_auth_user_id()

-- Tabla User: Los usuarios pueden ver y editar su propio perfil, los admins pueden ver todo
DROP POLICY IF EXISTS "Users can view and edit own profile" ON public."user";
CREATE POLICY "Users can view and edit own profile" 
ON public."user" 
FOR ALL
TO authenticated
USING (
  id = get_auth_user_id() OR
  (SELECT is_superuser FROM public."user" WHERE id = get_auth_user_id())
);

-- Tabla Categoría: Todos pueden ver, solo admins pueden modificar
DROP POLICY IF EXISTS "All users can view categories" ON public.categoria;
DROP POLICY IF EXISTS "Admins can manage categories" ON public.categoria;

CREATE POLICY "All users can view categories" 
ON public.categoria 
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Admins can manage categories" 
ON public.categoria 
FOR ALL
TO authenticated
USING (
  (SELECT is_superuser FROM public."user" WHERE id = get_auth_user_id())
);

-- Tabla Producto: Todos pueden ver, solo admins pueden modificar
DROP POLICY IF EXISTS "All users can view products" ON public.producto;
DROP POLICY IF EXISTS "Admins can manage products" ON public.producto;

CREATE POLICY "All users can view products" 
ON public.producto 
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Admins can manage products" 
ON public.producto 
FOR ALL
TO authenticated
USING (
  (SELECT is_superuser FROM public."user" WHERE id = get_auth_user_id())
);

-- Tabla Orden: Todos los usuarios autenticados pueden ver las órdenes, solo los admins pueden modificar
DROP POLICY IF EXISTS "Users can view orders" ON public.orden;
DROP POLICY IF EXISTS "Admins can manage orders" ON public.orden;

CREATE POLICY "Users can view orders" 
ON public.orden 
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Admins can manage orders" 
ON public.orden 
FOR ALL
TO authenticated
USING (
  (SELECT is_superuser FROM public."user" WHERE id = get_auth_user_id())
);

-- Tabla OrdenItem: Todos los usuarios pueden ver los items, solo admins pueden modificar
DROP POLICY IF EXISTS "Users can view order items" ON public.ordenitem;
DROP POLICY IF EXISTS "Admins can manage order items" ON public.ordenitem;

CREATE POLICY "Users can view order items" 
ON public.ordenitem 
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Admins can manage order items" 
ON public.ordenitem 
FOR ALL
TO authenticated
USING (
  (SELECT is_superuser FROM public."user" WHERE id = get_auth_user_id())
);
