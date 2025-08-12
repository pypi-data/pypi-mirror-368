from pydantic_settings import BaseSettings, SettingsConfigDict


class LsRestClientSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="lsrestclient_")
    insert_no_cache: bool = True
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 10
    redis_ttl: bool = True
    redis_ttl_offset: int = 3600
