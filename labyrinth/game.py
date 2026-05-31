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
        
        
        self.cell_size = 56
        self.panel_width = 400
    
        self.board_pixel_size = self.board.size * self.cell_size
        self.screen_width = self.board_pixel_size + self.panel_width
        self.screen_height = max(self.board_pixel_size, 720)
    
        self.fps = 60
    
        self.message = "Recull primer tots els anells de bronze."
    
        self.reset_button = None
        self.hint_button = None
        self.god_button = None
    
        self.hint_cell = None
        self.god_mode_active = False
        self.shortest_path = []
        self.recompute_shortest_path()

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
        panel_x = self.board_pixel_size + 40

        self.reset_button = pr.Rectangle(panel_x, 430, 320, 46)
        self.hint_button = pr.Rectangle(panel_x, 490, 320, 46)
        self.god_button = pr.Rectangle(panel_x, 550, 320, 46)

    def handle_input(self):
        self.handle_keyboard_input()
        self.handle_mouse_input()

    def handle_keyboard_input(self):
        key_moves = {
            pr.KEY_UP: (-1, 0), pr.KEY_W: (-1, 0),
            pr.KEY_DOWN: (1, 0), pr.KEY_S: (1, 0),
            pr.KEY_LEFT: (0, -1), pr.KEY_A: (0, -1),
            pr.KEY_RIGHT: (0, 1), pr.KEY_D: (0, 1)
        }
        actions = {
            pr.KEY_R: self.reset_game,
            pr.KEY_H: self.activate_hint_mode,
            pr.KEY_G: self.activate_god_mode
        }
        for key, move in key_moves.items():
            if pr.is_key_pressed(key):
                self.hint_cell = None
                if self.board.move_player(*move):
                    self.recompute_shortest_path()
                    self.update_message()
                else:
                    self.message = "Moviment no vàlid."
                return
        for key, action in actions.items():
            if pr.is_key_pressed(key):
                action()
                return

    def handle_mouse_input(self):
        if pr.is_mouse_button_pressed(pr.MOUSE_LEFT_BUTTON):
            mouse = pr.get_mouse_position()
            buttons = [
                (self.reset_button, self.reset_game),
                (self.hint_button, self.activate_hint_mode),
                (self.god_button, self.activate_god_mode)
            ]
            for button, action in buttons:
                if pr.check_collision_point_rec(mouse, button):
                    action()
                    break

    def reset_game(self):
        self.board.reset()
        self.hint_cell = None
        self.recompute_shortest_path()
        self.message = "Mapa reiniciat. Recull primer els bronze."

    def activate_hint_mode(self):
        if self.shortest_path and len(self.shortest_path) > 1:
            self.hint_cell = self.shortest_path[1]
            self.message = "Hint: Segueix la casella verda!"
        else:
            self.hint_cell = None
            self.message = "No s'ha trobat cap camí fins a l'or!"

    def activate_god_mode(self):
        self.god_mode_active = not self.god_mode_active
        if self.god_mode_active:
            if self.shortest_path:
                self.message = f"God Mode actiu! Camí de {len(self.shortest_path) - 1} passos trobat."
            else:
                self.message = "No s'ha trobat cap camí fins a l'or!"
        else:
            self.message = "God Mode desactivat."

    def recompute_shortest_path(self):
        if self.board.defeat:
            self.shortest_path = []
        else:
            self.shortest_path = get_astar_path(self.board)

    def update_message(self):
        if self.board.victory:
            self.message = "Has aconseguit l'anell d'or. Victòria!"
            return

        if self.board.defeat:
            self.message = f"Derrota! Has superat el cost mínim ({self.board.initial_min_cost}) en 5 o més punts."
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
        bg = pr.Color(45, 45, 50, 255) if cell == BARRIER else pr.Color(38, 40, 46, 255)
        pr.draw_rectangle(x, y, self.cell_size, self.cell_size, bg)
        pr.draw_rectangle_lines(x, y, self.cell_size, self.cell_size, pr.Color(90, 90, 100, 255))
        
        rings = {
            BRONZE: ("B", pr.Color(170, 95, 35, 255), pr.WHITE),
            SILVER: ("S", pr.Color(195, 200, 210, 255), pr.BLACK),
            GOLD: ("O", pr.Color(245, 190, 35, 255), pr.BLACK)
        }
        if cell == BARRIER:
            self.draw_barrier(x, y)
        elif cell in rings:
            self.draw_ring(x, y, *rings[cell])

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
        if not self.god_mode_active or not self.shortest_path:
            return

        path = self.shortest_path
        N = len(path)
        if N <= 1:
            return

        # Colors del gradient: de verd  a taronja
        start_color = pr.Color(80, 220, 120, 180)
        end_color = pr.Color(245, 150, 35, 180)

        for i in range(N - 1, 0, -1):
            row, col = path[i]

            t = i / (N - 1)
            r = int(start_color.r + t * (end_color.r - start_color.r))
            g = int(start_color.g + t * (end_color.g - start_color.g))
            b = int(start_color.b + t * (end_color.b - start_color.b))
            a = int(start_color.a + t * (end_color.a - start_color.a))
            color = pr.Color(r, g, b, a)

            x = col * self.cell_size
            y = row * self.cell_size

            # Dibuixem un rectangle una mica més reduït per a un efecte més polit
            pr.draw_rectangle(
                x + 8,
                y + 8,
                self.cell_size - 16,
                self.cell_size - 16,
                color,
            )

            # Dibuixem el número de pas en blanc amb contrast alt sobre un disc fosc
            text = str(i)
            font_size = 18
            text_width = pr.measure_text(text, font_size)
            center_x = x + self.cell_size // 2
            center_y = y + self.cell_size // 2

            pr.draw_circle(center_x, center_y, 12, pr.Color(20, 20, 25, 200))
            pr.draw_text(
                text,
                center_x - text_width // 2,
                center_y - 9,
                font_size,
                pr.WHITE,
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
    
        x = panel_x + 40
    
        pr.draw_text("Laberint de l'Anell d'Or", x, 36, 30, pr.WHITE)
    
        self.draw_stats(x, 100)
        self.draw_controls(x, 310)
        self.draw_buttons()
        self.draw_message(x, 610)

    def draw_stats(self, x, y):
        pr.draw_text("Estat", x, y, 24, pr.WHITE)
        
        line_gap = 26
        current_y = y + 36
        
        cost_diff = self.board.move_count - self.board.initial_min_cost
        if self.board.defeat:
            cost_color = pr.Color(220, 80, 80, 255)  # Vermell
        elif cost_diff > 0:
            cost_color = pr.Color(245, 150, 35, 255)  # Taronja
        else:
            cost_color = pr.Color(80, 220, 120, 255)  # Verd vibrant
            
        pr.draw_text(
            f"Cost: {self.board.move_count}/{self.board.initial_min_cost + 5}",
            x,
            current_y,
            20,
            cost_color,
        )
        
        current_y += line_gap
        
        pr.draw_text(
            f"Cost mínim: {self.board.initial_min_cost}",
            x,
            current_y,
            20,
            pr.Color(130, 200, 250, 255),
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

        current_y += line_gap

        shortest_path_len = len(self.shortest_path) - 1 if self.shortest_path else 0
        if self.board.victory:
            path_text = "Completat!"
            color = pr.Color(80, 220, 120, 255)
        elif self.board.defeat:
            path_text = "Derrota"
            color = pr.Color(220, 80, 80, 255)
        elif self.shortest_path:
            path_text = f"{shortest_path_len} pas" + ("s" if shortest_path_len != 1 else "")
            color = pr.Color(80, 220, 120, 255)
        else:
            path_text = "No disponible"
            color = pr.Color(220, 80, 80, 255)

        pr.draw_text(
            f"Camí restant: {path_text}",
            x,
            current_y,
            20,
            color,
        )

    def draw_controls(self, x, y):
        pr.draw_text("Controls", x, y, 24, pr.WHITE)
        
        controls = [
            "Fletxes / WASD: moure",
            "R: reiniciar mapa",
            "H: Hint Mode",
            "G: God Mode",
        ]
        
        current_y = y + 30
        
        for control in controls:
            pr.draw_text(control, x, current_y, 18, pr.LIGHTGRAY)
            current_y += 22

    def draw_buttons(self):
        self.draw_button(self.reset_button, "Reiniciar mapa")
        self.draw_button(self.hint_button, "Hint Mode")
        self.draw_button(self.god_button, "God Mode")

    def draw_button(self, rectangle, text):
        hover = pr.check_collision_point_rec(pr.get_mouse_position(), rectangle)
        color = pr.Color(78, 80, 96, 255) if hover else pr.Color(50, 52, 64, 255)
        border = pr.Color(185, 185, 210, 255) if hover else pr.Color(120, 120, 145, 255)
        pr.draw_rectangle_rec(rectangle, color)
        pr.draw_rectangle_lines_ex(rectangle, 2, border)
        text_x = int(rectangle.x + rectangle.width / 2 - pr.measure_text(text, 20) / 2)
        pr.draw_text(text, text_x, int(rectangle.y + rectangle.height / 2 - 10), 20, pr.WHITE)

    def draw_message(self, x, y):
        pr.draw_text("Missatge", x, y, 22, pr.WHITE)
        self.draw_wrapped_text(
            self.message,
            x,
            y + 34,
            18,
            self.panel_width - 80,
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