import enum
import json
import os
from pathlib import Path
from typing import Optional, Any, Dict, List

from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
from pydantic.v1 import BaseSettings, validator, PostgresDsn, AnyUrl, Field


def get_absolute_path(path: str):
    directory = os.getcwd()
    test = 'test'
    main = 'main'
    if test in directory:
        directory = directory.split(sep=test)[0]
    if main in directory:
        directory = directory.split(sep=main)[0]
    directory = os.path.join(directory, path)

    return directory


class SupportedDB(str, enum.Enum):
    MYSQL = 'MYSQL'
    MSSQL = 'MSSQL'
    POSTGRES = 'POSTGRES'
    ORACLE = 'ORACLE'

class Environment(str, enum.Enum):
    PRODUCTION = "prod"
    STAGING = "staging"
    TEST = "test"
    DEVELOPMENT = "dev"
    LOCAL = "local"

class TemplatingEngine(str, enum.Enum):
    JINJA2 = "jinja2"


class AppodusBaseSettings(BaseSettings):
    APP_NAME: str = "appodus"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    ALLOW_AUTH_BYPASS: bool = False  # Optional
    ENABLE_OUT_MESSAGING: bool = False
    BASE_DIR: str = str(Path(__file__).parent.parent) # Used for accessing local files, e.g message templates

    APP_DOMAIN: str = "http://localhost:8000"
    SHOW_API: bool = True

    # APPODUS
    APPODUS_SERVICES_URL: str = "https://8d39e6e80670.ngrok-free.app"
    APPODUS_CLIENT_ID: str = "b91b0ecb-7bd7-4630-91cb-af20549c8667"
    APPODUS_CLIENT_SECRET: str = "kQWzK2eeNM_9uN16ZmbHCdJNRSw9UQ5eF2PhwqZRz2I="
    APPODUS_CLIENT_SECRET_ENCRYPTION_KEY: str = '1dXgFqcjihJaeCBIYWZf-kjWvBbXkBpxT-5IOWY-G0Y='

    APPODUS_CLIENT_REQUEST_EXPIRES_SECONDS: Optional[int] = 60 * 5 # 5mins

    # Enable / Disable Services
    DISABLE_RATE_LIMITING: bool = False

    # LOGGING
    LOG_LEVEL: Optional[str] = 'DEBUG'
    LOGGER_FILE: Optional[str] = 'logs.txt'
    LOGGER_FILE_PATH: Optional[str] = '/tmp/logs'

    # ACTIVES
    ACTIVE_TEMPLATING_ENGINE: TemplatingEngine = TemplatingEngine.JINJA2

    # TOKEN
    OTP_TOKEN_EXPIRE_SECONDS: Optional[int] = 60 * 5 # 5 mins
    EMAIL_OTP_TOKEN_EXPIRE_SECONDS: Optional[int] = 60 * 30 # 30 mins
    ACCESS_TOKEN_EXPIRE_SECONDS: Optional[int] = 60 * 60 * 24 * 8
    REFRESH_TOKEN_EXPIRE_SECONDS: Optional[int] = 60 * 60 * 24 * 8
    CACHE_DATA_EXPIRES_SECONDS: Optional[int] = 60 * 60 * 24 * 8 # Redis Default

    # WEBHOOK
    WEBHOOK_PATH: Optional[str] = "/webhooks"

    # AUTH
    AUTH_URL_PATH: str = "/auths"
    # SOCIAL LOGIN
    SOCIAL_LOGIN_CALLBACK_PATH: Optional[str] = "/socials"
    # GOOGLE
    GOOGLE_AUTH_BASE_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_CLIENT_ID: Optional[str]
    GOOGLE_CLIENT_SECRET: Optional[str]
    # FACEBOOK
    FACEBOOK_AUTH_BASE_URL: str = "https://www.facebook.com/v22.0/dialog/oauth"
    FACEBOOK_APP_ID: Optional[str]
    FACEBOOK_APP_SECRET: Optional[str]
    # APPLE
    APPLE_AUTH_BASE_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    APPLE_TEAM_ID: Optional[str]
    APPLE_CLIENT_ID: Optional[str]
    APPLE_KEY_ID: Optional[str]
    APPLE_PRIVATE_KEY: Optional[str]

    # AUTHJWT
    AUTHJWT_SECRET_KEY: str = "auth_jwt_s3cr3t"
    # Configure application to store and get JWT from cookies
    AUTHJWT_TOKEN_LOCATION: List[str] =  Field(default_factory=lambda: ["cookies"], env=None)
    # Only allow JWT cookies to be sent over https
    AUTHJWT_COOKIE_SECURE: bool = True
    # Enable csrf double submit protection. default is True
    AUTHJWT_COOKIE_CSRF_PROTECT: bool = True
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    AUTHJWT_COOKIE_SAMESITE: str = 'none' # Must be 'none' when AUTHJWT_COOKIE_SECURE = True
    # AUTHJWT_ACCESS_COOKIE_KEY: str = 'Host-access_token'
    # AUTHJWT_REFRESH_COOKIE_KEY: str = 'Host-refresh_token'
    # AUTHJWT_ALGORITHM: str = ""
    # MESSAGING
    EMAIL_FROM_ADDRESS: Optional[str] = "noreply@example.com"
    EMAIL_FROM_NAME: str = "veriprops"
    EMAIL_SUBJECTS: Dict[str, str] = {
        "otp_subject": "Extra Security: Your 2FA Code Inside",
        "account_activation_subject": "Important: Your Account Status",
        "account_deactivation_subject": "Important: Your Account Status",
        "email_verification_subject": "One Quick Step: Verify Your Email",
        "login_diff_device_security_alert_subject": "New Login Detected - Was This You?",
        "name_update_success_subject": "Your Name Has Been Updated ✅",
        "new_feature_announcement_subject": "Exciting New Features Just Launched!",
        "new_user_email_verification_subject": "One Quick Step: Verify Your Email",
        "new_user_welcome_subject": "Welcome to Your Real Estate Journey! 🏡",
        "password_reset_request_subject": "Reset Your Password - Quick & Easy",
        "password_update_success_subject": "Your Password Has Been Updated ✅",
        "phone_verification_subject": "Verify Your Phone - Stay Secure",
    }
    SMS_SENDER_ID: Optional[str] = "veriprops"
    SMS_TTL = 25000
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = "766140453239478"
    MESSAGE_TEMPLATE_DIR: str = "resources/templates"
    MESSAGING_BRAND_NAME: str = "appodus"

    # REDIS
    REDIS_ENABLED: Optional[bool] = False
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[str] = None
    REDIS_USERNAME: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: Optional[str] = '0'
    REDIS_THREAD_SLEEP_TIME: Optional[float] = 0.01

    # DB
    ACTIVE_DB: Optional[SupportedDB] = SupportedDB.POSTGRES
    DB_SCHEME: Optional[str] = None
    DB_SERVER: Optional[str] = "sqlite:///"
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_ADDITIONAL_CONFIG: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[Any] = None
    DB_ENABLE_LOGS: Optional[bool] = True
    DB_ENABLE_LOG_POOL: Optional[bool] = True
    DB_MAIN_THREAD_CONTEXT_ID: int = 12345

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        db_url = v
        if isinstance(v, str):
            return v

        if SupportedDB.POSTGRES == values.get("ACTIVE_DB"):
            db_url = PostgresDsn.build(
                scheme=values.get("DB_SCHEME"),
                user=values.get("DB_USER"),
                password=values.get("DB_PASSWORD"),
                host=values.get("DB_SERVER"),
                port=values.get("DB_PORT"),
                path=f"/{values.get('DB_NAME') or ''}?{values.get('DB_ADDITIONAL_CONFIG')}",
            )
        elif SupportedDB.MYSQL == values.get("ACTIVE_DB"):
            db_url = AnyUrl.build(
                scheme=values.get("DB_SCHEME"),
                user=values.get("DB_USER"),
                password=values.get("DB_PASSWORD"),
                host=values.get("DB_SERVER"),
                port=values.get("DB_PORT"),
                path=f"/{values.get('DB_NAME') or ''}?{values.get('DB_ADDITIONAL_CONFIG')}",
            )
        else:
            db_path = get_absolute_path(os.path.join("main", "app", "db"))
            db = os.path.join(db_path, values.get('DB_NAME'))
            db_url = f"{values.get('DB_SERVER')}{db}?{values.get('DB_ADDITIONAL_CONFIG')}"

            print('db_url: ', db_url)

        return db_url

    class Config:
        env_file = get_absolute_path(f'.env.{os.getenv("appodus_active_env", "local")}')

        load_dotenv(dotenv_path=env_file)
        print(f'env_file: {env_file}')
        env_file_encoding = "utf-8"
        case_sensitive = False

    def set_env_vars(self):
        """Set all settings as environment variables."""
        for key, value in self.dict().items():
            os.environ[key.upper()] = str(value)

        # Set the whole object, for use in this utils project
        settings_dict = jsonable_encoder(self)
        os.environ["APPODUS_SETTINGS"] = json.dumps(settings_dict)


appodus_base_settings = AppodusBaseSettings()
appodus_base_settings.set_env_vars() # Set the env vars in os.environ