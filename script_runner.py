import asyncio
import subprocess
import os
import sys

async def run_script(task_id: int, script_path: str, timeout: int = 300) -> tuple:
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
        
        # Ожидаем завершение процесса с таймаутом
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
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