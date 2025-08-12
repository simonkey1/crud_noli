# utils/cache.py

from functools import wraps
from typing import Optional, Dict, Any, Union
import time
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

class SimpleCache:
    def __init__(self, default_ttl: int = 300):  # 5 minutos por defecto
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Genera una clave única para la función y sus parámetros"""
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': {k: v for k, v in kwargs.items() if k not in ['session', 'db']}  # Excluir session de DB
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry['expires']:
                logger.debug(f"Cache HIT: {key}")
                return entry['data']
            else:
                del self.cache[key]
                logger.debug(f"Cache EXPIRED: {key}")
        logger.debug(f"Cache MISS: {key}")
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'data': data,
            'expires': time.time() + ttl
        }
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalida todas las claves que contienen el patrón"""
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.cache[key]
        logger.info(f"Cache invalidated {len(keys_to_delete)} keys matching: {pattern}")
    
    def clear(self) -> None:
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")
    
    def stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del cache"""
        now = time.time()
        active_entries = sum(1 for entry in self.cache.values() if entry['expires'] > now)
        expired_entries = len(self.cache) - active_entries
        
        return {
            'total_entries': len(self.cache),
            'active_entries': active_entries,
            'expired_entries': expired_entries
        }

# Cache global
app_cache = SimpleCache(default_ttl=300)  # 5 minutos

def cached(ttl: Optional[int] = None, cache_key_prefix: str = ""):
    """Decorador para cachear resultados de funciones"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de cache
            cache_key = f"{cache_key_prefix}_{app_cache._generate_key(func.__name__, args, kwargs)}"
            
            # Intentar obtener del cache
            cached_result = app_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            app_cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Función helper para invalidar cache"""
    app_cache.invalidate_pattern(pattern)

def clear_cache():
    """Función helper para limpiar todo el cache"""
    app_cache.clear()

def cache_stats():
    """Función helper para obtener estadísticas del cache"""
    return app_cache.stats()
