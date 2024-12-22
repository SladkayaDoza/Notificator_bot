import json
import os
from config import ADMIN_ID

ALLOWED_USERS_FILE = "users.json"

if not os.path.exists(ALLOWED_USERS_FILE):
    with open(ALLOWED_USERS_FILE, "w") as file:
        json.dump([], file)

def load_allowed_users():
    with open(ALLOWED_USERS_FILE, "r") as file:
        return set(json.load(file))

# Функция для сохранения пользователей
def save_allowed_users(users):
    with open(ALLOWED_USERS_FILE, "w") as file:
        json.dump(list(users), file)

# Загружаем пользователей в память
ALLOWED_USERS = load_allowed_users()


# Функция проверки доступа
def is_allowed_user(user_id):
    return user_id in ALLOWED_USERS or user_id == ADMIN_ID

def get_allowed_users():
    return ALLOWED_USERS

def remove_allowed_user(user_id):
    try:
        ALLOWED_USERS.remove(user_id)
        save_allowed_users(ALLOWED_USERS)
        return f"Пользователь с id {user_id} успешно удален"
    except Exception as e:
        return e
    return True

def add_allowed_user(user_id):
    try:
        ALLOWED_USERS.add(user_id)
        save_allowed_users(ALLOWED_USERS)
        return f"Пользователь с id {user_id} успешно добавлен"
    except Exception as e:
        return e
    return True