import datetime

import telebot
# import MainDirectory.DataBase.DataBase as database
#import MainDirectory.DataProcessor.DataProcessor as da
from telebot import types

bot = telebot.TeleBot("1438178504:AAF5-LIj7iPbGZWmPT8vOJJeGHjyjH3NTiQ")

pool = {418531001: {"role": 2, "last_time": datetime.datetime.now(), "log": ["Мой курсы", "BD"]}, 485330050:{"role": 2, "last_time": datetime.datetime.now(), "log": ["Мой курсы", "BD"]}}

course_functions = ['ДЗ', 'Работа со студентами']


# начальная клавиатура
def start_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('ДЗ', 'Работа со студентами', 'Посещение')
    return markup

def completed_task_students(call):
    dz_id = call.data.split('-')[1]
    ret = {"id_subject": '1',
           "name_subject": 'БД',
           "students": []}
    for i in range(3):
        ret['students'].append({"id_student": (str)(i + 1),
                                "name_student": 'Эмиль' + (str)(i + 1),
                                "surname_student": 'Закиев' + (str)(i + 1),
                                "middle_name_student": 'Рамилевич' + (str)(i + 1),
                                "rating": '10000000' + (str)(i + 1)})
    inline_markup = types.InlineKeyboardMarkup()
    for i in ret['students']:
        inline_markup.row(
            types.InlineKeyboardButton(i['surname_student'] + " " + i["name_student"] + " " + i["middle_name_student"],
                                       callback_data='comp_stud-' + i['id_student'] + "-" + dz_id))
    inline_markup.row(types.InlineKeyboardButton('Назад', callback_data='mark_dz-'+dz_id))
    return inline_markup

def not_comoleted_task_sudents(call, mode):
    dz_id = call.data.split('-')[1]
    ret = {"id_subject": '1',
           "name_subject": 'БД',
           "students": []}
    for i in range(3):
        ret['students'].append({"id_student": (str)(i + 1),
                                "name_student": 'Александр' + (str)(i + 1),
                                "surname_student": 'Коробов' + (str)(i + 1),
                                "middle_name_student": 'Александрович' + (str)(i + 1),
                                "rating": '10000000' + (str)(i + 1)})
    inline_markup = types.InlineKeyboardMarkup()
    if mode == 'accept':
        for i in ret['students']:
            inline_markup.row(
                types.InlineKeyboardButton(i['surname_student'] + " " + i["name_student"] + " " + i["middle_name_student"],
                                           callback_data='ac_stud-' + dz_id + "-" + i['id_student']))
    elif mode == 'refactor':
        for i in ret['students']:
            inline_markup.row(
                types.InlineKeyboardButton(i['surname_student'] + " " + i["name_student"] + " " + i["middle_name_student"],
                                           callback_data='refact_stud-' + dz_id + "-" + i['id_student']))
    inline_markup.row(types.InlineKeyboardButton('Назад', callback_data='mark_dz-'+dz_id))
    return inline_markup

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
        user = {"role": role, "last_time": datetime.datetime.now(), "log": user_log}
        pool[id_user] = user
    else:
        user["time"] = datetime.datetime.now()

    for key, value in pool.items():
        if (datetime.datetime.now() - value["last_time"]).total_seconds() > 15 * 60:
            pool.pop(key)

    return user


@bot.message_handler(commands=['start'])
def Hello(message):
    print(message.chat.id)
    bot.send_message(message.chat.id, message.chat.id, reply_markup=start_keyboard())


def homework(message):
    # ret = database.get_home_work(name_course=pool[message.chat.id]['log][1]) # список дз из базы
    user = check(message.chat.id)
    ret = {"name_course": 'БД',
           "tasks": {}}
    for i in range(3):
        ret['tasks'][i + 1] = {"info_task": "info" + (str)(i + 1), "dead_line": "dead_line" + (str)(i + 1)}
    task_ids = list(ret['tasks'].keys())
    inline_markup = types.InlineKeyboardMarkup()
    for i in range(len(ret['tasks'])):
        inline_markup.row(
            types.InlineKeyboardButton('ДЗ ' + (str)(i + 1),
                                       callback_data='dz-' + (str)(task_ids[i]) + '-' + (str)(i + 1)))
    inline_markup.row(types.InlineKeyboardButton('Создать', callback_data='create_dz'))
    bot.send_message(message.chat.id, "Выберите ДЗ:", reply_markup=inline_markup)


def student_work(message):
    user = check(message.chat.id)
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Все студенты', callback_data='all_stud'))
    # ret = database.get_students_from_course(message.chat.id, user['log'][1])
    ret = {'students': [{'id_student': 418531001, 'name_student':'Эмиль', "surname_student": 'Закиев',
                                        "middle_name_student": 'Рамилевич',
                                        "rating": 100000}, {'id_student': 485330050, 'name_student':'Александр', "surname_student": 'Коробов',
                                        "middle_name_student": 'Александрович',
                                        "rating": 20000}]}
    for i in ret['students']:
        FIO = i['surname_student'] + " " + i['name_student'] + " " + i["middle_name_student"]
        id_stud = i['id_student']
        rating = i['rating']
        inline_markup.row(types.InlineKeyboardButton(FIO, callback_data='one_stud-' + str(id_stud) + '-' + str(rating)))
    bot.send_message(message.chat.id, 'Вы хотите работать с конкретным студентом или же со всеми сразу?', reply_markup=inline_markup)


def attendance(message):
    user = check(message.chat.id)
    #ret = database.get_lessons_from_course(message.chat.id, user['log'][1])
    ret_until_today = []
    ret = {'lessons': []}
    k = 1
    for i in range(3):
        ret["lessons"].append({"id_lesson": i+1,
                               "date_lesson": datetime.datetime.strptime('0'+str(i+1)+'.01.2020', '%d.%m.%Y').date()})
    ret['lessons'].append({'id_lesson': 3, 'date_lesson': datetime.datetime.strptime('0'+str(i+1)+'.01.2021', '%d.%m.%Y').date()})
    for i in ret['lessons']:
        if i['date_lesson'] <= datetime.date.today():
            ret_until_today.append(i)
    inline_markup = types.InlineKeyboardMarkup()
    for i in ret_until_today:
        date_to_str = datetime.datetime.strftime(i['date_lesson'], '%d.%m.%Y')
        inline_markup.row(types.InlineKeyboardButton(date_to_str, callback_data='att-' + str(i['id_lesson']) + '-' + date_to_str))
    bot.send_message(message.chat.id, 'Выберите занятие:', reply_markup=inline_markup)


d = {'ДЗ': homework, 'Работа со студентами':student_work, 'Посещение': attendance}


@bot.message_handler(func=lambda message: message.text in ['ДЗ', 'Работа со студентами', 'Посещение'])
def action(message):
    try:
        bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id - 1, reply_markup='')
    finally:
        d[message.text](message)


@bot.callback_query_handler(func=lambda call: call.data[0] == 'd' and call.data[1] == 'z')
def callback_dz(call):
    user = check(call.message.chat.id)
    ret = {"name_course": 'БД',
           "tasks": {}}
    for i in range(3):
        ret['tasks'][(str)(i + 1)] = {"info_task": "info" + (str)(i + 1), "dead_line": "dead_line" + (str)(i + 1)}
    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)  # удаление строго сообщения
    data = call.data.split('-')
    s = 'ДЗ ' + data[2] + "\n\n" + ret['tasks'][data[1]]["info_task"] + "\n\n" + "Сделать до: " + ret['tasks'][data[1]][
        "dead_line"]
    bot.answer_callback_query(call.id)
    if user['role'] == 2:
        inline_markup = types.InlineKeyboardMarkup()
        inline_markup.row(types.InlineKeyboardButton('Редактировать', callback_data='edit_dz-' + data[1]),
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
    #занесение нового дз
    bot.send_message(message.chat.id, 'Задание успешно создано')
    #ret = database.get_students_from_course(message.chat.id, user['log'][1])
    ret = {'students':[{'id_student':418531001}, {'id_student':485330050}]}
    for i in ret['students']:
        bot.send_message(i['id_student'], 'Создано новое ДЗ!\n\n' + task['info_task'] + '\n\n' + "Выполнить до " + str(task['dead_line']))


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
    bot.register_next_step_handler(msg, edit_homework, call.data.split('-')[1])


def edit_homework(message, dz_id):
    user = check(message.chat.id)
    # здесь идет загрузка в бд
    bot.delete_message(message.chat.id, message_id=message.message_id - 1)
    bot.send_message(message.chat.id, 'Изменения сохранены!')


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
    # удаление дз из бд
    dz_id = call.data.split('-')[1]
    bot.delete_message(call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id, 'Задание удалено!')


@bot.callback_query_handler(func=lambda call: 'cancel_delete_dz' in call.data)
def finish_del_dz(call):
    user = check(call.message.chat.id)
    dz_id = call.data.split('-')[1]
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'Удаление отменено!')


@bot.callback_query_handler(func=lambda call: 'mark_dz' in call.data)
def callback_mark_dz(call):
    user = check(call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id)
    inline_markup = types.InlineKeyboardMarkup()
    dz_id = call.data.split('-')[1]
    inline_markup.row(types.InlineKeyboardButton('Принять сдачу', callback_data='accept_dz-' + dz_id))
    inline_markup.row(types.InlineKeyboardButton('Изменить сдачу', callback_data='refactor_dz-' + dz_id))
    inline_markup.row(types.InlineKeyboardButton('Отменить сдачу', callback_data='deny_dz-' + dz_id))
    bot.send_message(call.message.chat.id,'Выберите действие:', reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: 'accept_dz' in call.data)
def accepting_dz(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'По нажатии на студента сдача автоматически засчитается:', reply_markup=not_comoleted_task_sudents(call, 'accept'))


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
    #database.mark_completed_task(message.chat.id, pool[message.chat.id]['log'][1], int(id_task), int(id_stud), points) # запись отметки в бд
    bot.send_message(message.chat.id, 'Задание успешно сдано!')
    bot.send_message(call.message.chat.id, 'По нажатии на студента сдача автоматически засчитается:', reply_markup=not_comoleted_task_sudents(call, 'accept'))



@bot.callback_query_handler(func=lambda call: 'refactor_dz' in call.data)
def callback_refactor_dz(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'По нажатии на студента начнётся редактирование баллов за данное задание:', reply_markup=not_comoleted_task_sudents(call, 'refactor'))


@bot.callback_query_handler(func=lambda call: 'refact_stud' in call.data)
def refactoring_dz(call):
    user = check(call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id, 'Отправленный вами текст будет сохранён! Нажмите "Отмена" для прерывания операции', show_alert=True)
    id_stud = call.data.split('-')[1]
    id_task = call.data.split('-')[2]
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Отмена', callback_data='cancel_dz'))
    msg = bot.send_message(call.message.chat.id, 'Введите количество баллов', reply_markup=inline_markup)
    bot.register_next_step_handler(msg, enter_new_point, id_stud, id_task, call)


def enter_new_point(message, call, id_stud, id_task):
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
        bot.register_next_step_handler(msg, enter_new_point, id_stud, id_task, call)
        return
    # изменение записей в бд
    bot.send_message(message.chat.id, 'Изменения сохранены!')
    bot.send_message(message.chat.id, 'По нажатии на студента начнётся редактирование баллов за данное задание:', reply_markup=not_comoleted_task_sudents(call, 'refactor'))


@bot.callback_query_handler(func=lambda call: 'deny_dz' in call.data)
def callback_deny_dz(call):
    user = check(call.message.chat.id)
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, 'По нажатии на студента сдача будет отменена:', reply_markup=completed_task_students(call))


@bot.callback_query_handler(func=lambda call: 'comp_stud' in call.data)
def denying_dz(call):
    user = check(call.message.chat.id)
    # удаление из базы
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=completed_task_students(call))
    bot.answer_callback_query(call.id)





#работа со студентами
@bot.callback_query_handler(func=lambda call: call.data == 'all_stud')
def all_stud_work(call):
    user = check(call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup='')
    bot.answer_callback_query(call.id, 'Режим работы со всеми студентами')
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Краткий журнал', callback_data='short_jurn'))
    inline_markup.row(types.InlineKeyboardButton('Журнал', callback_data='jurnal'), types.InlineKeyboardButton('Анализ', callback_data='analiz'))
    bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: call.data == 'short_jurn')
def show_short_jurnal(call):
    user = check(call.message.chat.id)
    bot.answer_callback_query(call.id)
    #short_j = da.get_course_info(call.message.chat.id, user['log'][1])
    #bot.send_message(call.message.chat.id, short_j)

@bot.callback_query_handler(func=lambda call: call.data == 'jurnal')
def show_short_jurnal(call):
    user = check(call.message.chat.id)
    bot.answer_callback_query(call.id, 'Файл сформирован')
    #bot.send_document(call.message.chat.id, )


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
    #image_path = da.create_rating_diagram(call.message.chat.id, user['log'][1])
    #bot.send_photo(call.message.chat.id, open(image_path, 'rb'))
    bot.answer_callback_query(call.id, 'Изображение построено')


@bot.callback_query_handler(func=lambda call: call.data == 'visit_hist')
def show_visit_hist(call):
    user = check(call.message.chat.id)
    #image_path = da.plot_number_of_attended_lessons_diagram(call.message.chat.id, user['log'][1])
    #bot.send_photo(call.message.chat.id, open(image_path, 'rb'))
    bot.answer_callback_query(call.id, 'Изображение построено')


@bot.callback_query_handler(func=lambda call: call.data == 'plot_dz')
def show_plot_bar_dz(call):
    user = check(call.message.chat.id)
    #image_path = da.plot_performed_homeworks_diagram(call.message.chat.id, user['log'][1])
    #bot.send_photo(call.message.chat.id, open(image_path, 'rb'))
    bot.answer_callback_query(call.id, 'Изображение построено')


@bot.callback_query_handler(func=lambda call: 'one_stud' in call.data)
def callback_one_stud(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)



#посещение
@bot.callback_query_handler(func=lambda call: 'att' in call.data)
def callback_attendance(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    id_lesson = call.data.split('-')[1]
    date_lesson = call.data.split('-')[2]
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Отметить присутствие', callback_data='mark_at-' + id_lesson + '-' + date_lesson))
    inline_markup.row(types.InlineKeyboardButton('Снять отметку', callback_data='del_mark_at-' + id_lesson + '-' + date_lesson))
    bot.send_message(call.message.chat.id, 'Занятие от ' + date_lesson)
    bot.send_message(call.message.chat.id, 'Выберите действие:', reply_markup=inline_markup)


def mark_att_keyboard(call):
    user = check(call.message.chat.id)
    # TODO здесь нужно извлечь из бд список студентов, которые еще не отмечены на данном занятии
    id_lesson = call.data.split('-')[1]
    date_lesson = call.data.split('-')[2]
    ret = {"students": []}
    for i in range(3):
        ret['students'].append({"id_student": (str)(i + 1),
                                "name_student": 'Эмиль' + (str)(i + 1),
                                "surname_student": 'Закиев' + (str)(i + 1),
                                "middle_name_student": 'Рамилевич' + (str)(i + 1),
                                "rating": '10000000' + (str)(i + 1)})
    inline_markup = types.InlineKeyboardMarkup()
    for i in ret['students']:
        inline_markup.row(types.InlineKeyboardButton(i['surname_student'] + ' ' + i['name_student'] + ' ' +
                                                     i['middle_name_student'], callback_data='not_here-' + id_lesson + '-' +date_lesson + '-' + str(i['id_student'])))
    inline_markup.row(types.InlineKeyboardButton('Назад', callback_data='att-' + id_lesson + '-' + date_lesson))
    return inline_markup


def not_mark_att_keyboard(call):
    user = check(call.message.chat.id)
    # TODO здесь нужно извлечь из бд список студентов, которые уже отмечены на данном занятии
    id_lesson = call.data.split('-')[1]
    date_lesson = call.data.split('-')[2]
    ret = {"students": []}
    for i in range(3):
        ret['students'].append({"id_student": (str)(i + 1),
                                "name_student": 'Эмиль' + (str)(i + 1),
                                "surname_student": 'Закиев' + (str)(i + 1),
                                "middle_name_student": 'Рамилевич' + (str)(i + 1),
                                "rating": '10000000' + (str)(i + 1)})
    inline_markup = types.InlineKeyboardMarkup()
    for i in ret['students']:
        inline_markup.row(types.InlineKeyboardButton(i['surname_student'] + ' ' + i['name_student'] + ' ' +
                                                     i['middle_name_student'], callback_data='is_here-' + id_lesson + '-' +date_lesson + '-' + str(i['id_student'])))
    inline_markup.row(types.InlineKeyboardButton('Назад', callback_data='att-' + id_lesson + '-' + date_lesson))
    return inline_markup


@bot.callback_query_handler(func=lambda call: 'mark_at' in call.data)
def marking_attendance(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'По нажатии на студента отметка поставится автоматически', reply_markup=not_mark_att_keyboard(call))


@bot.callback_query_handler(func=lambda call: 'is_here' in call.data)
def student_is_here(call):
    user = check(call.message.chat.id)
    id_lesson = call.data.split('-')[1]
    id_student = call.data.split('-')[3]
    #database.mark_student_in_class(call.message.chat.id, user['log'][1], id_lesson, id_student) #занесение отметки в бд
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup='')
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=not_mark_att_keyboard(call))
    bot.answer_callback_query(call.id, 'Успешно!')


@bot.callback_query_handler(func=lambda call: 'del_mark_at' in call.data)
def marking_attendance(call):
    user = check(call.message.chat.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, 'По нажатии на студента отметка снимется автоматически', reply_markup=mark_att_keyboard(call))


@bot.callback_query_handler(func=lambda call: 'not_here' in call.data)
def student_is_here(call):
    user = check(call.message.chat.id)
    id_lesson = call.data.split('-')[1]
    id_student = call.data.split('-')[3]
    #database.not_mark_student_in_class(id_student, id_lesson) #удаление отметки в бд
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=mark_att_keyboard(call))
    bot.answer_callback_query(call.id, 'Успешно!')


bot.polling(none_stop=True)

# user[0] = message.chat.id
