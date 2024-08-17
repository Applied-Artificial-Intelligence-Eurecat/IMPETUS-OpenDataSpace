from fastapi import APIRouter
from routers.auth import auth_router
# from routers.datatypes import datatypes_router
from routers.datacatalog import datacatalog_router
from routers.insert import inserdata_router
from routers.query import query_router
from routers.subscription import subscription_router
from routers.download import download_router
api_router = APIRouter()
api_router.include_router(auth_router, prefix= "/auth")
api_router.include_router(datacatalog_router, prefix= "/datacatalog")
api_router.include_router(query_router, prefix="/query")
api_router.include_router(inserdata_router, prefix="/insert")
api_router.include_router(subscription_router, prefix="/subscription")
api_router.include_router(download_router, prefix="/download")