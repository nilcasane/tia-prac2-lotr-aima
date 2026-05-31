import random


EMPTY = "."
BARRIER = "#"
BRONZE = "B"
SILVER = "S"
GOLD = "G"

BRONZE_TOTAL = 6
SILVER_TOTAL = 3
GOLD_TOTAL = 1

BARRIER_LENGTHS = [5, 4, 3, 3, 3]

DIRECTIONS = [
    (-1, 0),  # amunt
    (1, 0),   # avall
    (0, -1),  # esquerra
    (0, 1),   # dreta
]


class Board:
    def __init__(self, size, seed=None):
        self.size = size
        self.rng = random.Random(seed)

        self.grid = []
        self.player_position = None

        self.bronze_collected = 0
        self.silver_collected = 0
        self.gold_collected = 0

        self.move_count = 0
        self.victory = False
        self.defeat = False
        self.initial_min_cost = 0

        self.generate_map()

    def generate_map(self):
        self.player_position = None
        self.bronze_collected = 0
        self.silver_collected = 0
        self.gold_collected = 0
        self.move_count = 0
        self.victory = False
        self.defeat = False
        
        for _ in range(500):
            self.grid = self.create_empty_grid()
            self.place_barriers()
            self.place_rings(BRONZE, BRONZE_TOTAL)
            self.place_rings(SILVER, SILVER_TOTAL)
            self.place_rings(GOLD, GOLD_TOTAL)
            self.player_position = self.get_random_empty_cell()
            
            if self.is_map_playable():
                return

        raise RuntimeError("No s'ha pogut generar un mapa vàlid.")

    def create_empty_grid(self):
        return [
            [EMPTY for _ in range(self.size)]
            for _ in range(self.size)
        ]

    def place_barriers(self):
        for length in BARRIER_LENGTHS:
            self.place_barrier(length)

    def place_barrier(self, length):
        """
        Col·loca una barrera de caselles consecutives.
        Pot ser horitzontal, vertical o diagonal.
        """
        orientations = [
            (0, 1),    # horitzontal cap a la dreta
            (1, 0),    # vertical cap avall
            (1, 1),    # diagonal cap avall-dreta
            (1, -1),   # diagonal cap avall-esquerra
        ]

        for _ in range(1000):
            start_row = self.rng.randint(0, self.size - 1)
            start_col = self.rng.randint(0, self.size - 1)
            d_row, d_col = self.rng.choice(orientations)

            cells = self.get_consecutive_cells(
                start_row,
                start_col,
                d_row,
                d_col,
                length
            )

            if self.are_cells_valid_for_barrier(cells):
                for row, col in cells:
                    self.grid[row][col] = BARRIER
                return

        raise RuntimeError(f"No s'ha pogut col·locar una barrera de mida {length}.")

    def get_consecutive_cells(self, start_row, start_col, d_row, d_col, length):
        cells = []

        for i in range(length):
            row = start_row + d_row * i
            col = start_col + d_col * i
            cells.append((row, col))

        return cells

    def are_cells_valid_for_barrier(self, cells):
        for row, col in cells:
            if not self.is_inside(row, col):
                return False

            if self.grid[row][col] != EMPTY:
                return False

        return True

    def place_rings(self, ring_type, amount):
        for _ in range(amount):
            row, col = self.get_random_empty_cell()
            self.grid[row][col] = ring_type

    def get_random_empty_cell(self):
        empty_cells = []

        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == EMPTY:
                    empty_cells.append((row, col))

        if not empty_cells:
            raise RuntimeError("No queden caselles buides disponibles.")

        return self.rng.choice(empty_cells)

    def is_inside(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def get_cell(self, row, col):
        if not self.is_inside(row, col):
            return None

        return self.grid[row][col]

    def can_enter(self, row, col):
        """
        Serveix per al moviment real del jugador.
        Té en compte els anells que el jugador ja ha recollit.
        """
        if not self.is_inside(row, col):
            return False

        cell = self.grid[row][col]

        if cell == BARRIER:
            return False

        if cell == BRONZE:
            return True

        if cell == SILVER:
            return self.bronze_collected == BRONZE_TOTAL

        if cell == GOLD:
            return self.silver_collected == SILVER_TOTAL

        return True

    def can_enter_with_counts(self, row, col, bronze_count, silver_count):
        """
        Aquesta funció serà útil després per A*.
        Permet comprovar moviments amb un estat simulat,
        no necessàriament amb l'estat real del jugador.
        """
        if not self.is_inside(row, col):
            return False

        cell = self.grid[row][col]

        if cell == BARRIER:
            return False

        if cell == BRONZE:
            return True

        if cell == SILVER:
            return bronze_count == BRONZE_TOTAL

        if cell == GOLD:
            return silver_count == SILVER_TOTAL

        return True

    def move_player(self, d_row, d_col):
        """
        Mou el jugador si el moviment és vàlid.
        Retorna True si s'ha mogut i False si no.
        """
        if self.victory or self.defeat:
            return False

        current_row, current_col = self.player_position
        new_row = current_row + d_row
        new_col = current_col + d_col

        if not self.can_enter(new_row, new_col):
            return False

        self.player_position = (new_row, new_col)
        self.move_count += 1

        self.collect_ring_if_needed(new_row, new_col)

        if self.move_count > self.initial_min_cost + 5:
            self.defeat = True

        return True

    def collect_ring_if_needed(self, row, col):
        cell = self.grid[row][col]

        if cell == BRONZE:
            self.bronze_collected += 1
            self.grid[row][col] = EMPTY

        elif cell == SILVER:
            self.silver_collected += 1
            self.grid[row][col] = EMPTY

        elif cell == GOLD:
            self.gold_collected = 1
            self.grid[row][col] = EMPTY
            self.victory = True

    def get_neighbors(self, row, col):
        """
        Retorna les caselles veïnes accessibles segons l'estat real del jugador.
        """
        neighbors = []

        for d_row, d_col in DIRECTIONS:
            new_row = row + d_row
            new_col = col + d_col

            if self.can_enter(new_row, new_col):
                neighbors.append((new_row, new_col))

        return neighbors

    def get_neighbors_with_counts(self, row, col, bronze_count, silver_count):
        """
        Retorna veïns accessibles per a un estat simulat.
        Això és útil per a A*.
        """
        neighbors = []

        for d_row, d_col in DIRECTIONS:
            new_row = row + d_row
            new_col = col + d_col

            if self.can_enter_with_counts(new_row, new_col, bronze_count, silver_count):
                neighbors.append((new_row, new_col))

        return neighbors

    def is_map_playable(self):
        from search import get_astar_path
        path = get_astar_path(self)
        if len(path) > 0:
            self.initial_min_cost = len(path) - 1
            return True
        return False

    def get_ring_positions(self, ring_type):
        positions = []

        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == ring_type:
                    positions.append((row, col))

        return positions

    def get_all_ring_positions(self):
        return {
            BRONZE: self.get_ring_positions(BRONZE),
            SILVER: self.get_ring_positions(SILVER),
            GOLD: self.get_ring_positions(GOLD),
        }

    def get_current_target_ring_type(self):
        """
        Indica quin tipus d'anell toca buscar ara.
        """
        if self.bronze_collected < BRONZE_TOTAL:
            return BRONZE

        if self.silver_collected < SILVER_TOTAL:
            return SILVER

        if self.gold_collected < GOLD_TOTAL:
            return GOLD

        return None

    def get_current_target_positions(self):
        target_type = self.get_current_target_ring_type()

        if target_type is None:
            return []

        return self.get_ring_positions(target_type)

    def reset(self):
        self.generate_map()