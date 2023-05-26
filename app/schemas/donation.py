from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, NonNegativeInt, PositiveInt


class DonationBase(BaseModel):
    """
    Базовая модель для пожертвования, определяющая общие атрибуты для
    пожертвования.

    Атрибуты:
        - full_amount (PositiveInt): Общая сумма пожертвования.
        - comment (str, необязательно): Необязательный комментарий,
          предоставленный спонсором.
    """
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationCreate(DonationBase):
    """
    Модель для создания нового пожертвования. Наследуется от DonationBase.
    """
    pass


class DonationDB(DonationBase):
    """
    Модель для данных о пожертвованиях в базе данных. Наследуется от
    DonationBase.

    Атрибуты:
        - id (int): Уникальный идентификатор для пожертвования.
        - create_date (datetime): Дата и время, когда пожертвование было
          создано.
    """
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationAdminDB(DonationDB):
    """
    Модель для данных о пожертвованиях в базе данных, с дополнительными
    атрибутами для административного использования. Наследуется от DonationDB.

    Атрибуты:
        - user_id (int): Уникальный идентификатор пользователя, сделавшего
          пожертвование.
        - invested_amount (NonNegativeInt): Сумма пожертвования, которая была
          инвестирована.
        - fully_invested (bool): Флаг, указывающий, была ли инвестирована вся
          сумма пожертвования.
        - close_date (datetime, необязательно): Дата и время, когда
          пожертвование было полностью инвестировано.
    """
    user_id: int
    invested_amount: NonNegativeInt
    fully_invested: bool
    close_date: Optional[datetime]
