# import time
# import requests
# import logging

# logger = logging.getLogger(__name__)



# def monday_request(query: str, api_key: str, max_retries: int = 5, retry_delay: int = 3) -> dict:
#     """
#     Realiza peticiones a la API de Monday.com con:
#     - Manejo de errores HTTP
#     - Reintentos en caso de error (hasta max_retries veces)
#     - Gestión de JSON inválido y errores de complejidad
#     """
#     api_url = "https://api.monday.com/v2"
#     headers = {
#         "Authorization": api_key,
#         "API-Version": "2025-04",
#         "Content-Type": "application/json"
#     }
#     payload = {"query": query}

#     for attempt in range(1, max_retries + 1):
#         logger.debug("Intento %d: ejecutando query=%s", attempt, query)
#         try:
#             r = requests.post(api_url, json=payload, headers=headers)
#             logger.debug("Respuesta status=%d body=%s", r.status_code, r.text)

#             if r.status_code == 403:
#                 logger.warning("Acceso denegado (403). Intento %d/%d", attempt, max_retries)
#                 time.sleep(retry_delay)
#                 continue

#             try:
#                 resp = r.json()
#             except ValueError:
#                 logger.error("JSON inválido en respuesta. Intento %d/%d", attempt, max_retries)
#                 time.sleep(retry_delay)
#                 continue

#             if "errors" in resp:
#                 logger.error("Errores GraphQL: %s", resp["errors"])
#                 if resp.get("error_code") == "ComplexityException":
#                     try:
#                         secs = int(resp["errors"][0].split()[-2]) + 1
#                     except Exception:
#                         secs = 5
#                     logger.info("Esperando %ds por ComplexityException", secs)
#                     time.sleep(secs)
#                     continue
#                 logger.warning("Error API desconocido. Intento %d/%d", attempt, max_retries)
#                 time.sleep(retry_delay)
#                 continue

#             return resp

#         except requests.RequestException as e:
#             logger.exception("Error de red en intento %d/%d", attempt, max_retries)
#             time.sleep(retry_delay)

#     logger.critical("Max retries alcanzados (%d). Abortando.", max_retries)
#     return {"errors": [{"message": "Max retries reached"}]}




import time
import requests
import logging
from typing import Any, Dict, Optional
from .exceptions import MondayAPIError

logger = logging.getLogger(__name__)

def monday_request(
    query: str,
    api_key: str,
    max_retries: int = 5,
    retry_delay: int = 3,
) -> Dict[str, Any]:
    """
    Ejecuta una petición GraphQL a Monday.com con:
      - Reintentos ante fallos HTTP graves o ComplexityException
      - Error inmediato ante errores GraphQL no retriables
    """
    api_url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "API-Version": "2025-07",
        "Content-Type": "application/json",
    }
    payload = {"query": query}

    for attempt in range(1, max_retries + 1):
        logger.debug("[Intento %d/%d] Query:\n%s", attempt, max_retries, query)
        try:
            r = requests.post(api_url, json=payload, headers=headers, timeout=10)
            logger.debug("Status=%d Body=%s", r.status_code, r.text)
            
            
            # --- NUEVO: reintentar si nos da 403 Forbidden ---
            if r.status_code == 403:
                logger.warning("HTTP 403 Forbidden (intento %d/%d). Reintentando tras %ds",
                               attempt, max_retries, retry_delay)
                time.sleep(retry_delay)
                continue
            

            # Reintentar ante HTTP 5xx
            if 500 <= r.status_code < 600:
                logger.warning("HTTP %d — retry %d/%d", r.status_code, attempt, max_retries)
                time.sleep(retry_delay)
                continue

            # Parseo JSON
            try:
                resp = r.json()
            except ValueError as e:
                logger.error("Respuesta no JSON. retry %d/%d", attempt, max_retries)
                time.sleep(retry_delay)
                continue

            # Si hay errores GraphQL:
            if "errors" in resp:
                errs = resp["errors"]
                code = resp.get("error_code") or errs[0].get("extensions", {}).get("code")
                # ComplexityException → reintentar
                if code in ("ComplexityException", "COMPLEXITY_BUDGET_EXHAUSTED"):
                    wait_secs = 10
                    try:
                        wait_secs = (
                            int(errs[0].get("extensions", {}).get("retry_in_seconds"))  # para COMPLEXITY_BUDGET_EXHAUSTED
                            or int(errs[0]["message"].split()[-2]) + 1  # fallback por si es ComplexityException clásico
                        )
                    except Exception:
                        pass
                    logger.info("%s — waiting %ds", code, wait_secs)
                    time.sleep(wait_secs)
                    continue
                # Cualquier otro error GraphQL → levantar YA
                logger.error("GraphQL error no retriable: %s", errs)
                raise MondayAPIError(errs)

            # Éxito
            return resp

        except requests.RequestException as e:
            logger.warning("RequestException: %s — retry %d/%d", e, attempt, max_retries)
            time.sleep(retry_delay)

    # Si agotamos reintentos de HTTP/Complexity
    raise MondayAPIError([{"message": "Max retries reached"}])
