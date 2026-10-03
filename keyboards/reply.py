from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_admin_main_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text = '+ Добавить услугу'),
             KeyboardButton(text="🛠 Управление услугами"),
             KeyboardButton(text = '📋 Список записей')]
        ],
        resize_keyboard=True,
        persistent=True
    )

def get_cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard = [
            [KeyboardButton(text = '❌ Отмена')]
        ],
        resize_keyboard=True
    )
def get_user_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='✂️ Записаться'),
                KeyboardButton(text='📋 Мои записи'),
            ],
            [KeyboardButton(text="📍 Контакты")]
        ],
        resize_keyboard=True,
        persistent=True
    )
