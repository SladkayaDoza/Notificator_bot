import asyncio
import os
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv
from script_runner import stop_script
import sys
import subprocess

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

    def add_task(self, script_path, process):
        task_id = self._next_task_id
        self.tasks[task_id] = {
            'script_path': script_path,
            'process': process,
            'start_time': asyncio.get_running_loop().time()
        }
        self._next_task_id += 1
        return task_id

    def remove_task(self, task_id):
        return self.tasks.pop(task_id, None)

    def get_tasks(self):
        return self.tasks

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def set_process(self, task_id, process):
        self.tasks[task_id]['process'] = process
        return task_id

# Создаем менеджер задач
task_manager = TaskManager()

# Команда /start
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! Отправьте мне Python-скрипт для выполнения 🐍")

# Обработка команды /code
@dp.message(Command("code"))
async def handle_code(message: Message):
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

    # Добавляем задачу в список активных
    # process = await run_script(task_manager._next_task_id, script_path)
    task_id = task_manager.add_task(script_path, None)

    asyncio.create_task(execute_script(message, script_path, script_name, task_id))

# Обработка загрузки скриптов
@dp.message(lambda m: m.document)
async def handle_script(message: Message):
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

    # Добавляем задачу в список активных
    # process = await run_script(task_manager._next_task_id, script_path)
    task_id = task_manager.add_task(script_path, None)
    
    asyncio.create_task(execute_script(message, script_path, document.file_name, task_id))

async def execute_script(message: Message, script_path: str, file_name: str, task_id: int):
    output, status = await run_script(task_id, script_path)
    
    # Удаляем задачу после завершения
    task_manager.remove_task(task_id)
    
    # Логируем результат
    log_path = os.path.join(LOGS_DIR, f"{file_name}.log")
    with open(log_path, "w") as log_file:
        log_file.write(output)
    
    # Отправляем статус и вывод
    response = f"**Статус**: {status}\n`\n{output}\n`"
    await message.reply(response, parse_mode="Markdown")

async def run_script(task_id: int, script_path: str) -> tuple:
    """
    Асинхронный запуск Python-скрипта с ограничением по времени
    
    :param task_id: Уникальный идентификатор задачи
    :param script_path: Путь к скрипту
    :param timeout: Максимальное время выполнения в секундах
    :return: Кортеж (вывод, статус)
    """
    try:
        # Создаем процесс с перенаправлением stdout и stderr
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        task_manager.set_process(task_id, process)
        
        # Ожидаем завершение процесса с таймаутом
        try:
            stdout, stderr = await process.communicate()
        except asyncio.TimeoutError:
            process.kill()
            return f"Превышено время выполнения ({timeout} сек)", "TIMEOUT"
        
        # Декодируем вывод
        output = (stdout + stderr).decode('utf-8', errors='replace').strip()
        
        # Определяем статус выполнения
        status = "✅" if process.returncode == 0 else "❌"
        
        return output, status
    
    except Exception as e:
        return f"Ошибка выполнения: {str(e)}", "EXCEPTION"

# Команда /tasks – показать все активные задачи
@dp.message(Command("tasks"))
async def list_tasks(message: Message):
    tasks = task_manager.get_tasks()
    
    if not tasks:
        print(tasks)
        await message.reply("Нет активных задач 💤")
        return
    
    current_time = asyncio.get_running_loop().time()
    tasks_list = []
    
    for task_id, task_info in tasks.items():
        runtime = current_time - task_info['start_time']
        task_description = (
            f"ID: {task_id} – {os.path.basename(task_info['script_path'])} "
            f"(Время выполнения: {runtime:.2f} сек)"
        )
        tasks_list.append(task_description)
    
    tasks_text = "\n".join(tasks_list)
    await message.reply(f"**Активные задачи:**\n{tasks_text}", parse_mode="Markdown")

# Команда /stop <task_id> – остановить задачу
@dp.message(Command("stop"))
async def stop_task(message: Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.reply("Использование: /stop <task_id>")
        return
    
    task_id = int(args[1])
    task = task_manager.get_task(task_id)
    
    if task:
        stop_script(task['process'])  # Завершаем процесс
        task_manager.remove_task(task_id)
        await message.reply(f"Задача с ID {task_id} остановлена ⛔")
    else:
        await message.reply("Задача с таким ID не найдена 🧐")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())