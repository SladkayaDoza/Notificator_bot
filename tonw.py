import datetime
import threading

def execute_task():
    # Выполнение команды print
    # print("Задача выполнена!")

# Определяем текущее время с временной зоной
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2)))  # GMT+2

# Устанавливаем целевое время
tomorrow = now + datetime.timedelta(days=0)
target_time = datetime.datetime(
    year=tomorrow.year,
    month=tomorrow.month,
    day=tomorrow.day,
    hour=17,
    minute=59,
    second=0,
    tzinfo=datetime.timezone(datetime.timedelta(hours=2))  # GMT+2
)

# Рассчитываем задержку до выполнения
delay = (target_time - now).total_seconds()

if delay > 0:
    print(f"Задача запланирована через {delay / 3600:.2f} часов.")
    # Запускаем задачу с задержкой
    threading.Timer(delay, execute_task).start()
else:
    print("Указанное время уже прошло. Задача не может быть запланирована.")