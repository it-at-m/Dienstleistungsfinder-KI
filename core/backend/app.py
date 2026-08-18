# ruff: noqa: E402 (no import at top level) suppressed on this file as we need to inject the truststore before importing the other modules

from dotenv import load_dotenv
from truststore import inject_into_ssl

inject_into_ssl()
load_dotenv()

import argparse

import uvicorn
from backend import backend

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--development", action="store_true", help="Run the server in development mode")
    args = parser.parse_args()

    host = "localhost" if args.development else "0.0.0.0"

    uvicorn.run(backend, host=host, port=8080, log_config="logconf.yaml")
