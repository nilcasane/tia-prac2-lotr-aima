import pyray as pr
from board import Board, CardType


class Game:
    def __init__(self):
        pr.init_window(1600, 900, "Card Game")
        pr.set_target_fps(60)

        self.board = Board()
        self.message = "Welcome to the Card Game!"

        self.button_width = 180
        self.button_height = 50
        self.button_spacing = 15

        self.bronze_texture = pr.load_texture(
            "../resources/anell-bronze.jpeg"
        )

        self.deck_texture = pr.load_texture(
            "../resources/deck.png"
        )

        self.silver_texture = pr.load_texture(
            "../resources/anell-plata.jpeg"
        )

        self.gold_texture = pr.load_texture(
            "../resources/anell-or.jpeg"
        )

        self.buttons = [
            ("Draw Card", self.board.draw_card),
            ("Release Card", self.board.release_current_card),
            ("Reserve Card", self.board.reserve_current_card),
            ("Release Reserved", self.board.release_reserved_card),
            ("Return To Deck", self.board.return_card_to_deck),
            ("Block Opponent", self.board.block_opponent),
            ("End Turn", self.end_turn),
        ]

    def end_turn(self):
        self.board.switch_turn()

        if self.board.current_player == self.board.ai_player:
            action = self.board.ai_turn()
            self.message = f"AI executed: {action}"

            if not self.board.game_over:
                self.board.switch_turn()
        else:
            self.message = f"Turn switched to {self.board.current_player.name}"

        return True

    def draw_card(self, card, x, y):

        width = 120
        height = 180

        if card == CardType.BRONZE:

            pr.draw_texture_pro(
                self.bronze_texture,
                pr.Rectangle(
                    0,
                    0,
                    self.bronze_texture.width,
                    self.bronze_texture.height
                ),
                pr.Rectangle(
                    x,
                    y,
                    width,
                    height
                ),
                pr.Vector2(0, 0),
                0,
                pr.WHITE
            )

        elif card == CardType.SILVER:

            pr.draw_texture_pro(
                self.silver_texture,
                pr.Rectangle(
                    0,
                    0,
                    self.silver_texture.width,
                    self.silver_texture.height
                ),
                pr.Rectangle(
                    x,
                    y,
                    width,
                    height
                ),
                pr.Vector2(0, 0),
                0,
                pr.WHITE
            )

        elif card == CardType.GOLD:

            pr.draw_texture_pro(
                self.gold_texture,
                pr.Rectangle(
                    0,
                    0,
                    self.gold_texture.width,
                    self.gold_texture.height
                ),
                pr.Rectangle(
                    x,
                    y,
                    width,
                    height
                ),
                pr.Vector2(0, 0),
                0,
                pr.WHITE
            )

        else:

            pr.draw_rectangle(
                x,
                y,
                width,
                height,
                pr.DARKGRAY
            )

            pr.draw_rectangle_lines(
                x,
                y,
                width,
                height,
                pr.WHITE
            )

            pr.draw_text(
                "EMPTY",
                x + 18,
                y + 80,
                20,
                pr.WHITE
            )

    def draw_released_cards(self, player, x, y, reverse=False):

        card_width = 40
        card_height = 60
        spacing = 8

        pr.draw_text("Released Bronze", x, y - 30, 16, pr.WHITE)
        pr.draw_text("Released Silver", x, y + 90, 16, pr.WHITE)
        pr.draw_text("Released Gold", x, y + 210, 16, pr.WHITE)

        # BRONZE
        for i in range(player.bronze_released):

            if reverse:
                card_x = x - i * (card_width + spacing)
            else:
                card_x = x + i * (card_width + spacing)

            pr.draw_texture_pro(
                self.bronze_texture,
                pr.Rectangle(
                    0,
                    0,
                    self.bronze_texture.width,
                    self.bronze_texture.height
                ),
                pr.Rectangle(
                    card_x,
                    y,
                    card_width,
                    card_height
                ),
                pr.Vector2(0, 0),
                0,
                pr.WHITE
            )

        # SILVER
        for i in range(player.silver_released):

            if reverse:
                card_x = x - i * (card_width + spacing)
            else:
                card_x = x + i * (card_width + spacing)

            pr.draw_texture_pro(
                self.silver_texture,
                pr.Rectangle(
                    0,
                    0,
                    self.silver_texture.width,
                    self.silver_texture.height
                ),
                pr.Rectangle(
                    card_x,
                    y + 120,
                    card_width,
                    card_height
                ),
                pr.Vector2(0, 0),
                0,
                pr.WHITE
            )

        # GOLD
        for i in range(player.gold_released):

            if reverse:
                card_x = x - i * (card_width + spacing)
            else:
                card_x = x + i * (card_width + spacing)

            pr.draw_texture_pro(
                self.gold_texture,
                pr.Rectangle(
                    0,
                    0,
                    self.gold_texture.width,
                    self.gold_texture.height
                ),
                pr.Rectangle(
                    card_x,
                    y + 240,
                    card_width,
                    card_height
                ),
                pr.Vector2(0, 0),
                0,
                pr.WHITE
            )
    def draw_player_panel(self, player, x, y):
        pr.draw_text(player.name, x, y, 30, pr.WHITE)
        pr.draw_text("Current Card", x, y + 40, 20, pr.WHITE)
        self.draw_card(player.current_card, x, y + 70)
        pr.draw_text("Reserved Card", x, y + 280, 20, pr.WHITE)
        self.draw_card(player.reserved_card, x, y + 310)

    def draw_deck(self):

        deck_width = 160
        deck_height = 240

        human_x = 460
        ai_x = 670
        y = 220

        # HUMAN DECK

        pr.draw_texture_pro(
            self.deck_texture,
            pr.Rectangle(
                0,
                0,
                self.deck_texture.width,
                self.deck_texture.height
            ),
            pr.Rectangle(
                human_x,
                y,
                280,
                260
            ),
            pr.Vector2(0, 0),
            0,
            pr.WHITE
        )

        pr.draw_text(
            "HUMAN DECK",
            human_x + 60,
            y - 40,
            20,
            pr.WHITE
        )

        pr.draw_text(
            "",
            human_x + 40,
            y + 100,
            30,
            pr.WHITE
        )

        pr.draw_text(
            f"Cards Left: {len(self.board.human_player.deck)}",
            human_x + 75,
            y + 260,
            20,
            pr.WHITE
        )

        # AI DECK

        pr.draw_texture_pro(
            self.deck_texture,
            pr.Rectangle(
                0,
                0,
                self.deck_texture.width,
                self.deck_texture.height
            ),
            pr.Rectangle(
                ai_x,
                y,
                280,
                260
            ),
            pr.Vector2(0, 0),
            0,
            pr.WHITE
        )

        pr.draw_text(
            "AI DECK",
            ai_x + 75,
            y - 40,
            20,
            pr.WHITE
        )

        pr.draw_text(
            "",
            ai_x + 40,
            y + 100,
            30,
            pr.WHITE
        )

        pr.draw_text(
            f"Cards Left: {len(self.board.ai_player.deck)}",
            ai_x + 70,
            y + 260,
            20,
            pr.WHITE
        )

    def draw_buttons(self):
        y = 790
        x = 20

        for label, action in self.buttons:
            if pr.gui_button(pr.Rectangle(x, y, self.button_width, self.button_height), label):
                if not self.board.game_over:
                    result = action()
                    if result is False:
                        self.message = f"Action failed: {label}"
                    else:
                        self.message = f"Action executed: {label}"

                        if label != "End Turn":
                            self.end_turn()
                else:
                    self.message = "Game Over"
            x += self.button_width + self.button_spacing

    def draw_message_panel(self):
        pr.draw_rectangle(0, 850, 1600, 50, pr.DARKGRAY)
        pr.draw_text(self.message, 20, 865, 20, pr.WHITE)

    def run(self):
        while not pr.window_should_close():
            pr.begin_drawing()
            pr.clear_background(pr.BLACK)

            pr.draw_text(f"Current Turn: {self.board.current_player.name}", 650, 20, 30, pr.WHITE)
            pr.draw_text(f"Turn Count: {self.board.turn_count}", 650, 60, 24, pr.LIGHTGRAY)

            self.draw_player_panel(self.board.human_player, 20, 100)
            self.draw_player_panel(self.board.ai_player, 1360, 100)

            self.draw_deck()


            self.draw_released_cards(
                self.board.human_player,
                230,
                260,
                False
            )

            self.draw_released_cards(
                self.board.ai_player,
                980,
                260,
                False
            )

            self.draw_buttons()
            self.draw_message_panel()

            if self.board.game_over:
                pr.draw_text(f"WINNER: {self.board.winner.name}", 650, 420, 40, pr.GREEN)

            pr.end_drawing()

        pr.unload_texture(self.bronze_texture)
        pr.unload_texture(self.silver_texture)
        pr.unload_texture(self.gold_texture)
        pr.unload_texture(self.deck_texture)

        pr.close_window()