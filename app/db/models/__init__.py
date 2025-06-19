# app/db/models/__init__.py
# Импортируем все модели для доступа через app.db.models
from .brand import Brand
from .category import Category
from .energy import Energy
from .user import User
from .role import Role
from .user_role import UserRole
from .criteria import Criteria
from .review import Review
from .rating import Rating