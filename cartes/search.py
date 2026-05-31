from cards import CardType


class AISearch:

    def __init__(self):

        self.nodes_explored = 0
        self.last_score = 0
        self.search_depth = 4

    def evaluate(self, board):

        ai = board.ai_player
        human = board.human_player

        ai_score = 0
        human_score = 0

        # VICTORIA
        if ai.gold_released >= 1:
            return 1000000

        if human.gold_released >= 1:
            return -1000000

        # PROGRESIÓN
        ai_score += ai.bronze_released * 1000
        ai_score += ai.silver_released * 10000
        ai_score += ai.gold_released * 100000

        human_score += human.bronze_released * 1000
        human_score += human.silver_released * 10000
        human_score += human.gold_released * 100000

        # CARTA EN MANO
        if ai.current_card == CardType.BRONZE:
            ai_score += 500

        elif ai.current_card == CardType.SILVER:
            ai_score += 300

        elif ai.current_card == CardType.GOLD:
            ai_score += 100

        # RESERVADAS
        if ai.reserved_card == CardType.GOLD:
            ai_score += 5000

        elif ai.reserved_card == CardType.SILVER:
            ai_score += 1000

        if human.reserved_card == CardType.GOLD:
            human_score += 5000

        elif human.reserved_card == CardType.SILVER:
            human_score += 1000

        # BLOQUEOS
        ai_score += ai.blocked_turns * 200
        human_score += human.blocked_turns * 200

        # BONUS POR ESTAR CERCA DE DESBLOQUEAR SILVER
        if ai.bronze_released >= 5:
            ai_score += 2500

        # BONUS POR ESTAR CERCA DE DESBLOQUEAR GOLD
        if ai.silver_released >= 2:
            ai_score += 5000

        return ai_score - human_score

    def alpha_beta(self, board, depth, alpha, beta, maximizing):

        self.nodes_explored += 1

        if depth == 0 or board.game_over:
            return self.evaluate(board)

        if maximizing:

            value = float("-inf")

            actions = board.generate_actions(
                board.ai_player
            )

            for action in actions:

                new_board = board.clone()

                new_board.apply_action(
                    new_board.ai_player,
                    action
                )

                score = self.alpha_beta(
                    new_board,
                    depth - 1,
                    alpha,
                    beta,
                    False
                )

                value = max(value, score)

                alpha = max(alpha, value)

                if beta <= alpha:
                    break

            return value

        else:

            value = float("inf")

            actions = board.generate_actions(
                board.human_player
            )

            for action in actions:

                new_board = board.clone()

                new_board.apply_action(
                    new_board.human_player,
                    action
                )

                score = self.alpha_beta(
                    new_board,
                    depth - 1,
                    alpha,
                    beta,
                    True
                )

                value = min(value, score)

                beta = min(beta, value)

                if beta <= alpha:
                    break

            return value

    def choose_action(self, board, player):

        self.nodes_explored = 0

        # HEURÍSTICAS RÁPIDAS

        if player.current_card == CardType.BRONZE:
            self.last_score = 999999
            return "release_card"

        if (
                player.current_card == CardType.SILVER
                and player.bronze_released >= 6
        ):
            self.last_score = 999999
            return "release_card"

        if (
                player.current_card == CardType.GOLD
                and player.silver_released >= 3
        ):
            self.last_score = 999999
            return "release_card"

        if (
                player.reserved_card == CardType.GOLD
                and player.silver_released >= 3
        ):
            self.last_score = 999999999
            return "release_reserved"

        if (
                player.reserved_card == CardType.SILVER
                and player.bronze_released >= 6
        ):
            self.last_score = 999999999
            return "release_reserved"

        best_action = "draw_card"
        best_score = float("-inf")

        actions = board.generate_actions(player)

        for action in actions:

            new_board = board.clone()

            new_board.apply_action(
                new_board.ai_player,
                action
            )

            score = self.alpha_beta(
                new_board,
                self.search_depth,
                float("-inf"),
                float("inf"),
                False
            )

            if score > best_score:

                best_score = score
                best_action = action

        self.last_score = best_score

        return best_action