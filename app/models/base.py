from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer
from sqlalchemy.orm import validates

from app.core.db import Base


class FinancialTransactionBase(Base):
    """
    Абстрактный базовый класс для финансовых операций.

    Атрибуты:
        - full_amount (int, gt=0): общая сумма транзакции.
        - invested_amount (int, по умолчанию = 0): сумма транзакции, которая
          была инвестирована или распределена.
        - fully_invested (bool, по умолчанию = False): флаг, указывающий, была
          ли инвестирована вся сумма.
        - create_date (datetime): дата и время, когда была создана транзакция.
          Это значение автоматически устанавливается при создании транзакции.
        - close_date (datetime): дата и время, когда транзакция была закрыта.
          Это значение автоматически устанавливается, когда вся сумма была
          инвестирована.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.invested_amount is None:
            self.invested_amount = 0

    __abstract__ = True
    __table_args__ = (
        CheckConstraint(
            sqltext='full_amount >= 0',
            name='check_full_amount_positive'
        ),
        CheckConstraint(
            sqltext='invested_amount <= full_amount',
            name='check_invested_amount_not_exceed_full_amount'
        ),
    )

    full_amount = Column(Integer, nullable=False)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime, default=datetime.now)
    close_date = Column(DateTime)

    @validates('invested_amount')
    def validate_invested_amount(self, key, invested_amount):
        """
        Проверяет значение инвестированной суммы.

        Атрибуты:
            - key (str): имя проверяемого атрибута ('invested_amount').
            - invested_amount (float): значение, которое нужно проверить.

        Возвращает:
            Проверенная инвестированная сумма.
        """
        if invested_amount == self.full_amount and not self.fully_invested:
            self.mark_as_fully_invested()
        return invested_amount

    def mark_as_fully_invested(self):
        """
        Отметить пожертвование или проект как полностью распределённое или
        проинвестированное.
        """
        self.fully_invested = True
        self.close_date = datetime.now()

    def __repr__(self):
        return (
            f'full_amount={self.full_amount}, '
            f'invested_amount={self.invested_amount}, '
            f'fully_invested={self.fully_invested}, '
            f'create_date={self.create_date}, '
            f'close_date={self.close_date}'
        )
