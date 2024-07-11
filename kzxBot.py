import telebot, random
from telebot.async_telebot import AsyncTeleBot

from telebot import types
token = ""
bot = telebot.TeleBot(token, parse_mode=None)
global stait
global games


class blackJack:
    def __init__(self):
        self.create_deck()
        self.hand = []
        self.dealer_hand = []

    def create_deck(self):# создаю рандомную колоду
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        random.shuffle(self.deck)
        return self.deck

    def give_hand(self):# описываю функцию раздачи карты
        card = self.deck.pop()
        self.hand.append(card)
        return card
        # return self.hand почему возвращает мне массив


    def give_dealerHand(self): # описываю функцию выше для диллера
        dealer_card = self.deck.pop()# удаляю карту и присваиваю удаленное значение переменной карте
        self.dealer_hand.append(dealer_card)
        # return self.dealer_hand почему-то вощврашает мне массив

    def player_hit(self): # эта функция сделана для присваивания кнопке после нажатия hit
        return self.give_hand()

    def calc_hand(self, hand):
        # Подсчет очков в руке, учитывая туз (11 или 1)
        total = sum(hand)
        aces = hand.count(11)
        while total > 21 and aces:
            total -= 10
            aces -= 1
            self.hand.remove(11)
            self.hand.append(1)

        return total


    def start_deal(self):# функция описывает начало игры - раздачу
        self.hand.clear()
        self.dealer_hand.clear()
        self.create_deck()
        # print(self.hand)
        # print(self.dealer_hand)
        self.give_hand()
        self.give_dealerHand()
        self.give_hand()

        print(f'рука игрока {self.hand}')
        print(f'рука диллера {self.dealer_hand}')


    # def victory(self):
    #     if sum(self.hand)>sum(self.dealer_hand):
    #         print('победа игрока!')
    #     if sum(self.dealer_hand) > sum(self.hand):
    #         print('победа диллера!')
    #     if sum(self.dealer_hand) == sum(self.hand):
    #         print('Ничья!')

    def get_game_state(self):
        # Возвращает текущее состояние игры
        return {
            'hand': self.hand,
            'dealer_hand': self.dealer_hand,
            'total': self.calc_hand(self.hand),
            'total_dealer': self.calc_hand(self.dealer_hand)
        }



@bot.message_handler(commands=['start'])
def start_game(message):
    global games
    chat_id = message.chat.id
    games = blackJack()
    stait = games.get_game_state()

    bot.send_message(chat_id,f'ваша рука: {stait['hand']}, ваш счёт: {stait['total']}')
    bot.send_message(chat_id,f'видимая карта диллера: {stait['dealer_hand']}, счёт диллера: {stait['total_dealer']}')
    game_do(chat_id)

@bot.message_handler(commands = ['button'])
def game_do(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('Hit')
    itembtn2 = types.KeyboardButton('Stand')
    markup.add(itembtn1, itembtn2)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Hit', 'Stand'])
def hadle_doing(message):
    global games
    chat_id = message.chat.id
    if message.text == 'Hit':

        # Игрок выбрал "Hit" (взять карту)
        card = games.player_hit()
        state = games.get_game_state()

        bot.send_message(chat_id, f'вы взяли карту {card}! ваша рука: {state['hand']}, счёт: {sum(state['hand'])}')

        if state['total'] > 21:#плаки-плаки
            # Игрок проиграл (перебор)
            bot.send_message(chat_id, "Вы проиграли! Перебор. Игра окончена.")
            del games[chat_id]
        else:
            game_do(chat_id)  # Повторная отправка клавиатуры если бро дурак

    elif message.text == 'Stand':
        # Игрок выбрал "Stand" (остановиться)
        games.give_dealerHand()
        state = games.get_game_state()
        bot.send_message(chat_id, f"Карты дилера: {state['dealer_hand']}, сумма очков: {state['total_dealer']}")

        player_total = state['total']
        total_dealer = state['total_dealer']

    # кто виннер?---->>>
        if total_dealer > 21 or player_total > total_dealer or player_total == 21:
            bot.send_message(chat_id, "Вы выиграли!")
        elif player_total < total_dealer:
            bot.send_message(chat_id, "Дилер выиграл!")
        else:
            bot.send_message(chat_id, "Ничья!")




bot.infinity_polling(none_stop = True, interval = 0)
# print(test.start_deal())
# print(test.deck)
# print(test.give_hand())
# print(test.give_dealerHand())
# print(test.start_deal())
















# @bot.message_handler(commands=['start', 'kz'])
# def start_game(message):
#     chatId = message.chat.id
#     bot.send_message(chatId, "добро пожаловать в игру 21 или как её называют в простонародие - очко/n"
#                              "правила игры известны многим и надеюсь вам, удачи!")
