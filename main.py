from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
from support_db import add_support_ticket, get_user_support_tickets

import sqlite3
import random

admin_user_id = '1951252873'

# Define the admin states
ADMIN_ADD_GAME, ADMIN_ADD_GAME_NAME, ADMIN_ADD_GAME_DESCRIPTION = range(3, 6)


# Создание базы данных и таблицы
def create_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            is_registered BOOLEAN NOT NULL DEFAULT 0,
            is_admin BOOLEAN NOT NULL DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()


def create_interest_database(interest):
    conn = sqlite3.connect(f'{interest}.db')
    cursor = conn.cursor()

    # Create the games table with a description column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# Добавление пользователя в базу данных
def add_user(user_id, is_registered=False, is_admin=False):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Добавление пользователя
    cursor.execute('''
        INSERT OR REPLACE INTO users (id, is_registered, is_admin)
        VALUES (?, ?, ?)
    ''', (user_id, is_registered, is_admin))

    conn.commit()
    conn.close()


# Получение информации о пользователе
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Получение пользователя
    cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user = cursor.fetchone()

    conn.close()
    return user if user else None


# Определите состояния, в которых может быть бот
GUEST, USER, ADMIN = range(3)

# Определите данные пользователя
user_data = {}


# Function to add a game to an interest database
def add_game_to_interest(interest, game_name, game_description):
    conn = sqlite3.connect(f'{interest}.db')
    cursor = conn.cursor()

    # Add the game with description
    cursor.execute('INSERT INTO games (name, description) VALUES (?, ?)', (game_name, game_description))

    conn.commit()
    conn.close()


# Function to get a random game from an interest database
def get_random_game_from_interest(interest):
    conn = sqlite3.connect(f'{interest}.db')
    cursor = conn.cursor()

    # Get all games
    cursor.execute('SELECT * FROM games')
    games = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return a random game
    return random.choice(games) if games else None


def show_game(interest, game_name):
    conn = sqlite3.connect(f'{interest}.db')
    cursor = conn.cursor()

    # Получаем описание игры из базы данных
    cursor.execute('SELECT description FROM games WHERE name = ?', (game_name,))
    game_description = cursor.fetchone()

    conn.close()

    if game_description:
        return game_description[0]  # Возвращаем описание игры
    else:
        return f"Игра '{game_name}' не найдена."


# Define the list of interests
interests = ["shooters", "strategy", 'horror', 'mmo', 'sports', 'rpg', 'adventure', '🏳️‍🌈']

# Recreate databases for each interest with the updated schema
for interest in interests:
    create_interest_database(interest)


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'state': GUEST}
        add_user(user_id, is_admin=(str(user_id) == admin_user_id))

    keyboard = [
        [InlineKeyboardButton("Выбрать игру", callback_data='choose_game')],
        [InlineKeyboardButton("Тех.поддержка", callback_data='support')],
        [InlineKeyboardButton("Помощь", callback_data='help')],
    ]
    if str(user_id) == admin_user_id:
        keyboard.append([InlineKeyboardButton("Добавить игру", callback_data='add_game')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Здравствуй друг, выбери что пожелаешь!', reply_markup=reply_markup)


async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
    """
    if update.message:
        await update.message.reply_text(help_text)
    else:
        # If the update is not a message update, you can use the original query to send a message
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=help_text)


# Function to get a random game from an interest database
def get_random_game_from_interest(interest):
    conn = sqlite3.connect(f'{interest}.db')
    cursor = conn.cursor()

    # Get all games
    cursor.execute('SELECT * FROM games')
    games = cursor.fetchall()

    # Close the connection
    conn.close()

    # Return a random game
    return random.choice(games) if games else None


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    user_id = update.callback_query.from_user.id
    if user_id not in user_data:
        # If the user's data is not initialized, initialize it
        user_data[user_id] = {'state': GUEST}
        add_user(user_id, is_admin=(str(user_id) == admin_user_id))

    user_id = query.from_user.id
    if user_data[user_id]['state'] == GUEST:
        if query.data == 'choose_game':
            keyboard = [[InlineKeyboardButton(interest, callback_data=interest)] for interest in interests]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Пожалуйста, выберите ваш интерес:", reply_markup=reply_markup)
        elif query.data in interests:
            game = get_random_game_from_interest(query.data)
            if game:
                game_name = game[1]  # Assuming the game name is the second column
                game_description = game[2]
                await query.edit_message_text(text=f"Ваша игра на сегодня: {game_name} \n{game_description}")
            else:
                await query.edit_message_text(text="Извините, игр по выбранному вами интересу нет.")
        elif query.data == 'support':
            await query.edit_message_text(text="Пожалуйста, опишите вашу проблему:")
            user_data[user_id]['state'] = 'support'
        elif query.data == 'help':
            await help_command(update, context)
        elif query.data == 'add_game' and str(user_id) == admin_user_id:
            keyboard = [[InlineKeyboardButton(interest, callback_data=f'add_game_{interest}')] for interest in
                        interests]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="В какой интерес вы хотите добавить игру?", reply_markup=reply_markup)
            user_data[user_id]['state'] = ADMIN_ADD_GAME
        else:
            await query.edit_message_text(text="Извините, я не понял ваш запрос.")
    elif user_data[user_id]['state'] == ADMIN_ADD_GAME:
        interest = query.data.split('_')[-1]
        user_data[user_id]['interest'] = interest
        await query.edit_message_text(text=f"Введите название игры для интереса {interest}:")
        user_data[user_id]['state'] = ADMIN_ADD_GAME_NAME
    elif user_data[user_id]['state'] == ADMIN_ADD_GAME_NAME:
        game_name = query.data
        user_data[user_id]['game_name'] = game_name
        await query.edit_message_text(text=f"Введите описание игры '{game_name}':")
        user_data[user_id]['state'] = ADMIN_ADD_GAME_DESCRIPTION
    elif user_data[user_id]['state'] == ADMIN_ADD_GAME_DESCRIPTION:
        game_description = query.data
        interest = user_data[user_id]['interest']
        game_name = user_data[user_id]['game_name']
        add_game_to_interest(interest, game_name, game_description)
        await query.edit_message_text(text=f"Игра '{game_name}' добавлена в интерес '{interest}'.")
        user_data[user_id]['state'] = GUEST
    else:
        await query.edit_message_text(text="Извините, я не понял ваш запрос.")


async def support_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    support_text = update.message.text
    add_support_ticket(user_id, support_text)
    await context.bot.send_message(chat_id=user_id,
                                   text="Ваше обращение принято. Мы постараемся помочь вам как можно скорее.")
    try:
        await context.bot.send_message(chat_id=admin_user_id,
                                       text=f"User {user_id} needs support with the following issue:\n{support_text}")
    except telegram.error.BadRequest as e:
        # Handle the error here, for example, log it or notify the user
        print(f"Error sending message: {e}")


async def message_handler(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {'state': GUEST}
        add_user(user_id, is_admin=(str(user_id) == admin_user_id))

    if user_data[user_id]['state'] == ADMIN_ADD_GAME_NAME:
        game_name = update.message.text
        user_data[user_id]['game_name'] = game_name
        await update.message.reply_text(f"Введите описание игры '{game_name}':")
        user_data[user_id]['state'] = ADMIN_ADD_GAME_DESCRIPTION
    elif user_data[user_id]['state'] == ADMIN_ADD_GAME_DESCRIPTION:
        game_description = update.message.text
        interest = user_data[user_id]['interest']
        game_name = user_data[user_id]['game_name']
        add_game_to_interest(interest, game_name, game_description)
        await update.message.reply_text(f"Игра '{game_name}' добавлена в интерес '{interest}'.")
        user_data[user_id]['state'] = GUEST
    else:
        # If the user is not in the process of adding a game, ignore the message
        pass


def main() -> None:
    # Создайте Application и передайте ему токен вашего бота.
    application = Application.builder().token("7039136722:AAGdRluqei0kMd0JPahe-Cx0JS8wCU_XIdc").build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Зарегистрируйте обработчик команды /start
    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    # Зарегистрируйте обработчик колбэков
    button_handler = CallbackQueryHandler(button)
    application.add_handler(button_handler)

    # Зарегистрируйте обработчик сообщений для тех.поддержки
    support_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), support_message)
    application.add_handler(support_handler)

    # Register the help command handler
    help_handler = CommandHandler("help", help_command)
    application.add_handler(help_handler)

    # Запустите бота до тех пор, пока пользователь не нажмет Ctrl-C
    application.run_polling()


if __name__ == '__main__':
    create_database()
    # Create databases for each interest
    for interest in interests:
        create_interest_database(interest)
    main()
