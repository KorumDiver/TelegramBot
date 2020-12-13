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
        request = """
        select s.id_student, s.name, s.surname, s.middle_name, i.* from students as s
            left join student_subject as s_s
                on s.id_student = s_s.id_student
            left join info_course_and_task as i
                on i.id_subject=s_s.id_subject
        where s.id_student = %s;
        """ % id_user
        cursor = self.__connection.cursor(dictionary=True)
        cursor.execute(request)
        response = cursor.fetchall()
        ret = {"id_user": response[0]["id_student"],
               "name_student": response[0]["name"],
               "surname_student": response[0]["surname"],
               "middle_name_student": response[0][""]}
        for i in response:
            pass
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

    # Получение информация (преподователь)
    def get_students_course(self, id_user: int, name_course: str):
        """
        Выдает список всех студентов по выбранному курсу
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :return: Словарь вида {id_user, name_course, [{id_student, name_student, surname_student, rating}]}


        Так же рейтинг курса выбирается по этому запросу
        """
        return {"id_user": id_user,
                "name_course": name_course,
                "info_students": [{"id_student": "Токен студента",
                                   "name_student": "Имя студента",
                                   "surname_student": "Фамилия студента",
                                   "rating": "Рейтинг студента по рассматриваемому курсу"}]}

    # Добавление информаций
    def add_home_work(self, id_user: int, name_course: str, info: str, dead_line: str):
        """
        Добавляет новое домашнее задание по определенному курсу.
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :param info: Информация по о домашнем заданий
        :param dead_line: Дата конца приема домашнего задания
        :param point: Количество баллов за задание
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

    # Изменение информаций
    def edit_info_cours(self, id_user: int, name_course: str, new_info: str):
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

    # Добавление информаций (Не использовать, пока не пропишу нормальные параметры
    def mark_student_in_class(self, id_user: int, name_course: str, num_student: int):
        """
        Отмечает студента на паре по его id.
        :param id_user: Токен пользователя
        :param name_course: Название курса
        :param num_student: Номер студента в выборке по курсу (начинаем с 0) # TODO Отметить функцию выдающую такую выборку
        """
        pass

    def mark_completed_task(self, num_student: int, num_task: int):
        """
        Отмечает, что студент выполнил задание
        :param num_student: Номер студента в выборке по курсу (начинаем с 0) # TODO Отметить функцию выдающую такую выборку
        :param num_task: Номер задания в выборке по курсу (начинаем с 0) # TODO Отметить функцию выдающую такую выборку
        """
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def random_data(self):
        # Создание пользоваетлей
        for i in range(50):
            self.registration_user(i, str(i), str(i), str(i), 0)

        for i in range(5):
            self.registration_user(i, str(i), str(i), str(i), 2)
            # Создание курсов
            self.create_course("Курс номер %s" % i, info="Info %s" % i, id_teacher=i)

        self.edit_info_cours(0, "Курс номер 0", "Новая информация по курсу")
        # Запись каждого студента на 1 курс
        for student in range(50):
            self.entry_to_course(student, "Курс номер %s" % random.randint(0, 4))
            self.entry_to_course(student, "Курс номер %s" % random.randint(0, 4))

        for i in range(50):
            a = random.randint(0, 4)
            self.add_literature(a, "Курс номер %s" % a, "Литература к курсу %s_%s" % (a, i))
            self.add_home_work(a, "Курс номер %s" % a, "Домашнее к курсу %s_%s" % (a, i), "2020-12-12")

        self.edit_home_work(0, "Курс номер 0", 0, "Номая информация по дз", "2020-12-12")
        self.edit_literature(0, "Курс номер 0", 0, "Новая литература")


if __name__ == '__main__':
    db = DataBase()
    db.get_info_student(2)
