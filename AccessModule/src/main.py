from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import config
from routers import api_router

app = FastAPI(    
    title=config.TITLE,
    version=config.VERSION
)

@app.on_event("startup")
async def setup():
    app.description = config.DESCRIPTION

app.include_router(api_router)

app.mount("/context", StaticFiles(directory=config.CONTEXT_PATH), name="static")
