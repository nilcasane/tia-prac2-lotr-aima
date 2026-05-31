from aima3.search import Problem, astar_search
from board import BRONZE, SILVER, GOLD, BRONZE_TOTAL, SILVER_TOTAL, DIRECTIONS

class LabyrinthProblem(Problem):
    """
    Definició de l'espai d'estats i regles de transició per al laberint.
    Hereda de la classe abstracta 'Problem' de la llibreria AIMA.
    """
    def __init__(self, board):
        # L'estat inicial es defineix com una tupla:
        # (posició_jugador, conjunt_bronzes_recollits, conjunt_plates_recollides)
        # Els conjunts són 'frozenset' perquè l'estat d'AIMA ha de ser immutable (hashable).
        super().__init__((board.player_position, frozenset(), frozenset()))
        self.board = board
        # Desem les posicions inicials dels anells de bronze, plata i or al mapa
        self.bronze_positions = frozenset(board.get_ring_positions(BRONZE))
        self.silver_positions = frozenset(board.get_ring_positions(SILVER))
        self.gold_position = next(iter(board.get_ring_positions(GOLD)), None)
        # Nombre total d'anells que queden per recollir en aquest mapa actualment
        self.bronze_to_collect = len(self.bronze_positions)
        self.silver_to_collect = len(self.silver_positions)

    def actions(self, state):
        """
        Retorna la llista d'accions (moviments) vàlides des d'un estat determinat.
        Cada acció és una tupla (desplaçament_fila, desplaçament_columna) de DIRECTIONS.
        """
        (r, c), b, s = state
        # Calculem el total d'anells recollits (els ja recollits al tauler real + els simulats en aquest camí)
        tot_b = self.board.bronze_collected + len(b)
        tot_s = self.board.silver_collected + len(s)
        # Retorna els moviments on la casella destí sigui accessible segons les regles de bloqueig dels anells
        return [(dr, dc) for dr, dc in DIRECTIONS if self.board.can_enter_with_counts(r + dr, c + dc, tot_b, tot_s)]

    def result(self, state, action):
        """
        Calcula el nou estat resultant d'aplicar una acció (moviment) a l'estat actual.
        """
        (r, c), b, s = state
        nr, nc = r + action[0], c + action[1]
        npos = (nr, nc)
        cell = self.board.grid[nr][nc]
        
        # Si la nova casella té un anell de bronze, l'afegim al conjunt de bronzes recollits d'aquest estat
        nb = b | {npos} if cell == BRONZE else b
        
        # El total de bronzes determina si podem recollir plata
        tot_b = self.board.bronze_collected + len(nb)
        
        # Si la casella té plata i ja tenim tots els bronzes necessaris, la recollim
        ns = s | {npos} if cell == SILVER and tot_b == BRONZE_TOTAL else s
        
        return (npos, frozenset(nb), frozenset(ns))

    def goal_test(self, state):
        """
        Comprova si s'ha assolit l'estat objectiu (la victòria).
        Retorna True si el jugador és a la casella de l'or i ha recollit tots els bronzes i plates.
        """
        pos, b, s = state
        return pos == self.gold_position and len(b) == self.bronze_to_collect and len(s) == self.silver_to_collect

    def path_cost(self, c, state1, action, state2):
        """
        Retorna el cost acumulat d'un camí. Cada moviment vàlid té un cost constant d'1 punt.
        """
        return c + 1


def labyrinth_heuristic(node, problem):
    """
    Funció heurística admissible i consistent per guiar l'algorisme A*.
    Calcula una estimació del cost restant des de l'estat del node fins al final.
    """
    (r, c), b, s = node.state
    
    # 1. Si encara queden bronzes per recollir, el nostre objectiu immediat són els bronzes restants
    if len(b) < problem.bronze_to_collect:
        targets = problem.bronze_positions - b
        # El cost restant simula el nombre de plates restants + arribar a l'or
        remaining_cost = problem.silver_to_collect + 1
        
    # 2. Si ja tenim els bronzes però falten plates, l'objectiu immediat són les plates restants
    elif len(s) < problem.silver_to_collect:
        targets = problem.silver_positions - s
        # El cost restant simula haver d'arribar a l'or (1)
        remaining_cost = 1
        
    # 3. Si ja ho tenim tot recollit, l'únic objectiu restant és la posició de l'or
    else:
        targets = {problem.gold_position} if problem.gold_position else set()
        remaining_cost = 0

    if not targets:
        return 0

    # Estimació de la distància de Manhattan cap a la fita objectiu més propera
    dist_to_closest = min(abs(r - tr) + abs(c - tc) for tr, tc in targets)
    
    # L'estimació total és: distància al més proper + penalització pels altres objectius restants + passos finals
    return dist_to_closest + (len(targets) - 1) + remaining_cost


def get_astar_path(board):
    """
    Instancia el problema i crida l'algorisme astar_search d'AIMA3.
    Retorna una llista de tuples (fila, columna) que representen les caselles
    del camí òptim calculat, o una llista buida si no hi ha camí disponible.
    """
    problem = LabyrinthProblem(board)
    goal = astar_search(problem, h=lambda n: labyrinth_heuristic(n, problem))
    return [n.state[0] for n in goal.path()] if goal else []
