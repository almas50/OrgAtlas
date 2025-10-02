from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.models import Organization, Building, Activity, Phone
from app.schemas import OrganizationCreate, BuildingCreate, ActivityCreate
from typing import List, Optional
import math


class OrganizationService:
    @staticmethod
    def get_organizations_by_building(db: Session, building_id: int) -> List[Organization]:
        """Получить все организации в конкретном здании"""
        return db.query(Organization).filter(Organization.building_id == building_id).all()
    
    @staticmethod
    def get_organizations_by_activity(db: Session, activity_id: int) -> List[Organization]:
        """Получить все организации по виду деятельности (включая дочерние)"""
        # Получаем все дочерние деятельности
        child_activities = ActivityService.get_all_child_activities(db, activity_id)
        activity_ids = [activity_id] + [child.id for child in child_activities]
        
        return db.query(Organization).join(Organization.activities).filter(
            Organization.activities.any(Activity.id.in_(activity_ids))
        ).all()
    
    @staticmethod
    def get_organizations_in_radius(db: Session, latitude: float, longitude: float, radius_km: float) -> List[Organization]:
        """Получить организации в радиусе от точки"""
        # Формула гаверсинуса для расчета расстояния
        earth_radius = 6371  # Радиус Земли в км
        
        # SQL запрос с использованием формулы гаверсинуса
        query = db.query(Organization).join(Building).filter(
            func.acos(
                func.sin(func.radians(latitude)) * func.sin(func.radians(Building.latitude)) +
                func.cos(func.radians(latitude)) * func.cos(func.radians(Building.latitude)) *
                func.cos(func.radians(longitude) - func.radians(Building.longitude))
            ) * earth_radius <= radius_km
        )
        
        return query.all()
    
    @staticmethod
    def get_organizations_in_rectangle(db: Session, min_lat: float, max_lat: float, 
                                     min_lon: float, max_lon: float) -> List[Organization]:
        """Получить организации в прямоугольной области"""
        return db.query(Organization).join(Building).filter(
            and_(
                Building.latitude >= min_lat,
                Building.latitude <= max_lat,
                Building.longitude >= min_lon,
                Building.longitude <= max_lon
            )
        ).all()
    
    @staticmethod
    def get_organization_by_id(db: Session, org_id: int) -> Optional[Organization]:
        """Получить организацию по ID"""
        return db.query(Organization).filter(Organization.id == org_id).first()
    
    @staticmethod
    def search_organizations_by_name(db: Session, name: str) -> List[Organization]:
        """Поиск организаций по названию"""
        return db.query(Organization).filter(
            Organization.name.ilike(f"%{name}%")
        ).all()
    
    @staticmethod
    def create_organization(db: Session, org_data: OrganizationCreate) -> Organization:
        """Создать новую организацию"""
        # Создаем телефоны
        phones = []
        for phone_number in org_data.phone_numbers:
            existing_phone = db.query(Phone).filter(Phone.number == phone_number).first()
            if existing_phone:
                phones.append(existing_phone)
            else:
                phone = Phone(number=phone_number)
                db.add(phone)
                db.flush()
                phones.append(phone)
        
        # Получаем виды деятельности
        activities = db.query(Activity).filter(Activity.id.in_(org_data.activity_ids)).all()
        
        # Создаем организацию
        organization = Organization(
            name=org_data.name,
            building_id=org_data.building_id,
            phones=phones,
            activities=activities
        )
        
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization


class BuildingService:
    @staticmethod
    def get_all_buildings(db: Session) -> List[Building]:
        """Получить все здания"""
        return db.query(Building).all()
    
    @staticmethod
    def get_building_by_id(db: Session, building_id: int) -> Optional[Building]:
        """Получить здание по ID"""
        return db.query(Building).filter(Building.id == building_id).first()
    
    @staticmethod
    def create_building(db: Session, building_data: BuildingCreate) -> Building:
        """Создать новое здание"""
        building = Building(**building_data.dict())
        db.add(building)
        db.commit()
        db.refresh(building)
        return building


class ActivityService:
    @staticmethod
    def get_all_activities(db: Session) -> List[Activity]:
        """Получить все виды деятельности"""
        return db.query(Activity).all()
    
    @staticmethod
    def get_activity_by_id(db: Session, activity_id: int) -> Optional[Activity]:
        """Получить вид деятельности по ID"""
        return db.query(Activity).filter(Activity.id == activity_id).first()
    
    @staticmethod
    def get_all_child_activities(db: Session, parent_id: int, max_level: int = 3) -> List[Activity]:
        """Получить все дочерние виды деятельности (рекурсивно, до 3 уровня)"""
        def get_children_recursive(parent_id: int, current_level: int = 1) -> List[Activity]:
            if current_level > max_level:
                return []
            
            children = db.query(Activity).filter(Activity.parent_id == parent_id).all()
            result = list(children)
            
            for child in children:
                result.extend(get_children_recursive(child.id, current_level + 1))
            
            return result
        
        return get_children_recursive(parent_id)
    
    @staticmethod
    def create_activity(db: Session, activity_data: ActivityCreate) -> Activity:
        """Создать новый вид деятельности"""
        # Проверяем уровень вложенности
        if activity_data.parent_id:
            parent = db.query(Activity).filter(Activity.id == activity_data.parent_id).first()
            if parent:
                level = ActivityService.get_activity_level(db, parent.id)
                if level >= 3:
                    raise ValueError("Максимальный уровень вложенности - 3")
        
        activity = Activity(**activity_data.dict())
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity
    
    @staticmethod
    def get_activity_level(db: Session, activity_id: int) -> int:
        """Получить уровень вложенности вида деятельности"""
        level = 1
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        
        while activity and activity.parent_id:
            level += 1
            activity = db.query(Activity).filter(Activity.id == activity.parent_id).first()
        
        return level
