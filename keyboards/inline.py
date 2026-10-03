from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_confirm_kb(app_id:int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅Подтвердить', callback_data=f"confirm_{app_id}"),
             InlineKeyboardButton(text='❌ Отклонить', callback_data= f"cancel_{app_id}")]
        ]
    )

def get_services_keyboard(services:list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for service in services:
        builder.button(text = f'{service['name']} - {service['price']} ₽',
                       callback_data=f'service_{service['id']}')

    builder.button(
        text = '🏠 Главное меню',
        callback_data = 'to_main'
    )
    builder.adjust(1)
    return builder.as_markup()
def get_delete_service_kb(service_id:int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard = [
            [InlineKeyboardButton(text = '🗑 Удалить услугу', callback_data=f'delete_service_{service_id}')]
        ]
    )
def get_user_cancel_kb(app_id:int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text = '🗑 Отменить эту запись',callback_data = f'user_cancel_{app_id}')]
        ]
    )
def get_admin_delete_app_kb(app_id:int)-> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
        [InlineKeyboardButton(text = '❌ Удалить запись', callback_data=f'admin_delete_{app_id}')]
        ]
    )
def get_masters_kb(service_name:str) -> InlineKeyboardMarkup:
    masters = [
        {'id' : 1 , "name" : "Алексей(Барбер)"},
        {'id' : 2, "name": "Дмитрий(Топ-Барбер)"}
    ]
    keyboard = []
    for master in masters:
        m_id = master['id']
        m_name = master['name']
        keyboard.append([
            InlineKeyboardButton(
                text=master['name'],
                callback_data=f"select_master_{m_id}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
def get_time_slots_kb(master_id:int, booked_slots:list[str] = None):
    if booked_slots is None:
        booked_slots = []
    avaible_slots = ["15:00", "16:00", "17:00", "18:00", "19:00"]
    builder = InlineKeyboardBuilder()

    keyboard = []
    row = []
    for slots in avaible_slots:
        
        if slots in booked_slots:
                    continue
        
        builder.button(
                text=f'⏰ {slots}',
                callback_data=f"select_time_{slots}"
                )
    builder.adjust(2)
    return builder.as_markup()
def get_user_appointments_kb(appointments):
    builder = InlineKeyboardBuilder()
    
    for app in appointments:
        app_id, service_name, date_time, status = app
        # На кнопке пишем понятные детали: "❌ Отменить #11 (16:00)"
        builder.button(
            text=f"❌ Отменить #{app_id} ({service_name[:12]}.. — {date_time})",
            callback_data=f"user_cancel_{app_id}"
        )
        
    builder.adjust(1) # Кнопки друг под другом
    return builder.as_markup()