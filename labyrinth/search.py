from aima3.search import Problem, astar_search
from board import BRONZE, SILVER, GOLD, BRONZE_TOTAL, SILVER_TOTAL, DIRECTIONS

class LabyrinthProblem(Problem):
    def __init__(self, board):
        super().__init__((board.player_position, frozenset(), frozenset()))
        self.board = board
        self.bronze_positions = frozenset(board.get_ring_positions(BRONZE))
        self.silver_positions = frozenset(board.get_ring_positions(SILVER))
        self.gold_position = next(iter(board.get_ring_positions(GOLD)), None)
        self.bronze_to_collect = len(self.bronze_positions)
        self.silver_to_collect = len(self.silver_positions)

    def actions(self, state):
        (r, c), b, s = state
        tot_b = self.board.bronze_collected + len(b)
        tot_s = self.board.silver_collected + len(s)
        return [(dr, dc) for dr, dc in DIRECTIONS if self.board.can_enter_with_counts(r + dr, c + dc, tot_b, tot_s)]

    def result(self, state, action):
        (r, c), b, s = state
        nr, nc = r + action[0], c + action[1]
        npos = (nr, nc)
        cell = self.board.grid[nr][nc]
        nb = b | {npos} if cell == BRONZE else b
        tot_b = self.board.bronze_collected + len(nb)
        ns = s | {npos} if cell == SILVER and tot_b == BRONZE_TOTAL else s
        return (npos, frozenset(nb), frozenset(ns))

    def goal_test(self, state):
        pos, b, s = state
        return pos == self.gold_position and len(b) == self.bronze_to_collect and len(s) == self.silver_to_collect

    def path_cost(self, c, state1, action, state2):
        return c + 1

def labyrinth_heuristic(node, problem):
    (r, c), b, s = node.state
    if len(b) < problem.bronze_to_collect:
        targets = problem.bronze_positions - b
        remaining_cost = problem.silver_to_collect + 1
    elif len(s) < problem.silver_to_collect:
        targets = problem.silver_positions - s
        remaining_cost = 1
    else:
        targets = {problem.gold_position} if problem.gold_position else set()
        remaining_cost = 0

    if not targets:
        return 0

    dist_to_closest = min(abs(r - tr) + abs(c - tc) for tr, tc in targets)
    return dist_to_closest + (len(targets) - 1) + remaining_cost

def get_astar_path(board):
    problem = LabyrinthProblem(board)
    goal = astar_search(problem, h=lambda n: labyrinth_heuristic(n, problem))
    return [n.state[0] for n in goal.path()] if goal else []
