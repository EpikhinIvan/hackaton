import telebot
from customers.models import Driver, Passenger
from telebot import types
from django.core.management.base import BaseCommand

bot = telebot.TeleBot('6618760153:AAEsWofXuZ8AkdxfOZPSdmCs0P67ytmuLM8')

logged_in_users = {}


def get_user_by_car_number(car_number):
    try:
        return Driver.objects.get(car_number=car_number)
    except Driver.DoesNotExist:
        return None


@bot.message_handler(commands=['start'])
def handle_start(message):
    user_telegram_id = message.from_user.id

    if user_telegram_id in logged_in_users:
        show_main_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Здравствуйте! Введите номер машины и пароль через запятую для аутентификации.")



# Завершить поездку
def end_trip(user_id):
    user_telegram_id = user_id
    if user_telegram_id in logged_in_users:
        user = logged_in_users[user_telegram_id]

        try:
            passenger = Passenger.objects.get(assigned_driver=user)
            passenger.assigned_driver = None  # Прерываем связь с водителем
            passenger.save()

            # Обновляем статус водителя
            user.status = 'not_working'
            user.save()

            del logged_in_users[user_telegram_id]
            bot.send_message(user_telegram_id, "Поездка завершена. Введите /start для нового входа.")
        except Passenger.DoesNotExist:
            bot.send_message(user_telegram_id, "У вас нет текущего пассажира.")
    else:
        bot.send_message(user_telegram_id, "Водитель не вошел в систему. Введите /start для входа.")




@bot.message_handler(func=lambda message: True)
def handle_credentials_input(message):
    user_telegram_id = message.from_user.id

    if user_telegram_id in logged_in_users:
        return

    input_text = message.text.strip()
    credentials = input_text.split(',')

    if len(credentials) == 2:
        car_number, password = credentials
        car_number = car_number.strip()
        password = password.strip()

        db_user = get_user_by_car_number(car_number)

        if db_user and db_user.password == password:
            logged_in_users[user_telegram_id] = db_user
            bot.send_message(message.chat.id, "Аутентификация прошла успешно!")
            show_main_menu(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Номер машины или пароль неверны. Пожалуйста, повторите попытку или введите /start для начала заново.")
    else:
        bot.send_message(message.chat.id, "Неверный формат ввода. Пожалуйста, введите номер машины и пароль через запятую.")


def show_main_menu(user_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    info = types.InlineKeyboardButton('Информация о рейсе', callback_data="info")
    update_status = types.InlineKeyboardButton('Обновить статус', callback_data="update_status")
    end_trip = types.InlineKeyboardButton('Завершить поездку', callback_data="end_trip")
    exit = types.InlineKeyboardButton('Выйти', callback_data="exit")
    keyboard.add(info, update_status, end_trip, exit)

    bot.send_message(user_id, "Выберите действие:", reply_markup=keyboard)



@bot.callback_query_handler(func=lambda call: call.data in ['info', 'update_status', 'end_trip', 'exit'])
def handle_main_menu_buttons(call):
    user_id = call.from_user.id

    if user_id not in logged_in_users:
        return

    if call.data == 'info':
        show_passenger_info(user_id)
    elif call.data == 'update_status':
        show_update_status_menu(user_id)
    elif call.data == 'end_trip':
        end_trip(user_id)
    elif call.data == 'exit':
        exit(user_id)

def exit(user_id):
    user_telegram_id = user_id
    if user_telegram_id in logged_in_users:
        del logged_in_users[user_telegram_id]
        bot.send_message(user_telegram_id, "Вы вышли из системы. Введите /start для нового входа.")
    else:
        bot.send_message(user_telegram_id, "Водитель не вошел в систему. Введите /start для входа.")
    

def show_passenger_info(user_id):
    user_telegram_id = user_id
    if user_telegram_id in logged_in_users:
        user = logged_in_users[user_telegram_id]
        
        try:
            passenger = Passenger.objects.get(assigned_driver=user)
            bot.send_message(user_id, f"Информация о пассажире:\nИмя: {passenger.name}\nВремя прибытия: {passenger.arrival_time}")
        except Passenger.DoesNotExist:
            bot.send_message(user_id, "У вас нет текущего пассажира.")
    else:
        bot.send_message(user_id, "Водитель не вошел в систему. Введите /start для входа.")



def show_update_status_menu(user_id):
    markup = types.InlineKeyboardMarkup(row_width=1)
    airport = types.InlineKeyboardButton('В аэропорту', callback_data="at_airport")
    way = types.InlineKeyboardButton('В пути', callback_data="in_transit")
    delivered = types.InlineKeyboardButton('Забрал клиента', callback_data="picked_up")
    markup.add(airport, way, delivered)

    bot.send_message(user_id, "Выберите статус:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['at_airport', 'in_transit', 'picked_up'])
def handle_update_status_buttons(call):
    user_id = call.from_user.id

    if user_id not in logged_in_users:
        return

    status_mapping = {
        'at_airport': 'В аэропорту',
        'in_transit': 'В пути',
        'picked_up': 'Забрал клиента',
    }

    status_key = call.data
    status = status_mapping.get(status_key)

    if status:
        update_status(user_id, status)

def update_status(user_id, new_status):
    user_telegram_id = user_id
    if user_telegram_id in logged_in_users:
        user = logged_in_users[user_telegram_id]

        # Обновляем статус водителя
        user.status = new_status
        user.save()

        bot.send_message(user_telegram_id, f"Статус обновлен: {new_status}")
    else:
        bot.send_message(user_telegram_id, "Водитель не вошел в систему. Введите /start для входа.")


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Starting bot...")
        bot.polling()
        print("Bot stopped")
