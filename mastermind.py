import tkinter as tk
from tkinter import messagebox, Toplevel
import sqlite3
import pandas as pd


# Database setup
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
        messagebox.showerror("Database Error", f"Database error: {e}")
    finally:
        conn.close()


def display_scores():
    conn = sqlite3.connect('mastermind_game.db')
    df = pd.read_sql_query("SELECT player_name, wins, guesses FROM scores ORDER BY wins DESC", conn)
    conn.close()

    score_window = Toplevel()
    score_window.title("Scores")
    score_text = tk.Text(score_window, wrap=tk.WORD, width=40, height=10)
    score_text.pack()
    score_text.insert(tk.END, df.to_string(index=False))


def set_secret_number(player_name, secret_var, root, callback, secrets):
    def on_submit():
        secret = secret_var.get()
        if len(secret) != 5 or not secret.isdigit():
            messagebox.showwarning("Invalid Input", "Secret number must be exactly 5 digits.")
        else:
            secrets[player_name] = list(secret)  # Store the secret in the secrets dictionary
            secret_window.destroy()  # Close the current window
            callback()  # Callback to show the next step

    secret_window = Toplevel(root)
    secret_window.title(f"{player_name} - Enter Secret Number")
    tk.Label(secret_window, text=f"{player_name}, enter your secret 5-digit number:").pack()
    secret_entry = tk.Entry(secret_window, textvariable=secret_var)
    secret_entry.pack()
    tk.Button(secret_window, text="Submit", command=on_submit).pack()



def mastermind_game():
    root = tk.Tk()
    root.title("Mastermind Game")

    # Game variables
    player_1_name = tk.StringVar()
    player_2_name = tk.StringVar()
    player_1_secret = tk.StringVar()
    player_2_secret = tk.StringVar()
    player_guess = tk.StringVar()
    current_turn = tk.StringVar(value="Player 1")
    feedback_label = None
    guesses = {"Player 1": 0, "Player 2": 0}
    secrets = {}  # Initialize secrets dictionary here

    def start_game():
        secret_label.config(text="Enter your 5-digit guess (space-separated):")
        tk.Button(root, text="Submit Guess", command=check_guess).pack()

    # Function to check each guess
    def check_guess():
        guess = player_guess.get().split()
        if len(guess) != 5 or not all(item.isdigit() for item in guess):
            messagebox.showwarning("Invalid Input", "Please enter exactly 5 digits separated by spaces.")
            return

        player = current_turn.get()
        guesses[player] += 1
        opponent = "Player 2" if player == "Player 1" else "Player 1"
        secret_to_guess = secrets[opponent]
        feedback, correct_count = give_feedback(secret_to_guess, guess)
        feedback_label.config(text=f"Feedback: {' '.join(feedback)}")

        if correct_count == 5:
            messagebox.showinfo("Game Over", f"{player} wins in {guesses[player]} guesses!")
            save_score(player_1_name.get() if player == "Player 1" else player_2_name.get(), guesses[player])
            root.quit()  # Exit game
        else:
            # Switch turns
            current_turn.set(opponent)
            guess_label.config(text=f"{current_turn.get()}'s turn to guess")

    # Function to provide feedback on a guess
    def give_feedback(secret, guess):
        feedback = ['_' for _ in range(5)]
        correct_count = 0
        for i in range(5):
            if guess[i] == secret[i]:
                feedback[i] = guess[i]  # Correct position and number
                correct_count += 1
            elif guess[i] in secret:
                feedback[i] = '*'  # Correct number but wrong position
        return feedback, correct_count

    # Function to start the game after both secrets are entered
    def on_secrets_entered():
        # Start the game only after both secrets have been entered
        start_game()

    # Reset game function
    def reset_game():
        player_1_name.set("")
        player_2_name.set("")
        player_1_secret.set("")
        player_2_secret.set("")
        player_guess.set("")
        current_turn.set("Player 1")
        feedback_label.config(text="Feedback: ")
        guesses["Player 1"] = 0
        guesses["Player 2"] = 0
        secrets.clear()
        secret_label.config(text="Waiting for players to enter secret numbers...")
        guess_label.config(text="Enter guess:")

    # Cancel game function
    def cancel_game():
        root.quit()

    # GUI layout
    tk.Label(root, text="Player 1 Name:").pack()
    tk.Entry(root, textvariable=player_1_name).pack()

    tk.Label(root, text="Player 2 Name:").pack()
    tk.Entry(root, textvariable=player_2_name).pack()

    tk.Button(root, text="Start Game", command=lambda: set_secret_number("Player 1", player_1_secret, root,
                                                                         lambda: set_secret_number("Player 2",
                                                                                                   player_2_secret,
                                                                                                   root,
                                                                                                   on_secrets_entered,
                                                                                                   secrets),
                                                                         secrets)).pack()

    secret_label = tk.Label(root, text="Waiting for players to enter secret numbers...")
    secret_label.pack()

    guess_label = tk.Label(root, text="Enter guess:")
    guess_label.pack()
    tk.Entry(root, textvariable=player_guess).pack()
    feedback_label = tk.Label(root, text="Feedback: ")
    feedback_label.pack()

    tk.Button(root, text="Show Scores", command=display_scores).pack()

    # Reset and Cancel buttons
    tk.Button(root, text="Reset Game", command=reset_game).pack()
    tk.Button(root, text="Cancel Game", command=cancel_game).pack()

    root.mainloop()


# Setup database and run the game
setup_database()
mastermind_game()
