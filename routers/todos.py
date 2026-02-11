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
     prefix = '/Todos',
    tags = ['Todos']
)
# app.include_router(auth.router)
# this includes all routers in auth file


# models.Base.metadata.create_all (bind=engine)

def get_db ():
    db = SessionLocal() #conecction  with db
    try:
        yield db 
    finally:
        db.close() # close connection 
        
# depend() -> a way to declare things that require for the application / function to work by injecting the dependencies
db_dependency = Annotated[Session, Depends(get_db)]  

user_dependency = Annotated[dict, Depends(get_current_user)]

# pydantic for post request 

class TodoRequest (BaseModel):
    title: str = Field (min_length=3 ,max_length=100)
    description: str = Field (min_length=3 ,max_length=100)
    priority:int = Field (gt=0,lt=6)
    complete: bool 
    
        
@router.get("/", status_code=status.HTTP_200_OK)       
async def read_All(user:user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependency, db:db_dependency, todo_id:int=Path(gt=0)) : #path parameter validation >0
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
#  to write on next line add \ 
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code =404, detail = 'Todo Id not found')


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, 
                      db:db_dependency, 
                      todo_request: TodoRequest):
    
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get('id'))
    
    db.add(todo_model)
    db.commit()
    
@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency,
                      user:user_dependency,
                      todo_request: TodoRequest ,
                      todo_id:int = Path(gt=0)
                      ):
    if user is None:
        raise HTTPException(status_code=401, detail="Autherisation failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id==user.get('id')).first()
        
    if todo_model is None:
        raise HTTPException(status_code=404, detail= "Todo id not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description  
    todo_model.priority = todo_request.priority  
    todo_model.complete = todo_request.complete
    
    db.add(todo_model)
    db.commit()
    
    
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency, db:db_dependency, todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    
    todo_model =  db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id==user.get('id')).first()
    
    if todo_model is None:
        raise HTTPException(status_code=404, detail= 'ToDo Id not found ')    
    db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id==user.get('id')).delete()
    
    db.commit()