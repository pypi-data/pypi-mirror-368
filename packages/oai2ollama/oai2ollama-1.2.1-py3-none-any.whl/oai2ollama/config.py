from os import getenv
from sys import stderr
from typing import Literal

from pydantic import Field, HttpUrl, ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "cli_parse_args": True,
        "cli_kebab_case": True,
        "cli_ignore_unknown_args": True,
        "extra": "ignore",
        "cli_shortcuts": {
            "capacities": "c",
        },
    }

    api_key: str = Field(getenv("OPENAI_API_KEY", ...), description="API key for authentication")  # type: ignore
    base_url: HttpUrl = Field(getenv("OPENAI_BASE_URL", ...), description="Base URL for the OpenAI-compatible API")  # type: ignore
    capacities: list[Literal["tools", "insert", "vision", "embedding", "thinking"]] = []
    host: str = Field("localhost", description="IP / hostname for the API server")


try:
    env = Settings()  # type: ignore
    print(env, file=stderr)
except ValidationError as err:
    print("\n  Error: invalid config:\n", file=stderr)
    for error in err.errors():
        print(" ", "".join(f".{x}" if isinstance(x, str) else f"[{x}]" for x in error["loc"]).lstrip(".") + ":", error["msg"], file=stderr)
    print(file=stderr)
    exit(1)
