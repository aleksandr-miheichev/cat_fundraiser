from typing import Optional

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    """
    Настройки приложения. Эти значения загружаются из переменных окружения.

    Атрибуты:
        - app_title (str, по умолчанию = 'Кошачий благотворительный фонд'):
          Название приложения.
        - description (str, по умолчанию = 'Сервис для поддержки котиков!'):
          Краткое описание приложения.
        - database_url (str,
          по умолчанию = 'sqlite+aiosqlite:///./fastapi.db'): параметры
          подключения к БД.
        - secret (str, по умолчанию = 'SECRET'): Секретный ключ, используемый
          для генерации токена ля пользователей.
        - first_superuser_email (EmailStr, необязательный): Адрес электронной
          почты первого суперпользователя.
        - first_superuser_password (str, необязательный): Пароль первого
          суперпользователя.
        - type (str, необязательный): тип сервисного аккаунта Google.
        - project_id (str, необязательный): ID проекта в Google Cloud.
        - private_key_id (str, необязательный): ID приватного ключа Google
          Cloud.
        - private_key (str, необязательный): приватный ключ Google Cloud.
        - client_email (str, необязательный): Email сервисного аккаунта Google
          Cloud.
        - client_id (str, необязательный): ID клиента Google Cloud.
        - auth_uri (str, необязательный): URI для авторизации в Google API.
        - token_uri (str, необязательный): URI для получения токена доступа к
          Google API.
        - auth_provider_x509_cert_url (str, необязательный): URL сертификата
          x509 провайдера аутентификации Google.
        - client_x509_cert_url (str, необязательный): URL сертификата x509
          клиента Google Cloud.
        - email (str, необязательный): Email, используемый для аутентификации в
          Google API.
    """
    app_title: str = 'Кошачий благотворительный фонд'
    description: str = 'Сервис для поддержки котиков!'
    database_url: str = 'sqlite+aiosqlite:///./cat_fund.db'
    secret: str = 'SECRET'
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    type: Optional[str] = None
    project_id: Optional[str] = None
    private_key_id: Optional[str] = None
    private_key: Optional[str] = None
    client_email: Optional[str] = None
    client_id: Optional[str] = None
    auth_uri: Optional[str] = None
    token_uri: Optional[str] = None
    auth_provider_x509_cert_url: Optional[str] = None
    client_x509_cert_url: Optional[str] = None
    email: Optional[str] = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
