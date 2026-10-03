from aiogram import F, Router
from aiogram.types import message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from states import BookingStates
from database.requests import get_services, add_appointment, get_user_appointment
from config import ADMIN_ID
from aiogram.filters import StateFilter
from keyboards.inline import get_user_cancel_kb
from database.requests import delete_appointment, get_appointments_by_id
from database.requests import get_service_name_by_id, get_booked_time_slots
from keyboards.inline import get_services_keyboard, get_admin_confirm_kb, get_masters_kb, get_time_slots_kb
from keyboards.reply import get_user_kb, get_cancel_kb, get_admin_main_kb
router = Router()
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_master_name_by_id(master_id:int)->str:
    masters = {
        1: "Алексей (Барбер)",
        2: "Дмитрий (Топ-Барбер)"
    }
    
    # .get() возвращает строку с именем (например, "Алексей (Барбер)")
    return masters.get(master_id, f"Мастер #{master_id}")
@router.message(CommandStart())
async def cmd_start(message):
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        f'Добро пожаловать в сервис онлайн-записи.\n'
        f'Нажмите кнопку ниже, чтобы выбрать услуги и время',
        reply_markup = get_user_kb()
    )


@router.message(F.text == "❌ Отмена", StateFilter("*"))
async def cancel_user_handler(message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    if message.from_user.id == ADMIN_ID:
            await message.answer("Запись отменена", reply_markup = get_admin_main_kb)
    else:
        await message.answer("Запись отменена", reply_markup = get_user_kb)
    


@router.message(F.text == "✂️ Записаться")
async def start_booking(message, state: FSMContext):
    services = await get_services()
    if not services:
        await message.answer("К сожалению, доступных услуг пока нет.")
        return

    await state.set_state(BookingStates.service)
    await message.answer(
        "Выберите услугу из списка ниже:",
        reply_markup=get_services_keyboard(services)
    )

@router.callback_query(BookingStates.service,F.data.startswith('service_'))
async def process_any_service(callback:CallbackQuery,state:FSMContext):
    service_id = int(callback.data.split('_')[1])

    await state.update_data(service_id = service_id)

    await state.set_state(BookingStates.choosing_master)
    await callback.message.edit_text("✂️ Вы выбрали услугу!\nТеперь выберите мастера",
                                     reply_markup=get_masters_kb(service_id),
                                     parse_mode="HTML")
    await callback.answer()
@router.callback_query(BookingStates.choosing_master,F.data.startswith("select_master_"))
async def process_master_selection(callback:CallbackQuery, state:FSMContext):
    master_id = int(callback.data.split('_')[2])
    await state.update_data(master_id = master_id)
    booked_slots = await get_booked_time_slots(master_id)

    
    await state.set_state(BookingStates.choosing_time)
    await callback.message.edit_text(
        "📅 Выберите свободное время для записи:",
        reply_markup=get_time_slots_kb(master_id, booked_slots),
        parse_mode="HTML"
    )
    await callback.answer()
@router.message(F.text=='📍 Контакты')
async def show_contacts(message):
    contacts_text = (
        "💈 <b>Барбершоп «TopCut»</b>\n\n"
        "📍 <b>Адрес:</b> ул. Пушкина, д. 10 (м. Центральная)\n"
        "📞 <b>Телефон:</b> +7 (999) 000-00-00\n"
        "⏰ <b>Режим работы:</b> Ежедневно с 10:00 до 20:00\n\n"
        "🅿️ Парковка возле входа бесплатная."
    )
    await message.answer(contacts_text, parse_mode='HTML')
@router.callback_query(BookingStates.choosing_time, F.data.startswith("select_time_"))
async def process_time_selectiont(callback:CallbackQuery,state:FSMContext):
    selected_time = callback.data.split("_")[2].strip()
    data = await state.get_data()
    user_id = callback.from_user.id

    service_id = data.get("service_id")
    master_id = data.get("master_id")
    username = callback.from_user.first_name
    service_name = await get_service_name_by_id(service_id)
    app_id = await add_appointment(
        user_id = callback.from_user.id,
        user_name= callback.from_user.full_name,
        service_id=service_id,
        master_id = master_id,
        date_time = selected_time
    )
    await state.clear()

    await callback.message.edit_text(
        f"✅ <b>Запись #{app_id} оформлена!</b>\n"
        f"⏱ Время: <b>{selected_time}</b>\n\n"
        f"Ожидайте подтверждения.",
        parse_mode="HTML"
    )
    await callback.answer()
    master_name = get_master_name_by_id(master_id)
    admin_text = (
        f"🔔 <b>Новая заявка на запись! #{app_id}</b>\n\n"
        f"👤 <b>Клиент:</b> {username}\n"
        f"🆔 <b>ID клиента:</b> <code>{user_id}</code>\n"
        f"✂️️ <b>Услуга:</b> {service_name}\n"
        f"💈 <b>Мастер:</b> {master_name}\n"
        f"📅 <b>Дата/Время:</b> {selected_time}\n\n"
        f"Статус: <b>На рассмотрении</b>"
    )
    try:
        await callback.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_text,
            reply_markup=get_admin_confirm_kb(app_id),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(f"Ошибка отправки уведомления админу: {e}")
@router.callback_query(F.data == 'to_main')
async def show_main_menu(callback:CallbackQuery):
    services = await get_services()
    if not services:
        await callback.message.edit_text('На данный момент доступных услуг нет. Попробуйте позже!')
        await callback.answer()
        return

    # text = 'Главное меню'
    # await callback.message.answer(text,
    #                               reply_markup = get_user_kb())
    await callback.answer()

@router.message(BookingStates.date_time)
async def process_date_time(message, state:FSMContext):
    user_data = await state.get_data()
    service_id = user_data.get('service_id')
    data = await state.get_data()
    date_time_text = message.text
    app_id = await add_appointment(
            user_id = message.from_user.id,
            user_name = message.from_user.full_name,
            service_id = service_id,
            date_time = date_time_text
        )
    
    await state.clear()
    await message.answer(
        f"⏳ Заявка на <b>{date_time_text}</b> отправлена!\n"
        f"Ожидайте подтверждения от администратора.",
        reply_markup = get_user_kb(),
        parse_mode="HTML"
    )


    await message.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 <b>Новая заявка #{app_id}!</b>\n\n"
            f"👤 Клиент: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"✂️ Услуга ID: {data['service_id']}\n"
            f"📅 Дата/Время: {date_time_text}"
        ),
        reply_markup=get_admin_confirm_kb(app_id),
        parse_mode="HTML"
    )
@router.message(F.text == '📋 Мои записи')
@router.message(Command("my_bookings"))
async def show_my_booking(message):
    appointments = await get_user_appointment(message.from_user.id)

    if not appointments:
        await message.answer('У вас пока нет активных записей.')
        return
    status_icon = {
        "pending" : "⏳ Ожидает подтверждения",
        "confirmed" :"✅ Подтверждена",
        "rejected" : "❌ Отклонена"
    }
    builder = InlineKeyboardBuilder()
    text = "📋 <b>Ваши записи:</b>\n\n"
    for app in appointments:
        app_id, service_name, date_time,status = app
        status_text = status_icon.get(status,status)
        text += (
            f"🔹 <b>Запись #{app_id}</b>\n"
            f"✂️ Услуга: {service_name}\n"
            f"⏰ Дата/Время: {date_time}\n"
            f"📌 Статус: {status_text}\n\n"
        )



        builder.button(
            text=f"❌ Отменить запись #{app_id}({date_time})", 
            callback_data=f"user_cancel_{app_id}"
        )
    builder.adjust(1)
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@router.callback_query(F.data.startswith('user_cancel_'))
async def process_user_cancel_appointments(callback:CallbackQuery):
    app_id = int(callback.data.split('_')[2])

    app = await get_appointments_by_id(app_id)
    if not app:
        await callback.answer("Запись не найдена или уже удалена", show_alert=True)
        return
    app_id, user_id, user_name, service_name, date_time, status = app

    await delete_appointment(app_id)
    await callback.message.edit_text(
        f"❌ Ваша запись <b>#{app_id}</b> ({service_name} — {date_time}) отменена.",
        parse_mode="HTML"
    )
    await callback.answer("Запись отменена")
    try:
        await callback.bot.send_message(chat_id=ADMIN_ID,
                                        text = f'🔔 Клиент <b>{callback.from_user.full_name}</b> отменил свою запись <b>#{app_id}</b> ({service_name}, {date_time}).',
                                        parse_mode='HTML')
    except Exception:
        pass

