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
    }

    sum = []
    course_name = "name_course1"

    home_works = {
        "tasks": {
            1: {
                "info_task": "asasf"
            },
            2: {
                "info_task": "asasf"
            },
            3: {
                "info_task": "asasf"
            }
        }
    }
    #
    # ret = {"name_course": name_course,
    #        "tasks": {}}
    # for row in cursor.fetchall():
    #     ret['tasks'][row['id_task']] = {"info_task": row["info"],
    #                                     "dead_line": row["dead_line"]}
    for student in students:

        data['Имя'].append(student['name_student'])
        data['Фамилия'].append(student['surname_student'])

        courses = student["info_about_courses"]
        target_course = None
        for course in courses:
            if course_name == course["name_course"]:
                target_course = course

            if target_course is not None:
                for task_id in home_works['tasks'].keys():
                    # {surname_student: ["asdasd", "sdfsdfs", "sdfsdfs"]
                    completed = {"name_subject": course_name,
                                 "students": ["фамилия студента", "фамилия студента2", "фамилия студента1"]}

                    if student['surname_student'] in completed['students']:
                        completed_task_column = "ДЗ" + str(task_id)
                        if completed_task_column in data is not None:
                            data[completed_task_column].append(5)
                        else:
                            data[completed_task_column] = [5]
                sum.append(target_course["rating"])

        data["Итого"] = sum
        dataframe = pd.DataFrame.from_dict(data, orient='index', )
        dataframe = dataframe.transpose()
        dataframe.to_excel("test.xlsx", index=False)


# 3
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


# 2
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


# 4
def plot_number_of_attended_lessons_diagram(id_user: int, course_name: str) -> str:
    values = db.get_count_lessons(course_name)

    fig, ax = plt.subplots()
    plt.ylabel('количество посещенных уроков')

    for index, value in enumerate(values):
        ax.bar(index, value, color=np.random.rand(3, ), width=0.1)

    # current path
    path = pathlib.Path().absolute()
    image_path = path.joinpath("number_of_attended_lessons_diagram.png")
    plt.savefig(image_path)
    return image_path


# 5
def plot_performed_homeworks_diagram(id_user: int, course_name: str) -> str:
    values = db.get_count_completed_task(course_name)

    fig, ax = plt.subplots()
    plt.ylabel('количество выполненных дз')

    for index, value in enumerate(values):
        ax.bar(index, value, color=np.random.rand(3, ), width=0.1)

    # current path
    path = pathlib.Path().absolute()
    image_path = path.joinpath("performed_homeworks_diagram.png")
    plt.savefig(image_path)
    return image_path
