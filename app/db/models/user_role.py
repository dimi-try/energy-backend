# Импортируем Column, Integer, ForeignKey из SQLAlchemy
from sqlalchemy import Column, Integer, BigInteger, ForeignKey
# Импортируем relationship для определения связей
from sqlalchemy.orm import relationship
# Импортируем базовый класс
from app.db.models.base import Base

# Определяем класс модели UserRole
class UserRole(Base):
    # Указываем имя таблицы
    __tablename__ = "user_roles"

    # Определяем поле user_id как первичный ключ и внешний ключ
    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    # Определяем поле role_id как первичный ключ и внешний ключ
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)

    # Определяем связь с пользователем
    user = relationship("User", back_populates="roles")
    # Определяем связь с ролью
    role = relationship("Role", back_populates="users")