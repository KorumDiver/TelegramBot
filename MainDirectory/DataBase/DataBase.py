import random

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
            self.__connection = mysql.connector.connect(host="127.0.0.1", user="root", password="korum123456",
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
            return 2

        request = "select idstudents from students where idstudents = %s" % id_user
        cursor.execute(request)
        if cursor.fetchall():
            return 1

        return 0

    def registration_user(self, id_user: int, name: str, surname: str, role: int):
        """
        Регистрация пользователя. Добавляет его в нужную таблицу в зависимоти от его статуса.
        :param role:
        :param id_user: Токен пользователя (id пользователя), для идентификаций в базе данных
        :param name: Имя пользователя
        :param surname: Фамилия пользователя
        :param is_teacher: Логическое выражение, если он преподаватель, то значение True, False иначе
        """
        cursor = self.__connection.cursor()
        cursor.callproc("registration_user", (id_user, name, surname, role == 2))
        self.__connection.commit()

    def delete_user(self, id_user):
        """
        Удаляет пользователя из базы данных. После удаления требуется повторная регистрация.
        :param id_user: Токен пользователя
        """
        cursor = self.__connection.cursor()
        cursor.callproc("delete_user", (id_user,))
        self.__connection.commit()

    def get_user_raiting(self, user_id):
        pass


if __name__ == '__main__':
    db = DataBase()
    print(db.test())
