from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Базовые схемы
class PhoneBase(BaseModel):
    number: str


class PhoneCreate(PhoneBase):
    pass


class Phone(PhoneBase):
    id: int
    
    class Config:
        from_attributes = True


class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    id: int
    
    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class ActivityCreate(ActivityBase):
    pass


class Activity(ActivityBase):
    id: int
    children: List['Activity'] = []
    
    class Config:
        from_attributes = True


class OrganizationBase(BaseModel):
    name: str
    building_id: int


class OrganizationCreate(OrganizationBase):
    phone_numbers: List[str] = []
    activity_ids: List[int] = []


class Organization(OrganizationBase):
    id: int
    building: Building
    phones: List[Phone] = []
    activities: List[Activity] = []
    
    class Config:
        from_attributes = True


# Обновляем forward references
Activity.model_rebuild()
