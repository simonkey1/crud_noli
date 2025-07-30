from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Middleware para controlar el caché del navegador y mejorar la experiencia de navegación.
    Especialmente útil para solucionar problemas al usar el botón de retroceso del navegador.
    """
    
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        super().__init__(app)
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Agregamos cabeceras para controlar el caché en todas las respuestas HTML
        if isinstance(response, Response) and "text/html" in response.headers.get("content-type", ""):
            # Permitir caché pero validar siempre con el servidor (no-cache)
            response.headers["Cache-Control"] = "no-cache, must-revalidate"
            # Evitar que el navegador guarde la página en caché
            response.headers["Pragma"] = "no-cache"
            
        return response
