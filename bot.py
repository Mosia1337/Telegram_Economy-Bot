import asyncio
import random
import datetime
import math
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Конфигурация
TOKEN = "ВАШ ТОКЕН"
bot = Bot(token=TOKEN)
dp = Dispatcher()


# Экономическая система с новыми функциями
class EconomySystem:
    def __init__(self):
        self.users = {}
        self.exchange_rates = {"USD": 1.0, "EUR": 0.85, "BTC": 0.000025, "GOLD": 0.0005}
        self.stock_market = {
            "TECH": {"price": 100, "volatility": 0.1, "emoji": "💻"},
            "OIL": {"price": 75, "volatility": 0.15, "emoji": "🛢️"},
            "GOLD": {"price": 1800, "volatility": 0.05, "emoji": "🥇"},
            "CRYPTO": {"price": 50, "volatility": 0.25, "emoji": "🔐"}
        }
        self.businesses = {
            "FACTORY": {"name": "Фабрика", "cost": 5000, "income": 300, "emoji": "🏭"},
            "SHOP": {"name": "Магазин", "cost": 2000, "income": 150, "emoji": "🏪"},
            "FARM": {"name": "Ферма", "cost": 1000, "income": 80, "emoji": "🚜"},
            "IT": {"name": "IT Компания", "cost": 10000, "income": 700, "emoji": "💻"}
        }
        self.transaction_log = []
        self.global_events = {
            "current": None,
            "end_time": None
        }
        self.lottery = {"pool": 0, "tickets": {}}
        self.last_market_update = datetime.datetime.now()
        self.black_market = {
            "WEAPON": {"price": 1500, "risk": 0.3, "emoji": "🔫"},
            "ARTIFACT": {"price": 3000, "risk": 0.5, "emoji": "🏺"},
            "DATA": {"price": 2500, "risk": 0.4, "emoji": "💾"}
        }

    def init_user(self, user_id, username):
        if user_id not in self.users:
            self.users[user_id] = {
                "coins": 1000,
                "gems": 0,
                "bank": 0,
                "last_daily": None,
                "last_work": None,
                "investments": {},
                "businesses": {},
                "username": username,
                "energy": 100,
                "prestige": 0,
                "last_lottery": None,
                "criminal_record": 0
            }
        return self.users[user_id]

    def update_market(self):
        now = datetime.datetime.now()
        # Обновляем рынок каждые 5 минут
        if (now - self.last_market_update).total_seconds() < 300:
            return

        self.last_market_update = now

        # Глобальные события
        if self.global_events["current"] and now > self.global_events["end_time"]:
            self.global_events["current"] = None

        # Случайное глобальное событие (10% шанс)
        if not self.global_events["current"] and random.random() < 0.1:
            events = [
                ("CRISIS", "💥 Финансовый кризис! Цены на акции упали!", -0.2),
                ("BOOM", "🚀 Экономический бум! Цены на акции растут!", 0.25),
                ("INFLATION", "📈 Инфляция! Цены на бизнес выросли!", 0.15),
                ("HACKING", "👨‍💻 Атака хакеров! Кибер-активы упали в цене!", -0.3)
            ]
            event = random.choice(events)
            self.global_events["current"] = event[0]
            self.global_events["end_time"] = now + datetime.timedelta(minutes=30)

            # Применяем эффект события
            for stock in self.stock_market.values():
                stock["price"] *= (1 + event[2])

            return event[1]

        # Обычное обновление рынка
        for currency in self.exchange_rates:
            if currency != "USD":
                change = random.uniform(-0.05, 0.05)
                self.exchange_rates[currency] *= (1 + change)

        for stock in self.stock_market.values():
            change = random.uniform(-stock["volatility"], stock["volatility"])
            stock["price"] = max(10, stock["price"] * (1 + change))

        return None

    def daily_bonus(self, user_id):
        user = self.users[user_id]
        now = datetime.datetime.now()

        if user["last_daily"]:
            elapsed = now - user["last_daily"]
            if elapsed.total_seconds() < 86400:
                next_bonus = user["last_daily"] + datetime.timedelta(days=1)
                return False, (next_bonus - now)

        streak = user.get("daily_streak", 0) + 1
        bonus = 50 + min(streak * 10, 100) + random.randint(1, 50)

        # Премиум-бонус за престиж
        prestige_bonus = min(user["prestige"] * 5, 50)
        bonus += prestige_bonus

        user["coins"] += bonus
        user["last_daily"] = now
        user["daily_streak"] = streak
        user["energy"] = min(user["energy"] + 30, 100)

        return True, bonus

    def work(self, user_id, job_type):
        user = self.users[user_id]
        now = datetime.datetime.now()

        if user["energy"] < 20:
            return False, "energy"

        if user["last_work"]:
            elapsed = (now - user["last_work"]).total_seconds()
            if elapsed < 300:
                cooldown = 300 - elapsed
                return False, cooldown

        if job_type == "clicker":
            income = random.randint(10, 30)
        elif job_type == "trader":
            income = random.randint(50, 100)
        elif job_type == "miner":
            income = random.randint(30, 70)
        else:
            income = random.randint(20, 50)

        # Улучшение за престиж
        income = int(income * (1 + user["prestige"] / 100))

        user["coins"] += income
        user["last_work"] = now
        user["energy"] = max(user["energy"] - 20, 0)
        return True, income

    def bank_interest(self):
        for user in self.users.values():
            if user["bank"] > 0:
                interest = user["bank"] * (0.01 + user["prestige"] / 5000)
                user["bank"] += interest
                self.log_transaction(
                    "BANK",
                    f"+{interest:.2f} coins (проценты)",
                    user["coins"],
                    user["bank"]
                )

    def transfer(self, sender_id, receiver_id, amount):
        if sender_id not in self.users or receiver_id not in self.users:
            return False, "Пользователь не найден"

        if self.users[sender_id]["coins"] < amount:
            return False, "Недостаточно средств"

        tax = int(amount * 0.1)
        received = amount - tax

        self.users[sender_id]["coins"] -= amount
        self.users[receiver_id]["coins"] += received

        # Престиж за переводы
        self.users[sender_id]["prestige"] += amount // 1000
        self.users[receiver_id]["prestige"] += received // 1000

        self.log_transaction(
            sender_id,
            f"Перевод {receiver_id}: -{amount} coins",
            self.users[sender_id]["coins"],
            self.users[sender_id]["bank"]
        )
        self.log_transaction(
            receiver_id,
            f"Перевод от {sender_id}: +{received} coins",
            self.users[receiver_id]["coins"],
            self.users[receiver_id]["bank"]
        )

        return True, (received, tax)

    def buy_business(self, user_id, business_type):
        if business_type not in self.businesses:
            return False, "Неизвестный бизнес"

        business = self.businesses[business_type]
        user = self.users[user_id]

        if user["coins"] < business["cost"]:
            return False, "Недостаточно средств"

        user["coins"] -= business["cost"]
        if business_type in user["businesses"]:
            user["businesses"][business_type] += 1
        else:
            user["businesses"][business_type] = 1

        user["prestige"] += business["cost"] // 500

        self.log_transaction(
            user_id,
            f"Покупка {business['name']}: -{business['cost']} coins",
            user["coins"],
            user["bank"]
        )

        return True, business["name"]

    def collect_business_income(self, user_id):
        user = self.users[user_id]
        total_income = 0

        for business_type, quantity in user["businesses"].items():
            business = self.businesses[business_type]
            income = business["income"] * quantity
            total_income += income
            user["coins"] += income

        # Престиж за доход
        user["prestige"] += total_income // 100

        return total_income

    def invest(self, user_id, asset, amount):
        if asset not in self.stock_market:
            return False, "Неизвестный актив"

        user = self.users[user_id]
        if user["coins"] < amount:
            return False, "Недостаточно средств"

        user["coins"] -= amount
        if asset in user["investments"]:
            user["investments"][asset] += amount
        else:
            user["investments"][asset] = amount

        user["prestige"] += amount // 500

        self.log_transaction(
            user_id,
            f"Инвестиция в {asset}: -{amount} coins",
            user["coins"],
            user["bank"]
        )

        return True, asset

    def sell_investment(self, user_id, asset):
        user = self.users[user_id]
        if asset not in user["investments"] or user["investments"][asset] <= 0:
            return False, "Нет инвестиций"

        amount = user["investments"][asset]
        current_value = int(amount * (self.stock_market[asset]["price"] / 100))

        user["coins"] += current_value
        user["investments"][asset] = 0

        profit = current_value - amount
        profit_text = f" (+{profit})" if profit > 0 else f" ({profit})"

        # Престиж за прибыль
        if profit > 0:
            user["prestige"] += profit // 200

        self.log_transaction(
            user_id,
            f"Продажа {asset}: +{current_value} coins{profit_text}",
            user["coins"],
            user["bank"]
        )

        return True, (current_value, profit)

    def deposit_to_bank(self, user_id, amount):
        user = self.users[user_id]
        if user["coins"] < amount:
            return False, "Недостаточно средств"

        user["coins"] -= amount
        user["bank"] += amount

        user["prestige"] += amount // 1000

        self.log_transaction(
            user_id,
            f"Банковский депозит: -{amount} coins",
            user["coins"],
            user["bank"]
        )

        return True, amount

    def withdraw_from_bank(self, user_id, amount):
        user = self.users[user_id]
        if user["bank"] < amount:
            return False, "Недостаточно средств в банке"

        user["bank"] -= amount
        user["coins"] += amount

        self.log_transaction(
            user_id,
            f"Снятие с банка: +{amount} coins",
            user["coins"],
            user["bank"]
        )

        return True, amount

    def exchange(self, user_id, from_curr, to_curr, amount):
        if from_curr == "COIN":
            value = amount * self.exchange_rates.get(to_curr, 1)
        else:
            value = amount / self.exchange_rates.get(from_curr, 1)

        return True, value

    def log_transaction(self, user_id, description, new_balance, new_bank):
        log_entry = {
            "timestamp": datetime.datetime.now(),
            "user_id": user_id,
            "description": description,
            "balance": new_balance,
            "bank": new_bank
        }
        self.transaction_log.append(log_entry)

    def get_rich_list(self):
        sorted_users = sorted(
            self.users.items(),
            key=lambda x: x[1]["coins"] + x[1]["bank"] + sum(
                self.stock_market[asset]["price"] / 100 * amount
                for asset, amount in x[1]["investments"].items()
            ) + sum(
                self.businesses[b]["cost"] * count
                for b, count in x[1]["businesses"].items()
            ),
            reverse=True
        )[:10]
        return sorted_users

    def get_power_list(self):
        sorted_users = sorted(
            self.users.items(),
            key=lambda x: sum(x[1]["businesses"].values()) * 100 +
                          sum(x[1]["investments"].values()) +
                          x[1]["prestige"] * 10,
            reverse=True
        )[:10]
        return sorted_users

    def buy_lottery_ticket(self, user_id, amount=1):
        user = self.users[user_id]
        cost = amount * 100

        if user["coins"] < cost:
            return False, "Недостаточно средств"

        now = datetime.datetime.now()
        if user["last_lottery"] and (now - user["last_lottery"]).total_seconds() < 3600:
            return False, "cooldown"

        user["coins"] -= cost
        self.lottery["pool"] += cost
        self.lottery["tickets"][user_id] = self.lottery["tickets"].get(user_id, 0) + amount
        user["last_lottery"] = now
        user["prestige"] += amount * 2

        return True, amount

    def draw_lottery(self):
        if not self.lottery["tickets"]:
            return None

        # Выбираем победителя
        tickets = []
        for user_id, count in self.lottery["tickets"].items():
            tickets.extend([user_id] * count)

        winner_id = random.choice(tickets)
        prize = int(self.lottery["pool"] * 0.8)  # 80% приз, 20% комиссия
        self.users[winner_id]["coins"] += prize
        self.users[winner_id]["prestige"] += prize // 100

        # Сбрасываем лотерею
        result = (winner_id, prize)
        self.lottery = {"pool": 0, "tickets": {}}

        return result

    def black_market_deal(self, user_id, item_type):
        if item_type not in self.black_market:
            return False, "Неизвестный товар"

        item = self.black_market[item_type]
        user = self.users[user_id]

        if user["coins"] < item["price"]:
            return False, "Недостаточно средств"

        # Риск быть пойманным
        if random.random() < item["risk"]:
            fine = int(item["price"] * 0.5)
            user["coins"] -= fine
            user["criminal_record"] += 1
            return False, f"Полиция поймала вас! Штраф: {fine} coins"

        # Успешная сделка
        profit = random.randint(200, 800)
        user["coins"] += profit
        user["criminal_record"] += 0.5

        return True, profit


# Инициализация экономической системы
economy = EconomySystem()


# Клавиатуры
def main_keyboard():
    buttons = [
        [KeyboardButton(text="💰 Кошелек"), KeyboardButton(text="💼 Работа")],
        [KeyboardButton(text="🏦 Банк"), KeyboardButton(text="📈 Инвестиции")],
        [KeyboardButton(text="🏭 Бизнес"), KeyboardButton(text="🎰 Лотерея")],
        [KeyboardButton(text="📊 Топы"), KeyboardButton(text="🔁 Обмен валют")],
        [KeyboardButton(text="🌑 Черный рынок")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def wallet_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="💸 Перевести деньги", callback_data="transfer_money")
    builder.button(text="📝 История операций", callback_data="transaction_history")
    builder.button(text="⚡ Энергия", callback_data="show_energy")
    return builder.as_markup()


def work_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🖱️ Кликер-ферма", callback_data="work:clicker")
    builder.button(text="📊 Биржевой трейдинг", callback_data="work:trader")
    builder.button(text="⛏️ Крипто-майнинг", callback_data="work:miner")
    builder.button(text="💎 Добыча кристаллов", callback_data="work:miner_gem")
    return builder.as_markup()


def bank_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Положить в банк", callback_data="bank:deposit")
    builder.button(text="🏧 Снять с банка", callback_data="bank:withdraw")
    builder.button(text="📊 Банковский процент", callback_data="bank:interest")
    return builder.as_markup()


def investment_keyboard():
    builder = InlineKeyboardBuilder()
    for asset, data in economy.stock_market.items():
        builder.button(text=f"{data['emoji']} {asset} (${data['price']})", callback_data=f"invest:{asset}")
    builder.button(text="💱 Продать активы", callback_data="invest:sell")
    builder.adjust(2)
    return builder.as_markup()


def business_keyboard():
    builder = InlineKeyboardBuilder()
    for business_id, business_data in economy.businesses.items():
        builder.button(text=f"{business_data['emoji']} {business_data['name']} (${business_data['cost']})",
                       callback_data=f"business:{business_id}")
    builder.button(text="🏭 Собрать доход", callback_data="business:collect")
    builder.adjust(1)
    return builder.as_markup()


def lottery_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎫 Купить 1 билет (100 coins)", callback_data="lottery:buy:1")
    builder.button(text="🎫🎫 Купить 5 билетов (450 coins)", callback_data="lottery:buy:5")
    builder.button(text="🏆 Проверить лотерею", callback_data="lottery:draw")
    return builder.as_markup()


def black_market_keyboard():
    builder = InlineKeyboardBuilder()
    for item_id, item_data in economy.black_market.items():
        builder.button(text=f"{item_data['emoji']} {item_id} (${item_data['price']})",
                       callback_data=f"black_market:{item_id}")
    builder.adjust(1)
    return builder.as_markup()


# =====================
# ОСНОВНЫЕ КОМАНДЫ
# =====================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    economy.init_user(user_id, message.from_user.full_name)

    await message.answer(
        "🏦 Добро пожаловать в Экономическую Империю 2.0!\n"
        "Вы начинаете с 1000 coins. Ваша цель - стать финансовым магнатом!\n\n"
        "🔥 Новые возможности:\n"
        "• ⚡ Система энергии для работы\n"
        "• 🏆 Система престижа и рейтинга\n"
        "• 🎰 Ежечасная лотерея\n"
        "• 🌑 Черный рынок с риском\n"
        "• 💥 Глобальные экономические события\n\n"
        "Используйте меню для управления вашей экономикой!",
        reply_markup=main_keyboard()
    )


@dp.message(F.text == "💰 Кошелек")
async def show_wallet(message: types.Message):
    user_id = message.from_user.id
    user = economy.users.get(user_id)

    if not user:
        await message.answer("Сначала зарегистрируйтесь с помощью /start")
        return

    event_msg = economy.update_market()
    if event_msg:
        await message.answer(f"⚠️ {event_msg}")

    investments_value = sum(
        economy.stock_market[asset]["price"] / 100 * amount
        for asset, amount in user["investments"].items()
    )
    business_value = sum(
        economy.businesses[b]["cost"] * count
        for b, count in user["businesses"].items()
    )
    total_assets = user["coins"] + user["bank"] + investments_value + business_value

    # Отображение глобального события
    event_info = ""
    if economy.global_events["current"]:
        event_time_left = (economy.global_events["end_time"] - datetime.datetime.now()).seconds // 60
        event_info = f"\n\n⚠️ Активно событие: {economy.global_events['current']} ({event_time_left} мин. осталось)"

    await message.answer(
        f"💼 Ваш финансовый статус:\n\n"
        f"💰 Наличные: {user['coins']} coins\n"
        f"🏦 Банковский счет: {user['bank']} coins\n"
        f"💎 Драгоценные камни: {user['gems']} gems\n"
        f"⚡ Энергия: {user['energy']}/100\n"
        f"🏆 Престиж: {user['prestige']} pts\n\n"
        f"📊 Инвестиции: {investments_value:.2f} coins\n"
        f"🏭 Бизнес активы: {business_value} coins\n"
        f"💵 Общий капитал: {total_assets:.2f} coins"
        f"{event_info}",
        reply_markup=wallet_keyboard()
    )


@dp.message(F.text == "💼 Работа")
async def show_work(message: types.Message):
    user = economy.users.get(message.from_user.id)
    if not user:
        return

    energy_info = f"\n⚡ Ваша энергия: {user['energy']}/100"
    await message.answer(f"💼 Выберите вид деятельности:{energy_info}", reply_markup=work_keyboard())


@dp.message(F.text == "🏦 Банк")
async def show_bank(message: types.Message):
    await message.answer("🏦 Банковские операции:", reply_markup=bank_keyboard())


@dp.message(F.text == "📈 Инвестиции")
async def show_investments(message: types.Message):
    event_msg = economy.update_market()
    if event_msg:
        await message.answer(f"⚠️ {event_msg}")

    rates_text = "\n".join(
        f"{data['emoji']} {asset}: ${data['price']} ({'+' if data['price'] > 100 else ''}{data['price'] - 100:.2f}%)"
        for asset, data in economy.stock_market.items()
    )

    await message.answer(
        f"📊 Текущие рыночные котировки:\n\n{rates_text}\n\n"
        "Выберите актив для инвестирования:",
        reply_markup=investment_keyboard()
    )


@dp.message(F.text == "🏭 Бизнес")
async def show_business(message: types.Message):
    business_list = "\n".join(
        f"{b['emoji']} {b['name']} - ${b['cost']} (+${b['income']}/день)"
        for b in economy.businesses.values()
    )

    await message.answer(
        f"🏭 Доступные предприятия:\n\n{business_list}\n\n"
        "Приобретайте бизнесы для пассивного дохода:",
        reply_markup=business_keyboard()
    )


@dp.message(F.text == "🎰 Лотерея")
async def show_lottery(message: types.Message):
    user_id = message.from_user.id
    user = economy.users.get(user_id)
    if not user:
        return

    tickets = economy.lottery["tickets"].get(user_id, 0)
    cooldown = ""

    if user["last_lottery"]:
        elapsed = (datetime.datetime.now() - user["last_lottery"]).total_seconds()
        if elapsed < 3600:
            cooldown = f"\n⏳ Следующая покупка через: {int((3600 - elapsed) // 60)} мин."

    await message.answer(
        f"🎰 Лотерея\n\n"
        f"🎫 Ваши билеты: {tickets}\n"
        f"💰 Призовой фонд: {economy.lottery['pool']} coins\n"
        f"🏆 Следующий розыгрыш через: {60 - datetime.datetime.now().minute} мин."
        f"{cooldown}",
        reply_markup=lottery_keyboard()
    )


@dp.message(F.text == "🌑 Черный рынок")
async def show_black_market(message: types.Message):
    user = economy.users.get(message.from_user.id)
    if not user:
        return

    risk_info = ""
    if user["criminal_record"] > 0:
        risk_info = f"\n⚠️ Уровень розыска: {min(100, int(user['criminal_record'] * 20))}%"

    await message.answer(
        f"🌑 Черный рынок\n\n"
        f"Здесь можно получить большую прибыль, но с риском быть пойманным.{risk_info}\n\n"
        f"Выберите товар:",
        reply_markup=black_market_keyboard()
    )


@dp.message(F.text == "📊 Топы")
async def show_tops(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Самые богатые", callback_data="top:rich")],
        [InlineKeyboardButton(text="💪 Самые влиятельные", callback_data="top:power")],
        [InlineKeyboardButton(text="🔫 Самые опасные", callback_data="top:criminal")]
    ])
    await message.answer("📊 Топы игроков:", reply_markup=keyboard)


@dp.message(F.text == "🔁 Обмен валют")
async def show_exchange(message: types.Message):
    rates_text = "\n".join(f"1 {curr} = {rate:.6f} BTC" for curr, rate in economy.exchange_rates.items())

    await message.answer(
        f"💱 Текущие курсы обмена:\n\n{rates_text}\n\n"
        "Используйте команду /exchange [из] [в] [сумма] для обмена валют\n"
        "Пример: /exchange COIN BTC 100"
    )


# =====================
# ОБРАБОТЧИКИ ИНЛАЙН-КНОПОК
# =====================

@dp.callback_query(F.data.startswith("work:"))
async def handle_work(callback: types.CallbackQuery):
    job_type = callback.data.split(":")[1]
    user_id = callback.from_user.id

    success, result = economy.work(user_id, job_type)

    if success:
        await callback.message.answer(
            f"💼 Вы заработали {result} coins! ⚡ Энергия: {economy.users[user_id]['energy']}/100")
    elif result == "energy":
        await callback.message.answer("🛑 Недостаточно энергии! Отдохните или подождите")
    else:
        minutes = int(result) // 60
        await callback.message.answer(
            f"⏳ Вы устали! Отдохните {minutes} минут перед следующей работой."
        )
    await callback.answer()


@dp.callback_query(F.data == "transfer_money")
async def start_transfer(callback: types.CallbackQuery):
    await callback.message.answer(
        "💸 Введите команду в формате:\n"
        "/transfer @username сумма\n"
        "Пример: /transfer @user123 500"
    )
    await callback.answer()


@dp.callback_query(F.data == "transaction_history")
async def show_history(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    transactions = [t for t in economy.transaction_log if t["user_id"] == user_id][-5:]

    if not transactions:
        await callback.message.answer("📝 История операций пуста")
        await callback.answer()
        return

    history_text = "\n\n".join(
        f"{t['timestamp'].strftime('%d.%m %H:%M')}: {t['description']}\n"
        f"Баланс: {t['balance']} coins, Банк: {t['bank']} coins"
        for t in reversed(transactions))

    await callback.message.answer(f"📝 Последние операции:\n\n{history_text}")
    await callback.answer()


@dp.callback_query(F.data == "show_energy")
async def show_energy(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = economy.users.get(user_id)
    if not user:
        return

    recharge_time = ""
    if user["energy"] < 100:
        recharge_minutes = (100 - user["energy"]) // 2
        recharge_time = f"\n\n⚡ Полное восстановление через: {recharge_minutes} мин."

    await callback.message.answer(
        f"⚡ Ваша энергия: {user['energy']}/100\n"
        f"💡 Энергия восстанавливается 1 единицу в минуту.{recharge_time}"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("bank:"))
async def handle_bank(callback: types.CallbackQuery):
    action = callback.data.split(":")[1]

    if action == "deposit":
        await callback.message.answer("💳 Введите сумму для внесения в банк:\n/deposit сумма")
    elif action == "withdraw":
        await callback.message.answer("🏧 Введите сумму для снятия с банка:\n/withdraw сумма")
    elif action == "interest":
        await callback.message.answer(
            "🏦 Банк начисляет 1% + 0.02% за каждый 1000 престижа ежедневно на ваш депозит. "
            "Следующее начисление через 24 часа после последнего."
        )

    await callback.answer()


@dp.callback_query(F.data.startswith("invest:"))
async def handle_investment(callback: types.CallbackQuery):
    _, asset = callback.data.split(":", 1)

    if asset == "sell":
        await callback.message.answer("💱 Введите актив для продажи:\n/sell [актив]")
        await callback.answer()
        return

    await callback.message.answer(
        f"📈 Введите сумму для инвестирования в {asset}:\n/invest {asset} сумма"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("business:"))
async def handle_business(callback: types.CallbackQuery):
    _, action = callback.data.split(":", 1)
    user_id = callback.from_user.id

    if action == "collect":
        income = economy.collect_business_income(user_id)
        await callback.message.answer(f"🏭 Ваши предприятия принесли {income} coins дохода!")
    else:
        for b_id, b_data in economy.businesses.items():
            if b_id == action:
                success, result = economy.buy_business(user_id, b_id)
                if success:
                    await callback.message.answer(f"🏭 Вы приобрели {result}!")
                else:
                    await callback.message.answer(f"❌ {result}")
                break

    await callback.answer()


@dp.callback_query(F.data.startswith("lottery:"))
async def handle_lottery(callback: types.CallbackQuery):
    action = callback.data.split(":")[1]
    user_id = callback.from_user.id

    if action == "buy":
        amount = int(callback.data.split(":")[2])
        discount = 0.9 if amount == 5 else 1
        cost = amount * 100 * discount

        success, result = economy.buy_lottery_ticket(user_id, amount)
        if success:
            await callback.message.answer(f"🎫 Вы купили {amount} лотерейных билетов за {cost} coins!")
        elif result == "cooldown":
            await callback.message.answer("⏳ Вы недавно покупали билеты. Попробуйте позже.")
        else:
            await callback.message.answer(f"❌ {result}")
    elif action == "draw":
        # Проверяем, что сейчас время розыгрыша (последние 5 минуты часа)
        if datetime.datetime.now().minute < 55:
            await callback.message.answer("⌛ Розыгрыш проводится в последние 5 минут каждого часа")
            await callback.answer()
            return

        winner = economy.draw_lottery()
        if not winner:
            await callback.message.answer("😢 В лотерее нет участников")
        else:
            winner_id, prize = winner
            username = economy.users[winner_id]["username"]
            await callback.message.answer(f"🏆 Победитель лотереи: {username}!\n💰 Выигрыш: {prize} coins!")

    await callback.answer()


@dp.callback_query(F.data.startswith("black_market:"))
async def handle_black_market(callback: types.CallbackQuery):
    item_id = callback.data.split(":")[1]
    user_id = callback.from_user.id

    success, result = economy.black_market_deal(user_id, item_id)

    if success:
        await callback.message.answer(f"🌑 Успешная сделка! Прибыль: {result} coins\n"
                                      f"⚠️ Уровень розыска: {min(100, int(economy.users[user_id]['criminal_record'] * 20))}%")
    else:
        await callback.message.answer(f"❌ {result}")

    await callback.answer()


@dp.callback_query(F.data.startswith("top:"))
async def handle_top(callback: types.CallbackQuery):
    top_type = callback.data.split(":")[1]

    if top_type == "rich":
        top_list = economy.get_rich_list()
        title = "🏆 Топ-10 самых богатых игроков"
    elif top_type == "power":
        top_list = economy.get_power_list()
        title = "💪 Топ-10 самых влиятельных игроков"
    else:
        top_list = sorted(
            economy.users.items(),
            key=lambda x: x[1]["criminal_record"],
            reverse=True
        )[:10]
        title = "🔫 Топ-10 самых опасных игроков"

    if not top_list:
        await callback.message.answer("😢 Пока нет данных для топа")
        await callback.answer()
        return

    top_text = []
    if top_type == "rich":
        for i, (uid, data) in enumerate(top_list):
            investments_value = sum(
                economy.stock_market[asset]["price"] / 100 * amount
                for asset, amount in data["investments"].items()
            )
            business_value = sum(
                economy.businesses[b]["cost"] * count
                for b, count in data["businesses"].items()
            )
            total = data["coins"] + data["bank"] + investments_value + business_value
            top_text.append(f"{i + 1}. {data['username']} - {total:.2f} coins")
    elif top_type == "power":
        for i, (uid, data) in enumerate(top_list):
            influence = sum(data["businesses"].values()) * 100 + sum(data["investments"].values()) + data[
                "prestige"] * 10
            top_text.append(f"{i + 1}. {data['username']} - {influence:.2f} влияния")
    else:
        for i, (uid, data) in enumerate(top_list):
            top_text.append(
                f"{i + 1}. {data['username']} - уровень угрозы: {min(100, int(data['criminal_record'] * 20))}%")

    await callback.message.answer(f"{title}:\n\n" + "\n".join(top_text))
    await callback.answer()


# =====================
# ОБРАБОТЧИКИ КОМАНД
# =====================

@dp.message(Command("daily"))
async def daily_command(message: types.Message):
    user_id = message.from_user.id
    success, result = economy.daily_bonus(user_id)

    if success:
        await message.answer(f"🎁 Ежедневный бонус: {result} coins! ⚡ Энергия +30")
    else:
        hours = result.seconds // 3600
        minutes = (result.seconds % 3600) // 60
        await message.answer(
            f"⏳ Вы уже получали награду сегодня. Следующая через: {hours}ч {minutes}мин"
        )


@dp.message(Command("transfer"))
async def transfer_command(message: types.Message):
    user_id = message.from_user.id
    parts = message.text.split()

    if len(parts) < 3:
        await message.answer("❌ Формат: /transfer @username сумма")
        return

    try:
        amount = int(parts[2])
        receiver_name = parts[1].lstrip('@')

        receiver_id = None
        for uid, data in economy.users.items():
            if data["username"] == receiver_name:
                receiver_id = uid
                break

        if not receiver_id:
            await message.answer("❌ Пользователь не найден")
            return

        success, result = economy.transfer(user_id, receiver_id, amount)

        if success:
            received, tax = result
            await message.answer(
                f"💸 Вы перевели {amount} coins пользователю {receiver_name}\n"
                f"📝 Налог: {tax} coins\n"
                f"💼 Получателю зачислено: {received} coins\n"
                f"🏆 +{amount // 1000} престижа"
            )
        else:
            await message.answer(f"❌ {result}")
    except ValueError:
        await message.answer("❌ Неверный формат суммы")


@dp.message(Command("deposit"))
async def deposit_command(message: types.Message):
    user_id = message.from_user.id
    try:
        amount = int(message.text.split()[1])
        success, result = economy.deposit_to_bank(user_id, amount)

        if success:
            await message.answer(f"💳 Вы внесли {amount} coins на банковский счет\n🏆 +{amount // 1000} престижа")
        else:
            await message.answer(f"❌ {result}")
    except (IndexError, ValueError):
        await message.answer("❌ Формат: /deposit сумма")


@dp.message(Command("withdraw"))
async def withdraw_command(message: types.Message):
    user_id = message.from_user.id
    try:
        amount = int(message.text.split()[1])
        success, result = economy.withdraw_from_bank(user_id, amount)

        if success:
            await message.answer(f"🏧 Вы сняли {amount} coins с банковского счета")
        else:
            await message.answer(f"❌ {result}")
    except (IndexError, ValueError):
        await message.answer("❌ Формат: /withdraw сумма")


@dp.message(Command("invest"))
async def invest_command(message: types.Message):
    user_id = message.from_user.id
    parts = message.text.split()

    if len(parts) < 3:
        await message.answer("❌ Формат: /invest [актив] сумма")
        return

    try:
        asset = parts[1].upper()
        amount = int(parts[2])
        success, result = economy.invest(user_id, asset, amount)

        if success:
            await message.answer(f"📈 Вы инвестировали {amount} coins в {asset}\n🏆 +{amount // 500} престижа")
        else:
            await message.answer(f"❌ {result}")
    except ValueError:
        await message.answer("❌ Неверный формат суммы")


@dp.message(Command("sell"))
async def sell_command(message: types.Message):
    user_id = message.from_user.id
    parts = message.text.split()

    if len(parts) < 2:
        await message.answer("❌ Формат: /sell [актив]")
        return

    asset = parts[1].upper()
    success, result = economy.sell_investment(user_id, asset)

    if success:
        current_value, profit = result
        profit_text = "Прибыль" if profit >= 0 else "Убыток"
        await message.answer(
            f"💱 Вы продали инвестиции в {asset} за {current_value} coins\n"
            f"📊 {profit_text}: {abs(profit)} coins"
        )
    else:
        await message.answer(f"❌ {result}")


@dp.message(Command("exchange"))
async def exchange_command(message: types.Message):
    user_id = message.from_user.id
    parts = message.text.split()

    if len(parts) < 4:
        await message.answer("❌ Формат: /exchange [из] [в] [сумма]")
        return

    from_curr = parts[1].upper()
    to_curr = parts[2].upper()

    try:
        amount = float(parts[3])
        success, result = economy.exchange(user_id, from_curr, to_curr, amount)

        if success:
            await message.answer(
                f"💱 Обмен: {amount} {from_curr} → {result:.6f} {to_curr}"
            )
        else:
            await message.answer("❌ Неверная валюта для обмена")
    except ValueError:
        await message.answer("❌ Неверный формат суммы")


@dp.message(Command("energy"))
async def energy_command(message: types.Message):
    user_id = message.from_user.id
    user = economy.users.get(user_id)
    if not user:
        return

    recharge_time = ""
    if user["energy"] < 100:
        recharge_minutes = (100 - user["energy"]) // 2
        recharge_time = f"\n\n⚡ Полное восстановление через: {recharge_minutes} мин."

    await message.answer(
        f"⚡ Ваша энергия: {user['energy']}/100\n"
        f"💡 Энергия восстанавливается 1 единицу в 2 минуты.{recharge_time}"
    )


# Фоновая задача для обновления рынка
async def market_updater():
    while True:
        await asyncio.sleep(60)  # Обновляем каждую минуту
        event_msg = economy.update_market()
        economy.bank_interest()

        # Розыгрыш лотереи в последние 5 минут часа
        now = datetime.datetime.now()
        if now.minute >= 55:  # Последние 5 минут часа
            winner = economy.draw_lottery()
            if winner:
                winner_id, prize = winner
                username = economy.users[winner_id]["username"]
                # Рассылаем всем участникам
                for user_id in economy.users:
                    try:
                        await bot.send_message(
                            user_id,
                            f"🏆 Результаты лотереи!\n\n"
                            f"Победитель: {username}\n"
                            f"Выигрыш: {prize} coins!\n\n"
                            f"Следующая лотерея через 1 час"
                        )
                    except:
                        pass  # Игрок не начал диалог с ботом


# Запуск бота
async def main():
    # Запускаем фоновую задачу для обновления рынка
    asyncio.create_task(market_updater())
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Экономический бот запущен! (Ctrl+C для остановки)")
    asyncio.run(main())