from aima3.search import Problem, astar_search
from board import BRONZE, SILVER, GOLD, BRONZE_TOTAL, SILVER_TOTAL, GOLD_TOTAL


class LabyrinthProblem(Problem):
    def __init__(self, board):
        # Definim l'estat inicial com una tupla:
        # (posició_jugador, frozenset de bronzes recollits, frozenset de plates recollides)
        initial_state = (
            board.player_position,
            frozenset(),
            frozenset()
        )
        super().__init__(initial_state)
        
        self.board = board
        # Guardem les posicions de tots els anells del mapa inicial
        self.bronze_positions = frozenset(board.get_ring_positions(BRONZE))
        self.silver_positions = frozenset(board.get_ring_positions(SILVER))
        gold_positions = board.get_ring_positions(GOLD)
        self.gold_position = gold_positions[0] if gold_positions else None

    def actions(self, state):
        """Retorna les accions vàlides (moviments) des d'un estat."""
        pos, bronze_collected, silver_collected = state
        row, col = pos
        
        valid_actions = []
        from board import DIRECTIONS
        
        for d_row, d_col in DIRECTIONS:
            new_row = row + d_row
            new_col = col + d_col
            
            # Comprovem si el jugador pot entrar en aquesta casella
            # simulant el nombre d'anells que portem recollits en aquest estat
            if self.board.can_enter_with_counts(
                new_row,
                new_col,
                len(bronze_collected),
                len(silver_collected)
            ):
                valid_actions.append((d_row, d_col))
                
        return valid_actions

    def result(self, state, action):
        """Aplica una acció (moviment) i retorna el nou estat resultant."""
        pos, bronze_collected, silver_collected = state
        row, col = pos
        d_row, d_col = action
        
        new_row = row + d_row
        new_col = col + d_col
        new_pos = (new_row, new_col)
        
        new_bronze = set(bronze_collected)
        new_silver = set(silver_collected)
        
        # Mirem quin element hi ha a la casella de destí
        cell_content = self.board.grid[new_row][new_col]
        
        if cell_content == BRONZE:
            new_bronze.add(new_pos)
        elif cell_content == SILVER:
            # Només el podem recollir si ja tenim tots els bronzes
            if len(bronze_collected) == BRONZE_TOTAL:
                new_silver.add(new_pos)
                
        return (new_pos, frozenset(new_bronze), frozenset(new_silver))

    def goal_test(self, state):
        """Comprova si l'estat és l'objectiu final (l'or amb tots els altres recollits)."""
        pos, bronze_collected, silver_collected = state
        
        has_all_bronze = len(bronze_collected) == BRONZE_TOTAL
        has_all_silver = len(silver_collected) == SILVER_TOTAL
        at_gold = pos == self.gold_position
        
        return at_gold and has_all_bronze and has_all_silver

    def path_cost(self, c, state1, action, state2):
        """Cada moviment en el laberint té un cost d'1."""
        return c + 1


def labyrinth_heuristic(node, problem):
    """
    Heurística consistent i admissible basada en la distància de Manhattan
    al següent objectiu més proper en la cadena lògica (Bronze -> Plata -> Or).
    """
    state = node.state
    pos, bronze_collected, silver_collected = state
    row, col = pos
    
    # 1. Si encara queden anells de bronze per recollir
    if len(bronze_collected) < BRONZE_TOTAL:
        remaining_bronze = problem.bronze_positions - bronze_collected
        if not remaining_bronze:
            return 0
        return min(abs(row - r) + abs(col - c) for r, c in remaining_bronze)
        
    # 2. Si ja tenim tots els bronzes però queden plates per recollir
    if len(silver_collected) < SILVER_TOTAL:
        remaining_silver = problem.silver_positions - silver_collected
        if not remaining_silver:
            return 0
        return min(abs(row - r) + abs(col - c) for r, c in remaining_silver)
        
    # 3. Si ja tenim tots els bronzes i plates, el destí és l'or
    if problem.gold_position:
        g_row, g_col = problem.gold_position
        return abs(row - g_row) + abs(col - g_col)
        
    return 0


def get_astar_path(board):
    """
    Executa l'algorisme A* d'AIMA i retorna una llista de coordenades (row, col)
    que formen el camí des de la posició inicial fins a la victòria.
    """
    problem = LabyrinthProblem(board)
    goal_node = astar_search(problem, h=lambda n: labyrinth_heuristic(n, problem))
    
    if goal_node:
        path_nodes = goal_node.path()
        return [node.state[0] for node in path_nodes]
    return []
