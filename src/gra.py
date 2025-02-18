from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        layout.add_widget(Image(source="logo.png"))

        start_button = Button(text="Rozpocznij grę", font_size=24, size_hint=(1, 0.3))
        start_button.bind(on_press=self.ask_player1_name)
        layout.add_widget(start_button)



        exit_button = Button(text="Zamknij grę", font_size=24, size_hint=(1, 0.3))
        exit_button.bind(on_press=self.exit_game)
        layout.add_widget(exit_button)

        self.add_widget(layout)

    def ask_player1_name(self, instance):
        self.manager.current = "name_input"
        self.manager.get_screen("name_input").ask_for_name(1)

    def exit_game(self, instance):
        App.get_running_app().stop()

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

class GameBoard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.player1_name = "Gracz 1"
        self.player2_name = "Gracz 2"

        self.background = Image(source="school_blackboard.jpg", allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)

        self.rows = 8
        self.cols = 12
        self.button_size = 29
        self.spacing = 13

        self.label_players = Label(text=f"{self.player1_name} (O) vs {self.player2_name} (X)",
                                   font_size=24, size_hint=(None, None), size=(400, 50),
                                   pos=(400, 550))  # Dodana nazwa graczy
        self.add_widget(self.label_players)

        start_x = 125
        start_y = 420

        self.buttons = {}
        for row in range(self.rows):
            for col in range(self.cols):
                button = Button(size_hint=(None, None), size=(self.button_size, self.button_size))
                button.pos = (start_x + col * (self.button_size + self.spacing),
                              start_y - row * (self.button_size + self.spacing))
                button.bind(on_press=self.on_button_click)
                self.buttons[(row, col)] = button
                self.add_widget(button)

        self.label_score = Label(text="0 : 0", size_hint=(None, None), size=(200, 50),
                                 pos=(500, 500))
        self.add_widget(self.label_score)

        self.player1_score = 0
        self.player2_score = 0
        self.current_player = "O"

    def update_player_names(self):
        """ Aktualizuje wyświetlane nazwy graczy i ich kolor w zależności od tury """
        if self.current_player == "O":
            self.label_players.text = f"[color=00ff00]{self.player1_name} [/color](O) vs {self.player2_name} (X)"
        else:
            self.label_players.text = f"{self.player1_name} (O) vs [color=00ff00]{self.player2_name} [/color](X)"
        self.label_players.markup = True

    def on_button_click(self, instance):
        if instance.text == "":
            instance.text = self.current_player
            instance.disabled = True

            if self.check_winner():
                self.handle_winner(self.current_player)

            self.current_player = "X" if self.current_player == "O" else "O"
            if self.current_player == "O":
                self.label_players.text = f"[color=green]{self.player1_name} (O)[/color] vs {self.player2_name} (X)"
            else:
                self.label_players.text = f"{self.player1_name} (O) vs [color=green]{self.player2_name} (X)[/color]"
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
        return sm

if __name__ == "__main__":
    TicTacToeApp().run()
