from src.termina.client import Termina
from os import environ
host = "https://app.termina.dev" if environ.get("IS_DEV") == "true" else "https://app.termina.ai"
cli = Termina(api_key=environ["API_KEY"], base_url=host)
token = cli._client_wrapper.get_headers()["Authorization"].split(" ")[-1]
print(token)

# TO RUN:
# API_KEY="YOUR_API_KEY_HERE" poetry run python generate_bearer_token_from_sdk.py
