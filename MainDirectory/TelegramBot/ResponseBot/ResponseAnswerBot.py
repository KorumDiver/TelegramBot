import telebot
from telebot import apihelper
#import MainDirectory.DataBase.DataBase as database
import MainDirectory.TelegramBot.VisualBot.TypesAndVisual as visual_class
bot = telebot.TeleBot("1438178504:AAF5-LIj7iPbGZWmPT8vOJJeGHjyjH3NTiQ")

class ResponseAnswerBot:

    # db = DataBase()

    # id| роль | last_time_message| tec_curs|
    cv_user_id = {}
    def __init__(self):
        #self.db = database.DataBase()
        self.visual = visual_class.TypesAndVisual()
        cv_user_id = {-1: [0, 0, {"course": ""}]}

    kursi_studenta = ["BD", " MATSTAt", "TAU", "RUSSIAN"]

    # STUDENT

    def check(self, id, new_time):
        if id not in self.cv_user_id.keys():
            #k = self.db.whoIs(id)
            k = 1
            if k == 0:
                bot.send_message("Извините, вы не зарегистрированы, отправьте /start снова.")
            elif k == 1:
                bot.send_message(id, "Выберите действие:", self.visual.start_keyboard)
            elif k == 2:
                bot.send_message(id, "Выберите действие:", 'клава препода')
            self.cv_user_id[id] = [k, new_time, ""]
            return False
        return True

    def Hello(self, message):
        if(self.check(message.chat.id)):
            if self.cv_user_id[message.chat.id] != 0:
                bot.send_message(message.chat.id, "Выберите действие:", self.visual.start_keyboard)
            else:
                bot.register_next_step_handler(bot.send_message(message.chat.id,
                                 "Здравствуйте, студент! Давайте приступим к регистрации. Введите свои ФИО через пробел."
                                 " Внимание, вы сможете это сделать только один раз!"), self.student_registration)

    def mainmain(self):
        @bot.message_handler(commands=['start'])
        def start_com(message):
            print(1)
            self.Hello(self, message)
        bot.polling(none_stop=True)

if __name__ == '__main__':
    ResponseAnswerBot.mainmain(None)



        # user[0] = message.chat.id
"""
    #@bot.message_handler(func=lambda message: message.text)
    def student_registration(self, message):
        if self.cv_user_id[message.chat.id][0] == 0:
            s = message.text.split(" ")
            if len(s) != 3:
                bot.send_message(message.chat.id, "Введи, пожалуйста, нормально свои ФИО, иначе БАН!!!")
            self.cv_user_id[message.chat.id][0] == 1
            bot.send_message(message.chat.id, "Вы успешно зарегистрированы")
            bot.send_message(message.chat.id, "Выберите действие:", self.visual.start_keyboard)
        elif message.chat.id not in cv_user_id:
            bl = bd.whoIs(message.chat.id)
            if bl == 0:
                s = message.text.split(" ")
                user_ids[cv_user_id[message.chat.id]][0] == 1
                bot.send_message(message.chat.id, "Вы успешно зарегистрированы")
                bot.send_message(message.chat.id, "Мои курсы \n Записаться \n  Инфорация о себе")

    @bot.message_handler(func=lambda message: message.text == "Мои курсы")
    def prosm_cv_kursov(message):
        bot.send_message(message.chat.id, "BD MATSTAt TAU RUSSIAN")
        print(tec_user)

    @bot.message_handler(func=lambda message: message.text == "Записаться")
    def prosm_cvob_kursov(message):
        bot.send_message(message.chat.id, "BD MATSTAt TAU RUSSIAN")
        print(tec_user)

    @bot.message_handler(func=lambda message: message.text in kursi_studenta)
    def prosm_cvob_kursov(message):
        bot.send_message(message.chat.id, "Выберите действие")
        tec_user["course"] = message.text
        print(tec_user)

    @bot.message_handler(func=lambda message: message.text not in kursi_studenta)
    def prosm_cvob_kursov(message):
        bot.send_message(message.chat.id, "Вы записаны на курс")
        bot.send_message(message.chat.id, "Мои курсы \n Записаться \n  Инфорация о себе")
        print(tec_user)
"""
