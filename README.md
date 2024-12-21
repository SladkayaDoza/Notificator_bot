### **README.md**

# **Telegram Bot Notifier for Running Python Scripts**

This bot accepts Python scripts, executes them in an isolated environment, and sends the execution results (text and status) to the user via Telegram.

---

## **1. How to Write Scripts**

To ensure your script executes correctly with the bot, follow these recommendations:

### **1.1. Basic Rules**
- The script must be written in **Python 3**.
- The file must have the **`.py`** extension.
- The script should output results using **print()**.
- The script should not require user input (**input()** is not supported).

---

### **1.2. Example of a Valid Script**

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
print("Execution started...")
time.sleep(5)  # 5-second delay
print("Execution completed!")
```

---

### **1.3. Prohibited Actions in Scripts**
- **Infinite loops**: Scripts that do not terminate will be stopped by a timeout.
- **Input requests**: Using `input()` will result in an execution error.
- **File system access**: Reading and writing files is only allowed within the provided directory, but it is recommended to avoid this.
- **Network requests**: Long or blocking network operations may cause errors or timeouts.

---

## **2. How to Send a Script to the Bot**
1. Create a script file, e.g., `my_script.py`.
2. Send the file to the bot as a **document** in Telegram.
3. The bot will automatically execute the script and send back the result.

---

## **3. Bot Response**

The bot will return a message in the following format:

```
**Status**: Successfully executed
**Output:**
```
```
Text output from your script
```

In case of an error:
```
**Status**: Execution error
**Output:**
```
```
Error text or failure reason
```

---

## **4. Examples of Errors**
| **Error**                         | **Reason**                           |
|----------------------------------|--------------------------------------|
| Execution error                   | Syntax or logical error              |
| Please send a .py file            | A file with a different extension was sent |

---

## **5. Recommendations**
- Test scripts locally before sending them.
- Avoid complex calculations and infinite loops.
- If problems arise, check the log files saved by the bot.

---

Now you are ready to use the bot to run and test your Python scripts! 🚀

