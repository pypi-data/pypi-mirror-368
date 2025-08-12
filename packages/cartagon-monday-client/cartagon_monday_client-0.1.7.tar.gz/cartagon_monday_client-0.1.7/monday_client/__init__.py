from .client import MondayClient

import os

def Client(api_key: str | None = None) -> MondayClient:
    """
    Fábrica que crea un MondayClient:
    - Si no pasas api_key, intenta leer la variable de entorno MONDAY_API_KEY.
    """
    key = api_key or os.getenv("MONDAY_API_KEY")
    if not key:
        raise ValueError(
            "Falta la API Key: pásala como argumento o define MONDAY_API_KEY"
        )
    return MondayClient(api_key=key)
