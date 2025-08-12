DOTENV_API_KEY_NAME: str = "API_KEY"
DOTENV_CATALOG_ID_NAME: str = "CATALOG_ID"

DBT_CLI_ARGS: list = [
    "--quiet",
    "--no-print",
    "compile",
]

GPT_TEMPERATURE: float = 0.3
GPT_MAX_TOKENS: int = 8000
GPT_RESPONSE_FORMAT: str = "json"
