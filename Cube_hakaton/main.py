import hashlib as hl
import time
import wordle_game as game
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import word_generator as wg
import config
import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from base import SQL

db = SQL('db.db')

bot = Bot(token=config.TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()
logging.basicConfig(level=logging.INFO)


kb1 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="войти", callback_data="log_in")]])

kb3 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Меню", callback_data="admin_menu")]])

kb4 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Добавить баллы", callback_data="add_b"),
                                             InlineKeyboardButton(text="Отнять баллы", callback_data="deduct_b")],
                                            [InlineKeyboardButton(text="Меню", callback_data="admin_menu")]])

kb5 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="добавить", callback_data="add")],
                                            [InlineKeyboardButton(text="не добавлять", callback_data="admin_menu")]])

kb6 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="отнять", callback_data="deduct")],
                                            [InlineKeyboardButton(text="не добавлять", callback_data="admin_menu")]])

buttons2 = [
        [InlineKeyboardButton(text="Найти пользователя", callback_data="get_us")],
        [InlineKeyboardButton(text="список лидеров", callback_data="liderboard")],
        [InlineKeyboardButton(text="Выйти из аккаунта", callback_data="exit_admin")],
        [InlineKeyboardButton(text="добавить слово", callback_data="add_word")]
    ]

kb2 = InlineKeyboardMarkup(inline_keyboard=buttons2)

kb9 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="да", callback_data="Y"), InlineKeyboardButton(text="нет", callback_data="admin_menu")]
])
kb10 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="случайное слово", callback_data="rand_word")]])

kb7 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="ежедневное слово", callback_data="daily_word")],
                                            [InlineKeyboardButton(text="бонусное слово", callback_data="bonus_word")],
                                            [InlineKeyboardButton(text="список лидеров", callback_data="us_liderboard")],
                                            [InlineKeyboardButton(text="Я", callback_data="prof")],
                                            [InlineKeyboardButton(text="Выйти из аккаунта", callback_data="exit_user")]])

kb8 = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Меню", callback_data="user_menu")]])

kb11 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="да", callback_data="Y_user"), InlineKeyboardButton(text="нет", callback_data="user_menu")]
])



async def scheduled_message():
    db.update_all("users", "daily_word", 0)
    db.update_all("users", "bonus_word", 0)
    s = db.get_words()
    try:
        for i in s:
            if i[1] != datetime.now().date():
                db.delete_word(i[0])
    except:
        pass
    a = wg.get_rand_word()
    db.add_word(a)
    db.update_word(a, "daily", True)
    db.update_word(a, "date", datetime.now().date())


scheduler.add_job(scheduled_message, 'cron', hour=12, minute=0)



@dp.message() # обработка сообщений
async def start(message):
    await message.delete()
    id = message.from_user.id

    if hl.sha256(message.text.encode()).hexdigest() == config.ADMINCODE: #user вводит зашифрованный
        #await bot.delete_message(id, message.message_id -1)
        db.add_user(id, "admins")
        await message.answer("Пожалуйста введите свое имя:")
        return

    if not db.user_exist(id, "users") and not db.user_exist(id, "admins"):  # если user еще не зарегисрировался
        await bot.send_photo(id, photo=FSInputFile('images/first_menu.png'),
                             caption="Добро пожаловать в wordle!\nТут можно отдохнуть и расслабиться!", reply_markup=kb1)

    # ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN

    elif db.user_exist(id, "admins"): # если user в таблице админов

        if db.get_field("admins", id, "status") == 0:
            #await bot.delete_message(id, message.message_id - 1)
            db.update_field("admins", id, "name", message.text)
            db.update_field("admins", id, "status", 1)

        if db.get_field("admins", id, "status") == 1:
            db.update_field("admins", id, "user", None)
            db.update_field("admins", id, "user_balance", 0)
            await message.answer_photo(photo=FSInputFile("images/admin_menu.png"), reply_markup=kb2)

        if db.get_field("admins", id, "status") == 2:
            await bot.delete_message(message.chat.id, message.message_id - 1)
            try:
                s = list(db.get_user(message.text))
                db.update_field("admins", id, "user", s[0])
                await message.answer_photo(photo=FSInputFile("images/user.jpeg"),
                                           caption=str(s[0]) + "\nBalance: " + str(s[1]), reply_markup=kb4)

            except:
                await message.answer("Не удалось найти ученика", reply_markup=kb3)

        if db.get_field("admins", id, "status") == 3:
            await bot.delete_message(message.chat.id, message.message_id - 1)
            n = db.get_field("admins", id, "user")
            await message.answer_photo(photo=FSInputFile("images/apr.jpg"), caption=f"Добавить {message.text} баллов ученику({n})?", reply_markup=kb5)
            db.update_field("admins", id, "user_balance", int(message.text))

        if db.get_field("admins", id, "status") == 4:
            await bot.delete_message(message.chat.id, message.message_id - 1)
            n = db.get_field("admins", id, "user")
            await message.answer_photo(photo=FSInputFile("images/apr.jpg"),caption=f"Отнять {message.text} баллов у ученика({n})?", reply_markup=kb6)
            db.update_field("admins", id, "user_balance", int(message.text))

        if db.get_field("admins", id, "status") == 5:
            word = message.text

            if wg.chek_word(word):
                db.add_word(word)
                db.update_word(word, "date", datetime.now().date())
                db.update_field("admins", id, "status", 1)
                await message.answer("Слово добавлено.", reply_markup=kb3)

            else:
                await message.answer("Это не слово, или его нельзя добавить\nВведите другое слово, или возвращайтесь назад", reply_markup=kb3)

    # ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN

    # USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER

    else:

        if db.get_field("users", id, "status") == 1:
            await message.answer_photo(photo=FSInputFile("images/i.jpg"), reply_markup=kb7)

        if db.get_field("users", id, "status") == 0:
            #await bot.delete_message(message.chat.id, message.message_id - 1)
            db.update_field("users", id, "name", message.text)
            db.update_field("users", id, "status", 1)
            await message.answer_photo(caption="Вы зарегистрировались!", photo=FSInputFile("images/apr.jpg"), reply_markup=kb8)

        if db.get_field("users", id, "status") == 2:
            word = db.get_daily(True)[0]
            game_result = game.w_game(word, message.text.lower())

            if game_result != False:
                await message.answer(game_result+"\n "+"   ".join(message.text))

            if game_result == False:
                await message.answer_photo(caption="Такого слово нет, или его нельзя писать", photo=FSInputFile("images/stop.jpg"))
                db.update_field("users", id, "attemp", db.get_field("users", id, "attemp") + 1)

            elif game_result == "🟩🟩🟩🟩🟩":
                time.sleep(0.5)
                db.update_field("users", id, "status", 1)
                db.update_field("users", id, "balance", db.get_field("users", id, "balance") + 5)
                db.update_field("users", id, "attemp", 6)
                await message.answer_photo(caption="Ты угадал слово!\nИ получаешь 5 баллов!", photo=FSInputFile("images/yeah.jpg"), reply_markup=kb8)

            db.update_field("users", id, "attemp", db.get_field("users", id, "attemp") - 1)

            if db.get_field("users", id, "attemp") == 0:
                db.update_field("users", id, "status", 1)
                db.update_field("users", id, "attemp", 6)
                await message.answer_photo(caption=f"Игра окончена.\n Загаданное слово: {word}", photo=FSInputFile("images/lose.jpg"), reply_markup=kb8)

        if db.get_field("users", id, "status") == 3:
            word = db.get_daily(0)[0]
            game_result = game.w_game(word, message.text.lower())

            if game_result != False:
                await message.answer(game_result+"\n "+"   ".join(message.text))

            if game_result == False:
                await message.answer_photo(caption="Такого слово нет, или его нельзя писать", photo=FSInputFile("images/stop.jpg"))
                db.update_field("users", id, "attemp", db.get_field("users", id, "attemp") + 1)

            elif game_result == "🟩🟩🟩🟩🟩":
                time.sleep(0.5)
                db.update_field("users", id, "status", 1)
                db.update_field("users", id, "balance", db.get_field("users", id, "balance") + 5)
                db.update_field("users", id, "attemp", 6)
                await message.answer_photo(caption="Ты угадал слово!\nИ получаешь 5 баллов!", photo=FSInputFile("images/yeah.jpg"), reply_markup=kb8)

            db.update_field("users", id, "attemp", db.get_field("users", id, "attemp") - 1)

            if db.get_field("users", id, "attemp") == 0:
                db.update_field("users", id, "status", 1)
                db.update_field("users", id, "attemp", 6)
                await message.answer_photo(caption=f"Игра окончена.\n Загаданное слово: {word}", photo=FSInputFile("images/lose.jpg"), reply_markup=kb8)

    # USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER



@dp.callback_query()# обработка кнопок
async def start_call(call):
    await call.message.delete()
    id = call.from_user.id

    # ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN

    if call.data == "admin_menu":
        await call.message.answer_photo(photo=FSInputFile("images/admin_menu.png"), reply_markup=kb2)

    if call.data == "liderboard":
        s = db.get_users()
        s = sorted(s, reverse=True)
        await call.message.answer_photo(photo=FSInputFile("images/liderboardimg.png"), caption='\n'.join(
            ' Balance   '.join(str(item) for item in sublist[::-1]) for sublist in s), reply_markup=kb3)

    if call.data == "get_us":
        await call.message.answer_photo(photo=FSInputFile("images/search.png"),
                                        caption="Введите имя пользователя, которого хотите найти:")
        db.update_field("admins", id, "status", 2)

    if call.data == "exit_admin":
        await call.message.answer("Вы уверенны что хотите выйти?", photo=FSInputFile("images/question.jpg"), reply_markup=kb9)


    if call.data == "Y":
        db.delete_user(id, "admins")

    if call.data == "add_b":
        await call.message.answer_photo(photo=FSInputFile("images/coins.jpg"), caption="Сколько баллов добавить?")
        db.update_field("admins", id, "status", 3)

    if call.data == "deduct_b":
        await call.message.answer_photo(photo=FSInputFile("images/coins.jpg"), caption="Сколько баллов отнять?")
        db.update_field("admins", id, "status", 4)

    if call.data == "add":
        n = db.get_field("admins", id, "user")
        db.update_field_name("users", n, "balance", db.get_field_name("users", n, "balance") + db.get_field("admins", id, "user_balance"))
        await call.message.answer_photo(photo=FSInputFile("images/aproved.png"), caption="Баллы успешно добавлены", reply_markup=kb3)
        db.update_field("admins", id, "status", 1)

    if call.data == "deduct":
        n = db.get_field("admins", id, "user")
        db.update_field_name("users", n, "balance", db.get_field_name("users", n, "balance") - db.get_field("admins", id, "user_balance"))
        await call.message.answer_photo(photo=FSInputFile("images/aproved.png"), caption="Баллы успешно отняты", reply_markup=kb3)
        db.update_field("admins", id, "status", 1)

    if call.data == "add_word":
        if db.get_daily(False) == None:
            await call.message.answer_photo(photo=FSInputFile("images/w1.jpg"), caption="Напишите свое слово, или добавьте случайное", reply_markup=kb10)
            db.update_field("admins", id, "status", 5)
        else:
            await call.message.answer_photo(photo=FSInputFile("images/sad.jpg"),
                                            caption="Бонусное слово уже добавляли сегодня", reply_markup=kb3)
            db.update_field("admins", id, "status", 1)

    if call.data == "rand_word":
        word = wg.get_rand_word()
        db.add_word(word)
        db.update_word(word, "date", datetime.now().date())
        db.update_field("admins", id, "status", 1)
        await call.message.answer_photo(photo=FSInputFile("images/aproved.png"),
                                        caption=f"Бонусное слово {word} успешно добавлено", reply_markup=kb3)

    # ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN ADMIN

    # USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER

    if call.data == "log_in":
        db.add_user(id, "users")
        await call.message.answer_photo(caption="Введите свое имя", photo=FSInputFile("images/login-icon-vector.jpg"))

    if call.data == "exit_user":
        await call.message.answer_photo(caption="Вы уверенны что хотите выйти?", photo=FSInputFile("images/question.jpg"), reply_markup=kb11)

    if call.data == "Y_user":
        db.delete_user(id, "users")

    if call.data == "prof":
        s = list(db.get_user(db.get_field("users", id, "name")))
        await call.message.answer_photo(photo=FSInputFile("images/user.jpeg"),
                                        caption=str(s[0]) + "\nScore: " + str(s[1]),
                                        reply_markup=kb8)

    if call.data == "user_menu":
        await call.message.answer_photo(photo=FSInputFile("images/i.jpg"), reply_markup=kb7)

    if call.data == "us_liderboard":
        s = db.get_users()
        s = sorted(s, reverse=True)
        await call.message.answer_photo(photo=FSInputFile("images/liderboardimg.png"), caption='\n'.join(
            ' Balance   '.join(str(item) for item in sublist[::-1]) for sublist in s), reply_markup=kb8)

    if call.data == "daily_word":
        if not db.get_field("users", id, "daily_word"):
            db.update_field("users", id, "status", 2)
            db.update_field("users", id, "daily_word", 1)
            await call.message.answer_photo(caption="Начали!\nПиши первое слово", photo=FSInputFile("images/wordle.jpg"))

        else:
            await call.message.answer_photo(caption="Ты уже играл сегодня.", photo=FSInputFile("images/stop.jpg"), reply_markup=kb8)

    if call.data == "bonus_word":
        if not db.get_field("users", id, "bonus_word") and db.get_daily(0) != None:
            db.update_field("users", id, "status", 3)
            db.update_field("users", id, "bonus_word", 1)
            await call.message.answer_photo(caption="Начали!\nПиши первое слово", photo=FSInputFile("images/wordle.jpg"))

        else:
            await call.message.answer_photo(caption="Бонусного слова пока нет.", photo=FSInputFile("images/stop.jpg"), reply_markup=kb8)

    # USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER USER



async def main():
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
