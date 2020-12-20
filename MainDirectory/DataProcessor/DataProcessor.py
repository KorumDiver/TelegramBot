from MainDirectory.DataBase.DataBase import db

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


async def get_grades(student_id: int) -> []:
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


async def get_students(id_user: int, course_name: str):
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


async def get_average_point(id_user: int, course_name: str):
    """
    Получение средней
    Args:
        user_id: Id
        course_name: Имя курса.
    Returns:
        Среднее значение баллов по курсу.
    """
    try:
        students: [] = await get_students(id_user, course_name)
        ratings = [student["rating"] for student in students]
        return sum(ratings) / len(ratings)
    except:
        raise Exception('Что-то пошло не так...')


async def get_top(id_user: int, course_name: str):
    """
    Рейтинг пользователей по оценкам(от наим к наиб)
    Args:
        user_id: Id
        course_name: Имя курса.
    Returns:
        Отсортированный список студентов .
    """
    try:
        students = await get_students(id_user, course_name)
        for student in students.items():
            rating = student["rating"]
            student["average_rating"] = sum(rating) / len(rating)

        sorted_rating = sorted(students, key=lambda x: x["average_rating"])
        return sorted_rating
    except:
        raise Exception('Что-то пошло не так...')

async def get_task(id_user: int, course_name: str):
    """
    Получение домашки
    Args:
        user_id: Id
        course_name: Имя курса.
    Returns:
        Список домашки.
    """
    try:
        ret = await db.get_tasks_from_course(id_user, course_name)
        tasks = ret["tasks"]
        return tasks
    except:
        raise Exception('Что-то пошло не так...')
