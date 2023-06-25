import telebot
from telebot import types
from datetime import datetime, timedelta
from meteostat import Point, Daily
import pandas as pd
from prophet import Prophet  # модель для прогнозирования временных рядов
import plotly.graph_objects as go
import requests
import numpy as np

# Ваш токен Telegram-бота
TOKEN = 'Your_telegram_api'

api_weather = 'your_api_weather'
url = 'http://api.openweathermap.org/data/2.5/weather'

# Название файла с координатами городов
COORDINATES_FILE_NAME = 'citiesы.xlsx'

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
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton(text="Хочу графики")
    button2 = types.KeyboardButton(text="Хочу текст")
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id,
                     "Привет! Для того, чтобы узнать функционал - напишите /help. "
                     "\nВыберите в каком виде хотели бы получить данные:", reply_markup=keyboard)


# Добавляем обработчик для кнопки "вернуться к выбору города"
@bot.message_handler(func=lambda message: message.text == 'Вернуться к выбору города')
def back_to_city(message):
    # Создаем клавиатуру и настройки кнопок с городами
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [types.KeyboardButton(city) for city in cities]
    keyboard.add(*buttons)

    # Отправляем сообщение с выбором города и клавиатурой
    bot.send_message(message.chat.id, "Введите или выберите город:", reply_markup=keyboard)

    # Регистрируем обработчик нажатия на кнопки города
    bot.register_next_step_handler(message, choose_city)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id,
                     "Пока что это прикол, инфа будет позже")


@bot.message_handler(func=lambda message: message.text == 'Хочу текст')
def for_test(message):
    # Создаем клавиатуру и настройки кнопок с городами
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [types.KeyboardButton(city) for city in cities]
    keyboard.add(*buttons)

    # Отправляем сообщение с выбором города и клавиатурой
    bot.send_message(message.chat.id, "Введите или выберите город:", reply_markup=keyboard)

    # Регистрируем обработчик нажатия на кнопки города
    bot.register_next_step_handler(message, test)


@bot.message_handler(func=lambda message: message.text == 'Хочу текст')
def test(message):
    city_name = message.text
    url = 'http://api.openweathermap.org/data/2.5/weather'

    try:
        params = {'APPID': api_weather, 'q': city_name, 'units': 'metric', 'lang': 'ru'}
        result = requests.get(url, params=params)
        weather = result.json()

        if weather["main"]['temp'] < 0:
            status = "инфа"
        elif weather["main"]['temp'] < 10:
            status = "инфа"
        elif weather["main"]['temp'] < 20:
            status = "инфа"
        elif weather["main"]['temp'] > 30:
            status = "инфа"
        else:
            status = "Сейчас отличная температура!\nнаверное\n"

        bot.send_message(message.chat.id, "В городе " + str(weather["name"]) + " температура " + str(
            float(weather["main"]['temp'])) + "\n" +
                         "Скорость ветра " + str(float(weather['wind']['speed'])) + "\n" +
                         "Давление " + str(round(float(weather['main']['pressure']) / 1.333, 1)) + "\n" +
                         "Влажность " + str(int(weather['main']['humidity'])) + "%" + "\n" +
                         "Видимость " + str(weather['visibility']) + "\n" +
                         "Описание: " + str(weather['weather'][0]["description"]) + "\n\n" + status)
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button = types.KeyboardButton(text="Хочу текст")
        button1 = types.KeyboardButton(text="Хочу графики")
        button2 = types.KeyboardButton(text="Вернуться к выбору города")
        keyboard.add(button, button1, button2)
        bot.send_message(chat_id=message.chat.id, text='Можете ввести город снова или заново определите режим работы',
                         reply_markup=keyboard)
        print('Я отправил текст с погодой на сегодня')

    except:
        bot.send_message(message.chat.id, "Город " + city_name + " не найден")
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button = types.KeyboardButton(text="Хочу текст")
        button1 = types.KeyboardButton(text="Хочу графики")
        button2 = types.KeyboardButton(text="Вернуться к выбору города")
        keyboard.add(button, button1, button2)
        bot.send_message(chat_id=message.chat.id, text='Можете ввести город снова или заново определите режим работы',
                         reply_markup=keyboard)
        print('Я отправил ошибку, город введен неверно')


@bot.message_handler(func=lambda message: message.text == 'Хочу графики')
def write_city(message):
    # Создаем клавиатуру и настройки кнопок с городами
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [types.KeyboardButton(city) for city in cities]
    keyboard.add(*buttons)

    # Отправляем сообщение с выбором города и клавиатурой
    bot.send_message(message.chat.id, "Введите или выберите город:", reply_markup=keyboard)

    # Регистрируем обработчик нажатия на кнопки города
    bot.register_next_step_handler(message, choose_city)


# Обработчик ввода названия города
@bot.message_handler(func=lambda message: message.text == 'Хочу графики')
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
        button5 = types.KeyboardButton(text="На 3 месяца")
        button6 = types.KeyboardButton(text="На год")
        button7 = types.KeyboardButton(text="Вернуться к выбору города")

        keyboard.add(button, button1, button2, button3, button4, button5, button6, button7)

        # Отправляем сообщение с выбором периода и клавиатурой
        bot.send_message(message.chat.id, f"Выбери период для {param}:", reply_markup=keyboard)

        # Регистрируем обработчик нажатия на кнопки периода
        bot.register_next_step_handler(message, get_weather)


# Обработчик получения погоды
def get_weather(message):
    # Получаем выбранный период
    period = message.text
    try:
        if city in cities:
            # Получаем координаты выбранного города
            location = get_location(city)
            date_str = '01.01.1900'
            start_date = date_str

            # Определяем начальную и конечную даты для выбранного периода
            if period == 'На cегодня':
                end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            elif period == "На завтра":
                end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=2)
            elif period == "На 3 дня":
                end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=4)
            elif period == "На неделю":
                end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=8)
            elif period == "На месяц":
                end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=32)
            elif period == "На 3 месяца":
                end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=94)
            elif period == "На год":
                end_date = datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=366)
            elif period == "Вернуться к выбору города":
                back_to_city(message)
                return

            # Получаем данные о погоде для выбранного города и периода
            weather_data = Daily(location, start_date, end_date).fetch()
            print(weather_data)  # Нужно для проверки фрейма
            weather_data['date'] = weather_data.index.strftime('%Y-%m-%d')
            # Приводим столбец с датой к нужному формату
            weather_data["date"] = pd.to_datetime(weather_data["date"], format='%Y-%m-%d')
            weather_data['year'] = weather_data['date'].dt.year
            weather_data["month"] = weather_data["date"].dt.month
            weather_data["day"] = weather_data["date"].dt.day

            # Отбираем нужный параметр из данных о погоде
            if param == "Температура":
                # Готовим данные для модели
                forecast_data = weather_data[["date", "tmin", "tmax", "tavg"]].rename(columns={"date": "ds"})
                y_label = "Температура, °C"

            elif param == "Осадки":
                forecast_data = weather_data.rename(columns={"date": "ds"})
                y_label = "Осадки, мм"

            elif param == "Давление":
                forecast_data = weather_data.rename(columns={"date": "ds",
                                                             "pres": "y"})
                y_label = "Давление, мм. рт. ст."

            if param == 'Температура':
                # Инициализируем прогнозную модель для tmin
                model_tmin = Prophet()
                # Обучаем модель
                model_tmin.fit(forecast_data[["ds", "tmin"]].rename(columns={"tmin": "y"}))

                # Инициализируем прогнозную модель для tmax
                model_tmax = Prophet()
                # Обучаем модель
                model_tmax.fit(forecast_data[["ds", "tmax"]].rename(columns={"tmax": "y"}))

                # Инициализируем прогнозную модель для tavg
                model_tavg = Prophet()
                # Обучаем модель
                model_tavg.fit(forecast_data[["ds", "tavg"]].rename(columns={"tavg": "y"}))

            elif param == 'Осадки':
                model_prcp = Prophet()
                model_prcp.fit(forecast_data[["ds", "prcp"]].rename(columns={"prcp": "y"}))

            else:
                # Инициализируем прогнозную модель
                model = Prophet()

                # Обучаем модель
                model.fit(forecast_data)

            # Получаем даты для прогноза
            if period == "На cегодня":
                future_dates = pd.date_range(start=datetime.now() - timedelta(days=1), end=end_date, freq='H')
            elif period == "На завтра":
                future_dates = pd.date_range(start=datetime.now() - timedelta(days=1), end=end_date, freq='H')
            elif period == "На 3 дня":
                future_dates = pd.date_range(start=datetime.now() - timedelta(days=1), end=end_date, freq='H')
            elif period == "На неделю":
                future_dates = pd.date_range(start=datetime.now() - timedelta(days=1), end=end_date, freq='H')
            elif period == "На месяц":
                future_dates = pd.date_range(start=datetime.now() - timedelta(days=1), end=end_date, freq='D')
            elif period == "На 3 месяца":
                future_dates = pd.date_range(start=datetime.now() - timedelta(days=1), end=end_date, freq='D')
            elif period == "На год":
                future_dates = pd.date_range(start=datetime.now() - timedelta(days=1), end=end_date, freq='D')
            elif period == "Вернуться к выбору города":
                back_to_city(message)
                return

            if param == 'Температура':
                future_tmin = model_tmin.predict(pd.DataFrame({"ds": future_dates}))
                future_tmax = model_tmax.predict(pd.DataFrame({"ds": future_dates}))
                future_tavg = model_tavg.predict(pd.DataFrame({"ds": future_dates}))
                fig = go.Figure()
                # Рисуем график с историческими данными и прогнозом для tmin
                # fig.add_trace(go.Scatter(x=forecast_data["ds"], y=forecast_data["tmin"], name='Исторические данные tmin'))
                fig.add_trace(go.Scatter(x=future_dates, y=future_tmin['yhat'], name='Прогноз минимальной температуры'))

                # Рисуем график с историческими данными и прогнозом для tmax
                # fig.add_trace(go.Scatter(x=forecast_data["ds"], y=forecast_data["tmax"], name='Исторические данные tmax'))
                fig.add_trace(
                    go.Scatter(x=future_dates, y=future_tmax['yhat'], name='Прогноз максимальной температуры'))

                # Рисуем график с историческими данными и прогнозом для tavg
                # fig.add_trace(go.Scatter(x=forecast_data["ds"], y=forecast_data["tavg"], name='Исторические данные tavg'))
                fig.add_trace(go.Scatter(x=future_dates, y=future_tavg['yhat'], name='Прогноз средней температуры'))

                fig.update_layout(title=f"{param} в городе {city} {period}", xaxis_title="Дата", yaxis_title=y_label)
                fig.update_xaxes(range=[datetime.now() - timedelta(days=1), end_date])
                bot.send_photo(chat_id=message.chat.id,
                               photo=fig.to_image(format='png'))  # Отправляем график пользователю
                keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                button = types.KeyboardButton(text="Хочу текст")
                button1 = types.KeyboardButton(text="Хочу графики")
                button2 = types.KeyboardButton(text="Вернуться к выбору города")
                keyboard.add(button, button1, button2)
                bot.send_message(chat_id=message.chat.id,
                                 text='Можете ввести город снова или заново определите режим работы',
                                 reply_markup=keyboard)

                print('~~~~~~~~~Отправил температуру~~~~~~~~~~~')
                # Отображение графика
                # fig.show()
            elif param == 'Осадки':
                # Получаем прогноз
                future_prcp = model_prcp.predict(pd.DataFrame({"ds": future_dates}))
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=future_dates, y=future_prcp['yhat'], name='Прогноз осадков'))
                fig.update_layout(title=f"{param} в городе {city} {period}", xaxis_title="Дата", yaxis_title=y_label)
                fig.update_xaxes(range=[datetime.now() - timedelta(days=1), end_date])

                # Получаем логарифмы данных
                log_prcp = np.log(future_prcp['yhat'])

                # Вычисляем среднегеометрическую величину
                mean_geo = np.exp(np.mean(log_prcp))

                # Добавляем на график
                fig.add_shape(type='line', x0=future_dates[0], y0=mean_geo,
                              x1=future_dates[-1], y1=mean_geo,
                              line=dict(color='red', width=2, dash='dot'))

                bot.send_photo(chat_id=message.chat.id,
                               photo=fig.to_image(format='png'))  # Отправляем график пользователю

                keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                button = types.KeyboardButton(text="Хочу текст")
                button1 = types.KeyboardButton(text="Хочу графики")
                button2 = types.KeyboardButton(text="Вернуться к выбору города")
                keyboard.add(button, button1, button2)
                bot.send_message(chat_id=message.chat.id,
                                 text='Можете ввести город снова или заново определите режим работы',
                                 reply_markup=keyboard)
                print('~~~~~~~~~Отправил осадки~~~~~~~~~~~')
            elif param == 'Давление':
                # Получаем прогноз
                future = model.predict(pd.DataFrame({"ds": future_dates}))
                # Рисуем график с историческими данными и прогнозом
                fig = go.Figure()
                # fig.add_trace(go.Scatter(x=weather_data.index, y=parameter.values, name='Исторические данные'))
                fig.add_trace(go.Scatter(x=future_dates, y=future['yhat'] / 1.333, name='Прогноз'))
                fig.update_layout(title=f"{param} в {city} {period}", xaxis_title="Дата", yaxis_title=y_label)
                fig.update_xaxes(range=[datetime.now() - timedelta(days=1), end_date])
                bot.send_photo(chat_id=message.chat.id,
                               photo=fig.to_image(format='png'))  # Отправляем график пользователю
                keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                button = types.KeyboardButton(text="Хочу текст")
                button1 = types.KeyboardButton(text="Хочу графики")
                button2 = types.KeyboardButton(text="Вернуться к выбору города")
                keyboard.add(button, button1, button2)
                bot.send_message(chat_id=message.chat.id, text='Можете ввести город снова или заново '
                                                               'определите режим работы', reply_markup=keyboard)
                print('~~~~~~~~~Отправил давление~~~~~~~~~~~')

        else:
            bot.send_message(message.chat.id, "Некорректный ввод. Введите название города заново:")
            print('Город ввели неверно')
    except:
        # bot.send_message(message.chat.id, "Для прогнозирования погоды для города" + city + "недостаточно данных:(.\n"
        #                                                                                   "Пожалуйста, выберите "
        #                                                                                   "другой город")
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button = types.KeyboardButton(text="Хочу текст")
        button1 = types.KeyboardButton(text="Хочу графики")
        button2 = types.KeyboardButton(text="Вернуться к выбору города")
        keyboard.add(button, button1, button2)
        bot.send_message(chat_id=message.chat.id, text="Для прогнозирования погоды города " + city + " недостаточно"
                                                                                                     " данных:(.\n"
                                                                                                     "Пожалуйста, "
                                                                                                     "выберите "
                                                                                                     "другой город",
                         reply_markup=keyboard)
        print('Я отправил ошибку, город введен неверно')


# Запускаем бота
bot.polling(none_stop=True)

