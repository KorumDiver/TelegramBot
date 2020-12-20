import telebot
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
def course_functions(role):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if role == 1:
        markup.add('Описание курса', 'ДЗ', 'Рейтинг', 'Журнал', 'Литература', 'Отписаться', 'К выбору курса')
    elif role == 2:
        markup.add('Описание курса', 'Список студентов', 'ДЗ', 'Постинг', 'Рейтинг', 'Журнал', 'Литература',
                   'К выбору курса')
    return markup


# клавиатура записи на курс (инлайн кнопки)
def sign_up_to_course():
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.row(types.InlineKeyboardButton('Записаться', callback_data='sign-up'))
    return inline_markup

def dz_keyboard(dz_count):
    inline_markup = types.InlineKeyboardMarkup()
    for i in range(dz_count):
        inline_markup.row(types.InlineKeyboardButton('ДЗ ' + (str)(i+1), callback_data='dz-'+(str)(i+1)))
    return inline_markup


# db = DataBase()

# id| роль | last_time_message| tec_curs| my_courses |
cv_user_id = {-1: [0, 0, {"course": ""}]}

kursi_studenta = ["BD", "MATSTAt", "TAU", "RUSSIAN"]
kursi_pr = ["Английский", "Python", "C#", "АСД", "Java"]
unsigned_courses = ['Философия', 'Электроника', 'Радиофизика', 'Механика', 'Сопромат']

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
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=start_keyboard())
        else:
            bot.send_message(message.chat.id, "Отправьте /register")
        #                                                  "Здравствуйте, студент! Давайте приступим к регистрации. Введите свои ФИО через пробел."
        #                                                 " Внимание, вы сможете это сделать только один раз!"), student_registration)


@bot.message_handler(commands=['register'])
def regist(message):
    if check(message.chat.id, message.date) and cv_user_id[message.chat.id][0] == 0:
        msg = bot.send_message(message.chat.id, "Отправьте свои ФИО, разделите пробелом:")
        bot.register_next_step_handler(msg, take_info)  # функция проверки сказала снова отправить комнаду, значит далее он отправляет ееё и заходит в первое условие, поэтому else
        # не нужен и нужно просто дальше принять данные


def take_info(message):
    s = message.text.split(" ")
    if len(s) != 3:
        bot.send_message(message.chat.id, 'Введите ФИО правильно! Зарегистируйтесь заново!')
    else:
        print(s[0], s[1], s[2])
        # Запись в бд и
        cv_user_id[message.chat.id][0] = 1
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=start_keyboard())


@bot.message_handler(regexp="Мои курсы")
def my_c(message):
    if (check(message.chat.id, message.date)):
        if cv_user_id[message.chat.id][0] == 1:
            msg = bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=courses_keyboard(kursi_studenta))  # Здесь отрпавка чуваку клавиатуры с его курсами, генерация клавы из бд
            bot.register_next_step_handler(msg, take_cours)
        elif cv_user_id[message.chat.id][0] == 2:
            msg = bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=courses_keyboard(kursi_pr))  # Здесь отрпавка чуваку клавиатуры с его курсами, генерация клавы из бд
            bot.register_next_step_handler(msg, take_cours_pr)

def take_cours(message):  # он выбрал предмет
    if message.text == '/start' or message.text == 'Назад':
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=start_keyboard())
    elif message.text not in kursi_studenta:
        bot.send_message(message.chat.id, "Я не знаю такого курса")
        my_c(message)
    elif message.text in kursi_studenta:
        cv_user_id[message.chat.id][2]["course"] = message.text
        bot.send_message(message.chat.id, "Выберите действие", reply_markup=course_functions(1))  # Здесь отправляется клава с вариантами действия функционала по курсу

def take_cours_pr(message):  # он выбрал предмет
    cv_user_id[message.chat.id][2]["course"] = message.text
    bot.send_message(message.chat.id, "Выберите действие", reply_markup=course_functions(2))

@bot.message_handler(regexp = "Записаться")
def reg_to_course(message):
    if (check(message.chat.id, message.date)):
        if cv_user_id[message.chat.id][0] == 1:
            msg = bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=courses_keyboard(unsigned_courses))  # Здесь отрпавка чуваку клавиатуры с курсами, на которые он не записан, генерация клавы хз
            bot.register_next_step_handler(msg, take_cours1)

def take_cours1(message):  # он выбрал предмет
    if message.text == '/start' or message.text == 'Назад':
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=start_keyboard())
    elif message.text not in unsigned_courses:
        bot.send_message(message.chat.id, "Я не знаю такого курса")
        reg_to_course(message)
    elif message.text in unsigned_courses:
        cv_user_id[message.chat.id][2]["course"] = message.text
        s = "Здесь будет описание курса"  # на самом деле здесь из бд берется описание по cv_user_id[message.chat.id][2]["course]
        bot.send_message(message.chat.id, s)  # Здесь отправляется описание
        bot.send_message(message.chat.id, "Хотите записаться?", reply_markup=sign_up_to_course())  # Здесь отправляется клава с вариантами Записаться

@bot.callback_query_handler(func=lambda c: c.data == 'sign-up')
def sign_up_user(c):
    if (check(c.message.chat.id, c.message.date)):
        # Здесь работа с записью в бд
        bot.answer_callback_query(c.id, text="Вы успешно записаны на курс " + cv_user_id[c.message.chat.id][2]["course"], show_alert=True)
        bot.edit_message_reply_markup(c.message.chat.id, message_id=c.message.message_id, reply_markup='')
        bot.send_message(c.message.chat.id, 'Выберите действие:', reply_markup=start_keyboard())  # отправили главную калвиатуру с мои курсы, записаться и инфо


@bot.message_handler(regexp="Описание курса")
def describe(message):
    if (check(message.chat.id, message.date)):
        s = "blablabla"  # на самом деле здесь из бд берется описание по cv_user_id[message.chat.id][2]["course]
        if cv_user_id[message.chat.id][0] == 1:
            bot.send_message(message.chat.id, s)
        elif cv_user_id[message.chat.id][0] == 2:
            bot.send_message(message.chat.id, s)  # кнопка с редактированием


@bot.message_handler(regexp="Редактировать описание")
def red(message):
    if (check(message.chat.id, message.date)):
        if cv_user_id[message.chat.id][0] == 2:
            s = "blablabla"  # на самом деле здесь из бд берется описание по cv_user_id[message.chat.id][2]["course]
            bot.send_message(message.chat.id, s)
            msg = bot.send_message(message.chat.id, "Введите новое описание")
            bot.register_next_step_handler(msg, take_new_des)

def take_new_des(message):
    s = message.text
    # добавление в бд нового описания
    bot.send_message(message.chat.id, "Описание успешно изменено")


@bot.message_handler(regexp="Список студентов")
def students(message):
    if (check(message.chat.id, message.date)):
        if cv_user_id[message.chat.id][0] == 2:
            s = "blablabla"  # на самом деле здесь из бд берется список студетов по и mesage.chat.id
            bot.send_message(message.chat.id, s)


dz = [{"id": 1, "info": "Сделайте бота", "deadline": "20.12.2020"}, {"id": 2, "info": "Сдать курсач по бд", "deadline": "25.12.2020"}]  # здесь из БД берется список домашек
@bot.message_handler(regexp="ДЗ")
def dz_funcs(message):
    if (check(message.chat.id, message.date)):
        if cv_user_id[message.chat.id][0] == 1:
            bot.send_message(message.chat.id, "Выберите ДЗ:", reply_markup=dz_keyboard(len(dz)))  # отрпавка inline кнопок
        if cv_user_id[message.chat.id][0] == 2:
            bot.send_message(message.chat.id, 'Выберите действие:', reply_markup='')#сюда добавить клаву с возможностями преподавателя


@bot.callback_query_handler(func=lambda call: call.data[0] == 'd' and call.data[1] == 'z')
def callback_inline(call):
    if (check(call.message.chat.id, call.message.date)):
        bot.edit_message_reply_markup(call.message.chat.id, message_id=call.message.message_id, reply_markup='')
        num_dz = int(call.data[3])
        s = "ДЗ " + call.data[3] + "\n\n" + dz[num_dz-1]["info"] + "\n\n" + "Сделать до: " + dz[num_dz-1]["deadline"]
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, s)

@bot.message_handler(regexp="Литература")
def litr(message):
    if (check(message.chat.id, message.date)):
        s = "Здесь будет литра"  # на самом деле здесь из бд берется литература по cv_user_id[message.chat.id][2]["course]
        msg = bot.send_message(message.chat.id, s)
        if cv_user_id[message.chat.id][0] == 2:
            bot.send_message(message.chat.id, "Редактировать литературу")  # Здесь выводится кнопка с редактированием литературы
            bot.register_next_step_handler(msg, take_new_lit)


def take_new_lit(message):
    s = message.text
    # добавление в бд новой литературы
    bot.send_message(message.chat.id, "Литература успешно изменена")


@bot.message_handler(regexp="Отписаться")
def deleeete(message):
    if (check(message.chat.id, message.date)):
        # на самом деле здесь из бд удаляется человек по cv_user_id[message.chat.id][2]["course] и mesage.chat.id
        cv_user_id[message.chat.id][2]["course"] = ''
        bot.send_message(message.chat.id, "Вы успешно удалены")

@bot.message_handler(regexp="К выбору курса")
def back_to_choise(message):
    my_c(message)

'''    
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
                info_course_text += """    Имя курса: %s\n    Преподователь: %s\n    Количество баллов: %s""" % \
                                    (course["name_course"], course["name_teacher"], course["rating"])
        text = "Имя: %s\nФамилия: %s\nОтчество: %s\n%s" % (info["name_student"], info["surname_student"],
                                                           info["middle_name_student"], info_course_text)
        bot.send_message(message.chat.id, text)
'''

bot.polling(none_stop=True)

# user[0] = message.chat.id