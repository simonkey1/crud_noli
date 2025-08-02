# Solución de Problemas de Seguridad y Rendimiento en Supabase

Este documento describe los problemas de seguridad y rendimiento que se encontraron en la base de datos de Supabase y las soluciones que se implementaron para resolverlos.

## Problemas detectados

### 1. Configuración incorrecta de Row Level Security (RLS)

- **Tablas sin RLS habilitado**: Las tablas `cierrecaja` y `alembic_version` no tenían RLS habilitado, lo que permitía acceso sin restricciones a estos datos.
- **Políticas de seguridad incompletas**: Faltaban políticas de seguridad en algunas tablas.

### 2. Permisos excesivos en funciones

- Las funciones `uuid_to_int` y `get_auth_user_id` estaban configuradas con `SECURITY DEFINER`, lo que les daba permisos excesivos.
- No había restricciones de ejecución adecuadas para estas funciones.

### 3. Índices faltantes para claves foráneas

- Algunas columnas de claves foráneas no tenían índices, lo que podría afectar el rendimiento de las consultas:
  - `ordenitem.orden_id`
  - `producto.categoria_id`

## Soluciones implementadas

### Scripts de corrección

Se crearon dos scripts para solucionar estos problemas:

1. **`fix_security_issues.py`**: Script principal que corrige:

   - Habilita RLS en tablas desprotegidas
   - Crea políticas de seguridad para administradores
   - Ajusta permisos en funciones
   - Crea índices para mejorar rendimiento

2. **`fix_additional_issues.py`**: Script complementario que:

   - Corrige problemas adicionales detectados en el diagnóstico
   - Enfoca en los índices faltantes y permisos de funciones

3. **`check_security_status.py`**: Script de diagnóstico que:
   - Verifica el estado de RLS en todas las tablas
   - Muestra las políticas de seguridad existentes
   - Comprueba índices en claves foráneas
   - Verifica configuración de seguridad en funciones

### Cambios específicos

#### Habilitación de RLS

```sql
ALTER TABLE public.cierrecaja ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;
```

#### Creación de políticas de seguridad

```sql
CREATE POLICY "Administradores pueden ver todos los cierres"
ON public.cierrecaja FOR SELECT
USING (auth.uid() IN (SELECT id FROM auth.users WHERE role = 'admin'));

CREATE POLICY "Administradores pueden insertar cierres"
ON public.cierrecaja FOR INSERT
WITH CHECK (auth.uid() IN (SELECT id FROM auth.users WHERE role = 'admin'));

CREATE POLICY "Administradores pueden modificar cierres"
ON public.cierrecaja FOR UPDATE
USING (auth.uid() IN (SELECT id FROM auth.users WHERE role = 'admin'));

CREATE POLICY "Solo administradores pueden ver alembic_version"
ON public.alembic_version FOR SELECT
USING (auth.uid() IN (SELECT id FROM auth.users WHERE role = 'admin'));
```

#### Corrección de permisos en funciones

```sql
REVOKE ALL ON FUNCTION public.uuid_to_int FROM PUBLIC;
REVOKE ALL ON FUNCTION public.get_auth_user_id FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.uuid_to_int TO authenticated;
GRANT EXECUTE ON FUNCTION public.get_auth_user_id TO authenticated;

CREATE OR REPLACE FUNCTION public.get_auth_user_id()
RETURNS UUID LANGUAGE sql STABLE SECURITY INVOKER
AS $$ SELECT auth.uid() $$;
```

#### Creación de índices

```sql
CREATE INDEX IF NOT EXISTS idx_orden_usuario_id ON public.orden(usuario_id);
CREATE INDEX IF NOT EXISTS idx_orden_cierre_id ON public.orden(cierre_id);
CREATE INDEX IF NOT EXISTS idx_ordenitem_orden_id ON public.ordenitem(orden_id);
CREATE INDEX IF NOT EXISTS idx_producto_categoria_id ON public.producto(categoria_id);
```

## Estado final

Después de aplicar estas correcciones:

1. Todas las tablas ahora tienen RLS habilitado con políticas adecuadas
2. Las funciones tienen permisos más restrictivos y seguros
3. Se han creado índices para todas las claves foráneas importantes

## Recomendaciones futuras

1. Revisar regularmente la configuración de RLS ejecutando `check_security_status.py`
2. Al crear nuevas tablas, asegurarse de habilitar RLS y definir políticas adecuadas
3. Crear índices para todas las columnas utilizadas frecuentemente en consultas JOIN
4. Usar `SECURITY INVOKER` en lugar de `SECURITY DEFINER` cuando sea posible
5. Aplicar el principio de mínimo privilegio en todos los aspectos de la base de datos
