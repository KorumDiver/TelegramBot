import datetime

import telebot
from telebot import types
import MainDirectory.DataBase.DataBase as database

# Создание бота и базы, инициализация пула
our = "1438178504:AAF5-LIj7iPbGZWmPT8vOJJeGHjyjH3NTiQ"
my = "839505966:AAGv0SHKb_jSQ_M6YUdx9G-SGSLS9MxHAF8"
bot = telebot.TeleBot(our)
db = database.DataBase()
# pool = {id:{role:1 ,last_time:121212, log:[my/record, name_course]}, ...}
pool = {}

# Список первых команд
first_command_students = ["Мой курсы", "Запись"]
button_back = "Назад"
# Список курсов доступных в данный момент(на момент запуска бота)
courses = [i["name"] for i in db.get_all_course()]


def start_keyboard_student():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(*first_command_students, "Инфо")
    return markup


def start_keyboard_teacher():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Мои курсы', 'Записаться', 'Инфо')
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
        role = db.whoIs(id_user)
        if role == 0:
            user = {"role": role, "time": datetime.datetime.now(), "log": [None, None]}
            pool[id_user] = user
        elif role == 1:
            user_log = db.get_log(id_user, role)
            user = {"role": role, "time": datetime.datetime.now(), "log": user_log}
            pool[id_user] = user
        elif role == 2:
            # TODO дописать логику пула для препода
            pass
    for key, value in pool.items():
        if (datetime.datetime.now() - value["time"]).total_seconds() > 15 * 60:
            pool.pop(key)
            # db.update_log(id_user, log) TODO Дописать обновление логов
        else:
            pool[key]["time"] = datetime.datetime.now()
    return user


# Начальная стадия работы бота
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
    elif role == 1:
        bot.send_message(id_user, "Выберете действие:", reply_markup=start_keyboard_student())
    elif role == 2:
        bot.send_message(id_user, "Выберете действие:",
                         reply_markup=start_keyboard_teacher())  # TODO дописать клавиатуру для препода


@bot.message_handler(commands=["register"])
def register(message):
    id_user = message.chat.id
    user = check(id_user)
    role = user["role"]
    if role == 0:
        msg = bot.send_message(message.chat.id, "Отправьте ФИО резделенное знаком пробела")
        bot.register_next_step_handler_by_chat_id(message.chat.id, __reg)
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированны", reply_markup=start_keyboard_student())


def __reg(message):
    fio = str(message.text).split(' ')
    if len(fio) == 3:
        db.registration_user(message.chat.id, fio[1], fio[0], fio[2], 1)
        bot.send_message(message.chat.id, "Выберете действие:", reply_markup=start_keyboard_student())
        pool[message.chat.id]["role"] = 1
    else:
        msg = bot.send_message(message.chat.id, "Отправьте ФИО резделенное знаком пробела")
        bot.register_next_step_handler_by_chat_id(message.chat.id, __reg)


# Этап выбора Мой курсы, запись и инфо
@bot.message_handler(regexp="Инфо")
def info_handler(message):
    role = db.whoIs(message.chat.id)
    if role == 0:
        bot.send_message(message.chat.id, "Вы не зарегестированны! Пройдите регистрацию /register")
    elif role == 1:
        info = db.get_info_student(message.chat.id)
        info_course = info["info_about_courses"]
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
        text = "Имя: %s\nФамилия: %s\nОтчество: %s\n%s" % (info["name_student"], info["surname_student"],
                                                           info["middle_name_student"], info_course_text)
        bot.send_message(message.chat.id, text)


# Переход к выбору курсов
@bot.message_handler(func=lambda message: message.text in first_command_students)
def work_or_record(message):
    id_user = message.chat.id
    user = check(id_user)
    role = user["role"]
    text = message.text
    if role == 0:
        bot.send_message(id_user, "Вы не зарегестрированны! Пройдите регистрацию: /register")
    elif role == 1:
        keyboard_course = courses_keyboard(id_user, role, text)
        if keyboard_course is None:
            return
        bot.send_message(id_user, "Выберете курс:", reply_markup=keyboard_course)
    elif role == 2:
        # TODO дописать поведение для препода
        pass


# Клавиатура для выбора курсов
def courses_keyboard(id_user, role, text):
    if text == first_command_students[0]:
        pool[id_user]["log"] = [first_command_students[0], None]
        course = [i["name"] for i in db.get_my_course(id_user, role)]
        error_text = "Вы не записанны ни на один курс"
    elif text == first_command_students[1]:
        pool[id_user]["log"] = [first_command_students[1], None]
        course = [i["name_subject"] for i in db.get_not_attend(id_user)]
        error_text = "Вы записанны на все доступные курсы"

    if len(course) == 0:
        bot.send_message(id_user, error_text)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*course, 'Назад')
    return markup


@bot.message_handler(func=lambda message: message.text in [*courses, button_back])
def courses_command(message):
    id_user = message.chat.id
    user = check(id_user)
    role = user["role"]
    text = message.text
    if role == 0:
        bot.send_message(id_user, "Вы не зарегестрированны! Пройдите регистрацию: /register")
    elif role == 1:
        if text == button_back:
            pool[id_user]["log"] = [None, None]
            bot.send_message(id_user, "Выберете действие:", reply_markup=start_keyboard_student())
        elif user["log"][0] == first_command_students[0]:  # Мой курсы
            pool[id_user]["log"][1] = text
            bot.send_message(id_user, "Выберете действие:", reply_markup=course_functions(role))
        elif user["log"][0] == first_command_students[1]:  # Запись
            inline_keyboard = types.InlineKeyboardMarkup()
            inline_keyboard.add(types.InlineKeyboardButton("Записаться", callback_data="record;%s" % text))
            bot.send_message(id_user, get_info_course(text), reply_markup=inline_keyboard)
        elif role == 2:
            pass  # TODO Дописать для препода


def get_info_course(name):
    info_course = db.get_info_to_course(name)
    text_response = "Название курса: %s\nИнформация по курсу: %s\nПреподователь: %s" % (
        info_course["name_subject"], info_course["info"], info_course["teacher"])
    return text_response


@bot.callback_query_handler(func=lambda message: True)
def record_course(message):
    id_user = message.message.chat.id
    user = check(id_user)
    role = user["role"]
    if "record" in message.data:
        course = message.data.split(";")[1]
        not_my_courses = [i["name_subject"] for i in db.get_not_attend(id_user)]
        if course in not_my_courses:
            db.entry_to_course(id_user, course)
            bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                  text="Вы успешно записанны на курс %s" % course, reply_markup=None)
            if len(not_my_courses) != 1:
                bot.send_message(id_user, "Хотите записаться еще на один курс?",
                                 reply_markup=courses_keyboard(id_user, role, first_command_students[1]))
            else:
                pool[id_user]["log"] = [None, None]
                bot.send_message(id_user, "Выберете действие:", reply_markup=start_keyboard_student())
        else:
            bot.send_message(bot.send_message(id_user, "Вы уже записанны на курс %s" % course,
                                              reply_markup=courses_keyboard(id_user, role, first_command_students[1])))
    elif "hw;" in message.data:
        num_course = int(message.data.split(";")[1])
        home_work = db.get_home_work(user['log'][1])["tasks"][num_course - 1]
        print(home_work)
        text_hw = "Информация по домашнему заданию:\n%s\nСдать до %s" % (home_work["info_task"], home_work["dead_line"])
        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                              text=text_hw, reply_markup=None)
    elif "unsubscribe;" in message.data:
        course = message.data.split(";")[1]
        my_course = [i["name"] for i in db.get_my_course(id_user, role)]
        if course in my_course:
            db.leave_to_course(id_user, course)
            bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.message_id,
                                  text="Вы успешно поку=инули курс: %s" % course, reply_markup=None)
            if len(my_course) == 1:
                bot.send_message(id_user, "Вы не записанны ни на один курс!", reply_markup=start_keyboard_student())
            else:
                bot.send_message(id_user, "Выберете курс:",
                                 reply_markup=courses_keyboard(id_user, role, user["log"][0]))

        else:
            pool[id_user]["log"][1] = None
            bot.send_message(bot.send_message(id_user, "Вы не посещаете данный курс!",
                                              reply_markup=courses_keyboard(id_user, role, first_command_students[0])))


# Список команд для работы с курсом
command_course_student = ["Описание курса", "Литература по курсу", "Домашнее задание", "Рейтинг", "Отписаться",
                          "К выбору курса"]


# клавиатура функционала курса
def course_functions(role):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if role == 1:
        markup.add(*command_course_student)
    elif role == 2:
        markup.add('Описание курса', 'Список студентов', 'ДЗ', 'Постинг', 'Рейтинг', 'Журнал', 'Литература',
                   'К выбору курса')
    return markup


# этап работы с курсом
@bot.message_handler(func=lambda message: message.text in command_course_student)
def work_in_course(message):
    id_user = message.chat.id
    user = check(id_user)
    role = user["role"]
    text = message.text
    if role == 0:
        bot.send_message(id_user, "Вы не зарегестрированны! Пройдите регистрацию: /register")
    elif role == 1:
        course = pool[id_user]["log"][1]
        if course is not None:
            if text == command_course_student[0]:  # Описание курса
                bot.send_message(id_user, get_info_course(course))
            elif text == command_course_student[1]:  # Литература
                literature_from_course = db.get_literature(course)["literatures"]
                response_text = "Литература по курсу %s\n" % course
                for i, value in enumerate(literature_from_course):
                    response_text += "%s: %s\n" % (i + 1, value["name"])
                bot.send_message(id_user, response_text)
            elif text == command_course_student[2]:  # Получение Дз
                size_home_work = len(db.get_home_work(course)["tasks"])
                if size_home_work == 0:
                    bot.send_message(id_user, "Ура!!! Нет домашнего задания!!!")
                else:
                    inline_keyboard = types.InlineKeyboardMarkup()
                    for i in range(1, size_home_work + 1):
                        inline_keyboard.add(
                            types.InlineKeyboardButton("Домашнее задание №%s" % i, callback_data="hw;%s" % i))
                    bot.send_message(id_user, "Выберете номер домашнего задания:", reply_markup=inline_keyboard)
            elif text == command_course_student[3]:  # Рейтинг
                info_course = db.get_info_student(id_user)["info_about_courses"]
                for i in info_course:
                    if i["name_course"] == course:
                        rating = i["rating"]
                        if rating is None:
                            rating = 0
                        bot.send_message(id_user, "Ваш рейтинг по курсу %s: %s" % (course, rating))
                        return
            elif text == command_course_student[4]:  # Отписаться
                inline_keyboard = types.InlineKeyboardMarkup()
                inline_keyboard.add(
                    types.InlineKeyboardButton("Отписаться", callback_data="unsubscribe;%s" % course))
                bot.send_message(id_user, "Вы точно хотите отписаться?", reply_markup=inline_keyboard)
            elif text == command_course_student[5]:  # К выбору курса
                pool[id_user]["log"][1] = None
                bot.send_message(id_user, "Выбирете курс:",
                                 reply_markup=courses_keyboard(id_user, role, user["log"][0]))

        else:
            bot.send_message(id_user, "Что то пошло не так)", start_keyboard_student())

    elif role == 2:
        pass


bot.polling(none_stop=True)
