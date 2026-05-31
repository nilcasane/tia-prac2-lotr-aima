import pyray as pr


from board import (
    Board,
    EMPTY,
    BARRIER,
    BRONZE,
    SILVER,
    GOLD,
    BRONZE_TOTAL,
    SILVER_TOTAL,
    GOLD_TOTAL,
)
from search import get_astar_path


class Game:
    def __init__(self):
        self.board = Board(size=12)
        
        
        self.cell_size = 48
        self.panel_width = 380
    
        self.board_pixel_size = self.board.size * self.cell_size
        self.screen_width = self.board_pixel_size + self.panel_width
        self.screen_height = max(self.board_pixel_size, 700)
    
        self.fps = 60
    
        self.message = "Recull primer tots els anells de bronze."
    
        self.reset_button = None
        self.hint_button = None
        self.god_button = None
    
        self.hint_cell = None
        self.god_path = []

    def run(self):
        pr.init_window(
            self.screen_width,
            self.screen_height,
            "TIA - Pràctica 2 - Laberint de l'Anell d'Or",
        )

        pr.set_target_fps(self.fps)

        self.create_buttons()

        while not pr.window_should_close():
            self.handle_input()
            self.draw()

        pr.close_window()

    def create_buttons(self):
        panel_x = self.board_pixel_size + 32

        self.reset_button = pr.Rectangle(panel_x, 470, 310, 46)
        self.hint_button = pr.Rectangle(panel_x, 530, 310, 46)
        self.god_button = pr.Rectangle(panel_x, 590, 310, 46)

    def handle_input(self):
        self.handle_keyboard_input()
        self.handle_mouse_input()

    def handle_keyboard_input(self):
        moved = False
        tried_to_move = False

        if pr.is_key_pressed(pr.KEY_UP) or pr.is_key_pressed(pr.KEY_W):
            tried_to_move = True
            moved = self.board.move_player(-1, 0)

        elif pr.is_key_pressed(pr.KEY_DOWN) or pr.is_key_pressed(pr.KEY_S):
            tried_to_move = True
            moved = self.board.move_player(1, 0)

        elif pr.is_key_pressed(pr.KEY_LEFT) or pr.is_key_pressed(pr.KEY_A):
            tried_to_move = True
            moved = self.board.move_player(0, -1)

        elif pr.is_key_pressed(pr.KEY_RIGHT) or pr.is_key_pressed(pr.KEY_D):
            tried_to_move = True
            moved = self.board.move_player(0, 1)

        elif pr.is_key_pressed(pr.KEY_R):
            self.reset_game()

        elif pr.is_key_pressed(pr.KEY_H):
            self.activate_hint_mode()

        elif pr.is_key_pressed(pr.KEY_G):
            self.activate_god_mode()

        if tried_to_move:
            self.hint_cell = None
            self.god_path = []

            if moved:
                self.update_message()
            else:
                self.message = "Moviment no vàlid."

    def handle_mouse_input(self):
        if not pr.is_mouse_button_pressed(pr.MOUSE_LEFT_BUTTON):
            return

        mouse_position = pr.get_mouse_position()

        if pr.check_collision_point_rec(mouse_position, self.reset_button):
            self.reset_game()

        elif pr.check_collision_point_rec(mouse_position, self.hint_button):
            self.activate_hint_mode()

        elif pr.check_collision_point_rec(mouse_position, self.god_button):
            self.activate_god_mode()

    def reset_game(self):
        self.board.reset()
        self.hint_cell = None
        self.god_path = []
        self.message = "Mapa reiniciat. Recull primer els bronze."

    def activate_hint_mode(self):
        path = get_astar_path(self.board)
        if len(path) > 1:
            self.hint_cell = path[1]
            self.message = "Hint: Segueix la casella verda!"
        else:
            self.hint_cell = None
            self.message = "No s'ha trobat cap camí fins a l'or!"

    def activate_god_mode(self):
        path = get_astar_path(self.board)
        if path:
            self.god_path = path
            self.message = f"God Mode actiu! Camí de {len(path) - 1} passos trobat."
        else:
            self.god_path = []
            self.message = "No s'ha trobat cap camí fins a l'or!"

    def update_message(self):
        if self.board.victory:
            self.message = "Has aconseguit l'anell d'or. Victòria!"
            return

        if self.board.bronze_collected < BRONZE_TOTAL:
            remaining = BRONZE_TOTAL - self.board.bronze_collected
            self.message = f"Et falten {remaining} anells de bronze."
            return

        if self.board.silver_collected < SILVER_TOTAL:
            remaining = SILVER_TOTAL - self.board.silver_collected
            self.message = f"Et falten {remaining} anells de plata."
            return

        self.message = "Ja pots recollir l'anell d'or."

    def draw(self):
        pr.begin_drawing()
        pr.clear_background(pr.Color(24, 24, 28, 255))

        self.draw_board()
        self.draw_god_path()
        self.draw_hint_cell()
        self.draw_player()
        self.draw_panel()

        pr.end_drawing()

    def draw_board(self):
        for row in range(self.board.size):
            for col in range(self.board.size):
                cell = self.board.grid[row][col]

                x = col * self.cell_size
                y = row * self.cell_size

                self.draw_cell(row, col, x, y, cell)

    def draw_cell(self, row, col, x, y, cell):
        background_color = self.get_cell_background_color(cell)

        pr.draw_rectangle(
            x,
            y,
            self.cell_size,
            self.cell_size,
            background_color,
        )

        pr.draw_rectangle_lines(
            x,
            y,
            self.cell_size,
            self.cell_size,
            pr.Color(90, 90, 100, 255),
        )

        if cell == BARRIER:
            self.draw_barrier(x, y)

        elif cell == BRONZE:
            self.draw_ring(x, y, "B", pr.Color(170, 95, 35, 255), pr.WHITE)

        elif cell == SILVER:
            self.draw_ring(x, y, "S", pr.Color(195, 200, 210, 255), pr.BLACK)

        elif cell == GOLD:
            self.draw_ring(x, y, "O", pr.Color(245, 190, 35, 255), pr.BLACK)

    def get_cell_background_color(self, cell):
        if cell == BARRIER:
            return pr.Color(45, 45, 50, 255)

        return pr.Color(38, 40, 46, 255)

    def draw_barrier(self, x, y):
        margin = 10

        pr.draw_rectangle(
            x + margin,
            y + margin,
            self.cell_size - margin * 2,
            self.cell_size - margin * 2,
            pr.Color(75, 75, 85, 255),
            )

        pr.draw_text(
            "#",
            x + self.cell_size // 2 - 6,
            y + self.cell_size // 2 - 11,
            24,
            pr.WHITE,
            )

    def draw_ring(self, x, y, text, circle_color, text_color):
        center_x = x + self.cell_size // 2
        center_y = y + self.cell_size // 2

        pr.draw_circle(center_x, center_y, 15, circle_color)

        text_width = pr.measure_text(text, 20)

        pr.draw_text(
            text,
            center_x - text_width // 2,
            center_y - 10,
            20,
            text_color,
            )

    def draw_player(self):
        row, col = self.board.player_position

        center_x = col * self.cell_size + self.cell_size // 2
        center_y = row * self.cell_size + self.cell_size // 2

        pr.draw_circle(center_x, center_y, 17, pr.Color(70, 160, 255, 255))
        pr.draw_circle_lines(center_x, center_y, 17, pr.WHITE)

        text = "P"
        text_width = pr.measure_text(text, 20)

        pr.draw_text(
            text,
            center_x - text_width // 2,
            center_y - 10,
            20,
            pr.WHITE,
            )

    def draw_hint_cell(self):
        if self.hint_cell is None:
            return

        row, col = self.hint_cell

        x = col * self.cell_size
        y = row * self.cell_size

        pr.draw_rectangle_lines_ex(
            pr.Rectangle(x + 3, y + 3, self.cell_size - 6, self.cell_size - 6),
            4,
            pr.Color(80, 220, 120, 255),
        )

    def draw_god_path(self):
        for row, col in self.god_path:
            x = col * self.cell_size
            y = row * self.cell_size

            pr.draw_rectangle(
                x + 8,
                y + 8,
                self.cell_size - 16,
                self.cell_size - 16,
                pr.Color(80, 220, 120, 90),
                )

    def draw_panel(self):
        panel_x = self.board_pixel_size

        pr.draw_rectangle(
            panel_x,
            0,
            self.panel_width,
            self.screen_height,
            pr.Color(29, 30, 36, 255),
        )
    
        x = panel_x + 32
    
        pr.draw_text("Laberint", x, 36, 30, pr.WHITE)
        pr.draw_text("de l'Anell d'Or", x, 72, 22, pr.LIGHTGRAY)
    
        self.draw_stats(x, 130)
        self.draw_controls(x, 305)
        self.draw_buttons()
        self.draw_message(x, 655)

    def draw_stats(self, x, y):
        pr.draw_text("Estat", x, y, 24, pr.WHITE)
        
        line_gap = 34
        current_y = y + 42
        
        pr.draw_text(
            f"Moviments: {self.board.move_count}",
            x,
            current_y,
            20,
            pr.LIGHTGRAY,
        )
        
        current_y += line_gap
        
        pr.draw_text(
            f"Bronze: {self.board.bronze_collected}/{BRONZE_TOTAL}",
            x,
            current_y,
            20,
            pr.Color(220, 155, 85, 255),
        )
        
        current_y += line_gap
        
        pr.draw_text(
            f"Plata: {self.board.silver_collected}/{SILVER_TOTAL}",
            x,
            current_y,
            20,
            pr.Color(220, 220, 230, 255),
        )
        
        current_y += line_gap
        
        pr.draw_text(
            f"Or: {self.board.gold_collected}/{GOLD_TOTAL}",
            x,
            current_y,
            20,
            pr.Color(245, 200, 60, 255),
        )

    def draw_controls(self, x, y):
        pr.draw_text("Controls", x, y, 24, pr.WHITE)
        
        controls = [
            "Fletxes / WASD: moure",
            "R: reiniciar mapa",
            "H: Hint Mode",
            "G: God Mode",
        ]
        
        current_y = y + 42
        
        for control in controls:
            pr.draw_text(control, x, current_y, 18, pr.LIGHTGRAY)
            current_y += 28

    def draw_buttons(self):
        self.draw_button(self.reset_button, "Reiniciar mapa")
        self.draw_button(self.hint_button, "Hint Mode")
        self.draw_button(self.god_button, "God Mode")

    def draw_button(self, rectangle, text):
        mouse_position = pr.get_mouse_position()
        is_hovered = pr.check_collision_point_rec(mouse_position, rectangle)
        
        if is_hovered:
            color = pr.Color(78, 80, 96, 255)
            border_color = pr.Color(185, 185, 210, 255)
        else:
            color = pr.Color(50, 52, 64, 255)
            border_color = pr.Color(120, 120, 145, 255)
        
        pr.draw_rectangle_rec(rectangle, color)
        pr.draw_rectangle_lines_ex(rectangle, 2, border_color)
        
        text_width = pr.measure_text(text, 20)
        text_x = int(rectangle.x + rectangle.width / 2 - text_width / 2)
        text_y = int(rectangle.y + rectangle.height / 2 - 10)
        
        pr.draw_text(text, text_x, text_y, 20, pr.WHITE)

    def draw_message(self, x, y):
        pr.draw_text("Missatge", x, y, 22, pr.WHITE)
        self.draw_wrapped_text(
            self.message,
            x,
            y + 34,
            18,
            self.panel_width - 64,
            pr.LIGHTGRAY,
            )

    def draw_wrapped_text(self, text, x, y, font_size, max_width, color):
        words = text.split()
        line = ""
        current_y = y
    
        for word in words:
            test_line = line + word + " "
            test_width = pr.measure_text(test_line, font_size)
    
            if test_width > max_width and line:
                pr.draw_text(line.strip(), x, current_y, font_size, color)
                line = word + " "
                current_y += font_size + 8
            else:
                line = test_line
    
        if line:
            pr.draw_text(line.strip(), x, current_y, font_size, color)