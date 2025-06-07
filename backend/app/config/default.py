from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth
from app.utils.s3_manager import S3Client
from app.utils.payment_manager import PaymentAPI


class DefaultSettings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: str

    BACKEND_HOST: str
    BACKEND_PORT: int
    PATH_PREFIX : str

    VUE_APP_DNS_URL: str

    API_KEY: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    AWS_ACCESS_KEY_ID: str 
    AWS_SECRET_ACCESS_KEY: str 
    AWS_BUCKET_NAME: str

    CRYPTO_API_KEY: str 

    PWD_CONTEXT: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    model_config = SettingsConfigDict(env_file="../.env", extra='ignore') 

    @property
    def OAUTH2_SCHEME(self) -> OAuth2PasswordBearer:
        return OAuth2PasswordBearer(
            tokenUrl=f"{self.PATH_PREFIX}/user/token"
        )

    @property
    def database_settings(self) -> dict:
        """
        Get all settings for connection with database.
        """
        return {
            "database": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )
    
    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )
    
    @property
    def google_oauth(self) -> OAuth:
        """
        Get google OAuth schema
        """
        oauth = OAuth()
        oauth.register(
            name='google',
            client_id=self.GOOGLE_CLIENT_ID,
            client_secret=self.GOOGLE_CLIENT_SECRET,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            api_base_url='https://www.googleapis.com/oauth2/v3/',
            client_kwargs={'scope': 'openid email profile'},
        )
        return oauth
    
    @property
    def s3_client(self) -> S3Client:
        return S3Client(
            access_key=self.AWS_ACCESS_KEY_ID,
            secret_key=self.AWS_SECRET_ACCESS_KEY,
            endpoint_url='https://storage.yandexcloud.net',
            bucket_name=self.AWS_BUCKET_NAME
        )
    
    @property
    def pay_client(self) -> PaymentAPI:
      return PaymentAPI(api_key=self.CRYPTO_API_KEY)

settings: DefaultSettings | None = None

def get_settings() -> DefaultSettings:
    global settings
    if settings is None:
        settings = DefaultSettings()
    return settings
