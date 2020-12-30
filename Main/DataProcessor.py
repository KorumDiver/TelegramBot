import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pathlib

db = DataBase.DataBase()


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
    students = get_students(id_user, course_name)
    print(*students, sep='\n')
    sorted_rating = sorted(students, key=lambda x: x["rating"])
    return sorted_rating


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
    students = db.get_students_from_course(id_user, course_name)['students']
    data = {}

    for student in students:
        data_student = db.get_excel_tasks(student["id_student"], course_name)
        data[student['id_student']] = [student['name_student'], data_student['surname'],
                                       *[i['point'] for i in data_student["tasks"]],
                                       student['rating']]
    dataframe = pd.DataFrame(data)
    ren = {0: "Имя", 1: "Фамилия"}
    for i in range(2, len(data_student['tasks'])+2):
        ren[i] = "ДЗ %s" % (i-1)
    ren[len(data_student['tasks'])+2] = "Итого"

    dataframe = dataframe.rename(ren)
    dataframe = dataframe.transpose()
    dataframe.to_excel("journal.xlsx", index=False)
    path = pathlib.Path().absolute()
    doc_path = path.joinpath("journal.xlsx")
    return doc_path
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
    students_top = db.get_students_from_course(id_user, course_name)['students']

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
    string_to_format = '{}: посещений {}/{}, заданий {}/{}, рейтинг {}'
    students = ret['students']
    students_info = ''
    for student in students:
        #  не понимаю, откуда брать информацию о кол-ве посещений и заданий
        students_info += string_to_format.format(student['name_student'], None, None, None, None,
                                                 student['rating']) + '\n'

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
        ax.bar(index + 1, value, color=np.random.rand(3, ), width=0.5)

    # current path
    path = pathlib.Path().absolute()
    image_path = path.joinpath("performed_homeworks_diagram.png")
    plt.savefig(image_path)
    return image_path
