"""
Middleware para medir el rendimiento de los endpoints
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware que mide el tiempo de respuesta de cada endpoint
    y registra métricas de rendimiento
    """
    
    def __init__(self, app, log_slow_requests: float = 1.0):
        super().__init__(app)
        self.log_slow_requests = log_slow_requests  # Segundos
        
    async def dispatch(self, request: Request, call_next):
        # Información de la request
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # Medir tiempo
        start_time = time.time()
        
        try:
            # Procesar request
            response = await call_next(request)
            
            # Calcular duración
            duration = time.time() - start_time
            status_code = response.status_code
            
            # Agregar header con tiempo de respuesta
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            # Log de la request con tiempo
            self._log_request(method, path, status_code, duration, client_ip)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error en {method} {path} - {duration:.3f}s - IP: {client_ip} - Error: {str(e)}"
            )
            raise
    
    def _log_request(self, method: str, path: str, status_code: int, duration: float, client_ip: str):
        """
        Registra la request con métricas de rendimiento
        """
        # Formatear duración
        duration_ms = duration * 1000
        
        # Determinar nivel de log basado en duración y status
        if duration > self.log_slow_requests:
            level = logging.WARNING
            emoji = "🐌"
        elif status_code >= 400:
            level = logging.WARNING  
            emoji = "❌"
        elif duration > 0.5:
            level = logging.INFO
            emoji = "⚠️"
        else:
            level = logging.DEBUG
            emoji = "✅"
        
        # Log message
        message = f"{emoji} {method} {path} - {status_code} - {duration_ms:.1f}ms - IP: {client_ip}"
        
        # Información adicional para requests lentas
        if duration > self.log_slow_requests:
            message += f" [SLOW REQUEST > {self.log_slow_requests}s]"
        
        logger.log(level, message)
        
        # Métricas específicas para endpoints del POS
        if path.startswith("/pos/"):
            self._log_pos_metrics(method, path, duration_ms, status_code)
    
    def _log_pos_metrics(self, method: str, path: str, duration_ms: float, status_code: int):
        """
        Log específico para métricas del POS
        """
        if status_code < 400:  # Solo requests exitosas
            if path == "/pos/products":
                if duration_ms > 500:
                    logger.warning(f"🔍 POS products endpoint slow: {duration_ms:.1f}ms")
                    
            elif path == "/pos/search":
                if duration_ms > 200:
                    logger.warning(f"🔍 POS search endpoint slow: {duration_ms:.1f}ms")
                    
            elif path.startswith("/pos/order"):
                if duration_ms > 1000:
                    logger.warning(f"💳 POS order processing slow: {duration_ms:.1f}ms")

class APIPerformanceLogger:
    """
    Utilidad para registrar métricas personalizadas desde los endpoints
    """
    
    @staticmethod
    def log_database_query(query_name: str, duration_ms: float, record_count: int = None):
        """
        Registra métricas de consultas a la base de datos
        """
        emoji = "🗃️"
        if duration_ms > 1000:
            emoji = "🐌"
        elif duration_ms > 500:
            emoji = "⚠️"
        
        message = f"{emoji} DB Query [{query_name}]: {duration_ms:.1f}ms"
        if record_count is not None:
            message += f" ({record_count} records)"
        
        level = logging.WARNING if duration_ms > 500 else logging.DEBUG
        logger.log(level, message)
    
    @staticmethod 
    def log_cache_hit(cache_name: str, hit: bool):
        """
        Registra hits/misses de cache
        """
        emoji = "🎯" if hit else "❌"
        message = f"{emoji} Cache [{cache_name}]: {'HIT' if hit else 'MISS'}"
        logger.debug(message)

# Decorator para medir funciones específicas
def measure_performance(operation_name: str):
    """
    Decorator para medir el tiempo de ejecución de funciones
    """
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                APIPerformanceLogger.log_database_query(operation_name, duration)
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(f"❌ {operation_name} failed after {duration:.1f}ms: {str(e)}")
                raise
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                APIPerformanceLogger.log_database_query(operation_name, duration)
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(f"❌ {operation_name} failed after {duration:.1f}ms: {str(e)}")
                raise
        
        return async_wrapper if hasattr(func, '__call__') and hasattr(func, '__await__') else sync_wrapper
    
    return decorator
