import sqlite3
import pandas as pd


def clear_screen():
    print('\n' * 50)


def setup_database():
    conn = sqlite3.connect('mastermind_game.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT UNIQUE,
            wins INTEGER DEFAULT 0,
            guesses INTEGER
        )
    ''')
    conn.commit()
    conn.close()


setup_database()


def save_score(player_name, guesses):
    conn = sqlite3.connect('mastermind_game.db')
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT wins FROM scores WHERE player_name = ?", (player_name,))
        result = cursor.fetchone()

        if result:
            wins = result[0] + 1
            cursor.execute("UPDATE scores SET wins = ?, guesses = ? WHERE player_name = ?",
                           (wins, guesses, player_name))
        else:
            cursor.execute("INSERT INTO scores (player_name, wins, guesses) VALUES (?, ?, ?)",
                           (player_name, 1, guesses))

        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


def display_scores():
    conn = sqlite3.connect('mastermind_game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT player_name, wins, guesses FROM scores ORDER BY wins DESC")
    scores = cursor.fetchall()
    conn.close()

    print("\n--- Game Scores ---")
    for player_name, wins, guesses in scores:
        print(f"{player_name}: {wins} Win(s), {guesses} Guesses")

    display_scores_table()


def display_scores_table():
    conn = sqlite3.connect('mastermind_game.db')
    df = pd.read_sql_query("SELECT * FROM scores ORDER BY wins DESC", conn)
    conn.close()

    print("\n--- Game Scores Table ---")
    display(df)


def get_valid_guess():
    while True:
        guess = input("Enter your 5-digit guess (space-separated): ").split()
        if len(guess) == 5 and all(item.isdigit() and len(item) == 1 for item in guess):
            return guess
        print("Please enter exactly 5 space-separated digits.")


def give_feedback(secret, guess):
    feedback = [' '] * 5
    wrong_digits = []
    correct_count = 0

    for i in range(5):
        if guess[i] == secret[i]:
            feedback[i] = guess[i]
            correct_count += 1
        elif guess[i] not in secret:
            wrong_digits.append(guess[i])

    for i in range(5):
        if guess[i] != secret[i] and guess[i] in secret:
            if feedback[i] == ' ':
                feedback[i] = '_'

    return feedback, wrong_digits, correct_count


def get_valid_secret_number():
    while True:
        secret = input("Enter your secret 5-digit number (space-separated): ").split()
        if len(secret) == 5 and all(item.isdigit() and len(item) == 1 for item in secret):
            return secret
        print("Please enter exactly 5 space-separated digits.")


def mastermind_multiplayer():
    setup_database()
    try:

        player_1_name = input("Enter Player 1's name: ")
        player_2_name = input("Enter Player 2's name: ")

        print(f"{player_1_name}, enter your 5-digit secret number:")
        secret_1 = get_valid_secret_number()
        clear_screen()

        print(f"{player_2_name}, enter your 5-digit secret number:")
        secret_2 = get_valid_secret_number()
        clear_screen()

        player_1_guesses = 0
        player_2_guesses = 0

        while True:
            print(f"\n{player_1_name}'s turn to guess {player_2_name}'s secret number.")
            guess_1 = get_valid_guess()
            feedback_1, wrong_digits_1, correct_1 = give_feedback(secret_2, guess_1)
            print(f"Feedback: {' '.join(feedback_1)}")
            print(f"Wrong digits: {', '.join(wrong_digits_1)}")
            player_1_guesses += 1
            if correct_1 == 5:
                print(f"{player_1_name} wins in {player_1_guesses} guesses!")
                save_score(player_1_name, player_1_guesses)
                break

            choice = input("Type 'try again' to continue or 'exit' to end the game: ").strip().lower()
            if choice == 'exit':
                print("Game exited.")
                save_score(player_1_name, player_1_guesses)
                display_scores()
                return

            print(f"\n{player_2_name}'s turn to guess {player_1_name}'s secret number.")
            guess_2 = get_valid_guess()
            feedback_2, wrong_digits_2, correct_2 = give_feedback(secret_1, guess_2)
            print(f"Feedback: {' '.join(feedback_2)}")
            print(f"Wrong digits: {', '.join(wrong_digits_2)}")
            player_2_guesses += 1
            if correct_2 == 5:
                print(f"{player_2_name} wins in {player_2_guesses} guesses!")
                save_score(player_2_name, player_2_guesses)
                break

            choice = input("Type 'try again' to continue or 'exit' to end the game: ").strip().lower()
            if choice == 'exit':
                print("Game exited.")
                save_score(player_2_name, player_2_guesses)
                display_scores()
                return
    except:
        print("Exit of Game")

    display_scores()


mastermind_multiplayer()
