from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    Extra,
    Field,
    NonNegativeInt,
    PositiveInt,
    validator
)

FIELDS_CAN_BE_EMPTY = 'Поля не могут быть пустыми!'
LONG_NAME = 'Имя слишком длинное!'


class CharityProjectBase(BaseModel):
    """
    Базовая модель для благотворительного проекта.

    Атрибуты:
        - name (str, необязательно): название благотворительного проекта.
          Максимальная длина - 100 символов.
        - description (str, необязательно): краткое описание
          благотворительного проекта.
        - full_amount (gt=0, необязательно): общая цель по сбору средств для
          благотворительного проекта.
    """
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str]
    full_amount: Optional[PositiveInt]

    class Config:
        extra = Extra.forbid


class CharityProjectUpdate(CharityProjectBase):
    """
    Модель для обновления благотворительного проекта. Наследуется от
    CharityProjectBase.
    """

    @validator('*')
    def validate_no_empty_fields(cls, value):
        """
        Проверяет, что ни одно поле в запросе на обновление не является пустым.

        Аргументы:
            - value: значение поля, которое нужно проверить.

        Вызывает:
            ValueError: если значение пустое.

        Возвращает:
            Исходное значение, если оно не пустое.
        """
        if not value:
            raise ValueError(FIELDS_CAN_BE_EMPTY)
        return value


class CharityProjectCreate(CharityProjectBase):
    """
    Модель для создания нового благотворительного проекта. Наследуется от
    CharityProjectBase.

    Атрибуты:
        - name (str, max_length=100): название благотворительного проекта.
        - description (str): подробное описание благотворительного проекта.
        - full_amount (PositiveInt): общая сумма средств, необходимых для
          благотворительного проекта.
    """
    name: str = Field(..., max_length=100)
    description: str
    full_amount: PositiveInt

    @validator('name', 'description')
    def check_fields(cls, value):
        """
        Проверяет, что поля 'name' и 'description' не пустые.

        Аргументы:
            - value (str): значение поля, которое нужно проверить.

        Вызывает:
            ValueError: если значение пустое.

        Возвращает:
            str: проверенное значение.
        """
        if not value:
            raise ValueError(FIELDS_CAN_BE_EMPTY)
        return value

    @validator('name')
    def check_name_length(cls, value):
        """
        Проверяет, что поле 'name' не длиннее 100 символов.

        Аргументы:
            - value (str): значение поля 'name' для проверки.

        Вызывает:
            ValueError: если 'name' длиннее 100 символов.

        Возвращает:
            str: проверенное 'name'.
        """
        if len(value) > 100:
            raise ValueError(LONG_NAME)
        return value


class CharityProjectDB(CharityProjectCreate):
    """
    Модель для благотворительного проекта, хранящегося в базе данных.
    Наследуется от CharityProjectCreate.

    Атрибуты:
        - id (int): уникальный идентификатор благотворительного проекта.
        - invested_amount (ge=0): сумма, которая уже была пожертвована в
          пользу проекта.
        - fully_invested (bool, по умолчанию = False): булевский флаг,
          указывающий, достиг ли проект своей цели по сбору средств.
        - create_date (datetime): дата создания проекта.
        - close_date (datetime, необязательно): дата, когда проект был закрыт.
    """
    id: int
    invested_amount: NonNegativeInt = Field(0)
    fully_invested: bool = Field(False)
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
