from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout


class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Image(source="logo.png"))

        start_button = Button(text="Rozpocznij grę", font_size=24, size_hint=(1, 0.3))
        start_button.bind(on_press=self.ask_player1_name)
        layout.add_widget(start_button)

        about_button = Button(text="Od autora", font_size=24, size_hint=(1, 0.3))
        about_button.bind(on_press=self.show_about)
        layout.add_widget(about_button)

        exit_button = Button(text="Zamknij grę", font_size=24, size_hint=(1, 0.3))
        exit_button.bind(on_press=self.exit_game)
        layout.add_widget(exit_button)

        self.add_widget(layout)

    def show_about(self, instance):
        self.manager.current = "about"

    def ask_player1_name(self, instance):
        self.manager.current = "name_input"
        self.manager.get_screen("name_input").ask_for_name(1)

    def exit_game(self, instance):
        App.get_running_app().stop()

class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # Próba wczytania pliku 'odautora.txt'
        try:
            with open("odautora.txt", "r", encoding="utf-8") as file:
                about_text = file.read()
        except FileNotFoundError:
            about_text = "Nie znaleziono pliku 'odautora.txt'."

        # Wyświetlenie tekstu z pliku
        about_label = Label(text=about_text, font_size=18, size_hint=(1, None), height=400)
        layout.add_widget(about_label)

        # Przycisk powrotu
        back_button = Button(text="Powrót", font_size=24, size_hint=(1, 0.2))
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "start"

class NameInputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.label = Label(text="Podaj nazwę pierwszego gracza:", font_size=24)
        self.layout.add_widget(self.label)

        self.text_input = TextInput(font_size=24, multiline=False)
        self.layout.add_widget(self.text_input)

        self.confirm_button = Button(text="Dalej", font_size=24, size_hint=(1, 0.3))
        self.confirm_button.bind(on_press=self.store_name)
        self.layout.add_widget(self.confirm_button)

        self.add_widget(self.layout)
        self.player_number = 1

    def ask_for_name(self, player_number):
        self.player_number = player_number
        self.label.text = f"Podaj nazwę {'pierwszego' if player_number == 1 else 'drugiego'} gracza:"
        self.text_input.text = ""

    def store_name(self, instance):
        name = self.text_input.text.strip()
        if name:
            game_screen = self.manager.get_screen("game")
            if self.player_number == 1:
                game_screen.player1_name = name
                self.ask_for_name(2)
            else:
                game_screen.player2_name = name
                game_screen.update_player_names()
                self.manager.current = "game"

from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.base import EventLoop


class GameBoard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.player1_name = "Gracz 1"
        self.player2_name = "Gracz 2"

        self.rows = 8
        self.cols = 12
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = "O"
        self.move_history = []  # Historia ruchów

        # Główny layout
        self.layout = FloatLayout()
        self.add_widget(self.layout)

        # Tło
        self.background = Image(source="school_blackboard.jpg",
                                allow_stretch=True, keep_ratio=False,
                                size_hint=(1, 1))
        self.layout.add_widget(self.background)

        # Pasek graczy
        self.label_players = Label(text=f"{self.player1_name} (O) vs {self.player2_name} (X)",
                                   font_size=24,
                                   size_hint=(None, None),
                                   size=(400, 50),
                                   pos_hint={"center_x": 0.5, "top": 0.95})
        self.layout.add_widget(self.label_players)

        # Wynik
        self.label_score = Label(text="0 : 0",
                                 size_hint=(None, None),
                                 size=(200, 50),
                                 pos_hint={"center_x": 0.5, "top": 0.9})
        self.layout.add_widget(self.label_score)

        # Siatka przycisków
        self.grid_layout = GridLayout(cols=self.cols, rows=self.rows, spacing=1,
                                      size_hint=(0.55, 0.55),
                                      pos_hint={"center_x": 0.49, "center_y": 0.45})
        self.layout.add_widget(self.grid_layout)

        # Dodaj przycisk menu w prawym górnym rogu
        self.menu_button = Button(text="Menu", size_hint=(None, None), size=(100, 50))
        self.menu_button.bind(on_press=self.show_menu)
        self.menu_button.pos_hint = {"right": 1, "top": 1}  # Ustawienie w prawym górnym rogu
        self.layout.add_widget(self.menu_button)

        # Inne przyciski w siatce gry
        self.buttons = {}
        for row in range(self.rows):
            for col in range(self.cols):
                button = Button(size_hint=(1, 1))  # Automatyczne skalowanie
                button.background_normal = ""
                button.background_down = ""
                button.background_color = (0, 0, 0, 0)  # Przezroczyste tło
                button.bind(on_press=self.on_button_click)
                self.buttons[(row, col)] = button
                self.grid_layout.add_widget(button)

    def update_player_names(self):
        """Metoda aktualizująca tekst na pasku graczy."""
        if self.current_player == "O":
            self.label_players.text = f"{self.player1_name} (O) vs {self.player2_name} (X)"
        else:
            self.label_players.text = f"{self.player1_name} (X) vs {self.player2_name} (O)"

    def show_menu(self, instance):
        content = BoxLayout(orientation="vertical", spacing=10)

        resume_button = Button(text="Powrót do gry", font_size=24)
        resume_button.bind(on_press=self.resume_game)

        undo_button = Button(text="Cofnij ruch", font_size=24)
        undo_button.bind(on_press=self.undo_move)

        main_menu_button = Button(text="Powrót do menu głównego", font_size=24)
        main_menu_button.bind(on_press=self.return_to_menu)

        content.add_widget(resume_button)
        content.add_widget(undo_button)
        content.add_widget(main_menu_button)

        self.popup = Popup(title="Menu", content=content, size_hint=(0.5, 0.5))
        self.popup.open()

    def resume_game(self, instance):
        self.popup.dismiss()

    def undo_move(self, instance):
        if self.move_history:
            # Cofnij ostatni ruch
            last_move = self.move_history.pop()
            row, col, player_symbol = last_move

            # Wyczyszczenie komórki
            self.buttons[(row, col)].text = ""
            self.buttons[(row, col)].disabled = False  # Ponownie aktywuj przycisk

            # Przywrócenie tury dla ostatniego gracza
            self.current_player = player_symbol
            self.update_player_names()

            self.popup.dismiss()

    def return_to_menu(self, instance):
        self.popup.dismiss()
        self.manager.current = "start"  # Zakładając, że ekran główny ma nazwę "start"

    def on_button_click(self, instance):
        if instance.text == "":  # Tylko, gdy komórka jest pusta
            instance.text = self.current_player
            instance.disabled = True  # Zablokowanie komórki po kliknięciu

            # Zapisz ruch w historii
            # Zmieniamy zapisywanie ruchu, by używać indeksów row i col, zamiast pos_hint
            for (row, col), button in self.buttons.items():
                if button == instance:
                    self.move_history.append((row, col, self.current_player))

            if self.check_winner():
                self.handle_winner(self.current_player)

            # Zmiana gracza
            self.current_player = "X" if self.current_player == "O" else "O"
            self.update_player_names()

    def check_winner(self):
        # Sprawdzenie wierszy
        for row in range(self.rows):
            for col in range(self.cols - 4):
                symbols = [self.buttons[(row, col + i)].text for i in range(5)]
                if symbols.count("O") == 5 or symbols.count("X") == 5:
                    return True

        # Sprawdzenie kolumn
        for col in range(self.cols):
            for row in range(self.rows - 4):
                symbols = [self.buttons[(row + i, col)].text for i in range(5)]
                if symbols.count("O") == 5 or symbols.count("X") == 5:
                    return True

        # Sprawdzenie ukośnych (↘)
        for row in range(self.rows - 4):
            for col in range(self.cols - 4):
                symbols = [self.buttons[(row + i, col + i)].text for i in range(5)]
                if symbols.count("O") == 5 or symbols.count("X") == 5:
                    return True

        # Sprawdzenie ukośnych (↙)
        for row in range(4, self.rows):
            for col in range(self.cols - 4):
                symbols = [self.buttons[(row - i, col + i)].text for i in range(5)]
                if symbols.count("O") == 5 or symbols.count("X") == 5:
                    return True

        return False

    def handle_winner(self, winner_symbol):
        winner_name = self.player1_name if winner_symbol == "O" else self.player2_name

        if winner_symbol == "O":
            self.player1_score += 1
        else:
            self.player2_score += 1

        self.label_score.text = f"{self.player1_score} : {self.player2_score}"

        content = BoxLayout(orientation="vertical")
        result_label = Label(text=f"{winner_name} wygrywa rundę! Czy chcecie kontynuować?", font_size=24)
        content.add_widget(result_label)

        button_layout = BoxLayout(size_hint=(1, 0.3))
        yes_button = Button(text="Kontynuuj", font_size=24)
        yes_button.bind(on_press=self.continue_game)
        no_button = Button(text="Powrót do menu", font_size=24)
        no_button.bind(on_press=self.return_to_menu)
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)

        content.add_widget(button_layout)

        self.popup = Popup(title="Koniec rundy", content=content, size_hint=(0.7, 0.5))
        self.popup.open()

    def continue_game(self, instance):
        self.popup.dismiss()
        self.reset_board()

    def return_to_menu(self, instance):
        self.popup.dismiss()
        self.reset_board()
        self.manager.current = "start"

    def reset_board(self):
        for button in self.buttons.values():
            button.text = ""
            button.disabled = False

class TicTacToeApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name="start"))
        sm.add_widget(NameInputScreen(name="name_input"))
        sm.add_widget(GameBoard(name="game"))
        sm.add_widget(AboutScreen(name="about"))
        return sm

if __name__ == "__main__":
    TicTacToeApp().run()
