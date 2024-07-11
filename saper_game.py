import asyncio
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.async_telebot import AsyncTeleBot
import random

TOKEN = ''
bot = AsyncTeleBot("")

# Глобальный словарь для хранения сессий пользователей
sessions = {}

def create_empty_board(size=8):
    return [[' ' for _ in range(size)] for _ in range(size)]

def place_ships(board, ship_count=15):
    size = len(board)
    placed_ships = 0
    while placed_ships < ship_count:
        row = random.randint(0, size - 1)
        col = random.randint(0, size - 1)
        if board[row][col] == ' ':
            board[row][col] = 'O'
            placed_ships += 1
    return board

def check_win(otvety, board):
    for row in range(len(board)):
        for col in range(len(board[row])):
            if otvety[row][col] == 'O' and board[row][col] != '🚩':
                return False
    return True

def count_ships_around(row, col, board):
    count = 0
    size = len(board)
    for r in range(max(0, row - 1), min(size, row + 2)):
        for c in range(max(0, col - 1), min(size, col + 2)):
            if board[r][c] == 'O' and (r != row or c != col):
                count += 1
    return str(count)

def create_game_board(board):
    markup = InlineKeyboardMarkup(row_width=8)
    buttons = []
    for row in range(len(board)):
        for col in range(len(board[row])):
            text = board[row][col]
            if text == ' ':
                text = f'{row},{col}'
            elif text == 'x':
                text = '💣'
            elif text == '1':
                text = '1️⃣'
            elif text == '2':
                text = '2️⃣'
            elif text == '3':
                text = '3️⃣'
            elif text == '4':
                text = '4️⃣'
            elif text == '5':
                text = '5️⃣'
            elif text == '6':
                text = '6️⃣'
            elif text == '7':
                text = '7️⃣'
            elif text == '0':
                text = '0️⃣'
            buttons.append(InlineKeyboardButton(text, callback_data=f'{row},{col}'))
    markup.row(InlineKeyboardButton("Поставить флаг", callback_data="flag"))

    for i in range(0, len(buttons), 8):
        markup.row(*buttons[i:i + 8])
    return markup

@bot.message_handler(commands=['start'])
async def start(message):
    chat_id = message.chat.id
    try:
        await bot.delete_message(message.chat.id, message.message_id - 1)
        await bot.delete_message(message.chat.id, message.message_id - 2)
    except:
        pass
    board_with_ships = create_empty_board()
    otvety = place_ships(board_with_ships)
    session = {
        'otvety': otvety,
        'board': create_empty_board(),
        'hits_count': 0,
        'game_active': True,
        'waiting_for_flag_input': False,
        'flag_message_id': None
    }
    sessions[chat_id] = session
    board_markup = create_game_board(session['board'])
    await bot.send_message(chat_id, "Добро пожаловать в игру 'Сапер'!", reply_markup=board_markup)

@bot.callback_query_handler(func=lambda call: call.data == 'flag')
async def handle_flag_query(call):
    chat_id = call.message.chat.id
    session = sessions.get(chat_id)
    if session and session['game_active']:
        try:
            session['waiting_for_flag_input'] = True
            message = await bot.send_message(chat_id, f"Введите координаты клетки для установки флага в формате 'строка,столбец' (например, 1,1):")
            session['flag_message_id'] = message.message_id

        except Exception as e:
            print(f"Ошибка при обработке запроса на постановку флага: {e}")


@bot.message_handler(func=lambda message: sessions.get(message.chat.id, {}).get('waiting_for_flag_input'))
async def process_flag_input(message):
    chat_id = message.chat.id
    session = sessions.get(chat_id)
    if not session:
        return
    try:
        row, col = map(int, message.text.split(','))
        if 0 <= row < len(session['board']) and 0 <= col < len(session['board'][0]):
            session['board'][row][col] = '🚩'
            new_board = create_game_board(session['board'])
            await bot.delete_message(chat_id, message.message_id)
            await bot.delete_message(chat_id, session['flag_message_id'])
            game_message = bot.send_message(chat_id, 'Флаг успешно поставлен', reply_markup=new_board)
            await bot.delete_message(chat_id, game_message.message_id - 1)
        else:
            await bot.send_message(chat_id, "Неверные координаты. Введите числа в допустимом диапазоне.")
        session['hits_count'] += 1
        if session['hits_count'] == 15:
            session['game_active'] = False
            if check_win(session['otvety'], session['board']):
                await bot.send_message(chat_id, "Поздравляю, вы выиграли! Чтобы начать новую игру, введите /start.")
            else:
                await bot.send_message(chat_id, "Вы проиграли! Не все флаги стоят на правильных местах. Чтобы начать новую игру, введите /start.")
        session['waiting_for_flag_input'] = False
    except ValueError:
        await bot.send_message(chat_id, "Неверный формат координат. Введите числа через запятую (например, 1,1).")
    except Exception as e:
        print(f"Ошибка при обработке ввода координат: {e}")

@bot.callback_query_handler(func=lambda call: True)
async def handle_query(call):
    chat_id = call.message.chat.id
    session = sessions.get(chat_id)
    if not session or not session['game_active']:
        return
    if call.data == 'flag':
        return
    if call.data == '🚩':
        return
    row, col = map(int, call.data.split(','))
    try:
        if session['otvety'][row][col] == 'O':
            session['board'][row][col] = 'x'
            session['game_active'] = False
            await bot.send_message(chat_id, "Вы проиграли! Чтобы начать новую игру, введите /start.")
            session['hits_count'] += 1
            await bot.answer_callback_query(call.id, f"вы попали {row},{col}")
        elif session['otvety'][row][col] == ' ':
            session['board'][row][col] = count_ships_around(row, col, session['otvety'])
    except:
        pass
    new_board = create_game_board(session['board'])
    await bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=new_board)

if __name__ == '__main__':
    asyncio.run(bot.polling())
