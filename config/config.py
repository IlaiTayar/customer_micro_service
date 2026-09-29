from pydantic_settings import BaseSettings


class Config(BaseSettings):
    MYSQL_USER: str = "user"
    MYSQL_PASSWORD: str = "password"
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "main"

    DATABASE_URL: str = f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
    TV_MAZE_BASE_URL: str = "https://api.tvmaze.com"
    SELLER_SERVICE_BASE_URL: str = "http://localhost:8001"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_TTL: int = 100