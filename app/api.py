from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import Organization, Building, Activity, OrganizationCreate, BuildingCreate, ActivityCreate
from app.services import OrganizationService, BuildingService, ActivityService

router = APIRouter()

# API Key для аутентификации
API_KEY = "orgatlas_api_key"

def verify_api_key(api_key: str = Query(..., description="API ключ")):
    """Проверка API ключа"""
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Неверный API ключ")
    return api_key


# Эндпоинты для организаций
@router.get("/organizations/by-building/{building_id}", response_model=List[Organization])
async def get_organizations_by_building(
    building_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получить все организации в конкретном здании"""
    organizations = OrganizationService.get_organizations_by_building(db, building_id)
    return organizations


@router.get("/organizations/by-activity/{activity_id}", response_model=List[Organization])
async def get_organizations_by_activity(
    activity_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получить все организации по виду деятельности (включая дочерние)"""
    organizations = OrganizationService.get_organizations_by_activity(db, activity_id)
    return organizations


@router.get("/organizations/in-radius", response_model=List[Organization])
async def get_organizations_in_radius(
    latitude: float = Query(..., description="Широта"),
    longitude: float = Query(..., description="Долгота"),
    radius_km: float = Query(..., description="Радиус в километрах"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получить организации в радиусе от точки"""
    organizations = OrganizationService.get_organizations_in_radius(db, latitude, longitude, radius_km)
    return organizations


@router.get("/organizations/in-rectangle", response_model=List[Organization])
async def get_organizations_in_rectangle(
    min_lat: float = Query(..., description="Минимальная широта"),
    max_lat: float = Query(..., description="Максимальная широта"),
    min_lon: float = Query(..., description="Минимальная долгота"),
    max_lon: float = Query(..., description="Максимальная долгота"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получить организации в прямоугольной области"""
    organizations = OrganizationService.get_organizations_in_rectangle(
        db, min_lat, max_lat, min_lon, max_lon
    )
    return organizations


@router.get("/organizations/{org_id}", response_model=Organization)
async def get_organization_by_id(
    org_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получить информацию об организации по ID"""
    organization = OrganizationService.get_organization_by_id(db, org_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return organization


@router.get("/organizations/search/by-name", response_model=List[Organization])
async def search_organizations_by_name(
    name: str = Query(..., description="Название для поиска"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Поиск организаций по названию"""
    organizations = OrganizationService.search_organizations_by_name(db, name)
    return organizations


@router.get("/organizations/search/by-activity", response_model=List[Organization])
async def search_organizations_by_activity(
    activity_name: str = Query(..., description="Название вида деятельности"),
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Поиск организаций по виду деятельности (включая дочерние)"""
    # Сначала найдем вид деятельности по названию
    activity = db.query(Activity).filter(Activity.name.ilike(f"%{activity_name}%")).first()
    if not activity:
        return []
    
    # Получим все организации с этим видом деятельности и дочерними
    organizations = OrganizationService.get_organizations_by_activity(db, activity.id)
    return organizations


@router.post("/organizations", response_model=Organization)
async def create_organization(
    organization_data: OrganizationCreate,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Создать новую организацию"""
    organization = OrganizationService.create_organization(db, organization_data)
    return organization


# Эндпоинты для зданий
@router.get("/buildings", response_model=List[Building])
async def get_all_buildings(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получить список всех зданий"""
    buildings = BuildingService.get_all_buildings(db)
    return buildings


@router.get("/buildings/{building_id}", response_model=Building)
async def get_building_by_id(
    building_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получить информацию о здании по ID"""
    building = BuildingService.get_building_by_id(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Здание не найдено")
    return building


@router.post("/buildings", response_model=Building)
async def create_building(
    building_data: BuildingCreate,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Создать новое здание"""
    building = BuildingService.create_building(db, building_data)
    return building


# Эндпоинты для видов деятельности
@router.get("/activities", response_model=List[Activity])
async def get_all_activities(
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получить список всех видов деятельности"""
    activities = ActivityService.get_all_activities(db)
    return activities


@router.get("/activities/{activity_id}", response_model=Activity)
async def get_activity_by_id(
    activity_id: int,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Получить информацию о виде деятельности по ID"""
    activity = ActivityService.get_activity_by_id(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Вид деятельности не найден")
    return activity


@router.post("/activities", response_model=Activity)
async def create_activity(
    activity_data: ActivityCreate,
    api_key: str = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Создать новый вид деятельности"""
    try:
        activity = ActivityService.create_activity(db, activity_data)
        return activity
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
