# tests/conftest.py
from dotenv import load_dotenv

# Esto se ejecuta antes de cualquier test, incluyendo imports
load_dotenv("tests/.env.test", override=True)
