from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Таблица для связи многие-ко-многим между организациями и видами деятельности
organization_activity = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id')),
    Column('activity_id', Integer, ForeignKey('activities.id'))
)

# Таблица для связи многие-ко-многим между организациями и телефонами
organization_phone = Table(
    'organization_phone',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id')),
    Column('phone_id', Integer, ForeignKey('phones.id'))
)


class Phone(Base):
    """Модель для хранения номеров телефонов"""
    __tablename__ = "phones"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True, nullable=False)
    
    # Связь с организациями
    organizations = relationship("Organization", secondary=organization_phone, back_populates="phones")


class Building(Base):
    """Модель здания"""
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)  # Широта
    longitude = Column(Float, nullable=False)  # Долгота
    
    # Связь с организациями (один-ко-многим)
    organizations = relationship("Organization", back_populates="building")


class Activity(Base):
    """Модель вида деятельности с поддержкой иерархии"""
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('activities.id'), nullable=True)
    
    # Связи
    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent")
    organizations = relationship("Organization", secondary=organization_activity, back_populates="activities")


class Organization(Base):
    """Модель организации"""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    building_id = Column(Integer, ForeignKey('buildings.id'), nullable=False)
    
    # Связи
    building = relationship("Building", back_populates="organizations")
    activities = relationship("Activity", secondary=organization_activity, back_populates="organizations")
    phones = relationship("Phone", secondary=organization_phone, back_populates="organizations")
