from sqlalchemy import Column, String, Text

from app.models.base import FinancialTransactionBase


class CharityProject(FinancialTransactionBase):
    """
    Представляет благотворительный проект, требующий финансирования.

    Атрибуты:
        - name (str, max_length=100): уникальное название проекта.
        - description (str): описание проекта.
    """
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return super().__repr__() + (
            f", name='{self.name}', description='{self.description[:20]}...'"
        )
