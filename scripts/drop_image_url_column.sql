-- Script para eliminar la columna image_url de la tabla producto
ALTER TABLE producto DROP COLUMN IF EXISTS image_url;
