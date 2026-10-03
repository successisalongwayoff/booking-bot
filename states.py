from aiogram.fsm.state import State, StatesGroup

class BookingStates(StatesGroup):
    service = State()
    date_time = State()
    choosing_master = State()
    choosing_time = State()

class AdminStates(StatesGroup):
    add_service_name = State()
    add_service_price = State()
    add_service_duration = State()

