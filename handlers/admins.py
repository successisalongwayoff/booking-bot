from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_admin_delete_app_kb
from database.requests import delete_appointment, get_appointments_by_id
from config import ADMIN_ID
from states import AdminStates
from aiogram.types import CallbackQuery
from database.requests import add_services, get_appointments, update_appointment_status, get_appointments_by_id, delete_service, get_services
from keyboards.reply import get_admin_main_kb, get_cancel_kb
from keyboards.inline import get_delete_service_kb


admin_router = Router()

# Фильтр: хэндлеры роутера сработают только для ADMIN_ID
admin_router.message.filter(F.from_user.id == ADMIN_ID)
admin_router.callback_query.filter(F.from_user.id == ADMIN_ID)


@admin_router.message(Command("admin"))
async def admin_start(message: Message):
    await message.answer(
        "Админ панель\n\n Используйте меню ниже, для управления:",
        reply_markup=get_admin_main_kb()
    )

@admin_router.message(F.text == '+ Добавить услугу')
@admin_router.message(Command('add_services'))
async def start_add_services(message: Message, state: FSMContext):
    await state.set_state(AdminStates.add_service_name)
    await message.answer("Введите название услуги:",
                         reply_markup=get_cancel_kb())


@admin_router.message(F.text =='❌ Отмена', StateFilter("*"))
async def cancel_handler(message, state:FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer('Действие отменено',
                         reply_markup = get_admin_main_kb())

@admin_router.message(AdminStates.add_service_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminStates.add_service_price)
    # Исправлена опечатка asnwer -> answer
    await message.answer("Введи цену услуги (только число, например: 1500):",
                         reply_markup=get_cancel_kb())

@admin_router.message(F.text=='📋 Список записей')
@admin_router.message(Command('appointments'))
async def show_appointments(message):
    appointments = await get_appointments()

    if not appointments:
        await message.answer('Записей пока нет')
        return

    text = "📋 <b>Список всех записей:</b>\n\n"
    for app in appointments:
        app_id, user_name, service_name, date_time = app
        text += f"🔹 <b>Запись #{app_id}</b>\n"
        text += f"Клиент: {user_name}\n"
        text += f"Услуга: {service_name}\n"
        text += f"Дата/Время: {date_time}\n\n"
        await message.answer(
            text,
            reply_markup=get_admin_delete_app_kb(app_id),
            parse_mode="HTML"
        )
   

@admin_router.message(AdminStates.add_service_price)
async def procces_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите только число!")
        return
        
    await state.update_data(price=int(message.text))
    await state.set_state(AdminStates.add_service_duration)
    await message.answer("Введи длительность услуги в минутах (например: 60):",
                         reply_markup=get_cancel_kb())

@admin_router.message(F.text== '🛠 Управление услугами')
async def manage_service(message):
    services = await get_services()
    print(services)
    if not services:
        await message.answer('В базе пока нет доступных услуг')
        return
    await message.answer("🛠 <b>Список доступных услуг:</b>\nНажмите «Удалить», чтобы убрать услугу из прайса.", parse_mode="HTML")
    for service in services:
        if isinstance(service, dict):
            service_id = service["id"]
            name = service["name"]
            price = service["price"]
            duration = service["duration"]
        else:

            service_id, name, price, duration = service
        text = (
            f"✂️ <b>{name}</b>\n"
            f"💰 Цена: {price}₽\n"
            f"⏱ Длительность: {duration} мин."
        )
        await message.answer(text, reply_markup = get_delete_service_kb(service_id), parse_mode = "HTML")

@admin_router.callback_query(F.data.startswith('admin_delete_'))
async def procss_admin_delete_appointment(callback:CallbackQuery):
    app_id = int(callback.data.split('_')[2])

    app = await get_appointments_by_id(app_id)
    if not app:
        await callback.answer("Запись не найдена!", show_alert=True)
        return
    _,user_id, user_name , service_name, date_time,_ = app
    await delete_appointment(app_id)

    try:
        await callback.bot.send_message(chat_id=user_id,
                                        text = f'🗑 Ваша запись на <b>{service_name}</b> ({date_time}) была отменена администратором.',
                                        parse_mode='HTML')
    except Exception:
        pass
    await callback.message.edit_text(
        f"🗑 Запись <b>#{app_id}</b> (Клиент: {user_name}) удалена.",
        parse_mode="HTML"
    )
    await callback.answer("Запись удалена")


@admin_router.callback_query(F.data.startswith('delete_service_'))
async def process_delete_message(callback:CallbackQuery):
    service_id = int(callback.data.split('_')[2])

    await delete_service(service_id)
    await callback.message.edit_text('Услуга успешно удалена')
    await callback.answer('Услуга удалена')


@admin_router.message(AdminStates.add_service_duration)
async def process_duration(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите длительность числом!")
        return
        
    duration = int(message.text)
    data = await state.get_data()

    # Вызываем твою функцию add_services
    await add_services(
        name=data['name'],
        price=data['price'],
        duration=duration
    )
    await state.clear()
    
    await message.answer(
        f"✅ Услуга <b>{data['name']}</b> за {data['price']}₽ ({duration} мин) успешно добавлена!",
        reply_markup=get_admin_main_kb(),
        parse_mode="HTML"
    )
@admin_router.callback_query(F.data.startswith('confirm_'))
async def confirm_keyboard(callback:CallbackQuery):
    app_id = int(callback.data.split('_')[1])
    app = await get_appointments_by_id(app_id)
    if not app:
        await callback.answer("Запись не найдена!", show_alert=True)
        return
    _,user_id,user_name,service_name,date_time, status = app
    await update_appointment_status(app_id, 'confirmed')

    try:
        await callback.bot.send_message(
            chat_id = user_id,
            text = f"✅ Ваша запись на <b>{service_name}</b> ({date_time}) успешно <b>подтверждена</b>!",
            parse_mode="HTML"
        )    
    except Exception:
        pass

    await callback.message.edit_text(f"✅ Запись #{app_id} (Клиент: {user_name}) — <b>ПОДТВЕРЖДЕНА</b>",
        parse_mode="HTML")
    await callback.answer("Запись подтверждена")

@admin_router.callback_query(F.data.startswith("reject_"))
async def cancel_keyboard(callback:CallbackQuery):
    app_id = int(callback.data.split('_')[1])
    app = await get_appointments_by_id(app_id)
    if not app:
        await callback.answer("Запись не найдена!", show_alert=True)
        return

    _, user_id, user_name, service_name, date_time, status = app
    
    await update_appointment_status(app_id, "rejected")
    
    # Уведомляем клиента
    try:
        await callback.bot.send_message(
            chat_id=user_id,
            text=f"❌ К сожалению, ваша запись на <b>{service_name}</b> ({date_time}) была <b>отклонена</b>.",
            parse_mode="HTML"
        )
    except Exception:
        pass

    await callback.message.edit_text(
        f"❌ Запись #{app_id} (Клиент: {user_name}) — <b>ОТКЛОНЕНА</b>",
        parse_mode="HTML"
    )
    await callback.answer("Запись отклонена")

