import telebot
from telebot import apihelper
# import MainDirectory.DataBase.DataBase as database
from telebot import types

bot = telebot.TeleBot("1438178504:AAF5-LIj7iPbGZWmPT8vOJJeGHjyjH3NTiQ")

# начальная клавиатура
def start_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Мои курсы', 'Записаться', 'Инфо')
    return markup


# клавиатура курсов (создаётся для каждого индивидуально)
def courses_keyboard(courses):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*courses, 'Назад')
    return markup


# клавиатура функционала курса
def course_functions():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Описание курса', 'ДЗ', 'Рейтинг', 'Журнал', 'Литература', 'Отписаться', 'К выбору курса')
    return markup


# клавиатура записи на курс (инлайн кнопки)
def sign_up_to_course():
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Записаться', callback_data='sign-up'),
                      types.InlineKeyboardButton('Назад', callback_data='start-panel'))
    return inline_markup


# db = DataBase()

# id| роль | last_time_message| tec_curs| my_courses |
cv_user_id = {-1: [0, 0, {"course": ""}]}

kursi_studenta = ["BD", " MATSTAt", "TAU", "RUSSIAN"]

funcional_po_c = ['Описание курса', 'Получить дз', 'Получить свой рейтинг по курсу', 'Литература по курсу']


# STUDENT

def check(id, new_time):
    if id not in cv_user_id.keys():
        # k = db.whoIs(id)
        k = 0
        if k == 0:
            bot.send_message(id, "Извините, вы не зарегистрированы, отправьте /register")
        elif k == 1:
            bot.send_message(id, "Выберите действие:", start_keyboard())
        elif k == 2:
            bot.send_message(id, "Выберите действие:", 'клава препода')
        cv_user_id[id] = [k, new_time, {}]
        return False
    return True


@bot.message_handler(commands=['start'])
def Hello(message):
    if (check(message.chat.id, message.date)):
        if cv_user_id[message.chat.id][0] != 0:
            bot.send_message(message.chat.id, "Выберите действие:", start_keyboard())
        else:
            bot.send_message(message.chat.id, "Отправьте /register")
        #                                                  "Здравствуйте, студент! Давайте приступим к регистрации. Введите свои ФИО через пробел."
        #                                                 " Внимание, вы сможете это сделать только один раз!"), student_registration)


@bot.message_handler(commands=['register'])
def regist(message):
    if (check(message.chat.id, message.date)):
        msg = bot.send_message(message.chat.id, "Отправьте свои ФИО, разделите пробелом:")
        bot.register_next_step_handler(msg,
                                       take_info)  # функция проверки сказала снова отправить комнаду, значит далее он отправляет ееё и заходит в первое условие, поэтому else
        # не нужен и нужно просто дальше принять данные


def take_info(message):
    s = message.text.split(" ")
    print(s[0], s[1])
    # Запись в бд и
    cv_user_id[message.chat.id][0] = 1
    bot.send_message(message.chat.id, "Выберите действие:", course_functions())


@bot.message_handler(func=lambda message: message.text == "Мои курсы")
def my_c(message):
    if (check(message.chat.id, message.date)):
        if cv_user_id[message.chat.id][0] == 1:
            msg = bot.send_message(message.chat.id, "Выберите предмет:", courses_keyboard())  # Здесь отрпавка чуваку клавиатуры с его курсами, генерация клавы из бд
            bot.register_next_step_handler(msg, take_cours)


def take_cours(message):  # он выбрал предмет
    cv_user_id[message.chat.id][2]["course"] = message.text
    bot.send_message(message.chat.id, "Выберите действие",
                     start_keyboard())  # Здесь отправляется клава с вариантами действия функционала по курсу


@bot.message_handler(func=lambda message: message.text == "Запись")
def my_c(message):
    if (check(message.chat.id, message.date)):
        if cv_user_id[message.chat.id][0] == 1:
            msg = bot.send_message(message.chat.id, "Выберите предмет:", sign_up_to_course())  # Здесь отрпавка чуваку клавиатуры с курсами, на которые он не записан, генерация клавы хз
            bot.register_next_step_handler(msg, take_cours1)


def take_cours1(message):  # он выбрал предмет
    cv_user_id[message.chat.id][2]["course"] = message.text
    s = "blablabla"  # на самом деле здесь из бд берется описание по cv_user_id[message.chat.id][2]["course]
    bot.send_message(message.chat.id, s)  # Здесь отправляется описание
    bot.send_message(message.chat.id, "Хотите записаться?",
                     start_keyboard())  # Здесь отправляется клава с вариантами Записаться
    bot.send_message(message.chat.id, s, start_keyboard)  # Здесь отправляется описание


@bot.message_handler(func=lambda message: message.text == "Записаться")
def my_c(message):
    if (check(message.chat.id, message.date)):
        # Здесь работа с записью в бд
        bot.send_message(message.chat.id, "Вы записаны")
        bot.send_message(message.chat.id,
                         start_keyboard())  # отправили главную калвиатуру с мои курсы, записаться и инфо


@bot.message_handler(func=lambda message: message.text == "Описание курса")
def describe(message):
    if (check(message.chat.id, message.date)):
        s = "blablabla"  # на самом деле здесь из бд берется описание по cv_user_id[message.chat.id][2]["course]
        bot.send_message(message.chat.id, s)


@bot.message_handler(func=lambda message: message.text == "Получить ДЗ")
def describe(message):
    if (check(message.chat.id, message.date)):
        s = "blablabla"  # на самом деле здесь из бд берется дз по cv_user_id[message.chat.id][2]["course] и mesage.chat.id
        bot.send_message(message.chat.id, s)


@bot.message_handler(func=lambda message: message.text == "Литература по курсу")
def litr(message):
    if (check(message.chat.id, message.date)):
        s = "blablabla"  # на самом деле здесь из бд берется литература по cv_user_id[message.chat.id][2]["course]
        bot.send_message(message.chat.id, s)


@bot.message_handler(func=lambda message: message.text == "Удалиться с курса ")
def deleeete(message):
    if (check(message.chat.id, message.date)):
        # на самом деле здесь из бд удаляется человек по cv_user_id[message.chat.id][2]["course] и mesage.chat.id
        del cv_user_id[message.chat.id]
        bot.send_message(message.chat.id, "Вы успешно удалены")


bot.polling(none_stop=True)

# user[0] = message.chat.id
