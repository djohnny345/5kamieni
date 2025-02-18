from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

class StartScreen(Screen):
    """ Ekran startowy z obrazkiem i przyciskiem do rozpoczęcia gry """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        # Dodanie obrazka (upewnij się, że obrazek jest w folderze projektu)
        layout.add_widget(Image(source="logo.png"))

        # Dodanie przycisku do rozpoczęcia gry
        start_button = Button(text="Rozpocznij grę", font_size=24, size_hint=(1, 0.3))
        start_button.bind(on_press=self.ask_player1_name)
        layout.add_widget(start_button)

        self.add_widget(layout)

    def ask_player1_name(self, instance):
        """ Prosi o nazwę pierwszego gracza """
        self.manager.current = "name_input"
        self.manager.get_screen("name_input").ask_for_name(1)


class NameInputScreen(Screen):
    """ Ekran do wpisywania nazw graczy """
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
        self.player_number = 1  # Domyślnie pierwszy gracz

    def ask_for_name(self, player_number):
        """ Aktualizuje ekran dla danego gracza """
        self.player_number = player_number
        self.label.text = f"Podaj nazwę {'pierwszego' if player_number == 1 else 'drugiego'} gracza:"
        self.text_input.text = ""

    def store_name(self, instance):
        """ Zapisuje nazwę gracza i przechodzi dalej """
        name = self.text_input.text.strip()
        if name:
            if self.player_number == 1:
                self.manager.get_screen("game").player1_name = name
                self.manager.get_screen("name_input").ask_for_name(2)
            else:
                self.manager.get_screen("game").player2_name = name
                self.manager.current = "game"

class GameBoard(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Dodaj obrazek jako tło (np. tablica szkolna)
        self.background = Image(source="school_blackboard.jpg", allow_stretch=True, keep_ratio=False)
        self.add_widget(self.background)

        # Parametry planszy
        self.rows = 8   # 8 wierszy
        self.cols = 12  # 12 kolumn
        self.button_size = 29  # Rozmiar przycisków
        self.spacing = 13  # Odstępy między przyciskami

        # Obliczenie pozycji startowej siatki (środek ekranu)
        screen_center_x = self.width / 2
        screen_center_y = self.height / 2

        grid_width = self.cols * (self.button_size + self.spacing) - self.spacing
        grid_height = self.rows * (self.button_size + self.spacing) - self.spacing

        start_x = 125

        start_y = 420  # Startujemy od góry

        # Tworzenie siatki przycisków
        self.buttons = {}
        for row in range(self.rows):
            for col in range(self.cols):
                button = Button(size_hint=(None, None), size=(self.button_size, self.button_size))
                button.pos = (start_x + col * (self.button_size + self.spacing),
                              start_y - row * (self.button_size + self.spacing))
                button.bind(on_press=self.on_button_click)
                self.buttons[(row, col)] = button
                self.add_widget(button)

        # Label wyniku nad planszą
        self.label_score = Label(text="0 : 0", size_hint=(None, None), size=(200, 50),
                                 pos=(screen_center_x + 230, start_y + 70))
        self.add_widget(self.label_score)

        # Inicjalizacja zmiennych gry
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = "O"

    def on_button_click(self, instance):
        """ Obsługuje kliknięcie przycisku (logika gry) """
        if instance.text == "":
            instance.text = self.current_player
            instance.disabled = True

            if self.check_winner():
                self.handle_winner(self.current_player)

            self.current_player = "X" if self.current_player == "O" else "O"

    def check_winner(self):
        """ Sprawdza, czy któryś gracz wygrał """
        # Sprawdzenie wierszy
        for row in range(self.rows):
            for col in range(self.cols - 4):  # 5 znaków w rzędzie
                symbols = [self.buttons[(row, col + i)].text for i in range(5)]
                if symbols.count("O") == 5 or symbols.count("X") == 5:
                    return True

        # Sprawdzenie kolumn
        for col in range(self.cols):
            for row in range(self.rows - 4):
                symbols = [self.buttons[(row + i, col)].text for i in range(5)]
                if symbols.count("O") == 5 or symbols.count("X") == 5:
                    return True

        # Sprawdzenie przekątnych ↘
        for row in range(self.rows - 4):
            for col in range(self.cols - 4):
                symbols = [self.buttons[(row + i, col + i)].text for i in range(5)]
                if symbols.count("O") == 5 or symbols.count("X") == 5:
                    return True

        # Sprawdzenie przekątnych ↙
        for row in range(4, self.rows):
            for col in range(self.cols - 4):
                symbols = [self.buttons[(row - i, col + i)].text for i in range(5)]
                if symbols.count("O") == 5 or symbols.count("X") == 5:
                    return True

        return False

    def handle_winner(self, winner_symbol):
        """ Obsługa wygranej rundy """
        if winner_symbol == "O":
            self.player1_score += 1
        else:
            self.player2_score += 1

        self.label_score.text = f"{self.player1_score} : {self.player2_score}"

        content = BoxLayout(orientation="vertical")
        result_label = Label(text=f"Rundę wygrywa {winner_symbol}! Czy chcecie kontynuować?", font_size=24)
        content.add_widget(result_label)

        button_layout = BoxLayout(size_hint=(1, 0.3))
        yes_button = Button(text="Tak", font_size=24)
        yes_button.bind(on_press=self.continue_game)
        no_button = Button(text="Nie", font_size=24)
        no_button.bind(on_press=self.end_game)
        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)

        content.add_widget(button_layout)

        popup = Popup(title="Koniec rundy", content=content, size_hint=(0.7, 0.5))
        popup.open()

    def continue_game(self, instance):
        """ Rozpoczęcie nowej rundy """
        instance.parent.parent.dismiss()
        self.reset_board()

    def end_game(self, instance):
        """ Koniec gry, powrót do menu """
        instance.parent.parent.dismiss()
        self.show_final_result()

    def reset_board(self):
        """ Resetuje planszę do stanu początkowego """
        for button in self.buttons.values():
            button.text = ""
            button.disabled = False

    def show_final_result(self):
        """ Pokazuje ostateczny wynik """
        if self.player1_score > self.player2_score:
            winner = "Gracz 1"
        elif self.player2_score > self.player1_score:
            winner = "Gracz 2"
        else:
            winner = "Remis"

        content = BoxLayout(orientation="vertical")
        result_label = Label(text=f"{winner} wygrywa wojnę!", font_size=24)
        content.add_widget(result_label)

        button_layout = BoxLayout(size_hint=(1, 0.3))
        back_button = Button(text="Wróć do menu", font_size=24)
        button_layout.add_widget(back_button)

        content.add_widget(button_layout)

        popup = Popup(title="Koniec gry", content=content, size_hint=(0.7, 0.5))
        popup.open()

class TicTacToeApp(App):
    """ Aplikacja Tic-Tac-Toe """
    def build(self):
        return GameBoard()

if __name__ == "__main__":
    TicTacToeApp().run()
