import datetime

import telebot
from telebot import types
import MainDirectory.DataBase.DataBase as database
import MainDirectory.DataProcessor.DataProcessor as da

my = "839505966:AAGv0SHKb_jSQ_M6YUdx9G-SGSLS9MxHAF8"
bot = telebot.TeleBot(my)
db = da.db

# pool = {id_user: {role, last_time, log:[мой курсы/записаться, название курса]}
# pool = {id_user: {role, last_time, log:[мой курсы, название курса]}
pool = {}
start_menu_button = 'В гланое меню'
choose_course_button = "К выбору курса"
all_courses = [i["name"] for i in db.get_all_course()]


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
        role = db.whoIs(id_user)
        user_log = db.get_log(id_user, role)
        user = {"role": role, "time": datetime.datetime.now(), "log": user_log}
        pool[id_user] = user
    else:
        user["time"] = datetime.datetime.now()

    for key, value in pool.items():
        if (datetime.datetime.now() - value["time"]).total_seconds() > 15 * 60:
            pool.pop(key)

    return user


# Global function


def get_start_keyboard(role):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key_keyboard = start_command_key
    if role == 0:
        markup = None
    elif role == 1:
        markup.row(*key_keyboard)
    elif role == 2:
        markup.row(key_keyboard[0], key_keyboard[2])
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    id_user = message.chat.id
    user = check(id_user)
    role = user["role"]
    print(pool)
    # Обнуление данных
    bot.send_message(id_user, "Добро пожаловать!", reply_markup=types.ReplyKeyboardRemove())
    pool[id_user]["log"] = [None, None]  # Режим выбора (Мой курсы, запись, инфо)

    if role == 0:
        bot.send_message(id_user, "Вы не зарегестрированны! Пройдите регистрацию: /register")
    else:
        bot.send_message(id_user, "Выберете дествие:", reply_markup=get_start_keyboard(role))


@bot.message_handler(commands=["register"])
def register(message):
    id_user = message.chat.id
    user = check(id_user)
    role = user["role"]
    if role == 0:
        msg = bot.send_message(message.chat.id, "Отправьте ФИО резделенное знаком пробела")
        bot.register_next_step_handler_by_chat_id(message.chat.id, __reg)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированны", reply_markup=get_start_keyboard(role))


def __reg(message):
    fio = str(message.text).split(' ')
    if len(fio) == 3:
        db.registration_user(message.chat.id, fio[1], fio[0], fio[2], 1)
        bot.send_message(message.chat.id, "Выберете действие:", reply_markup=get_start_keyboard(1))
        pool[message.chat.id]["role"] = 1
    else:
        msg = bot.send_message(message.chat.id, "Отправьте ФИО резделенное знаком пробела")
        bot.register_next_step_handler_by_chat_id(message.chat.id, __reg)


# ---------------------------------------------------

# Стартовое меню для препода и студента

def my_courses(id_user):
    user = check(id_user)
    user["log"][0] = start_command_key[0]
    role = user["role"]
    if role == 0:
        text = "Вы не зарегестированны! Пройдите регистрацию /register"
        markup = types.ReplyKeyboardRemove()
    else:
        courses = [i["name"] for i in db.get_my_course(id_user, role)]
        if len(courses) == 0:
            markup = None
            text = "Вы не записанны ни на один курс!"
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*courses, start_menu_button)
            text = "Выберете курс:"
    bot.send_message(id_user, text, reply_markup=markup)


def record_courses(id_user):
    user = check(id_user)
    user["log"][0] = start_command_key[1]
    role = user['role']
    if role == 0:
        text = "Вы не зарегестированны! Пройдите регистрацию /register"
        markup = types.ReplyKeyboardRemove()
    elif role == 1:
        courses = [i["name"] for i in db.get_not_attend(id_user)]
        if len(courses) == 0:
            text = "Вы записанны на все курсы!"
            markup = None
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*courses, start_menu_button)
            text = "Выберете курс:"
    bot.send_message(id_user, text, reply_markup=markup)


def info(id_user):
    user = check(id_user)
    role = user['role']
    if role == 0:
        bot.send_message(id_user, "Вы не зарегестированны! Пройдите регистрацию /register")
    elif role == 1:
        info_stud = db.get_info_student(id_user)
        info_course = info_stud["info_about_courses"]
        info_course_text = "Список посещаемых курсов:\n"
        if info_course[0]["name_course"] is None:
            info_course_text = "Вы не записанны ни на один курс"
        else:
            for course in info_course:
                rating = course["rating"]
                if rating is None:
                    rating = 0
                info_course_text += """    Имя курса: %s\n    Преподователь: %s\n    Количество баллов: %s\n\n""" % \
                                    (course["name_course"], course["name_teacher"], rating)
        text = "Имя: %s\nФамилия: %s\nОтчество: %s\n%s" % (info_stud["name_student"], info_stud["surname_student"],
                                                           info_stud["middle_name_student"], info_course_text)
        bot.send_message(id_user, text)
    elif role == 2:
        text = db.get_info_teacher(id_user)
        bot.send_message(id_user, text)


start_command_key = ["Мой курсы", "Запись", "Инфо"]
start_command_function = [my_courses, record_courses, info]
start_command_dict = dict([(start_command_key[i], start_command_function[i]) for i in range(len(start_command_key))])


@bot.message_handler(func=lambda message: message.text in start_command_key)
def main_functions(message):
    try:
        bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id - 1, reply_markup='')
    finally:
        id_user = message.chat.id
        start_command_dict[message.text](id_user)


# ______________________________________________________________________________________________________________________
# Этап выбор курса
@bot.message_handler(func=lambda message: message.text in [*all_courses, start_menu_button])
def choose_course(message):
    try:
        bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id - 1, reply_markup='')
    finally:
        id_user = message.chat.id
        user = check(id_user)
        role = user["role"]
        if role == 0:
            text = "Вы не зарегестированны! Пройдите регистрацию /register"
            markup = types.ReplyKeyboardRemove()
            bot.send_message(id_user, text, reply_markup=markup)
        elif message.text == start_menu_button:
            user['log'][0] = None
            bot.send_message(id_user, "Выберете действие:", reply_markup=get_start_keyboard(role))
        else:
            if user["log"][0] == start_command_key[0]:
                main_menu_course(id_user, user, message.text)
            elif user["log"][0] == start_command_key[1]:
                record_course(id_user, user, message.text)


def main_menu_course(id_user, user, course):
    role = user["role"]
    text = "Выберете действие"
    user["log"][1] = course
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if role == 1:
        markup.add(*courses_command_key[:5], choose_course_button)
    elif role == 2:
        markup.add(*courses_command_key[:2], courses_command_key[3], *courses_command_key[5:], choose_course_button)
    bot.send_message(id_user, text, reply_markup=markup)


def record_course(id_user, user, course):
    role = user["role"]
    if role == 1:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Записаться", callback_data="record;%s" % course))
        bot.send_message(id_user, get_info_course(course), reply_markup=markup)
    else:
        bot.send_message(id_user, "Вы не можете записаться на курс!")


@bot.callback_query_handler(func=lambda call: "record;" in call.data)
def entry_to_course(call):
    id_user = call.message.chat.id
    course = call.data.split(";")[1]
    not_my_courses = [i["name"] for i in db.get_not_attend(id_user)]
    if course in not_my_courses:
        db.entry_to_course(id_user, course)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Вы успешно записанны на курс '%s'" % course)
        if len(not_my_courses) != 1:
            bot.send_message(id_user, "Хотите записаться еще на один курс?")
            record_courses(id_user)
        else:
            pool[id_user]["log"] = [None, None]
            bot.send_message(id_user, "Выберете действие:", reply_markup=get_start_keyboard(1))
    else:
        bot.send_message(id_user, "Вы уже записанны на курс %s" % course)


def get_info_course(name):
    info_course = db.get_info_to_course(name)
    text_response = "Название курса: %s\nИнформация по курсу: %s\nПреподователь: %s" % (
        info_course["name_subject"], info_course["info"], info_course["teacher"])
    return text_response


# ______________________________________________________________________________________________________________________
@bot.callback_query_handler(func=lambda call: "change" in call.data)  # change; info/literature; name_course
def change(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
    finally:
        what_change, course = call.data.split(";")[1:]
        msg = bot.send_message(call.message.chat.id,
                               "Все, что вы напишете будет сохранено в том же виде. Проверьте правильность перед отправкой!")
        if what_change == "info":
            bot.register_next_step_handler(msg, edit_info)
        elif what_change == "literature":
            bot.register_next_step_handler(msg, edit_literature)


def edit_info(message):
    id_user = message.chat.id
    user = check(id_user)
    db.edit_info_course(id_user, user["log"][1], message.text)
    bot.send_message(id_user, "Описание курса изменено на:\n%s" % message.text)


def edit_literature(message):
    id_user = message.chat.id
    user = check(id_user)
    db.edit_literature(id_user, user["log"][1], 0, message.text)
    bot.send_message(id_user, "Литература успешно изменена:\n%s" % message.text)


def info_course_func(id_user):
    user = check(id_user)
    text = get_info_course(user['log'][1])
    role = user["role"]
    markup = None
    if role == 2:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Редактировать", callback_data="change;info;%s" % user["log"][1]))
    bot.send_message(id_user, text, reply_markup=markup)


def literature(id_user):
    user = check(id_user)
    text = db.get_literature(user["log"][1])["literatures"][0]["name"]
    role = user["role"]
    markup = None
    if role == 2:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Редактировать", callback_data="change;literature;%s" % user["log"][1]))
    bot.send_message(id_user, text, reply_markup=markup)


def rating(id_user):
    user = check(id_user)
    course = user['log'][1]
    info_course = db.get_info_student(id_user)["info_about_courses"]
    for i in info_course:
        if i["name_course"] == course:
            my_rating = i["rating"]
            if my_rating is None:
                my_rating = 0
            bot.send_message(id_user, "Ваш рейтинг по курсу %s: %s" % (course, my_rating))
            return

    bot.send_message(id_user, "Вы не записанны на курс '%s'" % course)


def home_work(id_user):
    user = check(id_user)

    ret = db.get_home_work(name_course=pool[id_user]['log'][1])  # список дз из базы
    task_ids = list(ret['tasks'].keys())
    inline_markup = types.InlineKeyboardMarkup()
    for i in range(len(ret['tasks'])):
        inline_markup.row(
            types.InlineKeyboardButton('ДЗ ' + str(i + 1),
                                       callback_data='dz-' + str(task_ids[i]) + '-' + str(i + 1)))
    if user['role'] == 2:
        inline_markup.row(types.InlineKeyboardButton('Создать', callback_data='create_dz'))
        inline_markup.row(types.InlineKeyboardButton('Журнал', callback_data='journal'))
    bot.send_message(id_user, "Выберите ДЗ:", reply_markup=inline_markup)


def leave_course(id_user):
    user = check(id_user)
    role = user['role']
    course = user['log'][1]
    if role == 1:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Уйти с курса", callback_data="unsubscribe;%s" % course))
        bot.send_message(id_user, "Вы точно хотите отписаться?", reply_markup=markup)

    else:
        bot.send_message("Не корректная команда!")


@bot.callback_query_handler(func=lambda call: 'unsubscribe;' in call.data)
def leave_course_inline(call):
    id_user = call.message.chat.id

    course = call.data.split(";")[1]
    my_course = [i["name"] for i in db.get_my_course(id_user, 1)]
    if course in my_course:
        db.leave_to_course(id_user, course)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Вы успешно покинули курс: %s" % course, reply_markup=None)
        if len(my_course) == 1:
            bot.send_message(id_user, "Вы не записанны ни на один курс!", reply_markup=get_start_keyboard(1))
        else:
            my_courses(id_user)


def mark_visit(id_user):
    pass


def work_on_student(id_user):
    user = check(id_user)
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Все студенты', callback_data='all_stud'))
    ret = db.get_students_from_course(id_user, user['log'][1])
    for i in ret['students']:
        FIO = i['surname_student'] + " " + i['name_student'] + " " + i["middle_name_student"]
        id_stud = i['id_student']
        rating = i['rating']
        inline_markup.row(types.InlineKeyboardButton(FIO, callback_data='one_stud-' + str(id_stud) + '-' + str(rating)))
    bot.send_message(id_user, 'Вы хотите работать с конкретным студентом или же со всеми сразу?',
                     reply_markup=inline_markup)


@bot.message_handler(func=lambda message: message.text in [*courses_command_key, choose_course_button])
def course_function(message):
    try:
        bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id - 1, reply_markup='')
    finally:
        id_user = message.chat.id
        user = check(id_user)
        role = user['log']
        if role == 0:
            bot.send_message(id_user, "Вы не зарегестированны! Пройдите регистрацию /register",
                             reply_markup=types.ReplyKeyboardRemove())
        elif message.text == choose_course_button:
            my_courses(id_user)
            user['log'][1] = None
        else:
            courses_command_dict[message.text](id_user)


courses_command_key = ["Описание курса", "Литература", "Рейтинг", "ДЗ", "Уйти с курса", "Посещение",
                       "Работа со студентами"]
courses_command_function = [info_course_func, literature, rating, home_work, leave_course, mark_visit, work_on_student]
courses_command_dict = dict(
    [(courses_command_key[i], courses_command_function[i]) for i in range(len(courses_command_key))])


# _____________________________________________________________________________________________________________________
def completed_task_students(call, mode):
    dz_id = call.data.split('-')[1]
    user = check(call.message.chat.id)
    ret = db.get_students_completed_task(1, user['log'][1], dz_id)
    inline_markup = types.InlineKeyboardMarkup()
    if mode == 'refactor':
        for i in ret['students']:
            inline_markup.row(
                types.InlineKeyboardButton(i['surname'] + " " + i["name"] + " " + i["middle_name"],
                                           callback_data='refact_stud-' + str(dz_id) + "-" + str(i['id_student'])))
    elif mode == 'deny':
        for i in ret['students']:
            inline_markup.row(
                types.InlineKeyboardButton(i['surname'] + " " + i["name"] + " " + i["middle_name"],
                                           callback_data='comp_stud-' + str(dz_id) + "-" + str(i['id_student'])))
    inline_markup.row(types.InlineKeyboardButton('Назад', callback_data='mark_dz-' + str(dz_id)))
    return inline_markup


def not_completed_task_students(call):
    dz_id = call.data.split('-')[1]
    user = check(call.message.chat.id)
    ret = db.get_students_not_completed_task(1, user['log'][1], dz_id)
    inline_markup = types.InlineKeyboardMarkup()
    for i in ret['students']:
        inline_markup.row(
            types.InlineKeyboardButton(
                i['surname'] + " " + i["name"] + " " + i["middle_name"],
                callback_data='ac_stud-' + str(dz_id) + "-" + str(i['id_student'])))
    inline_markup.row(types.InlineKeyboardButton('Назад', callback_data='mark_dz-' + str(dz_id)))
    return inline_markup


@bot.callback_query_handler(func=lambda call: call.data[0] == 'd' and call.data[1] == 'z')
def callback_dz(call):
    user = check(call.message.chat.id)
    ret = db.get_home_work(user['log'][1])
    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)  # удаление строго сообщения
    data = call.data.split('-')
    s = 'ДЗ ' + data[2] + "\n\n" + ret['tasks'][int(data[1])]["info_task"] + "\n\n" + "Сделать до: " + \
        str(ret['tasks'][int(data[1])]["dead_line"])
    bot.answer_callback_query(call.id)
    if user['role'] == 2:
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(types.InlineKeyboardButton('Редактировать',
                                                     callback_data='edit_dz-' + data[1] + '-' + data[2] + '-' +
                                                                   ret['tasks'][int(data[1])]["info_task"] + '-' + str(
                                                         ret['tasks'][int(data[1])]["dead_line"])),
                          types.InlineKeyboardButton('Удалить', callback_data='del_dz-' + data[1]))
        inline_markup.row(types.InlineKeyboardButton('Отметить выполнение', callback_data='mark_dz-' + data[1]))
        bot.send_message(call.message.chat.id, s, reply_markup=inline_markup)
    else:
        bot.send_message(call.message.chat.id, s)


@bot.callback_query_handler(func=lambda call: 'create_dz' in call.data)
def callback_create_dz(call):
    user = check(call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id)
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
    msg = bot.send_message(call.message.chat.id, 'Введите текст ДЗ:', reply_markup=inline_markup)
    bot.register_next_step_handler(msg, enter_new_dz)


def enter_new_dz(message):
    user = check(message.chat.id)
    s = message.text
    bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id - 1, reply_markup='')
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
    msg = bot.send_message(message.chat.id, 'Введите дедлайн в формате dd.mm.yyyy', reply_markup=inline_markup)
    bot.register_next_step_handler(msg, enter_new_deadline, s)


def enter_new_deadline(message, s):
    user = check(message.chat.id)
    try:
        time = datetime.datetime.strptime(message.text, '%d.%m.%Y').date()
        bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id - 1, reply_markup='')
    except(ValueError):
        bot.send_message(message.chat.id, 'Дата некорректна. Введите дату правильно!')
        bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id - 1, reply_markup='')
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
        msg = bot.send_message(message.chat.id, 'Введите дедлайн в формате dd.mm.yyyy', reply_markup=inline_markup)
        bot.register_next_step_handler(msg, enter_new_deadline, s)
        return
    task = {"info_task": s, "dead_line": time}
    db.add_home_work(message.chat.id, user['log'][1], task['info_task'], task["dead_line"])
    bot.send_message(message.chat.id, 'Задание успешно создано')
    ret = db.get_students_from_course(message.chat.id, user['log'][1])
    for i in ret['students']:
        try:
            bot.send_message(i['id_student'],
                             user['log'][1] + '\n\nСоздано новое ДЗ!\n\n' + task[
                                 'info_task'] + "\n\nВыполнить до " + str(task['dead_line']))
        except:
            continue


@bot.callback_query_handler(func=lambda call: 'edit_dz' in call.data)
def callback_edit_dz(call):
    user = check(call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id,
                              'Отправленный вами текст будет сохранён! Нажмите "Отмена" для прерывания операции',
                              show_alert=True)
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
    msg = bot.send_message(call.message.chat.id, 'Введите новый текст:', reply_markup=inline_markup)
    bot.register_next_step_handler(msg, edit_homework, call.data.split('-')[1], call.data.split('-')[2],
                                   call.data.split('-')[3], call.data.split('-')[4])


def edit_homework(message, dz_id, dz_num, dz_info, dz_deadline):
    user = check(message.chat.id)
    db.edit_home_work(message.chat.id, user['log'][1], dz_id, message.text)
    bot.delete_message(message.chat.id, message_id=message.message_id - 1)
    bot.send_message(message.chat.id, 'Изменения сохранены!')
    ret = db.get_students_from_course(message.chat.id, user['log'][1])
    for i in ret['students']:
        try:
            bot.send_message(i['id_student'],
                             user['log'][
                                 1] + '\n\nДЗ ' + dz_num + ' было отредактировано!\n\n' + dz_info + "\n\nВыполнить до: " + dz_deadline)
        except:
            continue


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_dz')
def finish_editing_dz(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id, 'Операция отменена')
    bot.clear_step_handler(call.message)


@bot.callback_query_handler(func=lambda call: 'del_dz' in call.data)
def callback_delete_dz(call):
    user = check(call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id)
    dz_id = call.data.split('-')[1]
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Подтвердить', callback_data='confirm_delete_dz-' + dz_id),
                      types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
    bot.send_message(call.message.chat.id, 'Вы желаете удалить данное задание?', reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: 'confirm_delete_dz' in call.data)
def deleting_dz(call):
    user = check(call.message.chat.id)
    dz_id = call.data.split('-')[1]
    db.delete_home_work(dz_id)
    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id, 'Задание удалено!')


@bot.callback_query_handler(func=lambda call: 'mark_dz' in call.data)
def callback_mark_dz(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)
    inline_markup = types.InlineKeyboardMarkup()
    dz_id = call.data.split('-')[1]
    inline_markup.row(types.InlineKeyboardButton('Принять сдачу', callback_data='accept_dz-' + dz_id))
    inline_markup.row(types.InlineKeyboardButton('Изменить сдачу', callback_data='refactor_dz-' + dz_id))
    inline_markup.row(types.InlineKeyboardButton('Отменить сдачу', callback_data='deny_dz-' + dz_id))
    bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: 'accept_dz' in call.data)
def accepting_dz(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'По нажатии на студента сдача автоматически засчитается:',
                     reply_markup=not_completed_task_students(call))


@bot.callback_query_handler(func=lambda call: 'ac_stud' in call.data)
def accept_student(call):
    user = check(call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id)
    id_stud = call.data.split('-')[2]
    id_task = call.data.split('-')[1]
    accepting_entering(call, id_stud, id_task)


def accepting_entering(call, id_stud, id_task):
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
    msg = bot.send_message(call.message.chat.id, 'Введите количество баллов', reply_markup=inline_markup)
    bot.register_next_step_handler(msg, enter_point, id_stud, id_task, call)


def enter_point(message, id_stud, id_task, call):
    user = check(message.chat.id)
    try:
        points = int(message.text)
        bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id - 1, reply_markup='')
    except:
        bot.send_message(message.chat.id, 'Неверный формат. Введите баллы корректно!')
        bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id - 1, reply_markup='')
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
        msg = bot.send_message(message.chat.id, 'Введите количество баллов', reply_markup=inline_markup)
        bot.register_next_step_handler(msg, enter_point, id_stud, id_task, call)
        return
    db.mark_completed_task(message.chat.id, pool[message.chat.id]['log'][1], int(id_task), int(id_stud),
                           points)  # запись отметки в бд
    bot.send_message(message.chat.id, 'Задание успешно сдано!')
    bot.send_message(call.message.chat.id, 'По нажатии на студента сдача автоматически засчитается:',
                     reply_markup=not_completed_task_students(call))


@bot.callback_query_handler(func=lambda call: 'refactor_dz' in call.data)
def callback_refactor_dz(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'По нажатии на студента начнётся редактирование баллов за данное задание:',
                     reply_markup=completed_task_students(call, 'refactor'))


@bot.callback_query_handler(func=lambda call: 'refact_stud' in call.data)
def refactoring_dz(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id,
                              'Отправленный вами текст будет сохранён! Нажмите "Отмена" для прерывания операции',
                              show_alert=True)
    id_stud = call.data.split('-')[2]
    id_task = call.data.split('-')[1]
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
    msg = bot.send_message(call.message.chat.id, 'Введите количество баллов', reply_markup=inline_markup)
    bot.register_next_step_handler(msg, enter_new_point, call, id_stud, id_task)


def enter_new_point(message, call, id_stud, id_task):
    user = check(message.chat.id)
    try:
        points = int(message.text)
        bot.delete_message(message.chat.id, message_id=message.message_id - 1)
    except:
        bot.send_message(message.chat.id, 'Неверный формат. Введите баллы корректно!')
        bot.delete_message(message.chat.id, message_id=message.message_id - 1)
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
        msg = bot.send_message(message.chat.id, 'Введите количество баллов', reply_markup=inline_markup)
        bot.register_next_step_handler(msg, enter_new_point, id_stud, id_task, call)
        return
    db.edit_completed_task(1, user['log'][1], id_task, id_stud, points)
    bot.send_message(message.chat.id, 'Изменения сохранены!')
    bot.send_message(message.chat.id, 'По нажатии на студента начнётся редактирование баллов за данное задание:',
                     reply_markup=completed_task_students(call, 'refactor'))


@bot.callback_query_handler(func=lambda call: 'deny_dz' in call.data)
def callback_deny_dz(call):
    user = check(call.message.chat.id)
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'По нажатии на студента сдача будет отменена:',
                     reply_markup=completed_task_students(call, 'deny'))


@bot.callback_query_handler(func=lambda call: 'comp_stud' in call.data)
def denying_dz(call):
    user = check(call.message.chat.id)
    db.del_mark_completed_task(*call.data.split('-')[1:])
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'Задание удалено!')
    bot.send_message(call.message.chat.id, 'По нажатии на студента сдача будет отменена:',
                     reply_markup=completed_task_students(call, 'deny'))


# работа со студентами
@bot.callback_query_handler(func=lambda call: call.data == 'all_stud')
def all_stud_work(call):
    user = check(call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id, 'Режим работы со всеми студентами')
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Краткий журнал', callback_data='short_jurn'))
    inline_markup.row(types.InlineKeyboardButton('Журнал', callback_data='jurnal'),
                      types.InlineKeyboardButton('Анализ', callback_data='analiz'))
    bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'short_jurn')
def show_short_jurnal(call):
    user = check(call.message.chat.id)
    bot.answer_callback_query(call.id)
    short_j = da.get_course_info(call.message.chat.id, user['log'][1])
    bot.send_message(call.message.chat.id, short_j)


@bot.callback_query_handler(func=lambda call: call.data == 'journal')
def show_jurnal(call):
    user = check(call.message.chat.id)
    bot.answer_callback_query(call.id, 'Файл сформирован')
    doc_path = da.generate_excel(call.message.chat.id, user['log'][1])
    bot.send_document(call.message.chat.id, open(doc_path, 'rb'))


@bot.callback_query_handler(func=lambda call: call.data == 'analiz')
def show_analiz(call):
    user = check(call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id)
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Гистограма по рейтингу', callback_data='rat_hist'))
    inline_markup.row(types.InlineKeyboardButton('Гистограма по посещаемости', callback_data='visit_hist'))
    inline_markup.row(types.InlineKeyboardButton('Выполнение дз', callback_data='plot_dz'))
    bot.send_message(call.message.chat.id, 'Что вы хотите получить?', reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'rat_hist')
def show_rating_hist(call):
    user = check(call.message.chat.id)
    image_path = da.create_rating_diagram(call.message.chat.id, user['log'][1])
    bot.send_photo(call.message.chat.id, open(image_path, 'rb'))
    bot.answer_callback_query(call.id, 'Изображение построено')


@bot.callback_query_handler(func=lambda call: call.data == 'visit_hist')
def show_visit_hist(call):
    user = check(call.message.chat.id)
    image_path = da.plot_number_of_attended_lessons_diagram(call.message.chat.id, user['log'][1])
    bot.send_photo(call.message.chat.id, open(image_path, 'rb'))
    bot.answer_callback_query(call.id, 'Изображение построено')


@bot.callback_query_handler(func=lambda call: call.data == 'plot_dz')
def show_plot_bar_dz(call):
    user = check(call.message.chat.id)
    image_path = da.plot_performed_homeworks_diagram(call.message.chat.id, user['log'][1])
    bot.send_photo(call.message.chat.id, open(image_path, 'rb'))
    bot.answer_callback_query(call.id, 'Изображение построено')


@bot.callback_query_handler(func=lambda call: 'one_stud' in call.data)
def callback_one_stud(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)


bot.polling(none_stop=True)
