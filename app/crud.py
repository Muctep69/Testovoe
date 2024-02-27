from sqlalchemy.orm import Session
from app import models, schemas


# Создание нового пользователя
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)

    db.commit()
    db.refresh(db_user)

    return db_user


# Получение пользователя по его идентификатору
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# Получение пользователя по его имени пользователя
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# Получение списка пользователей
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


# Удаления пользователя
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(db_user)
    db.commit()


# Обновление данных пользователя
def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    for key, value in user_data.dict().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


# Создание новой заметки
def create_note(db: Session, note: schemas.NoteCreate, user_id: int):
    db_note = models.Note(**note.dict(), user_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


# Получение заметки по ее идентификатору
def get_note(db: Session, note_id: int, user_id: int):
    return db.query(models.Note).filter(models.Note.id == note_id, models.Note.user_id == user_id).first()


# Получение списка заметок пользователя
def get_notes_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Note).filter(models.Note.user_id == user_id).offset(skip).limit(limit).all()


# Обновление заметки
def update_note(db: Session, note_id: int, note_in: schemas.NoteUpdate, user_id: int):
    db_note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.user_id == user_id).first()
    if db_note:
        db_note.title = note_in.title
        db_note.content = note_in.content
        db.commit()
        db.refresh(db_note)
        return db_note


# Удаление заметки
def delete_note(db: Session, note_id: int, user_id: int):
    db_note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.user_id == user_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()
        return db_note
