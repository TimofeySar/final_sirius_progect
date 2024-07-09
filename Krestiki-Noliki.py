import telebot
from telebot import types

token = "7253160866:AAERrlt_AfAf-a6UM0-G3Qvam3MZfHv1aUg"
bot = telebot.TeleBot(token, parse_mode=None)

item = {}

gameIsStart = False

gameGround = [" ", " ", " ",
              " ", " ", " ",
              " ", " ", " ", ]

playerSymbols = ["❌", "🔵"]
currentPlayer = 0

print("Bot is start")

def clear():
    global gameGround
    gameGround = [" ", " ", " ",
                  " ", " ", " ",
                  " ", " ", " ", ]

def check_winner():
    winning_positions = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]
    for pos in winning_positions:
        if gameGround[pos[0]] == gameGround[pos[1]] == gameGround[pos[2]] and gameGround[pos[0]] != " ":
            return gameGround[pos[0]]
    if " " not in gameGround:
        return "draw"
    return None

@bot.message_handler(commands=['start'])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item[0] = types.KeyboardButton("Крестики нолики")
    markup.add(item[0])

    bot.send_message(message.chat.id,
                     "Привет, давай поиграем в крестики-нолики!",
                     parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def mess(message):
    global gameIsStart
    if message.chat.type == 'private':
        if message.text == "Крестики нолики":
            gameIsStart = True
            start_game(message)
        else:
            bot.send_message(message.chat.id, "Я не знаю таких слов :(")

def start_game(message):
    global markup, item
    bot.send_message(message.chat.id, "Игра началась")
    markup = types.InlineKeyboardMarkup(row_width=3)
    for i in range(9):
        item[i] = types.InlineKeyboardButton(gameGround[i], callback_data=str(i))
    markup.row(item[0], item[1], item[2])
    markup.row(item[3], item[4], item[5])
    markup.row(item[6], item[7], item[8])
    bot.send_message(message.chat.id, "Первый ход - ❌. Выберите клетку:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callbackInline(call):
    global currentPlayer
    global gameIsStart
    if call.message:
        for i in range(9):
            if call.data == str(i):
                if gameGround[i] == " ":
                    gameGround[i] = playerSymbols[currentPlayer]
                    currentPlayer = 1 - currentPlayer

        winner = check_winner()

        for i in range(9):
            item[i] = types.InlineKeyboardButton(gameGround[i], callback_data=str(i))

        global markup
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.row(item[0], item[1], item[2])
        markup.row(item[3], item[4], item[5])
        markup.row(item[6], item[7], item[8])

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)

        if winner:
            clear()
            if winner == "draw":
                bot.send_message(call.message.chat.id, "Ничья!")
                currentPlayer = 0
            else:
                bot.send_message(call.message.chat.id, f"Победил {winner}!")
                gameIsStart = False
                currentPlayer = 0
        else:
            bot.edit_message_text(call.message.id, 'Выберите клетку', reply_markup=markup)


bot.infinity_polling(none_stop=True, interval=0)

