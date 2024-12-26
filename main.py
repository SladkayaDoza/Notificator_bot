import asyncio
import os
import uuid
from users import get_allowed_users, add_allowed_user, remove_allowed_user, is_allowed_user
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from psutil import cpu_percent, virtual_memory, disk_usage
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
from users import add_waiter, remove_waiter, is_waiter
import sys
import psutil
import subprocess
import datetime
import platform
from config import cancel_message, ADMIN_ID, memory_limit
from database import Task, session

IS_WINDOWS = platform.system() == "Windows"
if not IS_WINDOWS:
    import resource  # Доступен только на Unix-системах

start_time = datetime.datetime.now()

# Загружаем токен
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Путь для хранения логов и скриптов
SCRIPTS_DIR = "scripts"
LOGS_DIR = "logs"
os.makedirs(SCRIPTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Улучшенная структура для хранения активных задач
class TaskManager:
    def __init__(self):
        self.tasks = {}
        self._next_task_id = 1

    def add_task(self, user_id: int, pid: int, name: str, path: str, chat_id: int):
        task_id = self.get_next_user_id(chat_id)
        # Добавляем новую задачу
        new_task = Task(user_id=user_id, chat_id=chat_id, user_task_id=task_id, task_name=name, started_time=datetime.datetime.now(), status="active", process_id = pid, code_path=path)
        session.add(new_task)
        session.commit()
        print("Задача добавлена!")

    def get_next_user_id(self, id):
        return session.query(Task).filter(Task.chat_id == id).count() + 1
    
    def update_status(self, pid, status):
        task = session.query(Task).filter(Task.process_id == pid).first()
        if task:
            task.status = status
            session.commit()
    
    def set_end_time(self, pid, end_time):
        task = session.query(Task).filter(Task.process_id == pid).first()
        if task:
            task.end_time = end_time
            session.commit()

    def remove_task(self, user_id, task_id):
        # return self.tasks.pop(task_id, None)
        task = session.query(Task).filter(Task.user_id == user_id, Task.user_task_id == task_id).first()
        if task:
            session.delete(task)
            session.commit()
            return "Задача удалена!"
        else: return "Задачи не существует"

    def get_tasks(self, id):
        return session.query(Task).filter(Task.chat_id == id, Task.status == "active").all()

    def get_task(self, id, task_id):
        return session.query(Task).filter(Task.chat_id == id, Task.user_task_id == task_id, Task.status == "active").first()

    def stop_process(self, pid):
        self.update_status(pid, "canceled")
        try:
            p = psutil.Process(pid)
            p.kill()
        except Exception as e:
            print(e)

# Создаем менеджер задач
task_manager = TaskManager()

# Команда /start
@dp.message(Command("start"))
async def start(message: Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply(cancel_message)
        return

    await message.answer("Привет! Отправьте мне Python-скрипт для выполнения 🐍")

# Обработка команды /code
@dp.message(Command("code"))
async def handle_code(message: Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply(cancel_message)
        return

    code = message.text.split(maxsplit=1)[1]
    if not code:
        await message.reply("Пожалуйста, укажите код после команды. Например: /code print(\"gg\")")
        return

    # Генерируем уникальное имя файла
    script_name = f"{uuid.uuid4().hex[:4]}.py"
    script_path = os.path.join(SCRIPTS_DIR, script_name)

    # Сохраняем код в файл
    with open(script_path, "w") as script_file:
        script_file.write(code)

    print(f"Код сохранён как `{script_name}`! Добавляю в очередь выполнения...")
    await message.reply(f"Код сохранён как `{script_name}`! Добавляю в очередь выполнения...", parse_mode="Markdown")

    asyncio.create_task(execute_script(message, script_path, script_name))

# Обработка загрузки скриптов
@dp.message(lambda m: m.document)
async def handle_script(message: Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply(cancel_message)
        return

    document = message.document
    if not document.file_name.endswith(".py"):
        print("Пожалуйста, отправьте файл с расширением .py")
        await message.reply("Пожалуйста, отправьте файл с расширением .py")
        return

    # Сохраняем скрипт
    script_path = os.path.join(SCRIPTS_DIR, document.file_name)
    await bot.download(document, destination=script_path)
    print("Скрипт получен! Добавляю в очередь выполнения...")
    await message.reply("Скрипт получен! Добавляю в очередь выполнения...")
    
    asyncio.create_task(execute_script(message, script_path, document.file_name))

async def execute_script(message: Message, script_path: str, file_name: str):
    output, status, pid = await run_script(message, script_path, file_name)
    task_manager.set_end_time(pid, datetime.datetime.now())
    
    # Логируем результат
    log_path = os.path.join(LOGS_DIR, f"{message.chat.id}_{pid}_{file_name}.log")
    with open(log_path, "w") as log_file:
        log_file.write(output)
    
    # Отправляем статус и вывод
    response = f"**Статус**: {status}\n`\n{output}\n`"
    await message.reply(response, parse_mode="Markdown")

async def run_script(message: Message, script_path: str, script_name: str) -> tuple:
    """
    Асинхронный запуск Python-скрипта с ограничением по времени
    
    :param task_id: Уникальный идентификатор задачи
    :param script_path: Путь к скрипту
    :param timeout: Максимальное время выполнения в секундах
    :return: Кортеж (вывод, статус)
    """
    try:
        # Создаем процесс с перенаправлением stdout и stderr
        def set_memory_limit():
            if not IS_WINDOWS and memory_limit is not None:
                # Преобразуем лимит в байты
                memory_limit_bytes = memory_limit * 1024 * 1024
                # Устанавливаем лимит памяти для процесса
                resource.setrlimit(resource.RLIMIT_AS, (memory_limit_bytes, memory_limit_bytes))


        process = await asyncio.create_subprocess_exec(
            sys.executable, script_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=set_memory_limit if not IS_WINDOWS else None
        )
        task_manager.add_task(message.from_user.id, process.pid, script_name, script_path, message.chat.id)
        
        # Ожидаем завершение процесса с таймаутом
        try:
            stdout, stderr = await process.communicate()
            task_manager.update_status(process.pid, "completed")
        except asyncio.TimeoutError:
            task_manager.update_status(process.pid, "timeout")
            process.kill()
            return f"Превышено время выполнения", "TIMEOUT", process.pid
        
        # Декодируем вывод
        output = (stdout + stderr).decode('utf-8', errors='replace').strip()
        
        # Определяем статус выполнения
        status = "✅" if process.returncode == 0 else "❌"
        
        return output, status, process.pid
    
    except Exception as e:
        return f"Ошибка выполнения: {str(e)}", "EXCEPTION", process.pid

# Команда /tasks – показать все активные задачи
@dp.message(Command("tasks"))
async def list_tasks(message: Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply(cancel_message)
        return

    tasks = task_manager.get_tasks(message.chat.id)
    
    if not tasks:
        print(tasks)
        await message.reply("Нет активных задач 💤")
        return
    
    current_time = datetime.datetime.now()
    tasks_list = []
    
    for task in tasks:
        runtime = current_time - task.started_time
        task_description = (
            f"ID: {task.user_task_id} – {os.path.basename(task.code_path)} "
            f": {runtime.seconds // 3600}:{(runtime.seconds // 60) % 60:02}:{runtime.seconds % 60:02}.{str(runtime.microseconds)[:3]}"
        )
        tasks_list.append(task_description)
    
    tasks_text = "\n".join(tasks_list)
    await message.reply(f"**Активные задачи:**\n{tasks_text}", parse_mode="Markdown")

# Команда /stop <task_id> – остановить задачу
@dp.message(Command("kill"))
async def stop_task(message: Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply(cancel_message)
        return
        
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply("Использование: /stop <task_id>")
        return
    
    task_id = int(args[1])
    task = task_manager.get_task(message.chat.id, task_id)
    
    if task:
        task_manager.stop_process(task.process_id)
        await message.reply(f"Задача с ID {task_id} остановлена ⛔")
    else:
        await message.reply("Задача с таким ID не найдена 🧐")


@dp.message(Command("bot"))
async def bot_info(message: Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply(cancel_message)
        return
        
    uptime = str(datetime.datetime.now() - start_time).split(".")[0]
    ram_total = virtual_memory().total // 1024 // 1024
    ram_used = virtual_memory().used // 1024 // 1024
    ram_used_percent = virtual_memory().percent
    disk_total = disk_usage('/').total // 1024 // 1024 // 1024
    disk_used = disk_usage('/').used // 1024 // 1024 // 1024
    disk_used_percent = disk_usage('/').percent

    msg = "*Статистика*\n\n" \
          f"*ОЗУ*: {ram_used}/{ram_total} МБ ({ram_used_percent:.1f}%)\n" \
          f"*ЦПУ*: {cpu_percent()}%\n" \
          f"*Диск*: {disk_used}/{disk_total} ГБ ({disk_used_percent:.1f}%)\n" \
          f"*Аптайм*: {uptime}\n\n\n"

    await message.reply(msg, parse_mode="Markdown")

@dp.message(Command("getusers"))
async def get_users(message: Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply(cancel_message)
        return

    if not get_allowed_users():  # Если список пустой
        await message.reply("Вайт-лист пуст 💤")
        return

    user_list = "\n".join([f"[{user_id}]" for user_id in get_allowed_users()])

    # Отправляем ответ
    await message.reply(f"Список разрешённых пользователей:\n{user_list}")

@dp.message(Command("adduser"))
async def add_user(message: Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply(cancel_message)
        return
        
    user_id = message.text.split()[1]
    
    reply_text = add_allowed_user(int(user_id))

    await message.reply(reply_text, parse_mode="Markdown")

@dp.message(Command("removeuser"))
async def remove_user(message: Message):
    if not is_allowed_user(message.from_user.id):
        await message.reply(cancel_message)
        return
        
    user_id = message.text.split()[1]
    
    reply_text = remove_allowed_user(int(user_id))

    await message.reply(reply_text, parse_mode="Markdown")

# Команда для подачи заявки
@dp.message(Command("request"))
async def apply_whitelist(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Без имени"
    if is_waiter(user_id):
        await message.reply("Ваша заявка уже отправлена администратору!")
        return
    add_waiter(user_id)

    # Клавиатура для принятия/отклонения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{user_id}_{username}"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}_{username}")]
    ])

    # Отправка заявки админу
    await bot.send_message(
        ADMIN_ID,
        f"Пользователь {username} (ID: {user_id}) подал заявку в вайт-лист.",
        reply_markup=keyboard
    )
    await message.reply("Ваша заявка отправлена администратору.")

# Обработка нажатий кнопок
@dp.callback_query(lambda c: c.data.startswith("accept") or c.data.startswith("reject"))
async def process_whitelist(callback: CallbackQuery):
    action, user_id, username = callback.data.split("_")

    if action == "accept":
        add_allowed_user(int(user_id))
        await bot.send_message(user_id, "Ваша заявка в вайт-лист принята ✅.")
        await callback.message.edit_text(f"Пользователь {username} ({user_id}) добавлен в вайт-лист.")
        remove_waiter(int(user_id))
    elif action == "reject":
        await bot.send_message(user_id, "Ваша заявка в вайт-лист отклонена ❌.")
        await callback.message.edit_text(f"Пользователь {username} ({user_id}) отклонён.")
        remove_waiter(int(user_id))
    await callback.answer()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
