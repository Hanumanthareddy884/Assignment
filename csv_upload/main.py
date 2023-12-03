from fastapi import FastAPI, Depends,File, UploadFile, Request
from . import models
from .database import engine,SessionLocal
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse
import uvicorn


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

@app.post("/upload")
def uploads(file: UploadFile = File(...),db:Session = Depends(get_db)):
    contents = file.file.read()
    buffer = BytesIO(contents)
    df = pd.read_csv(buffer)
    data = df.to_dict(orient="records")
    buffer.close()
    file.file.close()
    for rows in data:
        new_user= models.Users(name = rows['Name'],age = rows['Age'])
        db.add(new_user)

    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/", status_code=302)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
