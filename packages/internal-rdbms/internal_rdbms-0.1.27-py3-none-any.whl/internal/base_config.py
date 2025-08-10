from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    DEBUG: bool = False
    RUN_PORT: int = 5000
    TIME_ZONE: str = "Asia/Taipei"

    OPEN_API_URL: str = "/openapi.json"

    # Request
    REQUEST_VERIFY_SSL: bool = True
    REQUEST_PROXY: str = ''
    REQUEST_RETRY_COUNT: int = 2
    REQUEST_RETRY_DELAY_INITIAL_SECONDS: float = 1.0
    REQUEST_RETRY_DELAY_FACTOR: float = 1.5
    REQUEST_RETRY_DELAY_RANDOM_JITTER_MIN: float = 0.0
    REQUEST_RETRY_DELAY_RANDOM_JITTER_MAX: float = 0.5
    REQUEST_CONN_POOL_TIMEOUT: float = 5.0
    REQUEST_CONN_TIMEOUT: float = 5.0
    REQUEST_WRITE_TIMEOUT: float = 5.0
    RESPONSE_READ_TIMEOUT: float = 10.0

    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_KEY: str = ""
    AWS_REGION: str = ""
    AWS_PARAMETER_PATH_PREFIX: str = ""
    AWS_LOGGROUP_NAME: str = ""

    # MariaDB
    DATABASE_HOST: str = ''
    DATABASE_USERNAME: str = ''
    DATABASE_PASSWORD: str = ''
    DATABASE_PORT: int = 3306
    DATABASE_NAME: str = ""

    # Exception Notify
    WEBHOOK_BASE_URL: str = ""
    WEBHOOK_RETRY_COUNT: int = 5
    WEBHOOK_RETRY_DELAY_INITIAL_SECONDS: float = 1.0
    WEBHOOK_RETRY_DELAY_FACTOR: float = 2.0
    WEBHOOK_RETRY_DELAY_RANDOM_JITTER_MIN: float = 0.0
    WEBHOOK_RETRY_DELAY_RANDOM_JITTER_MAX: float = 0.5

    class Config:
        case_sensitive = False
