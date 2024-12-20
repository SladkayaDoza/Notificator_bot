import asyncio
import subprocess
import os
import sys
# from main import task_manager

def stop_script(process):
    """
    Принудительная остановка процесса
    
    :param process: Объект процесса для остановки
    """
    try:
        # Завершаем процесс
        process.terminate()
        
        # На всякий случай убиваем, если не завершился
        process.kill()
    except Exception as e:
        print(f"Ошибка при остановке процесса: {e}")