from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud, auth
from fastapi.security import OAuth2PasswordRequestForm
from app.database import get_db
from app.auth import get_current_user
from typing import List, Optional
from datetime import datetime
from datetime import timedelta

app = FastAPI()



@app.post("/token", operation_id="login_for_access_token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Получаем пользователя из базы данных
    user = auth.authenticate_user(form_data.username, form_data.password, db)

    # Проверяем, найден ли пользователь и совпадает ли введенный пароль с хэшированным паролем пользователя
    if user:
        # Если все проверки прошли успешно, генерируем JWT токен
        expires_delta = timedelta(minutes=15)
        access_token = auth.create_access_token(data={"sub": user.username},expires_delta=expires_delta)
        return {"access_token": access_token, "token_type": "bearer"}

    # Если пользователь не найден или пароль неверный, возбуждаем исключение
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )



# Эндпоинты для пользователей
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    check_email = crud.get_user_by_email(db, user.email)
    check_user = crud.get_user_by_username(db, user.username)
    if check_email:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    if check_user:
        raise HTTPException(status_code=400, detail="User with this username already exists")
    # Хешируем пароль перед созданием пользователя
    hashed_password = auth.get_password_hash(user.password)
    # Заменяем пароль на хешированный в объекте пользователя
    user_data = schemas.UserCreate(username=user.username, email=user.email, password=hashed_password)
    # Создаем пользователя с хешированным паролем
    return crud.create_user(db=db, user=user_data)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user(db=db, user_id=user_id)

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):

    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own user data")

    if user_update.password:
        user_update.password=auth.get_password_hash(user_update.password)
    updated_user = crud.update_user(db, user_id, user_update)



    return updated_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):

    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own account")

    deleted_user = crud.delete_user(db, user_id)


    return {"message": "User deleted successfully"}


# Эндпоинты для заметок

@app.post("/notes/", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cr_note= crud.create_note(db=db, note=note, user_id=current_user.id)
    return cr_note


@app.put("/notes/{note_id}", response_model=schemas.Note)
def update_note(note_id: int, note_in: schemas.NoteUpdate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_note = crud.get_note(db, note_id, user_id=current_user.id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    updated_note = crud.update_note(db, note_id, note_in, user_id=current_user.id)
    return updated_note


@app.delete("/notes/{note_id}", response_model=schemas.Note)
def delete_note(note_id: int, current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    db_note = crud.get_note(db, note_id, user_id=current_user.id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    deleted_note = crud.delete_note(db, note_id, user_id=current_user.id)
    return deleted_note




@app.get("/notes/", response_model=List[schemas.Note])
def read_notes(filter_title: Optional[str] = None, filter_created_at: Optional[datetime] = None,current_user: schemas.User = Depends(auth.get_current_user),db: Session = Depends(get_db)):
    # Получаем список заметок пользователя
    notes = crud.get_notes_by_user(db, user_id=current_user.id)

    # Применяем фильтры, если они заданы
    if filter_title:
        notes = [note for note in notes if filter_title.lower() in note.title.lower()]

    if filter_created_at:
        notes = [note for note in notes if note.created_at >= filter_created_at]

    return notes





