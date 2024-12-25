from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Создаём базу данных SQLite
engine = create_engine('sqlite:///tasks.db')  # Имя файла базы данных
Base = declarative_base()

# Определяем таблицу с задачами
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)  # Уникальный идентификатор задачи
    user_id = Column(Integer, nullable=False)  # ID пользователя
    user_task_id = Column(Integer, nullable=False)  # ID задачи пользователя
    task_name = Column(String, nullable=False)  # Название задачи
    started_time = Column(DateTime, default=datetime.utcnow)  # Время начала
    end_time = Column(DateTime, nullable=True)  # Время завершения
    process_id = Column(Integer, nullable=True)  # PID процесса
    status = Column(String, nullable=True)      # Статус (active, completed)
    code_path = Column(String, nullable=True)      # Путь к файлу с кодом

# Создаем таблицы
Base.metadata.create_all(engine)

# Создаем сессию для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()
