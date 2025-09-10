# Импортируем нужное из SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship
# Импортируем time для работы с временными метками
import time

# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели Blacklist
class Blacklist(Base):
    # Указываем имя таблицы
    __tablename__ = "blacklist"

    # Определяем поле id как первичный ключ
    id = Column(Integer, primary_key=True, index=True)
    # Определяем поле user_id
    user_id = Column(BigInteger, nullable=False, unique=True)
    # Причина добавления в черный список
    reason = Column(String, nullable=True)
    # Определяем поле created_at с текущей датой по умолчанию
    created_at = Column(BigInteger, default=lambda: int(time.time()))  # Unix timestamp в секундах
    # Определяем связь с моделью User, даже если пользователь еще не зарегистрирован
    user = relationship(
        "User",
        back_populates="blacklist_entry",
        primaryjoin="foreign(Blacklist.user_id)==User.id",
        uselist=False
    )