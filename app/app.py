"""Punto de entrada: `python app.py`. Todo vive en main.py y en las carpetas; este archivo solo arranca."""
from main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    import config
    print(f"Facturio Soporte en http://localhost:{config.PORT}  | modelo {config.MODEL} | effort {config.REASONING_EFFORT}")
    uvicorn.run(app, host="127.0.0.1", port=config.PORT, log_level="warning")
