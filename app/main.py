from fastapi import FastAPI
from app.database import engine
from app import models
from app.api import router as api_router

# Создаем таблицы в базе данных
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OrgAtlas API", 
    description="Справочник организаций, зданий и видов деятельности",
    version="1.0.0"
)

# Подключаем API роуты
app.include_router(api_router, prefix="/api/v1")
