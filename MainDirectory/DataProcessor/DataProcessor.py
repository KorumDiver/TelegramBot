import telebot
from telebot import types
from MainDirectory.DataBase.DataBase import db
from MainDirectory.TelegramBot.ResponseBot.ResponseAnswerBot import bot
bot = telebot.TeleBot("1438178504:AAF5-LIj7iPbGZWmPT8vOJJeGHjyjH3NTiQ")
class DataProcessor:
    """
    Данный класс реализует статистическую обработку данных по командам из ResponseAnswerBot.

    Тербуется реализовать набор разных статистических обработчиков. В основном в методы должен приходить список данных
    и отдаваться список или словарь полученных значений.

    Плюсом будет возможность построения гистограмм и графиков с последующим выводом изображений в сообщение пользователю.
    (Но это не обязательно)
    """

    def __init__(self):
        """
        Инициализирует нужные переменные в классе. Импортирует библиотеки
        """
        pass

@bot.message_handler(commands=["grades"])
async def get_grades(message):
    try:
        student_id = db.get_course_id_by_name(< сюда название курса из кнопок наверное преедавать >)
        answer = db.get_students_grade(student_id )
        await bot.send_message("Оценки:\n"+answer)
    except:
        await bot.send_message('Что-то пошло не так...')

@bot.message_handler(commands=["number"])
async def get_number_student(message):
    try:
        student_id = db.get_course_id_by_name(< сюда название курса из кнопок наверное преедавать >)
        answer = db.get_students_from_course(student_id )
        await bot.send_message("Кол-во студентов на курсе:\n"+answer)
    except:
        await bot.send_message('Что-то пошло не так...')



@bot.message_handler(commands=["average_rating"])
async def get_avarage(message):
        try:
            course_id = db.get_course_id_by_name(< сюда название курса из кнопок наверное преедавать >)
            course_work_grades: [] = db.get_work_grades_by_course(course_id)
            res = sum(course_work_grades) / len(course_work_grades)
            await bot.send_message("Средняя оценка по курсу:\n" + res)
        except:
            await bot.send_message('Что-то пошло не так...')

@bot.message_handler(commands=["top5_from_the_end"])
async def get_top(message):
        try:
            course_id = db.get_course_id_by_name(< сюда название курса из кнопок наверное преедавать >)
            students = db.get_students_course(message.from_user.id,course_id)
            for key, value in students.items():
                grades = students[key]
                students[key] = sum(grades)/len(grades)
            print(students)
            sorted_rating = sorted(students.items(), key=lambda average_grade: average_grade[1], reverse=True)
            await bot.send_message("Топ  с конца:\n" + sorted_rating)
        except:
            await bot.send_message('Что-то пошло не так...')



