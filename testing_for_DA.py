import telebot
from telebot import types
from datetime import datetime, timedelta
from meteostat import Point, Daily
import pandas as pd
from prophet import Prophet  # модель для прогнозирования временных рядов
import plotly.graph_objects as go

# Ваш токен Telegram-бота
TOKEN = '1628816265:AAGdCGQ5CyipLFU_fdKv8RvXZiq7N4CHQvQ'
# Название excel файла для анализа
EXCEL_FILE_NAME = 'vlad_weather.xlsx'
# Название файла с координатами городов
COORDINATES_FILE_NAME = 'citiesы.xlsx'

# Читаем данные из Excel-файла
data = pd.read_excel(EXCEL_FILE_NAME)

# Приводим столбец с датой к нужному формату
data["date"] = pd.to_datetime(data["date"], format='%Y-%m-%d')
data['year'] = data['date'].dt.year
data["month"] = data["date"].dt.month
data["day"] = data["date"].dt.day

# Читаем файл с координатами городов
coordinates = pd.read_excel(COORDINATES_FILE_NAME)

# Создаем список городов для выпадающего списка
cities = list(coordinates['city'])


# Определяем функцию для получения координат выбранного города
def get_location(city):
    # Получаем координаты для выбранного города из файла
    row = coordinates.loc[coordinates['city'] == city].iloc[0]
    return Point(row['latitude'], row['longitude'])


# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Чтобы узнать погоду, введите название города:")

# Добавляем обработчик для кнопки "вернуться к выбору города"
@bot.message_handler(func=lambda message: message.text == 'Вернуться к выбору города')
def back_to_city(message):
    # Создаем клавиатуру и настройки кнопок с городами
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton(city) for city in cities]
    keyboard.add(*buttons)

    # Отправляем сообщение с выбором города и клавиатурой
    bot.send_message(message.chat.id, "Введите или выберите город:", reply_markup=keyboard)

    # Регистрируем обработчик нажатия на кнопки города
    bot.register_next_step_handler(message, choose_city)

# Обработчик ввода названия города
@bot.message_handler(func=lambda message: True)
def choose_city(message):
    # Получаем название города и сохраняем в глобальную переменную
    global city
    city = message.text

    if message.text == 'Выбрать город':
        back_to_city(message)
        return

    # Создаем клавиатуру и настройки кнопок
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button1 = types.KeyboardButton(text="Температура")
    button2 = types.KeyboardButton(text="Осадки")
    button3 = types.KeyboardButton(text="Давление")
    button4 = types.KeyboardButton(text="Вернуться к выбору города")
    keyboard.add(button1, button2, button3, button4)

    # Отправляем сообщение с выбором параметра и клавиатурой
    bot.send_message(message.chat.id, "Выберите параметр:", reply_markup=keyboard)

    # Регистрируем обработчик нажатия на кнопки параметра
    bot.register_next_step_handler(message, choose_param)

# Обработчик выбора параметра
def choose_param(message):
    # Получаем выбранный параметр и сохраняем в глобальную переменную
    global param
    param = message.text

    if param == "Вернуться к выбору города":
        back_to_city(message)
        return
    else:
        # Создаем клавиатуру и настройки кнопок
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button = types.KeyboardButton(text="На cегодня")
        button1 = types.KeyboardButton(text="На завтра")
        button2 = types.KeyboardButton(text="На 3 дня")
        button3 = types.KeyboardButton(text="На неделю")
        button4 = types.KeyboardButton(text="На месяц")
        button5 = types.KeyboardButton(text="На год")
        button6 = types.KeyboardButton(text="Вернуться к выбору города")

        keyboard.add(button, button1, button2, button3, button4, button5, button6)

        # Отправляем сообщение с выбором периода и клавиатурой
        bot.send_message(message.chat.id, f"Выбери период для {param}:", reply_markup=keyboard)

        # Регистрируем обработчик нажатия на кнопки периода
        bot.register_next_step_handler(message, get_weather)


# Обработчик получения погоды
def get_weather(message):
    # Получаем выбранный период и сохраняем в глобальную переменную
    global period
    period = message.text

    if city in cities:
        # Получаем координаты выбранного города
        location = get_location(city)
        date_str = '01.01.2001'
        date = datetime.strptime(date_str, '%d.%m.%Y')

        # Определяем начальную и конечную даты для выбранного периода
        if period == 'На cегодня':
            start_date = datetime.now().replace(hour=0, minute=0, second=0)
            end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        elif period == "На завтра":
            start_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=2)
        elif period == "На 3 дня":
            start_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=4)
        elif period == "На неделю":
            start_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=8)
        elif period == "На месяц":
            start_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=32)
        elif period == "На год":
            start_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=366)
        elif period == "Вернуться к выбору города":
            back_to_city(message)
            return

        # Получаем данные о погоде для выбранного города и периода
        weather_data = Daily(location, start_date, end_date).fetch()

        # Отбираем нужный параметр из данных о погоде
        if param == "Температура":
            # Готовим данные для модели
            forecast_data = data.rename(columns={"date": "ds",
                                                 "tavg": "y"})
            y_label = "Температура, °C"
        elif param == "Осадки":
            forecast_data = data.rename(columns={"date": "ds",
                                                 "prcp": "y"})
            y_label = "Осадки, мм"
        elif param == "Давление":
            y_label = "Давление, мм.рт.ст."
            forecast_data = data.rename(columns={"date": "ds",
                                                 "pres": "y"})

        # Инициализируем прогнозную модель
        model = Prophet()

        # Обучаем модель
        model.fit(forecast_data)

        # Получаем даты для прогноза
        if period == "На cегодня":
            future_dates = pd.date_range(start=datetime.now(), end=end_date, freq='H')
        elif period == "На завтра":
            future_dates = pd.date_range(start=datetime.now(), end=end_date, freq='H')
        elif period == "На 3 дня":
            future_dates = pd.date_range(start=datetime.now(), end=end_date, freq='H')
        elif period == "На неделю":
            future_dates = pd.date_range(start=datetime.now(), end=end_date, freq='H')
        elif period == "На месяц":
            future_dates = pd.date_range(start=datetime.now(), end=end_date, freq='D')
        elif period == "На год":
            future_dates = pd.date_range(start=datetime.now(), end=end_date, freq='D')
        elif period == "Вернуться к выбору города":
            back_to_city(message)
            return

        # Получаем прогноз
        future = model.predict(pd.DataFrame({"ds": future_dates}))
        print('here')
        # Рисуем график с историческими данными и прогнозом
        fig = go.Figure()
        # fig.add_trace(go.Scatter(x=weather_data.index, y=parameter.values, name='Исторические данные'))
        fig.add_trace(go.Scatter(x=future_dates, y=future['yhat'], name='Прогноз'))
        fig.update_layout(title=f"{param} в {city} {period}", xaxis_title="Дата", yaxis_title=y_label)
        fig.update_xaxes(range=[datetime.now(), end_date])
        bot.send_photo(chat_id=message.chat.id, photo=fig.to_image(format='png'))  # Отправляем график пользователю
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button = types.KeyboardButton(text="Вернуться к выбору города")
        keyboard.add(button)
        bot.send_message(chat_id=message.chat.id, text='Можете ввести город снова', reply_markup=keyboard)


    else:
        bot.send_message(message.chat.id, "Некорректный ввод. Введите название города заново:")


# Запускаем бота
bot.polling(none_stop=True)
