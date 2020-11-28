import mysql.connector
from mysql.connector import Error


class DataBase:
    """
    Класс реализующий связь бота с базой данных.

    Требуется реализовать набор методов для выдачи информаций по определенным шблонам, также набор команд для изменения
    данных в базе. (добавление тоже)
    """

    def __init__(self):
        try:
            self.__connection = mysql.connector.connect(host="127.0.0.1", user="root", password="",
                                                        database="mydb")
        except Error as e:
            print(e)

    def whoIs(self, id_user):
        """
        Определяет является ли пользователь преподователем
        :param id_user: Токен пользователя
        :return: Кто это, преподователь, студент или, что такого нет в базе
        """
        cursor = self.__connection.cursor()

        request = "select idteachers from teachers where idteachers = %s" % id_user
        cursor.execute(request)
        if cursor.fetchall():
            return "Teacher"

        request = "select idstudents from students where idstudents = %s" % id_user
        cursor.execute(request)
        if cursor.fetchall():
            return "Student"

        return "Nobody"

    def registration_user(self, id_user: int, name: str, surname: str, is_teacher: bool):
        """
        Регистрация пользователя. Добавляет его в нужную таблицу в зависимоти от его статуса.
        :param id_user: Токен пользователя (id пользователя), для идентификаций в базе данных
        :param name: Имя пользователя
        :param surname: Фамилия пользователя
        :param is_teacher: Логическое выражение, если он преподаватель, то значение True, False иначе
        """
        cursor = self.__connection.cursor()
        cursor.callproc("registration_user", (id_user, name, surname, is_teacher))
        self.__connection.commit()

    def delete_user(self, id_user):
        """
        Удаляет пользователя из базы данных. После удаления требуется повторная регистрация.
        :param id_user: Токен пользователя
        :return:
        """
        cursor = self.__connection.cursor()
        cursor.callproc("delete_user", (id_user,))
        self.__connection.commit()

    def add_course_student(self, id_user, name_course):
        """
        Записывает пользователя на курс
        :param id_user: Токен пользователя
        :param name_course: Название курса на который хочет записаться пользователь
        """
        request = "select idsubjects from subjects where name=\"%s\";" % name_course
        cursor = self.__connection.cursor()
        cursor.execute(request)
        id_course = cursor.fetchall()[0][0]
        request = "insert into student_subject(idstudents, idsubjects) value ({0}, {1});".format(id_user, id_course)
        cursor.execute(request)
        self.__connection.commit()

    def get_all_courses(self):
        """
        Получает список всех доступных курсов
        :return: Список строк, в котором записанны названия курсов
        """
        request = "select name from subjects;"
        cursor = self.__connection.cursor()
        cursor.execute(request)
        courses = cursor.fetchall()
        return courses

    def get_user_courses(self, id_users, role: str):
        """
        Получает список курсов определенного пользователя
        Не отличается для студента и преподователя
        :param role: Роль пользователя
        :param id_users: Токен пользователя
        :return: Список строк, в котором записанны названия курсов
        """
        cursor = self.__connection.cursor()
        if role == "T":
            request = "select name from subjects where idteachers = %s" % id_users
        elif role == "S":
            request = ""
        else:
            return None
        cursor.execute()
        courses = cursor.fetchall()
        return courses

    def _random_add(self):
        cursor = self.__connection.cursor()
        n_1 = 5
        n_2 = 100

        request = "insert into teachers(idteachers, name, surname) values "
        for i in range(n_1):
            request += '(%s, "%s", "%s"),' % (i, i, i)
        cursor.execute(request[:-1] + ";")

        request = "insert into students(idstudents, name, surname) values "
        for i in range(n_1, n_1 + n_2):
            request += '(%s, "%s", "%s"),' % (i, i, i)
        cursor.execute(request[:-1] + ";")

        self.__connection.commit()

        request = """insert into subjects(name, info, idteachers) values
					("A", "...", 0),
					("B", "...", 1),
					("C", "...", 2),
					("D", "...", 3),
					("E", "...", 4);
                """
        cursor.execute(request)
        self.__connection.commit()


if __name__ == '__main__':
    db = DataBase()
    db.add_course_student(55, "A")
