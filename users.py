import json
import os
from config import ADMIN_ID

ALLOWED_USERS_FILE = "users.json"
waiting_users = []

if not os.path.exists(ALLOWED_USERS_FILE):
    with open(ALLOWED_USERS_FILE, "w") as file:
        json.dump([], file)

def load_allowed_users():
    with open(ALLOWED_USERS_FILE, "r") as file:
        return list(json.load(file))

# Функция для сохранения пользователей
def save_allowed_users(users):
    with open(ALLOWED_USERS_FILE, "w") as file:
        json.dump(list(users), file)

# Загружаем пользователей в память
allowed_users = load_allowed_users()


# Функция проверки доступа
def is_allowed_user(user_id):
    return True if int(user_id) in allowed_users or user_id == ADMIN_ID else False

def is_waiter(user_id):
    return True if user_id in waiting_users else False

def remove_waiter(user_id):
    print(waiting_users)
    if user_id in waiting_users:
        waiting_users.remove(user_id)

def add_waiter(user_id):
    waiting_users.append(user_id)

def get_allowed_users():
    print(allowed_users)
    return allowed_users

def remove_allowed_user(user_id):
    try:
        allowed_users.remove(user_id)
        save_allowed_users(allowed_users)
        return f"Пользователь с id {user_id} успешно удален"
    except Exception as e:
        return e

def add_allowed_user(user_id):
    try:
        allowed_users.append(user_id)
        save_allowed_users(allowed_users)
        return f"Пользователь с id {user_id} успешно добавлен"
    except Exception as e:
        return e