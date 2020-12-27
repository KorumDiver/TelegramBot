import datetime

import telebot
# import MainDirectory.DataBase.DataBase as database
from telebot import types

bot = telebot.TeleBot("1438178504:AAF5-LIj7iPbGZWmPT8vOJJeGHjyjH3NTiQ")

pool = {418531001: {"role": 2, "last_time": datetime.datetime.now(), "log": ["Мой курсы", "BD"]}}


# начальная клавиатура
def start_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('ДЗ', 'Работа со студентами')
    return markup


def check(id_user: int):
    """
    Поверяет пользователя на наличее в пуле
    :param id_user: токен пользователя
    :return:
    """
    # Получение пользователя из пула
    user = pool.get(id_user)
    # Если пользователя нет в пуле, то запрос в базу. И создание пользователя.
    if user is None:
        # role = db.whoIs(id_user)
        role = 1  # чисто заглушка
        # user_log = db.get_log(id_user, role)
        user_log = ["Мой курсы", "BD"]  # чисто заглушка
        user = {"role": role, "time": datetime.datetime.now(), "log": user_log}
        pool[id_user] = user
    else:
        user["time"] = datetime.datetime.now()

    for key, value in pool.items():
        if (datetime.datetime.now() - value["time"]).total_seconds() > 15 * 60:
            pool.pop(key)

    return user


@bot.message_handler(commands=['start'])
def Hello(message):
    bot.send_message(message.chat.id, message.chat.id, reply_markup=start_keyboard())


def homework(message):
    # ret = database.get_home_work(name_course=pool[message.chat.id]) # список дз из базы
    user = check(message.chat.id)
    ret = {"name_course": 'БД',
           "tasks": {}}
    for i in range(3):
        ret['tasks'][i + 1] = {"info_task": "info" + (str)(i + 1), "dead_line": "dead_line" + (str)(i + 1)}
    task_ids = list(ret['tasks'].keys())
    inline_markup = types.InlineKeyboardMarkup()
    for i in range(len(ret['tasks'])):
        inline_markup.row(
            types.InlineKeyboardButton('ДЗ ' + (str)(i + 1), callback_data='dz-' + (str)(task_ids[i]) + '-' + (str)(i + 1)))
    bot.send_message(message.chat.id, "Выберите ДЗ:", reply_markup=inline_markup)


d = {'ДЗ': homework}


@bot.message_handler(func=lambda message: message.text in ['ДЗ', 'Работа со студентами'])
def actioin(message):
    d[message.text](message)


@bot.callback_query_handler(func=lambda call: call.data[0] == 'd' and call.data[1] == 'z')
def callback_dz(call):
    user = check(call.message.chat.id)
    ret = {"name_course": 'БД',
           "tasks": {}}
    for i in range(3):
        ret['tasks'][(str)(i + 1)] = {"info_task": "info" + (str)(i + 1), "dead_line": "dead_line" + (str)(i + 1)}
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='') # удаление страой инлайн-клавиатуры
    data = call.data.split('-')
    s = 'ДЗ ' + data[2] + "\n\n" + ret['tasks'][data[1]]["info_task"] + "\n\n" + "Сделать до: " + ret['tasks'][data[1]]["dead_line"]
    bot.answer_callback_query(call.id)
    if user['role'] == 2:
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(types.InlineKeyboardButton('Редактировать', callback_data='edit_dz-' + data[1]),
                          types.InlineKeyboardButton('Удалить', callback_data='del_dz-' + data[1]))
        inline_markup.row(types.InlineKeyboardButton('Отметить выполнение', callback_data='mark_dz-' + data[1]))
        bot.send_message(call.message.chat.id, s, reply_markup=inline_markup)
    else:
        bot.send_message(call.message.chat.id, s)

@bot.callback_query_handler(func=lambda call: 'edit_dz' in call.data)
def callback_edit_dz(call):
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')

'''def homework(message):
    tasks = database.get_home_work(name_course=pool[message.chat.id])
    inline_markup = types.InlineKeyboardMarkup()
    for i in range(dz_count):
        inline_markup.row(types.InlineKeyboardButton('ДЗ ' + (str)(i + 1), callback_data='dz-' + (str)(i + 1)))
    return inline_markup'''

bot.polling(none_stop=True)

# user[0] = message.chat.id
