from fastapi import FastAPI, Depends,File, UploadFile, Request
from pydantic import BaseModel
from . import schemas,models
from .database import engine,SessionLocal
from sqlalchemy.orm import Session
import pandas as pd
from io import StringIO,BytesIO
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse



app= FastAPI()
models.Base.metadata.create_all(engine)


def get_db():
    db =SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates= Jinja2Templates(directory = "templates")

@app.get('/',response_class=HTMLResponse)
async def all(request:Request,db:Session = Depends(get_db)):
    users = db.query(models.Users).all()
    return templates.TemplateResponse("index.html",{"request":request, "title":"MagicPitch LLC","users":users})

@app.post('/register',status_code=201)
def add(request:schemas.User,db:Session = Depends(get_db)):
    new_user= models.Users(name = request.name,age = request.age)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/upload")
def upload(file: UploadFile = File(...),db:Session = Depends(get_db)):
    contents = file.file.read()
    buffer = BytesIO(contents)
    df = pd.read_csv(buffer)
    buffer.close()
    file.file.close()

    return df.to_dict(orient='records')