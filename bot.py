import telebot
from telebot import types
import random

# --- ВСТАВЬ СВОЙ ТОКЕН ТУТ ---
TOKEN = "9231437945:AAEa_TaU9DYjKHzZyUYwp7hmzsqzcfWEJhc"
# -----------------------------

bot = telebot.TeleBot(TOKEN)

number_games = {}
word_games = {}
ttt_games = {}

# Словарь слов и подсказок к ним
WORDS_DATA = {
    "программирование": ["Это процесс создания кода", "Без этого не работает ни одна игра", "Этим занимаются разработчики"],
    "телеграм": ["Это мессенджер", "Там живут боты", "У него есть бумажный самолетик на иконке"],
    "питон": ["Это язык программирования", "Назван в честь комиков, а не змеи", "На нем мы пишем этого бота"],
    "компьютер": ["Устройство для работы и игр", "Состоит из монитора и системного блока", "На нем ты сейчас запускаешь VS Code"],
    "клавиатура": ["Устройство ввода", "На ней много кнопок", "Ты стучишь по ней, когда пишешь"],
    "интернет": ["Всемирная сеть", "Позволяет общаться на расстоянии", "Без него бот бы не работал"],
    "робот": ["Механизм, который может работать сам", "Иногда похож на человека", "Слово происходит от чешского 'robota'"]
}

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🎮 Угадай число")
    btn2 = types.KeyboardButton("✂️ Камень-Ножницы-Бумага")
    btn3 = types.KeyboardButton("🔤 Угадай слово")
    btn4 = types.KeyboardButton("❌ Крестики-нолики")
    btn5 = types.KeyboardButton("🧠 ИИ скоро...")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

def get_game_menu(show_hint=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if show_hint:
        markup.add(types.KeyboardButton("💡 Подсказка"))
    btn_back = types.KeyboardButton("🔙 Главное меню")
    markup.add(btn_back)
    return markup

@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    if chat_id in number_games: del number_games[chat_id]
    if chat_id in word_games: del word_games[chat_id]
    if chat_id in ttt_games: del ttt_games[chat_id]
    bot.send_message(chat_id, "Привет! Выбери действие 👇", reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: message.text == "🔙 Главное меню")
def back_to_menu(message):
    chat_id = message.chat.id
    if chat_id in number_games: del number_games[chat_id]
    if chat_id in word_games: del word_games[chat_id]
    if chat_id in ttt_games: del ttt_games[chat_id]
    bot.send_message(chat_id, "Возвращаемся в меню!", reply_markup=get_main_menu())

# --- ИГРА 1: УГАДАЙ ЧИСЛО ---
@bot.message_handler(func=lambda message: message.text == "🎮 Угадай число")
def start_number_game(message):
    number_games[message.chat.id] = random.randint(1, 50)
    bot.send_message(message.chat.id, "Я загадал число от 1 до 50. Пиши вариант!", reply_markup=get_game_menu())

# --- ИГРА 2: КАМЕНЬ-НОЖНИЦЫ-БУМАГА ---
@bot.message_handler(func=lambda message: message.text == "✂️ Камень-Ножницы-Бумага")
def start_rps_game(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Камень 🪨"), types.KeyboardButton("Ножницы ✂️"), types.KeyboardButton("Бумага 📄"))
    markup.add(types.KeyboardButton("🔙 Главное меню"))
    bot.send_message(message.chat.id, "Твой ход!", reply_markup=markup)

# --- ИГРА 3: УГАДАЙ СЛОВО (С ПОДСКАЗКАМИ И ВВОДОМ СЛОВА) ---
@bot.message_handler(func=lambda message: message.text == "🔤 Угадай слово")
def start_word_game(message):
    chat_id = message.chat.id
    secret_word = random.choice(list(WORDS_DATA.keys()))
    hidden_word = "*" * len(secret_word)
    
    word_games[chat_id] = {
        "word": secret_word,
        "hidden": hidden_word,
        "guessed_letters": [],
        "hints_used": 0,
        "hints": WORDS_DATA[secret_word]
    }
    bot.send_message(
        chat_id, 
        f"Я загадал слово из {len(secret_word)} букв:\n{hidden_word}\n\nПиши буквы или сразу целое слово!", 
        reply_markup=get_game_menu(show_hint=True)
    )

@bot.message_handler(func=lambda message: message.text == "💡 Подсказка")
def give_hint(message):
    chat_id = message.chat.id
    if chat_id not in word_games: return
    
    game = word_games[chat_id]
    if game["hints_used"] >= 3:
        bot.send_message(chat_id, "Ты уже использовал все 3 подсказки! Дальше только сам.")
        return
        
    hint = game["hints"][game["hints_used"]]
    game["hints_used"] += 1
    remaining = 3 - game["hints_used"]
    bot.send_message(chat_id, f"💡 Подсказка {game['hints_used']}: {hint}\n(Осталось подсказок: {remaining})")

# --- ИГРА 4: КРЕСТИКИ-НОЛИКИ (УМНЫЙ БОТ) ---
@bot.message_handler(func=lambda message: message.text == "❌ Крестики-нолики")
def choose_ttt_side(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup()
    btn_x = types.InlineKeyboardButton("Играть за ❌", callback_data="ttt_start_X")
    btn_o = types.InlineKeyboardButton("Играть за ⭕", callback_data="ttt_start_O")
    markup.add(btn_x, btn_o)
    bot.send_message(chat_id, "Выбери, кем ты будешь играть:", reply_markup=markup)

def draw_board(board, game_over=False):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for i in range(9):
        if board[i] == "X": text = "❌"
        elif board[i] == "O": text = "⭕"
        else: text = "·"
        
        btn = types.InlineKeyboardButton(text=text, callback_data=f"ttt_move_{i}" if board[i] == "" and not game_over else "none")
        buttons.append(btn)
    markup.add(*buttons)
    
    if game_over:
        markup.add(types.InlineKeyboardButton("🔄 Играть заново", callback_data="ttt_restart"))
    return markup

def draw_text_board(board):
    res = ""
    for i in range(9):
        if board[i] == "X": res += "❌"
        elif board[i] == "O": res += "⭕"
        else: res += "⬜"
        if (i + 1) % 3 == 0: res += "\n"
    return res

def check_win(board, symbol):
    win_combos = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in win_combos:
        if board[a] == board[b] == board[c] == symbol:
            return True
    return False

def get_smart_move(board, bot_symbol, player_symbol):
    # 1. Бот выигрывает?
    for i in range(9):
        if board[i] == "":
            board[i] = bot_symbol
            if check_win(board, bot_symbol):
                board[i] = ""
                return i
            board[i] = ""
            
    # 2. Игрок выигрывает? Блокируем.
    for i in range(9):
        if board[i] == "":
            board[i] = player_symbol
            if check_win(board, player_symbol):
                board[i] = ""
                return i
            board[i] = ""
            
    # 3. Центр
    if board[4] == "": return 4
        
    # 4. Углы
    corners = [0, 2, 6, 8]
    empty_corners = [c for c in corners if board[c] == ""]
    if empty_corners: return random.choice(empty_corners)
        
    # 5. Любая
    empty_cells = [i for i, val in enumerate(board) if val == ""]
    if empty_cells: return random.choice(empty_cells)
    return None

@bot.callback_query_handler(func=lambda call: call.data.startswith("ttt_start_"))
def start_ttt_game(call):
    chat_id = call.message.chat.id
    player_symbol = call.data.split("_")[2]
    bot_symbol = "O" if player_symbol == "X" else "X"
    
    ttt_games[chat_id] = {"board": [""] * 9, "player": player_symbol, "bot": bot_symbol}
    
    if player_symbol == "O":
        move = get_smart_move(ttt_games[chat_id]["board"], bot_symbol, player_symbol)
        ttt_games[chat_id]["board"][move] = bot_symbol
    
    icon = "❌" if player_symbol == "X" else "⭕"
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"Ты играешь за {icon}. Твой ход:",
        reply_markup=draw_board(ttt_games[chat_id]["board"])
    )

@bot.callback_query_handler(func=lambda call: call.data == "ttt_restart")
def restart_ttt_game(call):
    chat_id = call.message.chat.id
    if chat_id in ttt_games: del ttt_games[chat_id]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Играть за ❌", callback_data="ttt_start_X"))
    markup.add(types.InlineKeyboardButton("Играть за ⭕", callback_data="ttt_start_O"))
    bot.edit_message_text("Выбери, кем ты будешь играть в этот раз:", chat_id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ttt_move_"))
def handle_ttt_move(call):
    chat_id = call.message.chat.id
    if chat_id not in ttt_games: 
        bot.answer_callback_query(call.id, "Игра не найдена.")
        return
    
    game = ttt_games[chat_id]
    board = game["board"]
    move = int(call.data.split("_")[2])
    
    if board[move] != "":
        bot.answer_callback_query(call.id, "Занято!")
        return

    board[move] = game["player"]
    
    if check_win(board, game["player"]):
        bot.edit_message_text(f"Ты победил! 🎉\n\n{draw_text_board(board)}", chat_id, call.message.message_id, reply_markup=draw_board(board, game_over=True), parse_mode="HTML")
        return
    if "" not in board:
        bot.edit_message_text(f"Ничья! 🤝\n\n{draw_text_board(board)}", chat_id, call.message.message_id, reply_markup=draw_board(board, game_over=True), parse_mode="HTML")
        return
        
    bot_move = get_smart_move(board, game["bot"], game["player"])
    if bot_move is not None: board[bot_move] = game["bot"]
    
    if check_win(board, game["bot"]):
        bot.edit_message_text(f"Я победил! 🤖\n\n{draw_text_board(board)}", chat_id, call.message.message_id, reply_markup=draw_board(board, game_over=True), parse_mode="HTML")
        return
    if "" not in board:
        bot.edit_message_text(f"Ничья! 🤝\n\n{draw_text_board(board)}", chat_id, call.message.message_id, reply_markup=draw_board(board, game_over=True), parse_mode="HTML")
        return

    bot.edit_message_text("Твой ход:", chat_id, call.message.message_id, reply_markup=draw_board(board))

# --- ОБРАБОТКА ТЕКСТА (Все игры) ---
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.lower()

    if message.text == "🧠 ИИ скоро...":
        bot.send_message(chat_id, "🧠 ИИ скоро появится! Я еще учусь думать. Пока что поиграй в игры 😉", reply_markup=get_game_menu())
        return

    if text in ["камень 🪨", "ножницы ✂️", "бумага 📄"]:
        player = text.split()[0] 
        comp = random.choice(["камень", "ножницы", "бумага"])
        bot.send_message(chat_id, f"Я выбрал: {comp}")
        if player == comp: bot.send_message(chat_id, "Ничья! 🤝")
        elif (player == "камень" and comp == "ножницы") or (player == "ножницы" and comp == "бумага") or (player == "бумага" and comp == "камень"):
            bot.send_message(chat_id, "Ты победил! 🎉")
        else: bot.send_message(chat_id, "Я победил! 🤖")
        return

    if chat_id in number_games:
        try: guess = int(message.text)
        except ValueError: pass
        else:
            secret = number_games[chat_id]
            if guess < secret: bot.send_message(chat_id, "Больше! ⬆️")
            elif guess > secret: bot.send_message(chat_id, "Меньше! ⬇️")
            else:
                bot.send_message(chat_id, "Угадал! 🎉", reply_markup=get_main_menu())
                del number_games[chat_id]
            return

    if chat_id in word_games:
        game = word_games[chat_id]
        user_input = message.text.lower().strip()
        
        # Проверка на ввод целого слова
        if len(user_input) > 1:
            if user_input == game["word"]:
                bot.send_message(chat_id, f"Поздравляю! Ты угадал слово целиком: {game['word']} 🎉", reply_markup=get_main_menu())
                del word_games[chat_id]
            else:
                bot.send_message(chat_id, f"❌ Это не то слово. Попробуй еще раз или вводи по одной букве!")
            return
            
        # Проверка на ввод одной буквы
        if len(user_input) == 1 and user_input.isalpha():
            letter = user_input
            if letter in game["guessed_letters"]:
                bot.send_message(chat_id, "Ты уже называл эту букву!")
                return
            game["guessed_letters"].append(letter)
            
            if letter in game["word"]:
                new_hidden = ""
                for i in range(len(game["word"])):
                    if game["word"][i] == letter or game["hidden"][i] != "*":
                        new_hidden += game["word"][i]
                    else:
                        new_hidden += "*"
                game["hidden"] = new_hidden
                
                if "*" not in new_hidden:
                    bot.send_message(chat_id, f"Поздравляю! Ты угадал слово: {game['word']} 🎉", reply_markup=get_main_menu())
                    del word_games[chat_id]
                else:
                    bot.send_message(chat_id, f"Есть такая буква! ✅\n{new_hidden}")
            else:
                bot.send_message(chat_id, f"Такой буквы нет ❌\n{game['hidden']}")
            return
            
        bot.send_message(chat_id, "Пожалуйста, введи ОДНУ букву или ЦЕЛОЕ слово.")
        return

    bot.send_message(chat_id, "Нажми на кнопки внизу!", reply_markup=get_main_menu())

print("Бот запущен!")
bot.infinity_polling()