from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+psycopg://rea_user:rea_password@localhost:5432/realestateagent"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"

    # Security
    SECRET_KEY: str = "change-me-at-least-32-characters-long!!"
    JWT_PRIVATE_KEY_PATH: str = "./secrets/jwt_private.pem"
    JWT_PUBLIC_KEY_PATH: str = "./secrets/jwt_public.pem"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "RS256"

    # LLM
    LLM_MODEL_ID: str = "blissful_ishizaka_626/gemma4-cloud"
    OPENROUTER_API_KEY: str = ""
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "real-estate-agent"

    # Vector DB
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_PROPERTIES: str = "properties"
    QDRANT_COLLECTION_CONVERSATIONS: str = "conversations"
    QDRANT_COLLECTION_KB: str = "knowledge_base"

    # Embeddings
    OPENAI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMS: int = 1536

    # WhatsApp Business API (Meta)
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "rea-whatsapp-verify"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""

    # CRM
    ZOHO_CLIENT_ID: str = ""
    ZOHO_CLIENT_SECRET: str = ""
    ZOHO_REFRESH_TOKEN: str = ""
    HUBSPOT_API_KEY: str = ""

    # Email (SendGrid)
    SENDGRID_API_KEY: str = ""
    SENDGRID_FROM_EMAIL: str = "noreply@sceptreestate.com"

    # Object Storage (Cloudflare R2)
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "real-estate-agent-docs"
    R2_ENDPOINT: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Agent session memory TTL (seconds)
    SESSION_TTL_SECONDS: int = 86400  # 24 hours


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
