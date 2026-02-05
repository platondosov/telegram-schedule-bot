import telebot
from telebot import types
from datetime import datetime, timedelta
import os  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
import time  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
import threading  # <-- ДОБАВИТЬ ЭТУ СТРОКУ
from flask import Flask  # <-- ДОБАВИТЬ ЭТУ СТРОКУ

# Flask приложение для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

# === ИСПРАВЬТЕ ТОКЕН БОТА ЗДЕСЬ ===
# Для теста можно оставить ваш, но лучше создать нового бота
BOT_TOKEN = "8036446753:AAHFkS2ntHfOFDIHJvrmEz9CHpeLCAZCJ1M"  # <-- ПРОВЕРЬТЕ ЭТОТ ТОКЕН!
bot = telebot.TeleBot(BOT_TOKEN)
# ===================================

# Дата начала весеннего семестра 2025-2026
START_DATE = datetime(2026, 2, 9)  # 9 февраля 2026 года


# Функция определения текущей недели
def get_current_week():
    today = datetime.now()
    if today < START_DATE:
        return "I"

    days_diff = (today - START_DATE).days
    week_num = (days_diff // 7) % 2
    return "I" if week_num == 0 else "II"


# Расписание для вашей группы
schedule = {
    "Понедельник": {
        "I": """📅 *ПОНЕДЕЛЬНИК | I неделя*

*1 пара (08:00-09:25):*
• Алгоритмы и структуры данных (лр 110а-1)

*2 пара (09:35-11:00):*
• Физика (лк 137-4, доц. Тульев В.В.)

*3 пара (11:25-12:50):*
• Компьютерные системы и сети (лр 105-1)

*Вторая половина дня:*
• Свободно""",

        "II": """📅 *ПОНЕДЕЛЬНИК | II неделя*

*1 пара (08:00-09:25):*
• Свободно

*2 пара (09:35-11:00):*
• Физика (лк 137-4, доц. Тульев В.В.)

*3 пара (11:25-12:50):*
• Свободно

*4 пара (13:00-14:25):*
• Свободно"""
    },

    "Вторник": {
        "I": """📅 *ВТОРНИК | I неделя*

*1 пара (08:00-09:25):*
• Математический анализ (пз 110-4)

*2 пара (09:35-11:00):*
• Основы алгоритмизации и программирования (лк 100-3а, доц. Белодед Н.И.)

*3 пара (11:25-12:50):*
• Физика (лк 114-4, доц. Тульев В.В.)

*4 пара (13:00-14:25):*
• Немецкий язык (пз 239-2 общ.)""",

        "II": """📅 *ВТОРНИК | II неделя*

*1 пара (08:00-09:25):*
• Математический анализ (пз 110-4)

*2 пара (09:35-11:00):*
• Основы алгоритмизации и программирования (лк 100-3а, доц. Белодед Н.И.)

*3 пара (11:25-12:50):*
• Физика (лк 114-4, доц. Тульев В.В.)

*4 пара (13:00-14:25):*
• Немецкий язык (пз 239-2 общ.)"""
    },

    "Среда": {
        "I": """📅 *СРЕДА | I неделя*

*1 пара (08:00-09:25):*
• Политология (пз 334-4) - с 18.03

*2 пара (09:35-11:00):*
• История мировой культуры (лк 100-3а, доц. Доморад А.А.)
• Политология (лк 137-4, доц. Крючек П.С.)

*3 пара (11:25-12:50):*
• Алгоритмы и структуры данных (лк 440-4, доц. Шиман Д.В.)

*4 пара (13:00-14:25):*
• Физическая культура""",

        "II": """📅 *СРЕДА | II неделя*

*1 пара (08:00-09:25):*
• История мировой культуры (пз 149-4)

*2 пара (09:35-11:00):*
• История мировой культуры (лк 100-3а, доц. Доморад А.А.)
• Политология (лк 137-4, доц. Крючек П.С.)

*3 пара (11:25-12:50):*
• Компьютерные системы и сети (лк 440-4, ст. преп. Королёв А.А.)

*4 пара (13:00-14:25):*
• Физическая культура"""
    },

    "Четверг": {
        "I": """📅 *ЧЕТВЕРГ | I неделя*

*1 пара (08:00-09:25):*
• История белорусской государственности (лк 301-4, доц. Коваль О.В.)

*2 пара (09:35-11:00):*
• Физика (лр 506, 512, 503, 513-1)

*3 пара (11:25-12:50):*
• Физика (лр 506, 512, 503, 513-1)

*4 пара (13:00-14:25):*
• Свободно""",

        "II": """📅 *ЧЕТВЕРГ | II неделя*

*1 пара (08:00-09:25):*
• История белорусской государственности (лк 301-4, доц. Коваль О.В.)

*2 пара (09:35-11:00):*
• Физика (лр 506, 512, 503, 513-1)

*3 пара (11:25-12:50):*
• Физика (лр 506, 512, 503, 513-1)

*4 пара (13:00-14:25):*
• Свободно"""
    },

    "Пятница": {
        "I": """📅 *ПЯТНИЦА | I неделя*

*1 пара (08:00-09:25):*
• Математический анализ (лк 100-3а, ст. преп. Калиновская Е.В.)

*2 пара (09:35-11:00):*
• Конструирование программного обеспечения (лк 132-4, ст. преп. Наркевич А.С.)

*3 пара (11:25-12:50):*
• История белорусской государственности (пз 331-4)

*4 пара (13:00-14:25):*
• История белорусской государственности (пз 331-4)""",

        "II": """📅 *ПЯТНИЦА | II неделя*

*1 пара (08:00-09:25):*
• Математический анализ (лк 100-3а, ст. преп. Калиновская Е.В.)

*2 пара (09:35-11:00):*
• Конструирование программного обеспечения (лк 132-4, ст. преп. Наркевич А.С.)

*3 пара (11:25-12:50):*
• История белорусской государственности (пз 331-4)

*4 пара (13:00-14:25):*
• История белорусской государственности (пз 331-4)"""
    },

    "Суббота": {
        "I": """📅 *СУББОТА | I неделя*

*1 пара (08:00-09:25):*
• Физика (пз 110-4)

*2 пара (09:35-11:00):*
• Физическая культура

*3 пара (11:25-12:50):*
• Английский язык (пз 233-2 общ.)

*4 пара (13:00-14:25):*
• Английский язык (пз 233-2 общ.)""",

        "II": """📅 *СУББОТА | II неделя*

*1 пара (08:00-09:25):*
• Свободно

*2 пара (09:35-11:00):*
• Физическая культура

*3 пара (11:25-12:50):*
• Английский язык (пз 233-2 общ.)

*4 пара (13:00-14:25):*
• Английский язык (пз 233-2 общ.)"""
    }
}


@bot.message_handler(commands=['start'])
def start(message):
    current_week = get_current_week()
    today = datetime.now()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

    # Кнопки дней недели
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    buttons = [types.KeyboardButton(day) for day in days]

    # Располагаем по 2 кнопки в ряд
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.row(buttons[i], buttons[i + 1])
        else:
            markup.row(buttons[i])

    # Дополнительные кнопки
    markup.row(
        types.KeyboardButton('📅 Сегодня'),
        types.KeyboardButton('📆 Завтра')
    )
    markup.row(
        types.KeyboardButton('ℹ️ Какая неделя?'),
        types.KeyboardButton('🔄 Сменить неделю')
    )
    markup.row(types.KeyboardButton('/help'))

    # Приветственное сообщение
    week_num = (today - START_DATE).days // 7 + 1 if today >= START_DATE else 0
    welcome_msg = f"""
🎓 *Расписание БГТУ*
*Семестр начинается:* 09.02.2026
*Текущая неделя:* {current_week} неделя
*С начала семестра:* {week_num} учебная неделя

📅 *{today.strftime('%d.%m.%Y')}* ({['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][today.weekday()]})

Выберите день недели:
"""

    bot.send_message(message.chat.id, welcome_msg,
                     reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📚 *Помощь по боту:*

*Основные команды:*
/start - Главное меню
/today - Расписание на сегодня
/tomorrow - Расписание на завтра
/week - Какая сейчас неделя (I/II)
/help - Эта справка

*Как пользоваться:*
1. Нажмите на кнопку с днем недели
2. Бот покажет расписание для этого дня
3. Используйте inline-кнопки под расписанием для переключения между неделями

*Информация:*
• Бот автоматически определяет I или II неделя
• Даты начала семестра: 09.02.2026
• Если пара не указана - время свободно
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


@bot.message_handler(commands=['today'])
def today_command(message):
    show_day_schedule(message, "today")


@bot.message_handler(commands=['tomorrow'])
def tomorrow_command(message):
    show_day_schedule(message, "tomorrow")


@bot.message_handler(commands=['week'])
def week_command(message):
    current_week = get_current_week()
    today = datetime.now()
    week_num = (today - START_DATE).days // 7 + 1 if today >= START_DATE else 0

    week_info = f"""
📆 *Информация о неделе:*

*Текущая неделя:* {current_week}
*Учебная неделя №:* {week_num}
*Дата:* {today.strftime('%d.%m.%Y')}

*Начало семестра:* 09.02.2026
*Прошло дней:* {(today - START_DATE).days if today >= START_DATE else 0}
"""
    bot.send_message(message.chat.id, week_info, parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == '📅 Сегодня':
        show_day_schedule(message, "today")
    elif message.text == '📆 Завтра':
        show_day_schedule(message, "tomorrow")
    elif message.text == 'ℹ️ Какая неделя?':
        week_command(message)
    elif message.text == '🔄 Сменить неделю':
        show_week_switch_menu(message)
    elif message.text in schedule:
        show_day_with_week_buttons(message, message.text)
    else:
        bot.send_message(message.chat.id,
                         "Пожалуйста, выберите день недели из меню ниже 👇")


def show_day_schedule(message, day_type):
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    today = datetime.now().weekday()

    if day_type == "today":
        if today < 6:
            day_name = days[today]
            prefix = f"📅 *СЕГОДНЯ ({day_name})*"
        else:
            bot.send_message(message.chat.id,
                             "Сегодня воскресенье - выходной день! 🎉\nОтдыхайте и готовьтесь к новой неделе!")
            return
    else:  # tomorrow
        tomorrow = (today + 1) % 7
        if tomorrow < 6:
            day_name = days[tomorrow]
            tomorrow_date = datetime.now() + timedelta(days=1)
            prefix = f"📆 *ЗАВТРА ({day_name}, {tomorrow_date.strftime('%d.%m')})*"
        else:
            bot.send_message(message.chat.id,
                             "Завтра воскресенье - выходной день! 🎉")
            return

    show_day_with_week_buttons(message, day_name, prefix)


def show_day_with_week_buttons(message, day_name, prefix=""):
    current_week = get_current_week()

    if day_name in schedule and current_week in schedule[day_name]:
        response = f"{prefix}\n\n"
        response += schedule[day_name][current_week]

        # Отправляем расписание
        bot.send_message(message.chat.id, response, parse_mode='Markdown')

        # Создаем inline-кнопки
        markup_inline = types.InlineKeyboardMarkup(row_width=2)

        # Определяем какую неделю показывать для переключения
        other_week = "II" if current_week == "I" else "I"

        btn_other_week = types.InlineKeyboardButton(
            f'📖 {other_week} неделя',
            callback_data=f'week_{other_week}_{day_name}'
        )
        btn_current = types.InlineKeyboardButton(
            f'✅ {current_week} неделя',
            callback_data='current'
        )
        btn_today = types.InlineKeyboardButton(
            '📅 Сегодня',
            callback_data='show_today'
        )
        btn_menu = types.InlineKeyboardButton(
            '🏠 Меню',
            callback_data='back_to_menu'
        )

        markup_inline.row(btn_other_week)
        markup_inline.row(btn_today, btn_menu)

        bot.send_message(
            message.chat.id,
            f"*Сейчас отображается {current_week} неделя*",
            reply_markup=markup_inline,
            parse_mode='Markdown'
        )
    else:
        bot.send_message(message.chat.id,
                         f"Расписание на {day_name} не найдено")


def show_week_switch_menu(message):
    current_week = get_current_week()
    other_week = "II" if current_week == "I" else "I"

    markup_inline = types.InlineKeyboardMarkup()

    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    for day in days:
        btn = types.InlineKeyboardButton(
            f'{day} ({other_week} нед.)',
            callback_data=f'week_{other_week}_{day}'
        )
        markup_inline.row(btn)

    btn_back = types.InlineKeyboardButton('🔙 Назад', callback_data='back_to_menu')
    markup_inline.row(btn_back)

    bot.send_message(
        message.chat.id,
        f"*Выберите день для просмотра {other_week} недели:*",
        reply_markup=markup_inline,
        parse_mode='Markdown'
    )


@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    if callback.data.startswith('week_I_'):
        day_name = callback.data.split('_')[2]
        if day_name in schedule and "I" in schedule[day_name]:
            # Редактируем сообщение с расписанием
            try:
                bot.edit_message_text(
                    schedule[day_name]["I"],
                    callback.message.chat.id,
                    callback.message.message_id - 1
                )
                # Обновляем кнопки
                markup_inline = types.InlineKeyboardMarkup(row_width=2)
                btn_other_week = types.InlineKeyboardButton(
                    '📖 II неделя',
                    callback_data=f'week_II_{day_name}'
                )
                btn_current = types.InlineKeyboardButton(
                    '✅ I неделя',
                    callback_data='current'
                )
                btn_today = types.InlineKeyboardButton(
                    '📅 Сегодня',
                    callback_data='show_today'
                )
                btn_menu = types.InlineKeyboardButton(
                    '🏠 Меню',
                    callback_data='back_to_menu'
                )
                markup_inline.row(btn_other_week)
                markup_inline.row(btn_today, btn_menu)

                bot.edit_message_reply_markup(
                    callback.message.chat.id,
                    callback.message.message_id,
                    reply_markup=markup_inline
                )
                bot.answer_callback_query(callback.id, "Показана I неделя")
            except:
                bot.answer_callback_query(callback.id, "Ошибка обновления")

    elif callback.data.startswith('week_II_'):
        day_name = callback.data.split('_')[2]
        if day_name in schedule and "II" in schedule[day_name]:
            try:
                bot.edit_message_text(
                    schedule[day_name]["II"],
                    callback.message.chat.id,
                    callback.message.message_id - 1
                )
                # Обновляем кнопки
                markup_inline = types.InlineKeyboardMarkup(row_width=2)
                btn_other_week = types.InlineKeyboardButton(
                    '📖 I неделя',
                    callback_data=f'week_I_{day_name}'
                )
                btn_current = types.InlineKeyboardButton(
                    '✅ II неделя',
                    callback_data='current'
                )
                btn_today = types.InlineKeyboardButton(
                    '📅 Сегодня',
                    callback_data='show_today'
                )
                btn_menu = types.InlineKeyboardButton(
                    '🏠 Меню',
                    callback_data='back_to_menu'
                )
                markup_inline.row(btn_other_week)
                markup_inline.row(btn_today, btn_menu)

                bot.edit_message_reply_markup(
                    callback.message.chat.id,
                    callback.message.message_id,
                    reply_markup=markup_inline
                )
                bot.answer_callback_query(callback.id, "Показана II неделя")
            except:
                bot.answer_callback_query(callback.id, "Ошибка обновления")

    elif callback.data == 'back_to_menu':
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except:
            pass
        start(callback.message)

    elif callback.data == 'show_today':
        try:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
        except:
            pass
        today_command(callback.message)

    elif callback.data == 'current':
        bot.answer_callback_query(callback.id, "Уже отображается текущая неделя")


# Запуск бота
if __name__ == "__main__":
    print("🤖 Бот с расписанием запущен!")
    print(f"📅 Семестр начинается: {START_DATE.strftime('%d.%m.%Y')}")
    print(f"📆 Текущая неделя: {get_current_week()}")
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Даем Flask время запуститься
    time.sleep(2)

    # Запускаем бота
    run_bot()