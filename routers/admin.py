from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
# import models
from starlette import status 
from pydantic import BaseModel, Field
from models import Todos
from .auth import get_current_user
# from routers import auth, todos


router = APIRouter (
     prefix = '/admin',
    tags = ['admin']
)

def get_db ():
    db = SessionLocal() #conecction  with db
    try:
        yield db 
    finally:
        db.close() # close connection 
        
# depend() -> a way to declare things that require for the application / function to work by injecting the dependencies
db_dependency = Annotated[Session, Depends(get_db)]  

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency, db:db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Autherisation failed")
    return db.query(Todos).all()


@router.delete("todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db:db_dependency, todo_id:int=Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401, detail = 'Autherisation failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:  
        raise HTTPException(status_code=401, detail="Todo not found")
    db.query(Todos).filter(Todos.id ==todo_id ).delete()