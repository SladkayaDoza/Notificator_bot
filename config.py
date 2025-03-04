
# ID владельца бота для приема заявок
ADMIN_ID = 718619868

# Ограничение использование памяти для одного процесса (рекомендовано 50мб)
memory_limit = 100

cancel_message = "У вас нет доступа к этому боту 🚫\n \
По причине возможного зловредного использования,\n \
Вы можете подать заявку коммандой `/request` \n \
Или установите код проекта на свой сервер.\n \
Код проекта: https://github.com/SladkayaDoza/Notificator_bot"

help_message = """
<b>✨ Available Commands:</b>

/start - <code>Start interacting with the bot</code>
/code &lt;script&gt; - <code>Send code directly as a command</code>
/tasks - <code>List all active tasks</code>
/archive - <code>List all completed tasks</code>
/launch &lt;task_id&gt; - <code>Run a script from the archive</code>
/kill &lt;task_id&gt; - <code>Stop a specific task</code>
/bot - <code>Display bot and system statistics</code>
/hide &lt;id or start-end or all&gt; - <code>Hide tasks from archive</code>

<b>👥 User Management:</b>
/getusers - <code>Show the list of allowed users</code>
/adduser &lt;user_id&gt; - <code>Add a user to the whitelist</code>
/removeuser &lt;user_id&gt; - <code>Remove a user from the whitelist</code>
/request - <code>Submit a request to be added to the whitelist</code>
"""