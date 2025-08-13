from sqlalchemy.orm import Session
from app.db.models import Blacklist, User
from app.schemas.blacklist import BlacklistCreate

def create_blacklist_entry(db: Session, blacklist: BlacklistCreate):
    """
    Добавляет пользователя в черный список, даже если пользователь еще не зарегистрирован.
    """
    # Проверяем, уже ли пользователь в черном списке
    existing_entry = db.query(Blacklist).filter(Blacklist.user_id == blacklist.user_id).first()
    if existing_entry:
        return None
    db_blacklist = Blacklist(
        user_id=blacklist.user_id,
        reason=blacklist.reason
    )
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    # Проверяем, существует ли пользователь, чтобы добавить username
    db_user = db.query(User).filter(User.id == blacklist.user_id).first()
    db_blacklist.username = db_user.username if db_user else "Пользователь не зарегистрирован"
    return db_blacklist

def get_blacklist_entry(db: Session, user_id: int):
    """
    Получает запись черного списка по user_id.
    """
    entry = db.query(Blacklist).filter(Blacklist.user_id == user_id).first()
    if entry:
        user = db.query(User).get(entry.user_id)
        entry.username = user.username if user else "Пользователь не зарегистрирован"
    return entry

def get_all_blacklist_entries(db: Session, skip: int = 0, limit: int = 100):
    """
    Получает список всех записей черного списка.
    """
    query = (
        db.query(Blacklist)
        .join(User, Blacklist.user_id == User.id, isouter=True)
        .order_by(Blacklist.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = query.all()
    for entry in result:
        entry.username = entry.user.username if entry.user else "Пользователь не зарегистрирован"
    return result

def delete_blacklist_entry(db: Session, user_id: int):
    """
    Удаляет пользователя из черного списка.
    """
    db_entry = db.query(Blacklist).filter(Blacklist.user_id == user_id).first()
    if not db_entry:
        return False
    db.delete(db_entry)
    db.commit()
    return True