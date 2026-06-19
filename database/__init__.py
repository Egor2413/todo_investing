from .db import engine, Base

def init_db():
    """Создание всех таблиц в базе данных"""
    Base.metadata.create_all(engine)
    print("✅ База данных и таблицы созданы")