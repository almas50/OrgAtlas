#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми данными
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Organization, Building, Activity, Phone
from app.services import OrganizationService, BuildingService, ActivityService

def create_test_data():
    """Создает тестовые данные в базе данных"""
    print("🌱 Заполнение базы данных тестовыми данными...")
    
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже данные
        existing_organizations = db.query(Organization).count()
        if existing_organizations > 0:
            print("✅ Тестовые данные уже существуют, пропускаем создание")
            return
        # 1. Создаем здания
        print("📦 Создание зданий...")
        buildings_data = [
            {
                "address": "г. Москва, ул. Тверская, 1",
                "latitude": 55.7558,
                "longitude": 37.6176
            },
            {
                "address": "г. Москва, ул. Арбат, 15",
                "latitude": 55.7520,
                "longitude": 37.5934
            },
            {
                "address": "г. Москва, ул. Ленинский проспект, 32",
                "latitude": 55.7033,
                "longitude": 37.5833
            },
            {
                "address": "г. Москва, ул. Блюхера, 32/1",
                "latitude": 55.7890,
                "longitude": 37.6123
            },
            {
                "address": "г. Москва, ул. Красная Площадь, 1",
                "latitude": 55.7539,
                "longitude": 37.6208
            }
        ]
        
        buildings = []
        for building_data in buildings_data:
            # Проверяем, не существует ли уже такое здание
            existing_building = db.query(Building).filter(
                Building.address == building_data["address"]
            ).first()
            if existing_building:
                buildings.append(existing_building)
            else:
                building = Building(**building_data)
                db.add(building)
                db.flush()  # Получаем ID
                buildings.append(building)
        
        # 2. Создаем иерархию видов деятельности
        print("🏢 Создание видов деятельности...")
        
        # Корневые категории
        food = db.query(Activity).filter(Activity.name == "Еда").first()
        if not food:
            food = Activity(name="Еда")
            db.add(food)
            db.flush()
        
        transport = db.query(Activity).filter(Activity.name == "Транспорт").first()
        if not transport:
            transport = Activity(name="Транспорт")
            db.add(transport)
            db.flush()
        
        services = db.query(Activity).filter(Activity.name == "Услуги").first()
        if not services:
            services = Activity(name="Услуги")
            db.add(services)
            db.flush()
        
        # Подкатегории для Еды
        meat = db.query(Activity).filter(Activity.name == "Мясная продукция").first()
        if not meat:
            meat = Activity(name="Мясная продукция", parent_id=food.id)
            db.add(meat)
            db.flush()
        
        dairy = db.query(Activity).filter(Activity.name == "Молочная продукция").first()
        if not dairy:
            dairy = Activity(name="Молочная продукция", parent_id=food.id)
            db.add(dairy)
            db.flush()
        
        bakery = db.query(Activity).filter(Activity.name == "Хлебобулочные изделия").first()
        if not bakery:
            bakery = Activity(name="Хлебобулочные изделия", parent_id=food.id)
            db.add(bakery)
            db.flush()
        
        # Подкатегории для Транспорта
        cars = db.query(Activity).filter(Activity.name == "Автомобили").first()
        if not cars:
            cars = Activity(name="Автомобили", parent_id=transport.id)
            db.add(cars)
            db.flush()
        
        trucks = db.query(Activity).filter(Activity.name == "Грузовые").first()
        if not trucks:
            trucks = Activity(name="Грузовые", parent_id=cars.id)
            db.add(trucks)
            db.flush()
        
        passenger = db.query(Activity).filter(Activity.name == "Легковые").first()
        if not passenger:
            passenger = Activity(name="Легковые", parent_id=cars.id)
            db.add(passenger)
            db.flush()
        
        # Подкатегории для Услуг
        repair = db.query(Activity).filter(Activity.name == "Ремонт").first()
        if not repair:
            repair = Activity(name="Ремонт", parent_id=services.id)
            db.add(repair)
            db.flush()
        
        consulting = db.query(Activity).filter(Activity.name == "Консультации").first()
        if not consulting:
            consulting = Activity(name="Консультации", parent_id=services.id)
            db.add(consulting)
            db.flush()
        
        # 3. Создаем телефоны
        print("📞 Создание телефонов...")
        phones_data = [
            "8-495-123-45-67",
            "8-495-234-56-78", 
            "8-495-345-67-89",
            "8-495-456-78-90",
            "8-495-567-89-01",
            "8-495-678-90-12",
            "8-495-789-01-23",
            "8-495-890-12-34"
        ]
        
        phones = []
        for phone_number in phones_data:
            # Проверяем, не существует ли уже такой телефон
            existing_phone = db.query(Phone).filter(Phone.number == phone_number).first()
            if existing_phone:
                phones.append(existing_phone)
            else:
                phone = Phone(number=phone_number)
                db.add(phone)
                db.flush()
                phones.append(phone)
        
        # 4. Создаем организации
        print("🏢 Создание организаций...")
        organizations_data = [
            {
                "name": "ООО Рога и Копыта",
                "building_id": buildings[0].id,
                "phone_numbers": [phones[0].number, phones[1].number],
                "activity_ids": [meat.id, dairy.id]
            },
            {
                "name": "ИП Иванов И.И.",
                "building_id": buildings[1].id,
                "phone_numbers": [phones[2].number],
                "activity_ids": [bakery.id]
            },
            {
                "name": "ЗАО АвтоМир",
                "building_id": buildings[2].id,
                "phone_numbers": [phones[3].number, phones[4].number],
                "activity_ids": [cars.id, trucks.id]
            },
            {
                "name": "ООО ТехСервис",
                "building_id": buildings[3].id,
                "phone_numbers": [phones[5].number],
                "activity_ids": [repair.id]
            },
            {
                "name": "ИП Петров П.П.",
                "building_id": buildings[4].id,
                "phone_numbers": [phones[6].number, phones[7].number],
                "activity_ids": [consulting.id]
            },
            {
                "name": "ООО Молочные продукты",
                "building_id": buildings[0].id,
                "phone_numbers": [phones[0].number],
                "activity_ids": [dairy.id]
            },
            {
                "name": "ИП Сидоров С.С.",
                "building_id": buildings[1].id,
                "phone_numbers": [phones[1].number],
                "activity_ids": [passenger.id]
            }
        ]
        
        for org_data in organizations_data:
            # Проверяем, не существует ли уже такая организация
            existing_org = db.query(Organization).filter(Organization.name == org_data["name"]).first()
            if existing_org:
                continue
            
            # Получаем телефоны
            org_phones = [p for p in phones if p.number in org_data["phone_numbers"]]
            
            # Получаем виды деятельности
            org_activities = db.query(Activity).filter(Activity.id.in_(org_data["activity_ids"])).all()
            
            # Создаем организацию
            organization = Organization(
                name=org_data["name"],
                building_id=org_data["building_id"],
                phones=org_phones,
                activities=org_activities
            )
            
            db.add(organization)
        
        # Сохраняем все изменения
        db.commit()
        
        print("✅ Тестовые данные успешно созданы!")
        print(f"📊 Создано:")
        print(f"   • Зданий: {len(buildings)}")
        print(f"   • Видов деятельности: {db.query(Activity).count()}")
        print(f"   • Телефонов: {len(phones)}")
        print(f"   • Организаций: {len(organizations_data)}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании тестовых данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()
