#!/usr/bin/env python
import uvicorn

if __name__ == "__main__":
    # Configuración específica para Render
    # Render proporciona la variable de entorno PORT
    import os
    port = int(os.environ.get("PORT", 8000))
    
    # Host debe ser 0.0.0.0 para Render
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
