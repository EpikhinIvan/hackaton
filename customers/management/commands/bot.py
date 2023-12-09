import telebot
import sqlite3
from telebot import types
from django.core.management.base import BaseCommand

bot = telebot.TeleBot('6618760153:AAEsWofXuZ8AkdxfOZPSdmCs0P67ytmuLM8')
DATABASE_PATH = 'auth_database.db'
FLIGHTS_DATABASE_PATH = 'info_database.db'  
CONNECTION_DATABASE_PATH = 'connection.db'

logged_in_users = {}


def get_user_by_car_number(car_number):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE car_number = ?', (car_number,))
    user = cursor.fetchone()
    conn.close()
    return user


@bot.message_handler(commands=['start'])
def handle_start(message):
    user = message.from_user

    if user.id in logged_in_users:
        show_main_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Здравствуйте! Введите номер машины и пароль через запятую для аутентификации.")



@bot.message_handler(commands=['end'])
def handle_end(message):
    user = message.from_user
    
    if user.id in logged_in_users:
        del logged_in_users[user.id]
        bot.send_message(message.chat.id, "Вы успешно вышли из системы! Введите /start для нового входа.")
    else:
        bot.send_message(message.chat.id, "Вы не вошли в систему. Введите /start для входа.")



@bot.message_handler(func=lambda message: True)
def handle_credentials_input(message):
    user = message.from_user

    if user.id in logged_in_users:
        return

    input_text = message.text.strip()

    credentials = input_text.split(',')

    if len(credentials) == 2:
        car_number, password = credentials
        car_number = car_number.strip()
        password = password.strip()

        db_user = get_user_by_car_number(car_number)

        if db_user and db_user[2] == password: 
    
            logged_in_users[user.id] = {'car_number': car_number}
            bot.send_message(message.chat.id, "Аутентификация прошла успешно!")
            show_main_menu(message.chat.id)
        else:
            bot.send_message(message.chat.id,"Номер машины или пароль неверны. Пожалуйста, повторите попытку или введите /start для начала заново.")
    else:
        bot.send_message(message.chat.id, "Неверный формат ввода. Пожалуйста, введите номер машины и пароль через запятую.")


def show_main_menu(user_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    info = types.InlineKeyboardButton('Информация о рейсе', callback_data="info")
    update_status = types.InlineKeyboardButton('Обновить статус', callback_data="update_status")
    end_trip = types.InlineKeyboardButton('Завершить поездку', callback_data="end_trip")
    keyboard.add(info, update_status, end_trip)

    bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data in ['info', 'update_status', 'end_trip'])
def handle_main_menu_buttons(call):
    user_id = call.from_user.id

    if user_id not in logged_in_users:
        return

    if call.data == 'info':
        show_flight_info(user_id)
    elif call.data == 'update_status':
        show_update_status_menu(user_id)
    elif call.data == 'end_trip':
         end_trip(user_id)



def show_flight_info(user_id):
    conn = sqlite3.connect(FLIGHTS_DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT name, time FROM flights WHERE car_number = ?',(logged_in_users[user_id]['car_number'],))
    result = cursor.fetchone()
    conn.close()

    if result:
        bot.send_message(user_id, f"Информация о рейсе:\nНазвание: {result[0]}\nВремя: {result[1]}")
    else:
        bot.send_message(user_id, "Информация о рейсе не найдена.")


def show_update_status_menu(user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    airport = types.InlineKeyboardButton('В аэропорту', callback_data="at_airport")
    way = types.InlineKeyboardButton('В пути', callback_data="on_the_way")
    delivered = types.InlineKeyboardButton('Клиент доставлен', callback_data="client_delivered")
    markup.add(airport, way, delivered)

    bot.send_message(user_id, "Выберите статус:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['at_airport', 'on_the_way', 'client_delivered'])
def handle_update_status_buttons(call):
    user_id = call.from_user.id

    if user_id not in logged_in_users:
        return

    status = call.data
    save_status_to_database(logged_in_users[user_id]['car_number'], status)
    bot.send_message(user_id, f"Статус обновлен: {status}")


def save_status_to_database(car_number, status):
    conn = sqlite3.connect(CONNECTION_DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE DriverPassengerRelation SET status = ? WHERE car_number = ?', (status, car_number))
    conn.commit()
    conn.close()

# 12222222222222222222222222222222222222222222222222222222222222222222222222222222222

# Завершить поездку
def end_trip(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE car_number = ?', (logged_in_users[user_id]['car_number'],))
    conn.commit()
    conn.close()

    # Удаляем пользователя из списка вошедших
    del logged_in_users[user_id]

    bot.send_message(user_id, "Поездка завершена. Введите /start для нового входа.")


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting bot...")
        bot.polling()
        print("Bot stopped")
