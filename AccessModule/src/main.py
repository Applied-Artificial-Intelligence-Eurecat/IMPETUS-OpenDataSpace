from fastapi import FastAPI
import models
from config.fastapi import TITLE, VERSION, DESCRIPTION
from db.postgres import get_db, engine, Base
from routers import api_router

app = FastAPI(    
    title=TITLE,
    version=VERSION
)

@app.on_event("startup")
async def setup():
    app.description = DESCRIPTION
    Base.metadata.create_all(engine)

app.include_router(api_router)