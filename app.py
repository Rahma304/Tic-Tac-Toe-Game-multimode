import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime
import random
import socket
import threading
import time

HISTORY_FILE = "history.json"


class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Multi Mode")
        self.root.geometry("450x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f0f1a")

        self.score_x = 0
        self.score_o = 0
        self.player_x = ""
        self.player_o = ""
        self.current_player = "X"
        self.board = [""] * 9
        self.history = []
        self.game_mode = None  # "single", "local", "online_host", "online_join"

        # Online multiplayer variables
        self.server_thread = None
        self.client_socket = None
        self.is_host = False
        self.connected = False

        self.load_history()
        self.start_screen()

    # ---------------- START SCREEN ----------------
    def start_screen(self):
        self.clear_screen()

        tk.Label(
            self.root,
            text="TIC TAC TOE",
            fg="#60a5fa",
            bg="#0f0f1a",
            font=("Segoe UI", 28, "bold")
        ).pack(pady=40)

        tk.Label(
            self.root,
            text="Select Game Mode",
            fg="#94a3b8",
            bg="#0f0f1a",
            font=("Segoe UI", 14)
        ).pack(pady=(0, 30))

        btn_frame = tk.Frame(self.root, bg="#0f0f1a")
        btn_frame.pack(pady=10)

        self.create_hover_button(
            btn_frame,
            text="Single Player\nvs AI",
            command=lambda: self.set_mode("single"),
            bg="#6366f1",
            hover_bg="#818cf8"
        ).pack(pady=12)

        self.create_hover_button(
            btn_frame,
            text="Local Multiplayer\nSame Device",
            command=lambda: self.set_mode("local"),
            bg="#ec4899",
            hover_bg="#f472b6"
        ).pack(pady=12)

        self.create_hover_button(
            btn_frame,
            text="Online Multiplayer\nDifferent Devices",
            command=self.online_mode_selection,
            bg="#10b981",
            hover_bg="#34d399"
        ).pack(pady=12)

        self.create_hover_button(
            self.root,
            text="View History",
            command=self.show_history,
            bg="#1e293b",
            hover_bg="#334155",
            width=20
        ).pack(pady=40)

    def create_hover_button(self, parent, text, command, bg, hover_bg, width=28):
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 13, "bold"),
            fg="white",
            bg=bg,
            activebackground=hover_bg,
            relief="flat",
            bd=0,
            padx=20,
            pady=15,
            width=width,
            command=command,
            cursor="hand2"
        )
        btn.pack()

        def on_enter(e): btn.config(bg=hover_bg)
        def on_leave(e): btn.config(bg=bg)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    # ---------------- MODE SELECTION ----------------
    def set_mode(self, mode):
        self.game_mode = mode
        self.show_name_inputs()

    def online_mode_selection(self):
        self.clear_screen()

        tk.Label(self.root, text="ONLINE MULTIPLAYER", fg="#34d399", bg="#0f0f1a",
                 font=("Segoe UI", 24, "bold")).pack(pady=40)

        tk.Label(self.root, text="Choose your role:", fg="#e0e7ff", bg="#0f0f1a",
                 font=("Segoe UI", 14)).pack(pady=20)

        # Get local IP
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
        except:
            local_ip = "127.0.0.1"

        ip_label = tk.Label(self.root,
                            text=f"Your IP: {local_ip}\n(Share this with friend to join)",
                            fg="#fbbf24", bg="#1e1b4b", font=("Consolas", 12),
                            padx=20, pady=10, relief="ridge")
        ip_label.pack(pady=20)

        btns = tk.Frame(self.root, bg="#0f0f1a")
        btns.pack(pady=30)

        self.create_hover_button(btns, "Host Game\n(You are X)", lambda: self.set_mode("online_host"), "#06b6d4", "#22d3ee")
        self.create_hover_button(btns, "Join Game\n(You are O)", self.join_game_prompt, "#f59e0b", "#f97316").pack(pady=15)
        self.create_hover_button(btns, "Back", self.start_screen, "#6b7280", "#9ca3af", width=15).pack(pady=10)

    def join_game_prompt(self):
        win = tk.Toplevel(self.root)
        win.title("Enter Host IP")
        win.geometry("300x200")
        win.configure(bg="#0f0f1a")

        tk.Label(win, text="Enter Host IP Address:", fg="#e0e7ff", bg="#0f0f1a",
                 font=("Segoe UI", 12)).pack(pady=20)

        entry = tk.Entry(win, font=("Segoe UI", 14), width=20, justify="center")
        entry.pack(pady=10)
        entry.insert(0, "192.168.")  # Hint

        def connect():
            ip = entry.get().strip()
            if ip:
                win.destroy()
                self.game_mode = "online_join"
                self.host_ip = ip
                self.show_name_inputs()

        tk.Button(win, text="Connect", command=connect, bg="#10b981", fg="white",
                  font=("Segoe UI", 12), padx=20, pady=8).pack(pady=20)

    # ---------------- NAME INPUT ----------------
    def show_name_inputs(self):
        self.clear_screen()

        mode_titles = {
            "single": "Single Player vs AI",
            "local": "Local Multiplayer",
            "online_host": "Online Host (You are X)",
            "online_join": "Online Join (You are O)"
        }

        tk.Label(self.root, text=mode_titles.get(self.game_mode, "Game Setup"),
                 fg="#60a5fa", bg="#0f0f1a", font=("Segoe UI", 20, "bold")).pack(pady=40)

        frame = tk.Frame(self.root, bg="#0f0f1a")
        frame.pack(pady=20)

        if self.game_mode in ["single", "online_host"]:
            tk.Label(frame, text="Your Name (X)", fg="#38bdf8", bg="#0f0f1a", font=("Segoe UI", 12)).pack()
            self.entry_x = tk.Entry(frame, font=("Segoe UI", 14), width=22, justify="center")
            self.entry_x.pack(pady=10)
            self.entry_x.insert(0, "Player X")

        if self.game_mode == "local":
            tk.Label(frame, text="Player X Name", fg="#38bdf8", bg="#0f0f1a", font=("Segoe UI", 12)).pack()
            self.entry_x = tk.Entry(frame, font=("Segoe UI", 14), width=22, justify="center")
            self.entry_x.pack(pady=10)

            tk.Label(frame, text="Player O Name", fg="#ec4899", bg="#0f0f1a", font=("Segoe UI", 12)).pack(pady=(20,0))
            self.entry_o = tk.Entry(frame, font=("Segoe UI", 14), width=22, justify="center")
            self.entry_o.pack(pady=10)

        if self.game_mode == "online_join":
            tk.Label(frame, text="Your Name (O)", fg="#ec4899", bg="#0f0f1a", font=("Segoe UI", 12)).pack()
            self.entry_o = tk.Entry(frame, font=("Segoe UI", 14), width=22, justify="center")
            self.entry_o.pack(pady=10)
            self.entry_o.insert(0, "Player O")

        btns = tk.Frame(self.root, bg="#0f0f1a")
        btns.pack(pady=40)

        self.create_hover_button(btns, "Start Game", self.start_game, "#10b981", "#34d399")
        self.create_hover_button(btns, "Back", self.start_screen, "#6b7280", "#9ca3af", width=15).pack(pady=10)

    # ---------------- GAME START ----------------
    def start_game(self):
        if self.game_mode in ["single", "local", "online_host"]:
            self.player_x = self.entry_x.get().strip() or "Player X"
        if self.game_mode in ["local"]:
            self.player_o = self.entry_o.get().strip() or "Player O"
        if self.game_mode == "online_join":
            self.player_o = self.entry_o.get().strip() or "Player O"

        if self.game_mode.startswith("online"):
            if self.game_mode == "online_host":
                self.is_host = True
                self.start_server()
            else:
                self.connect_to_host()
            return  # Wait for connection

        self.current_player = "X"
        self.board = [""] * 9
        self.game_screen()

    # ---------------- ONLINE LOGIC ----------------
    def start_server(self):
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
        self.waiting_screen("Waiting for opponent to connect...")

    def run_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('', 5555))
        server.listen(1)
        self.status_label.config(text="Waiting for connection...")
        client, addr = server.accept()
        self.client_socket = client
        self.connected = True
        self.root.after(0, lambda: self.finalize_online_game(True))

    def connect_to_host(self):
        threading.Thread(target=self.run_client, daemon=True).start()
        self.waiting_screen("Connecting to host...")

    def run_client(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.host_ip, 5555))
            self.client_socket = client
            self.connected = True
            self.root.after(0, lambda: self.finalize_online_game(False))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Connection Failed", f"Cannot connect to host:\n{e}"))

    def waiting_screen(self, msg):
        self.clear_screen()
        tk.Label(self.root, text=msg, fg="#fbbf24", bg="#0f0f1a",
                 font=("Segoe UI", 16)).pack(pady=200)
        self.status_label = tk.Label(self.root, text="", fg="#94a3b8", bg="#0f0f1a")
        self.status_label.pack(pady=20)

    def finalize_online_game(self, is_host):
        if not self.connected:
            return
        self.player_x = self.player_x if is_host else "Host"
        self.player_o = "Guest" if is_host else self.player_o
        self.current_player = "X"  # Host always starts
        self.board = [""] * 9
        self.game_screen()
        if not is_host:
            threading.Thread(target=self.receive_moves, daemon=True).start()
        else:
            threading.Thread(target=self.receive_moves, daemon=True).start()

    def send_move(self, index):
        if self.client_socket:
            try:
                self.client_socket.send(str(index).encode())
            except:
                messagebox.showerror("Error", "Connection lost!")

    def receive_moves(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if data:
                    index = int(data)
                    self.root.after(0, lambda i=index: self.online_opponent_move(i))
            except:
                break

    def online_opponent_move(self, index):
        if self.board[index] == "" and self.current_player != ("X" if self.is_host else "O"):
            self.make_move(index)

    # ---------------- GAME SCREEN & LOGIC ----------------
    def game_screen(self):
        self.clear_screen()

        mode_text = {"single": "vs AI", "local": "Local", "online_host": "Online (Host)", "online_join": "Online (Guest)"}.get(self.game_mode, "")
        tk.Label(self.root, text=f"{mode_text}\n{self.player_x} (X) vs {self.player_o} (O)",
                 fg="#e0e7ff", bg="#0f0f1a", font=("Segoe UI", 14)).pack(pady=(20,5))

        tk.Label(self.root, text=f"Score: {self.score_x} - {self.score_o}",
                 fg="#fbbf24", bg="#1e1b4b", font=("Segoe UI", 14), padx=20, pady=6, relief="ridge").pack(pady=5)

        self.status = tk.Label(self.root, text=f"{self.player_x if self.current_player == 'X' else self.player_o}'s Turn",
                               fg="#60a5fa", bg="#0f0f1a", font=("Segoe UI", 16, "bold"))
        self.status.pack(pady=20)

        board_frame = tk.Frame(self.root, bg="#0f0f1a")
        board_frame.pack(pady=10)

        self.buttons = []
        for i in range(9):
            btn = tk.Button(board_frame, text="", font=("Segoe UI", 36, "bold"), width=3, height=1,
                            bg="#1e293b", fg="#38bdf8", relief="raised", bd=4,
                            command=lambda idx=i: self.make_move(idx), cursor="hand2")
            btn.grid(row=i//3, column=i%3, padx=8, pady=8)
            self.buttons.append(btn)

            def on_enter(e, b=btn):
                if b["text"] == "": b.config(bg="#334155")
            def on_leave(e, b=btn):
                if b["text"] == "": b.config(bg="#1e293b")
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

        tk.Button(self.root, text="Main Menu", font=("Segoe UI", 12), bg="#ef4444", fg="white",
                  padx=20, pady=10, command=self.start_screen).pack(pady=30)

    def make_move(self, index):
        if self.board[index] != "":
            return

        # Online: only allow move if it's your turn
        my_symbol = "X" if (self.game_mode == "online_host" or (self.game_mode == "local" and self.current_player == "X")) else "O"
        if self.game_mode.startswith("online") and self.current_player != my_symbol:
            return

        symbol = self.current_player
        color = "#38bdf8" if symbol == "X" else "#ec4899"
        self.board[index] = symbol
        self.buttons[index].config(text=symbol, fg=color, state="disabled")

        if self.game_mode.startswith("online"):
            self.send_move(index)

        if self.check_winner():
            winner = self.player_x if symbol == "X" else self.player_o
            if symbol == "X": self.score_x += 1
            else: self.score_o += 1
            result = winner
            self.save_history(result)
            messagebox.showinfo("Victory!", f"{winner} Wins!")
            self.game_screen()
            return

        if "" not in self.board:
            self.save_history("Draw")
            messagebox.showinfo("Draw", "It's a Draw!")
            self.game_screen()
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        name = self.player_x if self.current_player == "X" else self.player_o
        self.status.config(text=f"{name}'s Turn")

        if self.game_mode == "single" and self.current_player == "O":
            self.root.after(600, self.ai_move)

    def ai_move(self):
        available = [i for i, v in enumerate(self.board) if v == ""]
        if available:
            self.make_move(random.choice(available))

    def check_winner(self):
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        for a,b,c in wins:
            if self.board[a] == self.board[b] == self.board[c] != "":
                for i in (a,b,c):
                    self.buttons[i].config(bg="#15803d")
                return True
        return False

    # ---------------- HISTORY ----------------
    def load_history(self):
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r") as f:
                    self.history = json.load(f)
        except:
            self.history = []

    def save_history(self, result):
        mode_name = {"single": "Single", "local": "Local", "online_host": "Online", "online_join": "Online"}.get(self.game_mode, self.game_mode)
        opponent = "AI" if self.game_mode == "single" else self.player_o
        self.history.append({
            "mode": mode_name,
            "player_x": self.player_x,
            "player_o": opponent,
            "result": result,
            "time": datetime.now().strftime("%b %d, %H:%M")
        })
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.history[-50:], f, indent=4)

    def show_history(self):
        win = tk.Toplevel(self.root)
        win.title("Match History")
        win.geometry("420x500")
        win.configure(bg="#0f0f1a")

        tk.Label(win, text="MATCH HISTORY", font=("Segoe UI", 16, "bold"), fg="#60a5fa", bg="#0f0f1a").pack(pady=15)

        text = tk.Text(win, bg="#1e1b4b", fg="#e0e7ff", font=("Consolas", 10), padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        for h in reversed(self.history):
            text.insert(tk.END, f"[{h['mode']}] {h['time']}\n{h['player_x']} vs {h['player_o']}\n→ {h['result']}\n{'-'*30}\n")

        text.config(state=tk.DISABLED)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    TicTacToe(root)
    root.mainloop()