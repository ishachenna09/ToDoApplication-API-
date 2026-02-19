from fastapi import FastAPI
from database import engine
import models
from routers import auth, todos, admin, users


app = FastAPI ()
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
# this includes all routers in auth file


models.Base.metadata.create_all (bind=engine)

