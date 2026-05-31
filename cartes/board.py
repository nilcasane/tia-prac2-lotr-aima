import random
from search import AISearch
from cards import CardType


class Player:

    def __init__(self, name):
        self.turn_action_done = False
        self.name = name

        self.deck = self.create_deck()

        self.current_card = None
        self.reserved_card = None

        self.bronze_released = 0
        self.silver_released = 0
        self.gold_released = 0

        self.blocked_turns = 0

    def clone(self):
        clone = Player(self.name)

        clone.turn_action_done = self.turn_action_done

        clone.deck = self.deck.copy()

        clone.current_card = self.current_card
        clone.reserved_card = self.reserved_card

        clone.bronze_released = self.bronze_released
        clone.silver_released = self.silver_released
        clone.gold_released = self.gold_released

        clone.blocked_turns = self.blocked_turns

        return clone

    def create_deck(self):

        deck = (
                [CardType.BRONZE] * 6
                + [CardType.SILVER] * 3
                + [CardType.GOLD]
        )

        random.shuffle(deck)

        return deck

    def draw_card(self):

        if not self.deck:
            self.current_card = None
            return None

        self.current_card = self.deck.pop(0)

        return self.current_card

    def can_release(self, card):

        if card == CardType.BRONZE:
            return True

        if card == CardType.SILVER:
            return self.bronze_released >= 6

        if card == CardType.GOLD:
            return self.silver_released >= 3

        return False

    def release_current_card(self):

        if self.current_card is None:
            return False

        if not self.can_release(self.current_card):
            return False

        if self.current_card == CardType.BRONZE:
            self.bronze_released += 1

        elif self.current_card == CardType.SILVER:
            self.silver_released += 1

        elif self.current_card == CardType.GOLD:
            self.gold_released += 1

        self.current_card = None

        return True

    def release_reserved_card(self):

        if self.reserved_card is None:
            return False

        if not self.can_release(self.reserved_card):
            return False

        if self.reserved_card == CardType.BRONZE:
            self.bronze_released += 1

        elif self.reserved_card == CardType.SILVER:
            self.silver_released += 1

        elif self.reserved_card == CardType.GOLD:
            self.gold_released += 1

        self.reserved_card = None

        return True

    def reserve_current_card(self):

        if self.current_card is None:
            return False

        if self.reserved_card is not None:
            return False

        self.reserved_card = self.current_card
        self.current_card = None

        return True

    def return_card_to_deck(self):

        if self.current_card is None:
            return False

        self.deck.append(self.current_card)

        random.shuffle(self.deck)

        self.current_card = None

        return True

    def block_opponent(self, opponent):

        opponent.blocked_turns += 1

    def get_score(self):

        return (
                self.bronze_released * 10
                + self.silver_released * 100
                + self.gold_released * 10000
        )


class Board:

    def __init__(self, human_name="Human", ai_name="AI"):

        self.human_player = Player(human_name)
        self.ai_player = Player(ai_name)

        self.ai_search = AISearch()

        self.current_player = self.human_player

        self.winner = None
        self.game_over = False

        self.turn_count = 0
        self.last_action = None

    def clone(self):

        clone = Board.__new__(Board)

        clone.human_player = self.human_player.clone()
        clone.ai_player = self.ai_player.clone()

        if self.current_player == self.human_player:
            clone.current_player = clone.human_player
        else:
            clone.current_player = clone.ai_player

        clone.winner = None
        clone.game_over = self.game_over

        clone.turn_count = self.turn_count
        clone.last_action = self.last_action

        clone.ai_search = None

        return clone

    def get_current_player(self):
        return self.current_player

    def get_opponent(self):

        if self.current_player == self.human_player:
            return self.ai_player

        return self.human_player

    def switch_turn(self):

        self.turn_action_done = False

        opponent = self.get_opponent()

        if opponent.blocked_turns > 0:

            opponent.blocked_turns -= 1
            self.turn_count += 1
            return

        self.current_player = opponent
        self.turn_count += 1

    def check_victory(self):

        if self.human_player.gold_released >= 1:
            self.winner = self.human_player
            self.game_over = True

        elif self.ai_player.gold_released >= 1:
            self.winner = self.ai_player
            self.game_over = True

        return self.game_over

    def draw_card(self):

        self.last_action = "draw_card"

        return self.current_player.draw_card()

    def release_current_card(self):

        success = self.current_player.release_current_card()

        if success:
            self.last_action = "release_current_card"
            self.check_victory()

        return success

    def reserve_current_card(self):

        success = self.current_player.reserve_current_card()

        if success:
            self.last_action = "reserve_current_card"

        return success

    def release_reserved_card(self):

        success = self.current_player.release_reserved_card()

        if success:
            self.last_action = "release_reserved_card"
            self.check_victory()

        return success

    def return_card_to_deck(self):

        success = self.current_player.return_card_to_deck()

        if success:
            self.last_action = "return_card_to_deck"

        return success

    def block_opponent(self):

        self.current_player.block_opponent(
            self.get_opponent()
        )

        self.last_action = "block_opponent"

        return True

    def generate_actions(self, player):

        actions = []

        if player.current_card is None and len(player.deck) > 0:
            actions.append("draw_card")

        if player.current_card is not None:
            actions.append("reserve_card")
            actions.append("return_to_deck")

            if player.can_release(player.current_card):
                actions.append("release_card")

        if (
                player.reserved_card is not None
                and player.can_release(player.reserved_card)
        ):
            actions.append("release_reserved")

        if self.get_opponent().blocked_turns == 0:
            actions.append("block_opponent")

        return actions

    def apply_action(self, player, action):

        if action == "draw_card":
            player.draw_card()

        elif action == "release_card":
            player.release_current_card()

        elif action == "reserve_card":
            player.reserve_current_card()

        elif action == "release_reserved":
            player.release_reserved_card()

        elif action == "return_to_deck":
            player.return_card_to_deck()

        elif action == "block_opponent":

            if player == self.ai_player:
                player.block_opponent(self.human_player)
            else:
                player.block_opponent(self.ai_player)

        self.check_victory()

    def ai_turn(self):

        if self.game_over:
            return

        ai = self.ai_player

        action = self.ai_search.choose_action(
            self,
            ai
        )

        print("================================")
        print(f"AI ACTION: {action}")
        print(f"Current Card: {ai.current_card}")
        print(f"Reserved Card: {ai.reserved_card}")
        print(f"Bronze: {ai.bronze_released}")
        print(f"Silver: {ai.silver_released}")
        print(f"Gold: {ai.gold_released}")
        print("================================")

        self.apply_action(ai, action)

        self.check_victory()

        return action