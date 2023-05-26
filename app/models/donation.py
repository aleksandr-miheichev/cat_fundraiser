from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import FinancialTransactionBase


class Donation(FinancialTransactionBase):
    """
    Представляет пожертвование, сделанное пользователем.

    Атрибуты:
        - user_id (int): идентификатор пользователя, сделавшего пожертвование.
          Это внешний ключ, ссылающийся на поле 'id' в таблице 'users'.
        - comment (str): необязательный комментарий, сделанный пользователем
          при совершении пожертвования.
    """
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    def __repr__(self):
        return super().__repr__() + (
            f", user_id={self.user_id}, comment='{self.comment[:20]}...'"
        )
