import os
import time
import json
import atexit
import threading
import requests
from datetime import datetime, timedelta
from flask import Flask
import telebot
from telebot import types

# ================ КОНФИГУРАЦИЯ ================

# Лучше задавать токен через переменные окружения в Render
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8036446753:AAHFkS2ntHfOFDIHJvrmEz9CHpeLCAZCJ1M")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)
DATA_FILE = "user_data.json"
START_DATE = datetime(2026, 2, 9)

# Данные пользователей в памяти
user_data = {
    'weeks': {},       # user_id (str) -> str ("I", "II", "auto")
    'subgroups': {}    # user_id (str) -> int (1 или 2)
}

# ================ РАСПИСАНИЕ ================
# (Твой оригинальный словарь schedule оставлен без изменений)
schedule = {
    1: {
        "Понедельник": {
            "I": "📅 *ПОНЕДЕЛЬНИК | I неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Алгоритмы и структуры данных (лр 110а-1)\n\n*2 пара (09:35-11:00):*\n• Физика (лк 137-4, доц. Тульев В.В.)\n\n*3 пара (11:25-12:50):*\n• Компьютерные системы и сети (лр 105-1)\n\n*Вторая половина дня:*\n• Свободно",
            "II": "📅 *ПОНЕДЕЛЬНИК | II неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Свободно\n\n*2 пара (09:35-11:00):*\n• Великая Отечественная война советского народа (лк 222-4, доц. Острога В.М)\n\n*3 пара (11:25-12:50):*\n• Свободно\n\n*4 пара (13:00-14:25):*\n• Свободно"
        },
        "Вторник": {
            "I": "📅 *ВТОРНИК | I неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Математический анализ (пз 110-4)\n\n*2 пара (09:35-11:00):*\n• Основы алгоритмизации и программирования (лк 100-3а, доц. Белодед Н.И.)\n\n*3 пара (11:25-12:50):*\n• Физика (лк 114-4, доц. Тульев В.В.)\n\n*4 пара (13:00-14:25):*\n• Немецкий язык (пз 239-2 общ.)",
            "II": "📅 *ВТОРНИК | II неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Математический анализ (пз 110-4)\n\n*2 пара (09:35-11:00):*\n• Основы алгоритмизации и программирования (лк 100-3а, доц. Белодед Н.И.)\n\n*3 пара (11:25-12:50):*\n• Физика (лк 114-4, доц. Тульев В.В.)\n\n*4 пара (13:00-14:25):*\n• Немецкий язык (пз 239-2 общ.)"
        },
        "Среда": {
            "I": "📅 *СРЕДА | I неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Политология (пз 334-4) - с 18.03\n\n*2 пара (09:35-11:00):*\n• История мировой культуры (лк 100-3а, доц. Доморад А.А.)\n• Политология (лк 137-4, доц. Крючек П.С.)\n\n*3 пара (11:25-12:50):*\n• Алгоритмы и структуры данных (лк 440-4, доц. Шиман Д.В.)\n\n*4 пара (13:00-14:25):*\n• Физическая культура",
            "II": "📅 *СРЕДА | II неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• История мировой культуры (пз 149-4)\n\n*2 пара (09:35-11:00):*\n• История мировой культуры (лк 100-3а, доц. Доморад А.А.)\n• Политология (лк 137-4, доц. Крючек П.С.)\n\n*3 пара (11:25-12:50):*\n• Компьютерные системы и сети (лк 440-4, ст. преп. Королёв А.А.)\n\n*4 пара (13:00-14:25):*\n• Физическая культура"
        },
        "Четверг": {
            "I": "📅 *ЧЕТВЕРГ | I неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Свободно\n\n*2 пара (09:35-11:00):*\n• История белорусской государственности (лк 301-4, доц. Коваль О.В.)\n\n*3 пара (11:25-12:50):*\n• Физика (лр 506, 512, 503, 513-1)\n\n*4 пара (13:00-14:25):*\n• Основы алгоритмизации и программирования (лр 322-1)",
            "II": "📅 *ЧЕТВЕРГ | II неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Свободно\n\n*2 пара (09:35-11:00):*\n• История белорусской государственности (лк 301-4, доц. Коваль О.В.)\n\n*3 пара (11:25-12:50):*\n• Физика (лр 506, 512, 503, 513-1)\n\n*4 пара (13:00-14:25):*\n• Основы алгоритмизации и программирования (лр 322-1)"
        },
        "Пятница": {
            "I": "📅 *ПЯТНИЦА | I неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Математический анализ (лк 100-3а, ст. преп. Калиновская Е.В.)\n\n*2 пара (09:35-11:00):*\n• Конструирование программного обеспечения (лк 132-4, ст. преп. Наркевич А.С.)\n\n*3 пара (11:25-12:50):*\n• История белорусской государственности (пз 331-4)\n\n*4 пара (13:00-14:25):*\n• Конструирование программного обеспечения (лр 413-)",
            "II": "📅 *ПЯТНИЦА | II неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Математический анализ (лк 100-3а, ст. преп. Калиновская Е.В.)\n\n*2 пара (09:35-11:00):*\n• Конструирование программного обеспечения (лк 132-4, ст. преп. Наркевич А.С.)\n\n*3 пара (11:25-12:50):*\n• История белорусской государственности (пз 331-4)\n\n*4 пара (13:00-14:25):*\n• Конструирование программного обеспечения (лр 413-)"
        },
        "Суббота": {
            "I": "📅 *СУББОТА | I неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Физика (пз 110-4)\n\n*2 пара (09:35-11:00):*\n• Физическая культура\n\n*3 пара (11:25-12:50):*\n• Английский язык (пз 233-2 общ.)\n\n*4 пара (13:00-14:25):*\n• Английский язык (пз 233-2 общ.)",
            "II": "📅 *СУББОТА | II неделя | Подгруппа 1*\n\n*1 пара (08:00-09:25):*\n• Свободно\n\n*2 пара (09:35-11:00):*\n• Физическая культура\n\n*3 пара (11:25-12:50):*\n• Английский язык (пз 233-2 общ.)\n\n*4 пара (13:00-14:25):*\n• Английский язык (пз 233-2 общ.)"
        }
    },
    2: {
        "Понедельник": {
            "I": "📅 *ПОНЕДЕЛЬНИК | I неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Свободно\n\n*2 пара (09:35-11:00):*\n• Физика (лк 137-4, доц. Тульев В.В.)\n\n*3 пара (11:25-12:50):*\n• Английский язык (пз 233-2 общ.)\n\n*4 пара (13:00-14:25):*\n• Английский язык (пз 233-2 общ.)",
            "II": "📅 *ПОНЕДЕЛЬНИК | II неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Алгоритмы и структуры данных (лр 110а-1)\n\n*2 пара (09:35-11:00):*\n• Великая Отечественная война советского народа (лк 222-4, доц. Острога В.М)\n\n*3 пара (11:25-12:50):*\n• Английский язык (пз 233-2 общ.)\n\n*4 пара (13:00-14:25):*\n• Английский язык (пз 233-2 общ.)"
        },
        "Вторник": {
            "I": "📅 *ВТОРНИК | I неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Математический анализ (пз 110-4)\n\n*2 пара (09:35-11:00):*\n• Основы алгоритмизации и программирования (лк 100-3а, доц. Белодед Н.И.)\n\n*3 пара (11:25-12:50):*\n• Физика (лк 114-4, доц. Тульев В.В.)\n\n*4 пара (13:00-14:25):*\n• Немецкий язык (пз 239-2 общ.)",
            "II": "📅 *ВТОРНИК | II неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Математический анализ (пз 110-4)\n\n*2 пара (09:35-11:00):*\n• Основы алгоритмизации и программирования (лк 100-3а, доц. Белодед Н.И.)\n\n*3 пара (11:25-12:50):*\n• Физика (лк 114-4, доц. Тульев В.В.)\n\n*4 пара (13:00-14:25):*\n• Немецкий язык (пз 239-2 общ.)"
        },
        "Среда": {
            "I": "📅 *СРЕДА | I неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Политология (пз 334-4) - с 18.03\n\n*2 пара (09:35-11:00):*\n• История мировой культуры (лк 100-3а, доц. Доморад А.А.)\n• Политология (лк 137-4, доц. Крючек П.С.)\n\n*3 пара (11:25-12:50):*\n• Алгоритмы и структуры данных (лк 440-4, доц. Шиман Д.В.)\n\n*4 пара (13:00-14:25):*\n• Физическая культура",
            "II": "📅 *СРЕДА | II неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• История мировой культуры (пз 149-4)\n\n*2 пара (09:35-11:00):*\n• История мировой культуры (лк 100-3а, доц. Доморад А.А.)\n• Политология (лк 137-4, доц. Крючек П.С.)\n\n*3 пара (11:25-12:50):*\n• Компьютерные системы и сети (лк 440-4, ст. преп. Королёв А.А.)\n\n*4 пара (13:00-14:25):*\n• Физическая культура"
        },
        "Четверг": {
            "I": "📅 *ЧЕТВЕРГ | I неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Конструирование программного обеспечения (лр 209-1)\n\n*2 пара (09:35-11:00):*\n• История белорусской государственности (лк 301-4, доц. Коваль О.В.)\n\n*3 пара (11:25-12:50):*\n• Основы алгоритмизации и программирования (лр 322-1)\n\n*4 пара (13:00-14:25):*\n• Физика (лр 506, 512, 503, 513-1)",
            "II": "📅 *ЧЕТВЕРГ | II неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Конструирование программного обеспечения (лр 209-1)\n\n*2 пара (09:35-11:00):*\n• История белорусской государственности (лк 301-4, доц. Коваль О.В.)\n\n*3 пара (11:25-12:50):*\n• Основы алгоритмизации и программирования (лр 322-1)\n\n*4 пара (13:00-14:25):*\n• Физика (лр 506, 512, 503, 513-1)"
        },
        "Пятница": {
            "I": "📅 *ПЯТНИЦА | I неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Математический анализ (лк 100-3а, ст. преп. Калиновская Е.В.)\n\n*2 пара (09:35-11:00):*\n• Конструирование программного обеспечения (лк 132-4, ст. преп. Наркевич А.С.)\n\n*3 пара (11:25-12:50):*\n• История белорусской государственности (пз 331-4)\n\n*4 пара (13:00-14:25):*\n• Свободно",
            "II": "📅 *ПЯТНИЦА | II неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Математический анализ (лк 100-3а, ст. преп. Калиновская Е.В.)\n\n*2 пара (09:35-11:00):*\n• Конструирование программного обеспечения (лк 132-4, ст. преп. Наркевич А.С.)\n\n*3 пара (11:25-12:50):*\n• История белорусской государственности (пз 331-4)\n\n*4 пара (13:00-14:25):*\n• Свободно"
        },
        "Суббота": {
            "I": "📅 *СУББОТА | I неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Физика (пз 110-4)\n\n*2 пара (09:35-11:00):*\n• Физическая культура\n\n*3 пара (11:25-12:50):*\n• Свободно\n\n*4 пара (13:00-14:25):*\n• Свободно",
            "II": "📅 *СУББОТА | II неделя | Подгруппа 2*\n\n*1 пара (08:00-09:25):*\n• Свободно\n\n*2 пара (09:35-11:00):*\n• Физическая культура\n\n*3 пара (11:25-12:50):*\n• Компьютерные системы и сети (лр 105-1)\n\n*4 пара (13:00-14:25):*\n• Свободно"
        }
    }
}

# ================ РАБОТА С ДАННЫМИ ================

def save_data():
    """Сохраняет данные в JSON файл (быстрее и безопаснее Pickle)"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

def load_data():
    """Загружает данные из JSON"""
    global user_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        user_data = {'weeks': {}, 'subgroups': {}}
        save_data()

load_data()
atexit.register(save_data)

# ================ ЛОГИКА ================

def get_current_week():
    today = datetime.now()
    if today.date() <= START_DATE.date():
        return "II"
    days_diff = (today - START_DATE).days
    return "II" if (days_diff // 7) % 2 == 0 else "I"

def get_user_week(user_id):
    uid_str = str(user_id)
    pref = user_data['weeks'].get(uid_str, "auto")
    return get_current_week() if pref == "auto" else pref

def get_user_subgroup(user_id):
    return user_data['subgroups'].get(str(user_id), 1)

# ================ ГЕНЕРАТОРЫ UI ================

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    markup.add(*[types.KeyboardButton(day) for day in days])
    markup.add(types.KeyboardButton('📅 Сегодня'), types.KeyboardButton('📆 Завтра'))
    markup.add(types.KeyboardButton('ℹ️ Какая неделя?'), types.KeyboardButton('🔄 Сменить неделю'))
    markup.add(types.KeyboardButton('👥 Сменить подгруппу'), types.KeyboardButton('/help'))
    return markup

def get_inline_schedule_keyboard(day_name, current_view_week):
    """Единая функция для генерации инлайн-кнопок под расписанием"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    other_week = "II" if current_view_week == "I" else "I"
    
    markup.add(
        types.InlineKeyboardButton(f'🔄 Показать {other_week} неделю', callback_data=f'view_{other_week}_{day_name}'),
        types.InlineKeyboardButton(f'⚙️ Сменить на {other_week}', callback_data=f'set_week_{other_week}')
    )
    markup.add(
        types.InlineKeyboardButton('📅 Сегодня', callback_data='show_today'),
        types.InlineKeyboardButton('🤖 Авто', callback_data='set_week_auto'),
        types.InlineKeyboardButton('🏠 Меню', callback_data='back_to_menu')
    )
    return markup

# ================ ОБРАБОТЧИКИ КОМАНД ================

@bot.message_handler(commands=['start', 'help', 'today', 'tomorrow', 'week', 'switch_week', 'auto_week', 'change_subgroup'])
def handle_commands(message):
    cmd = message.text.split()[0].replace('/', '')
    user_id = message.chat.id
    
    if cmd not in ['start', 'help'] and str(user_id) not in user_data['subgroups']:
        show_subgroup_selection(message)
        return

    if cmd == 'start':
        if str(user_id) not in user_data['subgroups']:
            show_subgroup_selection(message)
            return
            
        today = datetime.now()
        week_status = "Автоматический режим" if user_data['weeks'].get(str(user_id), 'auto') == "auto" else f"Ручной режим: {get_user_week(user_id)} неделя"
        week_num = max(0, (today - START_DATE).days // 7 + 1)
        
        msg = (f"🎓 *Расписание БГТУ*\n*Семестр начинается:* {START_DATE.strftime('%d.%m.%Y')}\n"
               f"*Текущая неделя:* {get_current_week()} неделя\n*Ваша неделя:* {get_user_week(user_id)} неделя\n"
               f"*Ваша подгруппа:* {get_user_subgroup(user_id)}\n*Режим:* {week_status}\n"
               f"*С начала семестра:* {week_num} учебная неделя\n\n"
               f"📅 *{today.strftime('%d.%m.%Y')}* ({['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][today.weekday()]})\n"
               "Выберите день недели:")
        bot.send_message(message.chat.id, msg, reply_markup=get_main_keyboard(), parse_mode='Markdown')

    elif cmd == 'help':
        help_text = f"📚 *ПОМОЩЬ ПО БОТУ*\n\n/start - Главное меню\n/today - На сегодня\n/tomorrow - На завтра\n/week - Какая неделя\n/switch_week - Сменить неделю\n/auto_week - Авторежим\n/change_subgroup - Сменить подгруппу"
        bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
        
    elif cmd in ['today', 'tomorrow']:
        show_day_schedule(message, cmd)
        
    elif cmd == 'week':
        today = datetime.now()
        msg = (f"📆 *Информация:*\n*Текущая:* {get_current_week()}\n*Ваша:* {get_user_week(user_id)}\n"
               f"*Подгруппа:* {get_user_subgroup(user_id)}\n*Учебная неделя №:* {max(0, (today - START_DATE).days // 7 + 1)}")
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')
        
    elif cmd == 'switch_week':
        show_week_selection_menu(message)
        
    elif cmd == 'auto_week':
        user_data['weeks'][str(user_id)] = "auto"
        save_data()
        bot.send_message(message.chat.id, f"✅ *Включен авторежим!*\nТекущая неделя: {get_current_week()}", parse_mode='Markdown')
        
    elif cmd == 'change_subgroup':
        show_subgroup_selection(message)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id
    if str(user_id) not in user_data['subgroups']:
        show_subgroup_selection(message)
        return

    txt = message.text
    if txt == '📅 Сегодня': show_day_schedule(message, "today")
    elif txt == '📆 Завтра': show_day_schedule(message, "tomorrow")
    elif txt == 'ℹ️ Какая неделя?': handle_commands(type('obj', (object,), {'text': '/week', 'chat': message.chat}))
    elif txt == '🔄 Сменить неделю': show_week_selection_menu(message)
    elif txt == '👥 Сменить подгруппу': show_subgroup_selection(message)
    elif txt in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]: show_day_with_week_buttons(message, txt)
    else: bot.send_message(message.chat.id, "Пожалуйста, выберите день недели из меню ниже 👇")

# ================ УТИЛИТЫ ОТОБРАЖЕНИЯ ================

def show_subgroup_selection(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('👥 Подгруппа 1', callback_data='set_sg_1'),
        types.InlineKeyboardButton('👥 Подгруппа 2', callback_data='set_sg_2')
    )
    bot.send_message(message.chat.id, "👋 *Добро пожаловать!*\n📚 *Выберите вашу подгруппу:*", reply_markup=markup, parse_mode='Markdown')

def show_week_selection_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('📘 I неделя', callback_data='set_week_I'),
        types.InlineKeyboardButton('📗 II неделя', callback_data='set_week_II'),
        types.InlineKeyboardButton('🤖 Автоматически', callback_data='set_week_auto'),
        types.InlineKeyboardButton(f'📅 Текущая ({get_current_week()})', callback_data=f'set_week_{get_current_week()}'),
        types.InlineKeyboardButton('❌ Отмена', callback_data='cancel_action')
    )
    bot.send_message(message.chat.id, "🔄 *Смена недели*\nВыберите действие:", reply_markup=markup, parse_mode='Markdown')

def show_day_schedule(message, day_type):
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
    target_idx = (datetime.now().weekday() + (1 if day_type == "tomorrow" else 0)) % 7
    
    if target_idx == 6:
        bot.send_message(message.chat.id, "Выходной день! 🎉\nОтдыхайте!")
        return
        
    prefix = f"📅 *{'СЕГОДНЯ' if day_type == 'today' else 'ЗАВТРА'} ({days[target_idx]})*"
    show_day_with_week_buttons(message, days[target_idx], prefix)

def show_day_with_week_buttons(message_or_call, day_name, prefix="", force_week=None):
    chat_id = message_or_call.chat.id if hasattr(message_or_call, 'chat') else message_or_call.message.chat.id
    user_week = force_week or get_user_week(chat_id)
    user_subgroup = get_user_subgroup(chat_id)

    try:
        sch_text = schedule[user_subgroup][day_name][user_week]
    except KeyError:
        bot.send_message(chat_id, f"Расписание на {day_name} не найдено.")
        return

    mode_text = "Ручной" if user_data['weeks'].get(str(chat_id), 'auto') != 'auto' else "Авто"
    response = f"{prefix}\n\n{sch_text}\n\n*Отображается {user_week} неделя*\n*Подгруппа:* {user_subgroup}\n*Режим:* {mode_text}\n*Текущая неделя:* {get_current_week()}"
    markup = get_inline_schedule_keyboard(day_name, user_week)

    if hasattr(message_or_call, 'data'): # Если это вызов из callback
        bot.edit_message_text(response, chat_id, message_or_call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(chat_id, response, reply_markup=markup, parse_mode='Markdown')

# ================ UNIFIED CALLBACK HANDLER ================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id_str = str(call.message.chat.id)
    data = call.data

    if data.startswith('set_sg_'):
        sg = int(data.split('_')[2])
        user_data['subgroups'][user_id_str] = sg
        save_data()
        bot.edit_message_text(f"✅ *Выбрана Подгруппа {sg}!*", call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        bot.send_message(call.message.chat.id, "🔄 Меню загружено.", reply_markup=get_main_keyboard())

    elif data.startswith('view_'):
        # Формат: view_I_Понедельник
        _, week, day_name = data.split('_')
        prefix = call.message.text.split('\n')[0] # Забираем префикс из старого сообщения
        show_day_with_week_buttons(call, day_name, prefix=prefix, force_week=week)
        bot.answer_callback_query(call.id, f"Показана {week} неделя")

    elif data.startswith('set_week_'):
        # Формат: set_week_I, set_week_II, set_week_auto
        target = data.replace('set_week_', '')
        user_data['weeks'][user_id_str] = target
        save_data()
        
        msg = f"✅ *Режим: {'Автоматический' if target == 'auto' else target + ' неделя'}*"
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Настройки сохранены")

    elif data == 'show_today':
        show_day_schedule(call.message, "today")
        bot.answer_callback_query(call.id)

    elif data in ['cancel_action', 'back_to_menu']:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if data == 'back_to_menu':
            bot.send_message(call.message.chat.id, "🏠 Главное меню", reply_markup=get_main_keyboard())

# ================ FLASK & ЗАПУСК ================

@app.route('/')
def home(): return "Bot is running!", 200

@app.route('/ping')
def ping(): return "pong", 200

def run_flask_server():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

def keep_alive():
    time.sleep(40)
    RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL", "https://telegram-schedule-bot-y7r4.onrender.com")
    while True:
        try: requests.get(f"{RENDER_URL}/ping", timeout=10)
        except: pass
        time.sleep(480)

if __name__ == "__main__":
    print("🎬 НАЧАЛО ЗАПУСКА СИСТЕМЫ")
    threading.Thread(target=keep_alive, daemon=True).start()
    threading.Thread(target=run_flask_server, daemon=True).start()
    
    print("🤖 Запуск Telegram бота (Polling)...")
    bot.polling(none_stop=True, interval=1, timeout=60)
