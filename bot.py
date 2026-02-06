import telebot
from telebot import types
from datetime import datetime, timedelta
import requests
import os
import time
import threading
from flask import Flask
from collections import OrderedDict

# ================ Flask для Render ================
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/ping')
def ping():
    return "pong", 200

@app.route('/health')
def health():
    return "OK", 200

# ================ НАСТРОЙКИ БОТА ================
BOT_TOKEN = "8036446753:AAHFkS2ntHfOFDIHJvrmEz9CHpeLCAZCJ1M"
bot = telebot.TeleBot(BOT_TOKEN)

# Дата начала весеннего семестра 2025-2026
START_DATE = datetime(2026, 2, 9)

# ================ КРАСИВОЕ ОФОРМЛЕНИЕ ================
# Эмодзи и стили
EMOJIS = {
    "week": "📆",
    "today": "📅",
    "tomorrow": "📆",
    "back": "🔙",
    "home": "🏠",
    "refresh": "🔄",
    "info": "ℹ️",
    "help": "❓",
    "menu": "📋",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "clock": "⏰",
    "bell": "🔔",
    "book": "📚",
    "computer": "💻",
    "math": "🧮",
    "physics": "⚛️",
    "language": "🔤",
    "sport": "⚽",
    "history": "🏛️",
    "free": "🎯",
    "pin": "📍",
    "university": "🎓"
}

# Функция для красивого форматирования
def format_schedule(day_name, week_type, schedule_text):
    """Форматирует расписание с красивым оформлением"""
    # Добавляем заголовок с эмодзи
    header = f"{EMOJIS['week']} *{day_name.upper()} | {week_type} НЕДЕЛЯ*\n"
    header += "═" * 35 + "\n\n"
    
    # Обрабатываем каждую строку расписания
    lines = schedule_text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip():
            # Добавляем эмодзи для пар
            if "пара (" in line:
                line = f"{EMOJIS['clock']} {line}"
            # Добавляем эмодзи для предметов
            elif "•" in line:
                if "Алгоритмы" in line or "программирования" in line:
                    line = line.replace("•", f"{EMOJIS['computer']}")
                elif "Физика" in line:
                    line = line.replace("•", f"{EMOJIS['physics']}")
                elif "Математический" in line:
                    line = line.replace("•", f"{EMOJIS['math']}")
                elif "Немецкий" in line or "Английский" in line:
                    line = line.replace("•", f"{EMOJIS['language']}")
                elif "История" in line or "Политология" in line:
                    line = line.replace("•", f"{EMOJIS['history']}")
                elif "Физическая" in line:
                    line = line.replace("•", f"{EMOJIS['sport']}")
                elif "Свободно" in line:
                    line = line.replace("• Свободно", f"{EMOJIS['free']} *СВОБОДНО*")
                else:
                    line = line.replace("•", f"{EMOJIS['book']}")
            formatted_lines.append(line)
    
    return header + '\n'.join(formatted_lines)

# ================ РАСПИСАНИЕ ================
schedule = OrderedDict([
    ("Понедельник", {
        "I": """*1 пара (08:00-09:25):*
• Алгоритмы и структуры данных (лр 110а-1)

*2 пара (09:35-11:00):*
• Физика (лк 137-4, доц. Тульев В.В.)

*3 пара (11:25-12:50):*
• Компьютерные системы и сети (лр 105-1)

*Вторая половина дня:*
• Свободно""",

        "II": """*1 пара (08:00-09:25):*
• Свободно

*2 пара (09:35-11:00):*
• Физика (лк 137-4, доц. Тульев В.В.)

*3 пара (11:25-12:50):*
• Свободно

*4 пара (13:00-14:25):*
• Свободно"""
    }),

    ("Вторник", {
        "I": """*1 пара (08:00-09:25):*
• Математический анализ (пз 110-4)

*2 пара (09:35-11:00):*
• Основы алгоритмизации и программирования (лк 100-3а, доц. Белодед Н.И.)

*3 пара (11:25-12:50):*
• Физика (лк 114-4, доц. Тульев В.В.)

*4 пара (13:00-14:25):*
• Немецкий язык (пз 239-2 общ.)""",

        "II": """*1 пара (08:00-09:25):*
• Математический анализ (пз 110-4)

*2 пара (09:35-11:00):*
• Основы алгоритмизации и программирования (лк 100-3а, доц. Белодед Н.И.)

*3 пара (11:25-12:50):*
• Физика (лк 114-4, доц. Тульев В.В.)

*4 пара (13:00-14:25):*
• Немецкий язык (пз 239-2 общ.)"""
    }),

    ("Среда", {
        "I": """*1 пара (08:00-09:25):*
• Политология (пз 334-4) - с 18.03

*2 пара (09:35-11:00):*
• История мировой культуры (лк 100-3а, доц. Доморад А.А.)
• Политология (лк 137-4, доц. Крючек П.С.)

*3 пара (11:25-12:50):*
• Алгоритмы и структуры данных (лк 440-4, доц. Шиман Д.В.)

*4 пара (13:00-14:25):*
• Физическая культура""",

        "II": """*1 пара (08:00-09:25):*
• История мировой культуры (пз 149-4)

*2 пара (09:35-11:00):*
• История мировой культуры (лк 100-3а, доц. Доморад А.А.)
• Политология (лк 137-4, доц. Крючек П.С.)

*3 пара (11:25-12:50):*
• Компьютерные системы и сети (лк 440-4, ст. преп. Королёв А.А.)

*4 пара (13:00-14:25):*
• Физическая культура"""
    }),

    ("Четверг", {
        "I": """*1 пара (08:00-09:25):*
• История белорусской государственности (лк 301-4, доц. Коваль О.В.)

*2 пара (09:35-11:00):*
• Физика (лр 506, 512, 503, 513-1)

*3 пара (11:25-12:50):*
• Физика (лр 506, 512, 503, 513-1)

*4 пара (13:00-14:25):*
• Свободно""",

        "II": """*1 пара (08:00-09:25):*
• История белорусской государственности (лк 301-4, доц. Коваль О.В.)

*2 пара (09:35-11:00):*
• Физика (лр 506, 512, 503, 513-1)

*3 пара (11:25-12:50):*
• Физика (лр 506, 512, 503, 513-1)

*4 пара (13:00-14:25):*
• Свободно"""
    }),

    ("Пятница", {
        "I": """*1 пара (08:00-09:25):*
• Математический анализ (лк 100-3а, ст. преп. Калиновская Е.В.)

*2 пара (09:35-11:00):*
• Конструирование программного обеспечения (лк 132-4, ст. преп. Наркевич А.С.)

*3 пара (11:25-12:50):*
• История белорусской государственности (пз 331-4)

*4 пара (13:00-14:25):*
• История белорусской государственности (пз 331-4)""",

        "II": """*1 пара (08:00-09:25):*
• Математический анализ (лк 100-3а, ст. преп. Калиновская Е.В.)

*2 пара (09:35-11:00):*
• Конструирование программного обеспечения (лк 132-4, ст. преп. Наркевич А.С.)

*3 пара (11:25-12:50):*
• История белорусской государственности (пз 331-4)

*4 пара (13:00-14:25):*
• История белорусской государственности (пз 331-4)"""
    }),

    ("Суббота", {
        "I": """*1 пара (08:00-09:25):*
• Физика (пз 110-4)

*2 пара (09:35-11:00):*
• Физическая культура

*3 пара (11:25-12:50):*
• Английский язык (пз 233-2 общ.)

*4 пара (13:00-14:25):*
• Английский язык (пз 233-2 общ.)""",

        "II": """*1 пара (08:00-09:25):*
• Свободно

*2 пара (09:35-11:00):*
• Физическая культура

*3 пара (11:25-12:50):*
• Английский язык (пз 233-2 общ.)

*4 пара (13:00-14:25):*
• Английский язык (пз 233-2 общ.)"""
    })
])

# ================ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ================
def get_current_week():
    """Определяет текущую неделю (I или II)"""
    today = datetime.now()
    if today < START_DATE:
        return "I"
    
    days_diff = (today - START_DATE).days
    week_num = (days_diff // 7) % 2
    return "I" if week_num == 0 else "II"

def create_main_menu():
    """Создает главное меню с красивыми кнопками"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Дни недели с эмодзи
    days_buttons = [
        types.KeyboardButton(f'📅 Понедельник'),
        types.KeyboardButton(f'📅 Вторник'),
        types.KeyboardButton(f'📅 Среда'),
        types.KeyboardButton(f'📅 Четверг'),
        types.KeyboardButton(f'📅 Пятница'),
        types.KeyboardButton(f'📅 Суббота')
    ]
    
    # Располагаем дни недели
    for i in range(0, len(days_buttons), 2):
        if i + 1 < len(days_buttons):
            markup.row(days_buttons[i], days_buttons[i + 1])
        else:
            markup.row(days_buttons[i])
    
    # Основные функции
    markup.row(
        types.KeyboardButton(f'{EMOJIS["today"]} Сегодня'),
        types.KeyboardButton(f'{EMOJIS["tomorrow"]} Завтра')
    )
    
    # Дополнительные функции
    markup.row(
        types.KeyboardButton(f'{EMOJIS["info"]} Какая неделя?'),
        types.KeyboardButton(f'{EMOJIS["refresh"]} Сменить неделю')
    )
    
    markup.row(types.KeyboardButton(f'{EMOJIS["help"]} Помощь'))
    
    return markup

def create_week_switch_menu():
    """Создает меню для смены недели"""
    current_week = get_current_week()
    other_week = "II" if current_week == "I" else "I"
    
    markup_inline = types.InlineKeyboardMarkup(row_width=1)
    
    # Создаем кнопки для каждого дня с другой неделей
    days = list(schedule.keys())
    for day in days:
        btn = types.InlineKeyboardButton(
            f'📅 {day} ({other_week} неделя)',
            callback_data=f'week_switch_{other_week}_{day}'
        )
        markup_inline.add(btn)
    
    # Кнопка возврата
    markup_inline.add(types.InlineKeyboardButton(
        f'{EMOJIS["back"]} Назад',
        callback_data='back_to_menu'
    ))
    
    return markup_inline, other_week

def create_schedule_buttons(day_name, current_week):
    """Создает inline-кнопки под расписанием"""
    markup_inline = types.InlineKeyboardMarkup(row_width=2)
    
    other_week = "II" if current_week == "I" else "I"
    
    # Основные кнопки
    btn_other_week = types.InlineKeyboardButton(
        f'{EMOJIS["refresh"]} {other_week} неделя',
        callback_data=f'schedule_{other_week}_{day_name}'
    )
    
    btn_current = types.InlineKeyboardButton(
        f'{EMOJIS["success"]} {current_week} неделя',
        callback_data='current_week'
    )
    
    btn_today = types.InlineKeyboardButton(
        f'{EMOJIS["today"]} Сегодня',
        callback_data='show_today'
    )
    
    btn_tomorrow = types.InlineKeyboardButton(
        f'{EMOJIS["tomorrow"]} Завтра',
        callback_data='show_tomorrow'
    )
    
    btn_menu = types.InlineKeyboardButton(
        f'{EMOJIS["home"]} Меню',
        callback_data='back_to_menu'
    )
    
    # Располагаем кнопки
    markup_inline.row(btn_other_week, btn_current)
    markup_inline.row(btn_today, btn_tomorrow)
    markup_inline.row(btn_menu)
    
    return markup_inline

# ================ ОБРАБОТЧИКИ КОМАНД ================
@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start"""
    current_week = get_current_week()
    today = datetime.now()
    
    # Красивое приветственное сообщение
    week_num = (today - START_DATE).days // 7 + 1 if today >= START_DATE else 0
    
    welcome_msg = f"""
{EMOJIS["university"]} *БОТ-РАСПИСАНИЕ БГТУ*
══════════════════════════════

{EMOJIS["pin"]} *Начало семестра:* 09.02.2026
{EMOJIS["week"]} *Текущая неделя:* {current_week}
{EMOJIS["calendar"]} *Учебная неделя №:* {week_num}

{EMOJIS["today"]} *{today.strftime('%d.%m.%Y')}* 
📌 *{['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][today.weekday()]}*

══════════════════════════════
*Выберите день недели:*
"""
    
    bot.send_message(
        message.chat.id, 
        welcome_msg,
        reply_markup=create_main_menu(),
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    """Обработчик команды /help"""
    help_text = f"""
{EMOJIS["help"]} *ПОМОЩЬ ПО БОТУ*
══════════════════════════════

{EMOJIS["book"]} *Основные команды:*
/start - Главное меню
/today - Расписание на сегодня
/tomorrow - Расписание на завтра
/week - Какая сейчас неделя
/help - Эта справка

{EMOJIS["bell"]} *Как пользоваться:*
1. Выберите день недели из меню
2. Используйте кнопки под расписанием для переключения недель
3. Для быстрого доступа используйте кнопки "Сегодня" и "Завтра"

{EMOJIS["info"]} *Особенности:*
• Бот автоматически определяет I/II неделю
• Даты начала семестра: 09.02.2026
• Если пара не указана - время свободно

{EMOJIS["pin"]} *Поддержка:*
При проблемах работы бота пишите разработчику
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['today'])
def today_command(message):
    """Показать расписание на сегодня"""
    show_day_schedule(message, "today")

@bot.message_handler(commands=['tomorrow'])
def tomorrow_command(message):
    """Показать расписание на завтра"""
    show_day_schedule(message, "tomorrow")

@bot.message_handler(commands=['week'])
def week_command(message):
    """Показать информацию о неделе"""
    current_week = get_current_week()
    today = datetime.now()
    week_num = (today - START_DATE).days // 7 + 1 if today >= START_DATE else 0
    
    week_info = f"""
{EMOJIS["week"]} *ИНФОРМАЦИЯ О НЕДЕЛЕ*
══════════════════════════════

{EMOJIS["success"]} *Текущая неделя:* {current_week}
{EMOJIS["calendar"]} *Учебная неделя №:* {week_num}
{EMOJIS["today"]} *Дата:* {today.strftime('%d.%m.%Y')}

{EMOJIS["pin"]} *Начало семестра:* 09.02.2026
{EMOJIS["clock"]} *Прошло дней:* {(today - START_DATE).days if today >= START_DATE else 0}

{EMOJIS["info"]} *Следующая неделя:* {"I" if current_week == "II" else "II"}
"""
    bot.send_message(message.chat.id, week_info, parse_mode='Markdown')

# ================ ОБРАБОТЧИКИ ТЕКСТОВЫХ СООБЩЕНИЙ ================
@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Обработка текстовых сообщений"""
    text = message.text
    
    if 'Понедельник' in text:
        show_day_with_buttons(message, 'Понедельник')
    elif 'Вторник' in text:
        show_day_with_buttons(message, 'Вторник')
    elif 'Среда' in text:
        show_day_with_buttons(message, 'Среда')
    elif 'Четверг' in text:
        show_day_with_buttons(message, 'Четверг')
    elif 'Пятница' in text:
        show_day_with_buttons(message, 'Пятница')
    elif 'Суббота' in text:
        show_day_with_buttons(message, 'Суббота')
    elif f'{EMOJIS["today"]} Сегодня' == text:
        show_day_schedule(message, "today")
    elif f'{EMOJIS["tomorrow"]} Завтра' == text:
        show_day_schedule(message, "tomorrow")
    elif f'{EMOJIS["info"]} Какая неделя?' == text:
        week_command(message)
    elif f'{EMOJIS["refresh"]} Сменить неделю' == text:
        show_week_switch_menu_handler(message)
    elif f'{EMOJIS["help"]} Помощь' in text:
        help_command(message)
    else:
        bot.send_message(
            message.chat.id,
            f"{EMOJIS['warning']} Пожалуйста, используйте меню ниже 👇",
            reply_markup=create_main_menu()
        )

# ================ ФУНКЦИИ ПОКАЗА РАСПИСАНИЯ ================
def show_day_schedule(message, day_type):
    """Показывает расписание на сегодня или завтра"""
    days = list(schedule.keys())
    today = datetime.now().weekday()
    
    if day_type == "today":
        if today < 6:
            day_name = days[today]
            date_prefix = f"{EMOJIS['today']} *СЕГОДНЯ ({day_name})*"
        else:
            bot.send_message(
                message.chat.id,
                f"{EMOJIS['free']} *ВОСКРЕСЕНЬЕ - ВЫХОДНОЙ!*\n\nОтдыхайте и готовьтесь к новой неделе! {EMOJIS['success']}"
            )
            return
    else:  # tomorrow
        tomorrow = (today + 1) % 7
        if tomorrow < 6:
            day_name = days[tomorrow]
            tomorrow_date = datetime.now() + timedelta(days=1)
            date_prefix = f"{EMOJIS['tomorrow']} *ЗАВТРА ({day_name}, {tomorrow_date.strftime('%d.%m')})*"
        else:
            bot.send_message(
                message.chat.id,
                f"{EMOJIS['free']} *ЗАВТРА ВОСКРЕСЕНЬЕ - ВЫХОДНОЙ!*\n\nОтдыхайте! {EMOJIS['success']}"
            )
            return
    
    show_day_with_buttons(message, day_name, date_prefix)

def show_day_with_buttons(message, day_name, prefix=""):
    """Показывает расписание с кнопками"""
    current_week = get_current_week()
    
    if day_name in schedule and current_week in schedule[day_name]:
        # Форматируем расписание
        formatted_schedule = format_schedule(
            day_name, 
            current_week, 
            schedule[day_name][current_week]
        )
        
        # Добавляем префикс если есть
        if prefix:
            response = f"{prefix}\n══════════════════════════════\n{formatted_schedule}"
        else:
            response = formatted_schedule
        
        # Отправляем расписание
        msg = bot.send_message(
            message.chat.id,
            response,
            parse_mode='Markdown'
        )
        
        # Отправляем кнопки управления
        bot.send_message(
            message.chat.id,
            f"{EMOJIS['info']} *Управление расписанием:*",
            reply_markup=create_schedule_buttons(day_name, current_week),
            parse_mode='Markdown'
        )
    else:
        bot.send_message(
            message.chat.id,
            f"{EMOJIS['error']} Расписание на {day_name} не найдено"
        )

def show_week_switch_menu_handler(message):
    """Обработчик кнопки 'Сменить неделю'"""
    markup_inline, other_week = create_week_switch_menu()
    
    bot.send_message(
        message.chat.id,
        f"{EMOJIS['refresh']} *ВЫБЕРИТЕ ДЕНЬ ДЛЯ ПРОСМОТРА {other_week} НЕДЕЛИ:*",
        reply_markup=markup_inline,
        parse_mode='Markdown'
    )

# ================ ОБРАБОТЧИКИ CALLBACK ================
@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    """Обработчик inline-кнопок"""
    data = callback.data
    
    try:
        if data.startswith('schedule_') or data.startswith('week_switch_'):
            # Разбираем данные
            parts = data.split('_')
            week_type = parts[1]  # I или II
            day_name = '_'.join(parts[2:])  # День недели
            
            if day_name in schedule and week_type in schedule[day_name]:
                # Форматируем расписание
                formatted_schedule = format_schedule(
                    day_name,
                    week_type,
                    schedule[day_name][week_type]
                )
                
                # Определяем заголовок
                if data.startswith('week_switch_'):
                    header = f"{EMOJIS['refresh']} *{day_name.upper()} | {week_type} НЕДЕЛЯ*"
                else:
                    current_day = datetime.now().strftime('%A')
                    if day_name.lower() == current_day.lower():
                        header = f"{EMOJIS['today']} *{day_name.upper()} | {week_type} НЕДЕЛЯ*"
                    else:
                        header = f"{EMOJIS['week']} *{day_name.upper()} | {week_type} НЕДЕЛЯ*"
                
                response = f"{header}\n══════════════════════════════\n{formatted_schedule}"
                
                # Обновляем сообщение с расписанием
                try:
                    bot.edit_message_text(
                        response,
                        callback.message.chat.id,
                        callback.message.message_id - 1,
                        parse_mode='Markdown'
                    )
                    
                    # Обновляем кнопки
                    new_markup = create_schedule_buttons(day_name, week_type)
                    bot.edit_message_reply_markup(
                        callback.message.chat.id,
                        callback.message.message_id,
                        reply_markup=new_markup
                    )
                    
                    bot.answer_callback_query(
                        callback.id,
                        f"Показана {week_type} неделя"
                    )
                except Exception as e:
                    # Если не удалось отредактировать, отправляем новое сообщение
                    bot.send_message(
                        callback.message.chat.id,
                        response,
                        parse_mode='Markdown'
                    )
                    bot.send_message(
                        callback.message.chat.id,
                        f"{EMOJIS['info']} *Управление расписанием:*",
                        reply_markup=create_schedule_buttons(day_name, week_type),
                        parse_mode='Markdown'
                    )
                    bot.answer_callback_query(callback.id)
            
        elif data == 'back_to_menu':
            # Удаляем сообщение с кнопками
            try:
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
            except:
                pass
            
            # Показываем главное меню
            start(callback.message)
            
        elif data == 'show_today':
            # Удаляем сообщение с кнопками
            try:
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
            except:
                pass
            
            # Показываем сегодня
            today_command(callback.message)
            
        elif data == 'show_tomorrow':
            # Удаляем сообщение с кнопками
            try:
                bot.delete_message(callback.message.chat.id, callback.message.message_id)
            except:
                pass
            
            # Показываем завтра
            tomorrow_command(callback.message)
            
        elif data == 'current_week':
            bot.answer_callback_query(
                callback.id,
                f"{EMOJIS['success']} Уже отображается текущая неделя"
            )
            
    except Exception as e:
        bot.answer_callback_query(
            callback.id,
            f"{EMOJIS['error']} Ошибка обновления"
        )

# ================ ФУНКЦИИ ДЛЯ RENDER ================
def run_flask_server():
    """Запуск Flask сервера для Render"""
    try:
        port = int(os.environ.get('PORT', 10000))
        print(f"{EMOJIS['success']} Flask сервер запущен на порту: {port}")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка Flask: {e}")

def keep_alive():
    """Периодически пингует бота, чтобы он не засыпал"""
    time.sleep(40)
    
    # ЗАМЕНИТЕ НА ВАШ НАСТОЯЩИЙ URL
    YOUR_RENDER_URL = "https://schedule-bot-x6xr.onrender.com"
    
    while True:
        try:
            response = requests.get(f"{YOUR_RENDER_URL}/ping", timeout=10)
            print(f"{EMOJIS['success']} Keep-alive ping: {response.status_code}")
        except Exception as e:
            print(f"{EMOJIS['warning']} Keep-alive ошибка: {e}")
        
        time.sleep(480)

def run_telegram_bot():
    """Запуск Telegram бота"""
    print(f"{EMOJIS['university']} Telegram бот запущен!")
    print(f"{EMOJIS['pin']} Начало семестра: {START_DATE.strftime('%d.%m.%Y')}")
    print(f"{EMOJIS['week']} Текущая неделя: {get_current_week()}")
    
    try:
        bot.polling(none_stop=True, interval=1, timeout=60)
    except Exception as e:
        print(f"{EMOJIS['error']} Ошибка бота: {e}")
        time.sleep(5)
        run_telegram_bot()

# ================ ЗАПУСК ПРИЛОЖЕНИЯ ================
if __name__ == "__main__":
    print(f"{EMOJIS['university']} ===== ЗАПУСК СИСТЕМЫ =====")
    
    # Запуск keep-alive в отдельном потоке
    print(f"1. {EMOJIS['clock']} Запуск keep-alive...")
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
    
    # Запуск Flask сервера
    print(f"2. {EMOJIS['success']} Запуск Flask сервера...")
    flask_thread = threading.Thread(target=run_flask_server)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Ожидание запуска
    print(f"3. {EMOJIS['clock']} Ожидание запуска компонентов...")
    time.sleep(5)
    
    # Запуск Telegram бота
    print(f"4. {EMOJIS['university']} Запуск Telegram бота...")
    run_telegram_bot()
    
    print(f"{EMOJIS['success']} Все системы запущены!")
