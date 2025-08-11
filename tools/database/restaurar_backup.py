#!/usr/bin/env python
# Script para restaurar el backup más reciente
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

# Restaurar el backup más reciente
os.system("python scripts/restore_database.py --restore")
