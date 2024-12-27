# Telegram Bot for Python Script Execution

This bot allows users to send Python scripts, execute them in a controlled environment, and receive execution results via Telegram. The bot also supports task management, user whitelisting, and system performance monitoring.

---

## Features

- **Script Execution:** Upload Python scripts and receive output directly in Telegram.
- **Task Management:** View, stop, and manage active tasks.
- **User Management:** Control access through a whitelist system.
- **System Monitoring:** Check CPU, memory, and disk usage.
- **Request System:** Apply for whitelist access directly via Telegram.

---

## Installation

### Prerequisites
- Python 3.8+
- Telegram bot token from BotFather
- PostgreSQL database for storing task and user data
- `dotenv` package for environment variables

### Steps
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add the following:
   ```env
   BOT_TOKEN=your_bot_token
   ```
5. Edit config.py file:
   ```py
   ADMIN_ID=your_admin_id
   MEMORY_LIMIT=256 # Memory limit in MB
   ```
5. Initialize the database:
   ```bash
   python init_db.py
   ```
6. Start the bot:
   ```bash
   python main.py
   ```

---

## Usage

### Commands

| **Command**              | **Description**                                                       |
|--------------------------|------------------------------------------------------------------------|
| `/start`                 | Start interaction with the bot.                                       |
| `/code <script>`         | Send code directly as a command.                                      |
| `/tasks`                 | List all active tasks.                                                |
| `/kill <task_id>`        | Stop a specific task.                                                 |
| `/bot`                   | Display bot and system statistics.                                    |
| `/getusers`              | List all allowed users.                                               |
| `/adduser <user_id>`     | Add a user to the whitelist.                                          |
| `/removeuser <user_id>`  | Remove a user from the whitelist.                                     |
| `/request`               | Submit a whitelist request to the administrator.                      |

### Sending Scripts
1. Prepare a Python script with a `.py` extension.
2. Send the script as a document attachment to the bot.
3. The bot executes the script and responds with the result.

---

## Example Script

Simple example:
```python
print("Hello, Telegram!")
```

Script with calculations:
```python
result = sum([i for i in range(1, 11)])
print(f"Sum of numbers from 1 to 10: {result}")
```

Script with a delay:
```python
import time
time.sleep(5)  # 5-second delay
print("Execution completed!")
```

---

## Task Management
- View all tasks using `/tasks`.
- Stop any active task with `/kill <task_id>`.
- Logs for executed scripts are saved in the `logs/` directory.

---

## Restrictions

- **No Infinite Loops:** Scripts exceeding execution time limits are terminated.
- **No Inputs:** Scripts requiring `input()` are not supported.
- **Memory Limit:** Scripts using excessive memory will be terminated.

---

## Logs and Monitoring
Logs for executed scripts are saved in the `logs/` directory, with timestamps and outputs.
System performance can be checked using the `/bot` command, displaying CPU, memory, and disk usage.

---

## Troubleshooting
- **Error: Invalid File Format**: Ensure the script has a `.py` extension.
- **Execution Timeout**: Optimize the script for shorter execution times.
- **Permission Denied**: Request admin approval through `/request`.

---

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss your ideas.

---

Now you are ready to manage and execute Python scripts using this bot! 🚀

