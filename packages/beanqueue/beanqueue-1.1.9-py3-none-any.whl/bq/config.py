import typing

from pydantic import Field
from pydantic import field_validator
from pydantic import PostgresDsn
from pydantic import ValidationInfo
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Config(BaseSettings):
    # Packages to scan for processor functions
    PROCESSOR_PACKAGES: list[str] = Field(default_factory=list)

    # Size of tasks batch to fetch each time from the database
    BATCH_SIZE: int = 1

    # How long we should poll before timeout in seconds
    POLL_TIMEOUT: int = 60

    # Interval of worker heartbeat update cycle in seconds
    WORKER_HEARTBEAT_PERIOD: int = 30

    # Timeout of worker heartbeat in seconds
    WORKER_HEARTBEAT_TIMEOUT: int = 100

    # which task model to use
    TASK_MODEL: str = "bq.Task"

    # which worker model to use
    WORKER_MODEL: str = "bq.Worker"

    # which event model to use
    EVENT_MODEL: str | None = "bq.Event"

    # Enable metrics HTTP server
    METRICS_HTTP_SERVER_ENABLED: bool = True

    # the metrics http server interface to listen
    METRICS_HTTP_SERVER_INTERFACE: str = ""

    # the metrics http server port to listen
    METRICS_HTTP_SERVER_PORT: int = 8000

    # default log level for metrics http server
    METRICS_HTTP_SERVER_LOG_LEVEL: int = 30

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "bq"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "bq"
    # The URL of postgresql database to connect
    DATABASE_URL: typing.Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(
        cls, v: typing.Optional[str], info: ValidationInfo
    ) -> typing.Any:
        if isinstance(v, str):
            return v
        # Notice: Older Pydantic version (2.7), PostgresDsn is an annotated MultiHostUrl object,
        #         we cannot use isinstance with PostgresDsn directly. We need to check and see if PostgresDsn
        #         is an annotated type or not before we decide how to check if the passed in object is an
        #         PostgresDsn or not.
        if typing.get_origin(PostgresDsn) is typing.Annotated:
            if isinstance(v, MultiHostUrl):
                return v
        else:
            if isinstance(v, PostgresDsn):
                return v
        if v is not None:
            raise ValueError("Unexpected DATABASE_URL type")
        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            path=f"{info.data.get('POSTGRES_DB') or ''}",
        )

    model_config = SettingsConfigDict(case_sensitive=True, env_prefix="BQ_")
