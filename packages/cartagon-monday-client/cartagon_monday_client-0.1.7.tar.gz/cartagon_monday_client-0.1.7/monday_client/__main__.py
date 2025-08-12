#!/usr/bin/env python3
import argparse
import logging
from .client import MondayClient

def parse_args():
    parser = argparse.ArgumentParser(
        description="CLI para ejecutar consultas básicas contra Monday.com"
    )
    parser.add_argument(
        "--api-key",
        "-k",
        required=True,
        help="Tu API Key de Monday.com"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # subcomando: test_connection
    sub.add_parser("test", help="Comprueba que la conexión funciona")

    # subcomando: get_boards
    p = sub.add_parser("boards", help="Lista tableros")
    p.add_argument("--limit", "-l", type=int, default=10)
    p.add_argument("--page", "-p", type=int, default=1)

    return parser.parse_args()

def main():
    # Configuración básica de logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    args = parse_args()
    client = MondayClient(api_key=args.api_key)

    if args.command == "test":
        ok = client.test_connection()
        print("✅ Conexión exitosa" if ok else "❌ Falló la conexión")
    elif args.command == "boards":
        boards = client.get_boards(limit=args.limit, page=args.page)
        for b in boards:
            print(f"- {b['id']}: {b['name']}")
    else:
        print("Comando no reconocido.")

if __name__ == "__main__":
    main()
