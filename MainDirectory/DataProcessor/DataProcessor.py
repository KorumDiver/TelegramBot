from MainDirectory.DataBase.DataBase import db
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pathlib


class DataProcessor:
    """
    Данный класс реализует статистическую обработку данных по командам из ResponseAnswerBot.

    Тербуется реализовать набор разных статистических обработчиков. В основном в методы должен приходить список данных
    и отдаваться список или словарь полученных значений.

    Плюсом будет возможность построения гистограмм и графиков с последующим выводом изображений в сообщение пользователю.
    (Но это не обязательно)
    """

    def __init__(self, db):
        """
        Инициализирует нужные переменные в классе. Импортирует библиотеки
        """
        pass


def get_grades(student_id: int) -> []:
    """
    Получение оценок, студента по курсу
    Args:
        student_id: Id студента.
    Returns:
        Список оценок студента.
    """
    try:
        user_info: {} = db.get_info_student(id_user=student_id)
        completed_tasks = user_info["info_about_courses"]["completed_tasks"]

        # Должно быть так
        #   completed_tasks = [
        #             {
        #                 "id_task": "afasfaf",
        #                 "info": "asfaf",
        #                 "dead_line": "sdfsdg",  # Должна быть датой, но пока так
        #                 "point": 5
        #             },
        #             {
        #                 "id_task": "afasfaf",
        #                 "info": "asfaf",
        #                 "dead_line": "sdfsdg",  # Должна быть датой, но пока так
        #                 "point": 4
        #             },
        #             {
        #                 "id_task": "afasfaf",
        #                 "info": "asfaf",
        #                 "dead_line": "sdfsdg",  # Должна быть датой, но пока так
        #                 "point": 3
        #             },
        #         ]

        points = [completed_task['point'] for completed_task in completed_tasks]

        return points
    except:
        raise Exception('Что-то пошло не так')


def get_students(id_user: int, course_name: str):
    """
    Получение списка студентов
    Args:
        user_id: Id
        course_name: Имя курса.
    Returns:
        Список список студентов.
    """
    try:
        ret: [] = db.get_students_from_course(id_user=id_user, name_course=course_name)
        students = ret["students"]
        return students
    except:
        raise Exception('Что-то пошло не так...')


def get_average_point(id_user: int, course_name: str):
    """
    Получение средней
    Args:
        user_id: Id
        course_name: Имя курса.
    Returns:
        Среднее значение баллов по курсу.
    """
    try:
        students: [] = get_students(id_user, course_name)
        ratings = [student["rating"] for student in students]
        return sum(ratings) / len(ratings)
    except:
        raise Exception('Что-то пошло не так...')


def get_top(id_user: int, course_name: str):
    """
    Рейтинг пользователей по оценкам(от наим к наиб)
    Args:
        user_id: Id
        course_name: Имя курса.
    Returns:
        Отсортированный список студентов .
    """
    try:
        students = get_students(id_user, course_name)
        for student in students:
            rating = student["rating"]
            student["average_rating"] = sum(rating) / len(rating)

        sorted_rating = sorted(students, key=lambda x: x["average_rating"])
        return sorted_rating
    except:
        raise Exception('Что-то пошло не так...')


def get_task(id_user: int, course_name: str):
    """
    Получение домашки
    Args:
        user_id: Id
        course_name: Имя курса.
    Returns:
        Список домашки.
    """
    try:
        ret = db.get_tasks_from_course(id_user, course_name)
        tasks = ret["tasks"]
        return tasks
    except:
        raise Exception('Что-то пошло не так...')


def generate_excel(id_user: int, course_name: str):
    students: [] = get_students(id_user, course_name)

    # {
    #     "id_student": i["id_student"],
    #     "name_student": i["name_student"],
    #     "surname_student": i["surname_student"],
    #     "middle_name_student": i["middle_name_student"],
    #     "rating": i["rating"]
    # }

    data = {
        "Имя": [],
        "Фамилия": [],
        "Итого": []
    }

    for student in students:
        info_student: {} = db.get_info_student(id_user=student["id_student"])
        courses = info_student["info_about_courses"]
        target_course = None
        for course in courses:
            if course_name == course["name_subject"]:
                target_course = course
        if target_course is None:
            completed_tasks = target_course["completed_tasks"]
            for completed_task in completed_tasks:
                completed_task_column = "ДЗ" + completed_task["id"]
                if data[completed_task_column] is not None:
                    data[completed_task_column].append(completed_task["point"])
                else:
                    data[completed_task_column] = [completed_task["point"]]
            data["Итого"].append(completed_task_column["rating"])

    dataframe = pd.DataFrame.from_dict(data, orient='index', )
    dataframe = dataframe.transpose()
    dataframe.to_excel("test.xlsx", index=False)

#3

def create_rating_diagram(id_user: int, course_name: str) -> str:
    """
       Создает диаграмму рейтинга студентов по курсу
       Args:
           id_user: Id
           course_name: Имя курса.
       Returns:
           Возвращает путь до созданного изображения
    """
    students_top = get_top(id_user, course_name)

    fig, ax = plt.subplots()
    plt.xlabel('студент')
    plt.ylabel('рейтинг')

    for student in students_top:
        ax.bar(student["name_student"], student["rating"], color=np.random.rand(3, ), width=0.1)

    # current path
    path = pathlib.Path().absolute()
    image_path = path.joinpath("rating_diagram.png")
    plt.savefig(image_path)
    return image_path

#2
def get_course_info(id_user: id, name_course: str) -> []:
    """
       Получение списка всех студентов по курсу
       Args:
           user_id: Id
           course_name: Имя курса.
       Returns:
           Строка формата: ФИО, кол-во посещений, кол-во заданий, рейтинг
    """
    ret = db.get_students_from_course(id_user, name_course)
    string_to_format = 'ФИО: {}, кол-во посещений: {}, кол-во заданий: {}, рейтинг: {}'
    students = ret['students']

    students_info = []
    for student in students:
        #  не понимаю, откуда брать информацию о кол-ве посещений и заданий
        student_info = string_to_format.format(student['name_student'], None, None, student['rating'])
        students_info.append(students)

    return students_info
