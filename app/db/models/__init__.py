# app/db/models/__init__.py
# Импортируем все модели для доступа через app.db.models
from .brand import Brand
from .category import Category
from .criteria import Criteria
from .role import Role
from .user import User
from .energy import Energy
from .suggestion import Suggestion
from .review import Review
from .rating import Rating
from .blacklist import Blacklist
from .user_role import UserRole