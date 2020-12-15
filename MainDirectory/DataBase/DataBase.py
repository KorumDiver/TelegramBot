import mysql.connector
from mysql.connector import Error
import random


class DataBase:
    """
    Класс реализующий связь бота с базой данных.

    Требуется реализовать набор методов для выдачи информаций по определенным шблонам, также набор команд для изменения
    данных в базе. (добавление тоже)
    """

    def __init__(self):
        try:
            self.__connection = mysql.connector.connect(host="127.0.0.1", user="root", password="korum123456",
                                                        database="mydb")
            print("Completed")
        except Error as e:
            print(e)

    def whoIs(self, id_user):
        """
        Определяет является ли пользователь преподователем
        :param id_user: Токен пользователя
        :return: Кто это, преподователь, студент или, что такого нет в базе
        """
        cursor = self.__connection.cursor()

        request = "select id_teachers from teachers where id_teachers = %s" % id_user
        cursor.execute(request)
        if cursor.fetchall():
            return 2

        request = "select id_students from students where id_students = %s" % id_user
        cursor.execute(request)
        if cursor.fetchall():
            return 1

        return 0

    def registration_user(self, id_user: int, name: str, surname: str, middle_name: str, role: int):
        """
        Регистрация пользователя. Добавляет его в нужную таблицу в зависимоти от его статуса.
        :param id_user: Токен пользователя (id пользователя), для идентификаций в базе данных
        :param name: Имя пользователя
        :param surname: Фамилия пользователя
        :param middle_name: Отчество
        :param role: Целочисленное значение роли пользователя
        """
        cursor = self.__connection.cursor()
        cursor.callproc("registration_user", (id_user, name, surname, middle_name, role == 2))
        self.__connection.commit()

    def delete_user(self, id_user):
        """
        Удаляет пользователя из базы данных. После удаления требуется повторная регистрация.
        :param id_user: Токен пользователя
        """
        cursor = self.__connection.cursor()
        cursor.callproc("delete_user", (id_user,))
        self.__connection.commit()

    def create_course(self, name_course: str, info="", id_teacher=0):
        request = 'insert into subjects (name, info, id_teacher) value ("%s","%s",%s)' % (name_course, info, id_teacher)
        cursor = self.__connection.cursor()
        cursor.execute(request)
        self.__connection.commit()

    # Student __________________________________________________________________________________________________________
    # Получение информаций______________________________________________________________________________________________
    def get_info_student(self, id_user: int):
        """
        Выдает информацию о студенте, включая рейтинг студента по всем дисциплинам на которые он записан
        :param id_user: Токен пользователя
        :return: Словарь вида {id_student | name_student | surname_student | [{rating | id_subject | name_subject}]}
        """
        request_info_student = "select id_student, name, surname, middle_name from students where id_student = %s" % id_user
        cursor = self.__connection.cursor(dictionary=True)
        cursor.execute(request_info_student)
        ris = cursor.fetchall()[0]  # response info student
        ret = {"id_user": ris["id_student"],
               "name_student": ris["name"],
               "surname_student": ris["surname"],
               "middle_name_student": ris["middle_name"],
               "info_about_course": []}

        request_courses = """select s.id_subject as id_subject,
                                   s.name as name_subject,
                                   s.info as info_subject,
                                   t.name as name_teacher,
                                   t.surname as surname_teacher,
                                   t.middle_name as middle_name_teacher
                            from student_subject as s_s 
                                left join subjects as s
                                on s_s.id_subject = s.id_subject 
                                left join teachers as t
                                on s.id_teacher = t.id_teacher
                            where s_s.id_student = %s""" % id_user
        cursor.execute(request_courses)
        courses = cursor.fetchall()
        for i in courses:
            course = {"id_subject": i["id_subject"],
                      "name_subject": i["name_subject"],
                      "name_teacher": i['name_teacher'],
                      "completed_task": []}
            request_tasks = "select "  # todo дописать запрос на вытаскивание заданий с баллами
            cursor.execute(request_tasks)
            tasks = cursor.fetchall()
            for task in tasks:
                course['completed_task'].append({"id_task": task["id_task"],
                                                 "info": task["info"],
                                                 "dead_line": task["dead_line"],
                                                 "point": task["point"]})
            ret["info_about_course"].append(course)
        return {"id_user": id_user,
                "name_student": "Александр",
                "surname_student": "Коробов",
                "middle_name_student": "Александрович",
                "info_about_course": [{"rating": 66,
                                       "id_subject": 1,  # Во нутреннем списке может быть много словарей
                                       "name_subject": "Название курса",
                                       "name_teacher": "111",
                                       "completed_tasks": [{"id_task": 15,
                                                            "info": "fkjsdfli",
                                                            "dead_line": 12122020,  # Должна быть датой, но пока так
                                                            "point": 5}
                                                           ]
                                       }]
                }

    def get_home_work(self, name_course: str):
        """
        Получение домашнего задания по определенному курсу
        :param name_course: Название курса. Точно также как и в базе.
        :return: Словарь вида {id_user, name_course, info_task, dead_line}


        Можно выдавать не только одно задание, но и сразу все задания по курсу, но думаю что это будет не удобно.
        Если решим так, то в выводе будет список таких списков.
        """
        return {"id_user": 1, "name_course": name_course, "info_task": "Задание по {name_course}",
                "dead_line": "01.12.2020"}

    def get_literature(self, name_course: str):
        """
        Выдает список литературы по его названию
        :param name_course: Название курса. Точно также как в базе.
        :return: Словарь вида {id_subject | name_subject | id_literature | name_literature}
        """
        return {"id_subject": 1,
                "name_subject": name_course,
                "literature": [{"id_literature": 15,
                                "info_literature": "Информация о книге"}]}

    def get_info_to_course(self, name_course: str):
        """
        Выдает список информаций по курсу по его названию
        :param name_course: Название курса. Точно также как в базе.
        :return: Словарь вида {id_subject | name_subject | info | teacher}
        """
        return {"id_subject": 1,
                "name_subject": name_course,
                "info": "Информация по курсу",
                "teacher": "Преподаватель (имя, фамилия в одну строку)"}

    def get_all_course(self, id_user):
        """
        Выводит все курсы доступные на данный момент
        :param id_user: Токен пользователя
        :return: Список вида [{id_course, name_course}]
        """
        return [{'id_course': 1,
                 'name_course': "DB"}]

    def get_not_attend(self, id_user: int):
        """
        Выдает список курсов на которые человек не записан
        :param id_user: Токен пользователя
        :return: Список
        """
        return [{"id_course": 1, "name_course": "Название"},
                {"id_course": 2, "name_course": "Название"}]

    # Добавление новой информаций_______________________________________________________________________________________
    def entry_to_course(self, id_user: int, name_course: str):
        """
        Запись определенного студента на курс
        :param id_user: Токен пользователя
        :param name_course: Название курса. Точно также как и в базе.
        """
        cursor = self.__connection.cursor()
        cursor.callproc("entry_to_course", (id_user, name_course))
        self.__connection.commit()

    # Изменение информаций______________________________________________________________________________________________
    def edit_info_student(self, id_user: int, new_name: str, new_surname: str, new_middle_name_student: str):
        """
        Изменяет информацию о студенте
        :param id_user: Токен пользователя
        :param new_name: Имя
        :param new_surname: Фамилия
        :param new_middle_name_student: Отчество
        """
        pass

    # Teacher___________________________________________________________________________________________________________
    # Преподователь может использовать методы студента, но не наоборот. Следующие методы только для преподователя
    # За исключением метода рейтинга. Для преподователя будет выдаваться список студентов с их рейтингами.
    # Во всех методах есть проверка на то, ведет ли припод этот курс, если нет то будет отказ в выполнений операций.
    # Так как методы изменения не возвращают ничего, то проблемой это не будет, но если вы хотите выводить пользователю
    # инфу о том, что в ему отказано в доступе, то скажите мне и я буду возврящать True или False при успешных
    # и не успешных операциях соответственнно.

    # Получение информаций (преподователь)
    def get_students_from_course(self, id_user: int, name_course: str):
        """
        Выдает список студентов посещающих определенный курс
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :return: Словарь вида {id_subject, name_subject,
            [{id_student, name_student, surname_student, middle_student, rating}]
        """
        cursor = self.__connection.cursor(dictionary=True)
        request = "select * from view_student_subject where id_teacher = %s and name_subject = '%s';" \
                  % (id_user, name_course)
        cursor.execute(request)
        response = cursor.fetchall()
        if len(response) != 0:
            ret = {"id_subject": response[0]["id_subject"],
                   "name_subject": response[0]["name_subject"],
                   "students": []}
            for i in response:
                ret["students"].append({"id_student": i["id_student"],
                                        "name_student": i["name_student"],
                                        "surname_student": i["surname_student"],
                                        "middle_name_student": i["middle_name_student"],
                                        "rating": i["rating"]})
            return ret
        else:
            print("Данный преподователь не имеет доступа к данным записям!!!")

    def get_lessons_from_course(self, id_user: int, name_course: str):
        """
        Выдает список всех занятий по определенному курсу
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :return: Словарь вида {id_subject, name_subject, [{id_lesson, date_lesson}]
        """
        cursor = self.__connection.cursor(dictionary=True)
        request = "select * from view_subject_lesson where id_teacher=%s and name_subject = '%s'" \
                  % (id_user, name_course)
        cursor.execute(request)
        response = cursor.fetchall()
        if len(response) != 0:
            ret = {"id_subject": response[0]["id_subject"],
                   "name_subject": response[0]["name_subject"],
                   "lessons": []}
            for i in response:
                ret["lessons"].append({"id_lesson": i["id_lesson"],
                                       "date_lesson": i["date_lesson"]})
            return ret
        else:
            print("Данный преподователь не имеет доступа к данным записям!!!")

    def get_tasks_from_course(self, id_user: int, name_course: str):
        """
        Выдает список всех задач по курсу
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :return: Словарь вида {id_subject, name_subject, [{id_task, task, dead_line}]}
        """
        cursor = self.__connection.cursor(dictionary=True)
        request = "select * from view_task_subject where id_teacher=%s and name_subject='%s'" % (id_user, name_course)
        cursor.execute(request)
        response = cursor.fetchall()
        if len(response) != 0:
            ret = {"id_subject": response[0]["id_subject"],
                   "name_subject": response[0]["name_subject"],
                   "tasks": []}
            for i in response:
                ret["tasks"].append({"id_task": i["id_task"],
                                     "info": i["info"],
                                     "dead_line": i["dead_line"]})
            return ret
        else:
            print("Данный преподователь не имеет доступа к данным записям!!!")

    # Добавление информаций
    def add_home_work(self, id_user: int, name_course: str, info: str, dead_line: str):
        """
        Добавляет новое домашнее задание по определенному курсу.
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :param info: Информация о домашнем заданий
        :param dead_line: Дата конца приема домашнего задания
        """
        cursor = self.__connection.cursor()
        cursor.callproc("add_home_work", (id_user, name_course, info, dead_line))
        self.__connection.commit()

    def add_literature(self, id_user: int, name_course: str, info_literature: str):
        """
        Добавляет новую записть в таблицу литературы, для определеного предмета.
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :param info_literature: Строка с инвормацией по литературе: название, автор, ссылка и тд.
        """
        cursor = self.__connection.cursor()
        cursor.callproc("add_literature", (id_user, name_course, info_literature))
        self.__connection.commit()

    def add_lesson(self, id_user: int, name_course: str, date: str):
        """
        Создает новый урок по заданной дате
        :param id_user: Токен пользоваетля
        :param name_course: Название курса
        :param date: Дата проведения урока
        """
        cursor = self.__connection.cursor()
        cursor.callproc("add_lesson", (id_user, name_course, date))
        self.__connection.commit()

    # Изменение информаций
    def edit_info_course(self, id_user: int, name_course: str, new_info: str):
        """
        Изменение информация по курсу.
        :param id_user: Токен пользователя
        :param name_course: Название курса. Точно также как в базе.
        :param new_info: Новая инвормация по курсу
        """
        cursor = self.__connection.cursor()
        cursor.callproc("edit_info_course", (id_user, name_course, new_info))
        self.__connection.commit()

    def edit_home_work(self, id_user: int, name_course: str, num_task: int, new_info: str, new_dead_line: str):
        """
        Изменяет конкретное дз в выборке
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :param num_task: Номер задания в выборке по курсу (начинаем с 0) # TODO Отметить функцию выдающую такую выборку
        :param new_info: Новая информация по ДЗ
        :param new_dead_line: Новый dead line
        """
        cursor = self.__connection.cursor()
        cursor.callproc("edit_home_work", (id_user, name_course, num_task, new_info, new_dead_line))
        self.__connection.commit()

    def edit_literature(self, id_user: int, name_course: str, num_literature: int, new_info_literature: str):
        """
        Таже самая проблемма, что и в изменений домашнего задания
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :param num_literature: Номер задания в выборке по курсу (начинаем с 0) # TODO Отметить функцию выдающую такую выборку
        :param new_info_literature: Строка с измененной информацией
        """
        cursor = self.__connection.cursor()
        cursor.callproc("edit_literature", (id_user, name_course, num_literature, new_info_literature))
        self.__connection.commit()

    # Функций отметки
    def mark_student_in_class(self, id_user: int, name_course: str, id_lesson: int, id_student: int):
        """
        Отмечает студента на паре по его id.
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :param id_lesson: Id предмета
        :param id_student: Id студента
        """
        cursor = self.__connection.cursor()
        cursor.callproc("mark_student_in_class", (id_user, name_course, id_lesson, id_student))
        self.__connection.commit()

    def mark_completed_task(self, id_user: int, name_course: str, id_task: int, id_student: int, point: int):
        """
        Отмечает, что студент выполнил определенное задание
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :param id_task: Id задания
        :param id_student: Id студентв
        :param point: Количество баллов за задание
        """
        cursor = self.__connection.cursor()
        cursor.callproc("mark_completed_task", (id_user, name_course, id_task, id_student, point))
        self.__connection.commit()

    # ------------------------------------------------------------------------------------------------------------------
    def random_data(self):
        # Создание студентов
        students = [i for i in range(10 ** 5, 10 ** 5 + 500)]
        for student in students:
            self.registration_user(student, "Имя %s" % student, "Фамилия %s" % student, "Отчество %s" % student, 0)

        # Создание преподователей
        teachers = [i for i in range(2 * 10 ** 5, 2 * 10 ** 5 + 50)]
        for teacher in teachers:
            self.registration_user(teacher, "Имя %s" % teacher, "Фамилия %s" % teacher, "Отчество %s" % teacher, 2)

        # Создание курсов и связка их с преподователем
        courses = [i for i in range(1, len(teachers) + 1)]  # Номера курсов в БД
        for course in courses:
            self.create_course("Курс: %s" % course, "Teacher: %s" % teachers[course - 1], teachers[course - 1])

        # Добавление литературы к каждому курсу
        for course in courses:
            for i in range(1, 5):
                self.add_literature(teachers[course - 1], "Курс: %s" % course, "Literature: course_%s_%s" % (course, i))

        # Добавление домашнего задания к каждому уроку
        for course in courses:
            for i in range(10):
                self.add_home_work(teachers[course - 1], "Курс: %s" % course, "Info: home_work_%s_%s" % (course, i),
                                   "2020-01-%s" % i)

        # Добавление 10 занятий для каждого курса
        for course in courses:
            for i in range(10):
                self.add_lesson(teachers[course - 1], "Курс: %s" % course, "2020-01-%s" % i)

        # Запись студента на 3 курса
        for student in students:
            for i in random.sample(courses, 3):
                self.entry_to_course(student, "Курс: %s" % i)

        # Запись студентов в таблицу выполненных домашних заданий (5 штук на каждого)
        for course in courses:
            list_student = self.get_students_from_course(teachers[course - 1], "Курс: %s" % course)["students"]
            list_task = self.get_tasks_from_course(teachers[course - 1], "Курс: %s" % course)["tasks"]
            for student in list_student:
                for task in random.sample(list_task, 5):
                    self.mark_completed_task(teachers[course - 1], "Курс: %s" % course, task["id_task"],
                                             student["id_student"], random.randint(1, 15))

        # Запись студентов в таблицу посещеных занятий (по 5 на каждого)
        for course in courses:
            list_student = self.get_students_from_course(teachers[course - 1], "Курс: %s" % course)["students"]
            list_lesson = self.get_lessons_from_course(teachers[course - 1], "Курс: %s" % course)["lessons"]
            for student in list_student:
                for lesson in random.sample(list_lesson, 5):
                    self.mark_student_in_class(teachers[course - 1], "Курс: %s" % course, lesson["id_lesson"],
                                               student["id_student"])


if __name__ == '__main__':
    db = DataBase()
