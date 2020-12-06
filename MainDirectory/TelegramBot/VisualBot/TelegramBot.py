import telebot
from telebot import types
bot = telebot.TeleBot("1438178504:AAF5-LIj7iPbGZWmPT8vOJJeGHjyjH3NTiQ")
class TelegramBot:
    def __init__(self):
        """
            Инициирует все возможные переменные класса. Создает связь с API Telegram, инициализирует бота в системе.
            Импортирует библиотеки. Инициализирует класс ResponseAnswerBot
        """

    # начальная клавиатура
    def start_keyboard(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row('Мои курсы', 'Записаться', 'Инфо')
        return markup

    # клавиатура курсов (создаётся для каждого индивидуально)
    def courses_keyboard(self, courses):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*courses, 'Назад')
        return markup

    # клавиатура функционала курса
    def course_functions(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('Описание курса', 'ДЗ', 'Рейтинг', 'Журнал', 'Литература', 'Отписаться', 'К выбору курса')
        return markup

    # клавиатура записи на курс (инлайн кнопки)
    def sign_up_to_course(self):
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(types.InlineKeyboardButton('Записаться', callback_data='sign-up'), types.InlineKeyboardButton('Назад', callback_data='start-panel'))
        return inline_markup

