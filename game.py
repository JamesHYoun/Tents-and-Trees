'''
If you want to try game with your own test cases, scroll down to "main" and "INPUT OWN".
'''

EMPTY = '-'
TREE = 't'
GRASS = 'v'
TENT = 'A'

DIRS = [(-1, 0), (0, -1), (1, 0), (0, 1)]


def print_board(row_params, col_params, grid):
    col_str = ' '.join([str(x) for x in col_params])
    print(f'  {col_str}')
    rows = []
    for i in range(len(grid)):
        row = [str(row_params[i])] + grid[i]
        rows.append(' '.join(row))
    print('\n'.join(rows))


def print_quads(grid):
    for r in range(0, len(grid), 4):
        for c in range(0, len(grid), 4):
            print(f'{r//4} {c//4}')
            for i in range(r, r + 4):
                row = [grid[i][j] for j in range(c, c + 4)]
                print(' '.join(row))
            print()


class GameController:
    
    def __init__(self, grid, row_param, col_param):
        self.grid = grid
        self.len_grid = len(grid)
        self.row_param = row_param
        self.col_param = col_param
        self.row_data = [[0, 0] for _ in range(self.len_grid)] # first: num_empties, second: num_tents
        self.col_data = [[0, 0] for _ in range(self.len_grid)]
        for row in range(self.len_grid):
            for col in range(self.len_grid):
                if grid[row][col] == EMPTY:
                    self.row_data[row][0] += 1
                    self.col_data[col][0] += 1

    # Attempts to logically deduce whether a square is a grass or tent as much as possible. Once this is impossible, it guesses for a square and repeats this entire process until a solution is found.
    def play_game(self):
        ops = []
        while not self.is_done():
            changed = False
            for row in range(self.len_grid):
                for col in range(self.len_grid):
                    if self.grid[row][col] == EMPTY:
                        must_grass = self.must_be_grass(row, col)
                        must_tent = self.must_be_tent(row, col)
                        if must_grass and must_tent:
                            self.revert_board(ops)
                            return False
                        if must_grass == must_tent:
                            continue
                        ops.append([row, col])
                        self.row_data[row][0] -= 1
                        self.col_data[col][0] -= 1
                        if must_grass:
                            self.grid[row][col] = GRASS
                        if must_tent:
                            self.grid[row][col] = TENT
                            self.row_data[row][1] += 1
                            self.col_data[col][1] += 1
                        changed = True
            if changed == False: # backtracking portion
                for row in range(self.len_grid):
                    for col in range(self.len_grid):
                        if self.grid[row][col] == EMPTY:
                            self.grid[row][col] = GRASS
                            self.row_data[row][0] -= 1
                            self.col_data[col][0] -= 1
                            if self.play_game():
                                return True
                            self.grid[row][col] = TENT
                            self.row_data[row][1] += 1
                            self.col_data[col][1] += 1
                            if self.play_game():
                                return True
                            self.revert_board(ops)
                            self.revert_board([[row, col]])
                            return False
        return self.check_camps()

    # Reverts board to a previous state.
    def revert_board(self, ops):
        while len(ops):
            op = ops.pop()
            row, col = op[0], op[1]
            if self.grid[row][col] == TENT:
                self.row_data[row][1] -= 1
                self.col_data[col][1] -= 1
            self.row_data[row][0] += 1
            self.col_data[col][0] += 1
            self.grid[row][col] = EMPTY

    # Once all empty squares are filled, checks to see whether each tree is paired with exactly one tent.
    def check_camps(self):
        visited = [[False for _ in range(self.len_grid)] for _ in range(self.len_grid)]
        def dfs(i, j):
            is_tent = self.grid[i][j] == TENT
            if is_tent:
                sum = 1
            else:
                sum = -1
            visited[i][j] = True
            for di, dj in DIRS:
                ni, nj = i + di, j + dj
                cond_met = self.in_bounds(ni, nj) and not visited[ni][nj]
                if cond_met and self.grid[ni][nj] != GRASS:
                    if is_tent == (self.grid[ni][nj] == TREE):
                        sum += dfs(ni, nj)
            return sum
        for i in range(self.len_grid):
            for j in range(self.len_grid):
                if not visited[i][j] and self.grid[i][j] != GRASS:
                    sum = dfs(i, j)
                    if sum != 0:
                        return False
        return True

    def is_done(self):
        for index in range(self.len_grid):
            if self.row_data[index][0] != 0 or self.col_data[index][0] != 0:
                return False
        return True

    def must_be_grass(self, row, col):
        # If the row or col already contains proper num of tents, then must be grass
        if self.row_param[row] == self.row_data[row][1]:
            return True
        if self.col_param[col] == self.col_data[col][1]:
            return True
        # If a tent is already in a vertical, horizontal, or diagonal cell, then must be grass
        for drow in range(-1, 2):
            for dcol in range(-1, 2):
                new_row = row + drow
                new_col = col + dcol
                if self.in_bounds(new_row, new_col) and self.grid[new_row][new_col] == TENT:
                    return True
        # If no tree is vertically or horizontally adjacent to this cell, then must be grass
        is_tree_adj = False
        for drow, dcol in DIRS:
            new_row = row + drow
            new_col = col + dcol
            if self.in_bounds(new_row, new_col) and self.grid[new_row][new_col] == TREE:
                is_tree_adj = True
                break
        return not is_tree_adj
    
    def must_be_tent(self, row, col):
        # If filling the empty cells with tents completes a tent requirement for a row or col, then must be tent
        if self.row_param[row] == sum(self.row_data[row]):
            return True
        if self.col_param[col] == sum(self.col_data[col]):
            return True
        # If there is a tree adjacent to the would-be tent and that tree is otherwise surrounded by only grass or other trees, then must be tent
        for drow, dcol in DIRS:
            new_row = row + drow
            new_col = col + dcol
            if self.in_bounds(new_row, new_col) and self.grid[new_row][new_col] == TREE:
                is_rest_full = True
                for dnrow, dncol in DIRS:
                    if dnrow == -1*drow and dncol == -1*dcol:
                        continue
                    nn_row = new_row + dnrow
                    nn_col = new_col + dncol
                    if self.in_bounds(nn_row, nn_col) and self.grid[nn_row][nn_col] != GRASS and self.grid[nn_row][nn_col] != TREE:
                        is_rest_full = False
                        break
                if is_rest_full:
                    return True
        return False

    def in_bounds(self, row, col):
        return 0 <= row and row < self.len_grid and 0 <= col and col < self.len_grid


if __name__ == "__main__":
    '''
    INPUT OWN

    Add your own test cases in the tests array right below.
    Some test cases are already written.
    Simply follow their formats.
    '''

    tests = [
        (   # test 0
            [1, 1, 0, 2, 1], # number of tents in each row
            [2, 0, 1, 1, 1], # number of tents in each col
            [                               # problem to be solved
                ['-', '-', '-', '-', '-'],
                ['-', 't', '-', 't', '-'],
                ['-', '-', '-', '-', '-'],
                ['t', 't', '-', '-', '-'],
                ['-', '-', '-', '-', 't']
            ],
            [                               # Correct Answer (Optional - see test 6 for formatting)
                ['v', 'v', 'v', 'A', 'v'],
                ['A', 't', 'v', 't', 'v'],
                ['v', 'v', 'v', 'v', 'v'],
                ['t', 't', 'A', 'v', 'A'],
                ['A', 'v', 'v', 'v', 't']
            ]
        ),
        (   # test 1
            [2, 0, 1, 0, 2],
            [1, 1, 1, 1, 1],
            [
                ['-', 't', '-', 't', '-'],
                ['-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-'],
                ['-', 't', '-', '-', '-'],
                ['-', 't', 't', '-', '-']
            ],
            [
                ['v', 't', 'A', 't', 'A'],
                ['v', 'v', 'v', 'v', 'v'],
                ['v', 'A', 'v', 'v', 'v'],
                ['v', 't', 'v', 'v', 'v'],
                ['A', 't', 't', 'A', 'v']
            ]
        ),
        (   # test 2
            [1, 1, 1, 2, 0],
            [1, 0, 2, 0, 2],
            [
                ['-', '-', '-', 't', 't'],
                ['t', '-', '-', '-', '-'],
                ['-', '-', 't', '-', '-'],
                ['-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', 't']
            ],
            [
                ['v', 'v', 'A', 't', 't'],
                ['t', 'v', 'v', 'v', 'A'],
                ['A', 'v', 't', 'v', 'v'],
                ['v', 'v', 'A', 'v', 'A'],
                ['v', 'v', 'v', 'v', 't']
            ]
        ),
        (   # test 3
            [2, 1, 2, 1, 1, 1],
            [1, 2, 1, 2, 0, 2],
            [
                ['-', '-', '-', '-', 't', '-'],
                ['-', '-', 't', 't', '-', 't'],
                ['t', '-', '-', '-', '-', '-'],
                ['-', '-', '-', 't', '-', '-'],
                ['-', 't', '-', '-', '-', '-'],
                ['t', '-', '-', '-', '-', '-']
            ],
            [
                ['v', 'v', 'A', 'v', 't', 'A'],
                ['A', 'v', 't', 't', 'v', 't'],
                ['t', 'v', 'v', 'A', 'v', 'A'],
                ['v', 'A', 'v', 't', 'v', 'v'],
                ['v', 't', 'v', 'A', 'v', 'v'],
                ['t', 'A', 'v', 'v', 'v', 'v']
            ]
        ),
        (   # test 4
            [2, 1, 1, 2, 0, 2],
            [2, 1, 1, 1, 2, 1],
            [
                ['-', 't', '-', '-', '-', '-'],
                ['-', 't', '-', '-', 't', '-'],
                ['-', 't', '-', '-', '-', '-'],
                ['-', '-', 't', '-', 't', '-'],
                ['-', '-', '-', '-', '-', '-'],
                ['-', '-', 't', '-', '-', 't']
            ],
            [
                ['A', 't', 'v', 'v', 'A', 'v'],
                ['v', 't', 'A', 'v', 't', 'v'],
                ['A', 't', 'v', 'v', 'v', 'v'],
                ['v', 'v', 't', 'A', 't', 'A'],
                ['v', 'v', 'v', 'v', 'v', 'v'],
                ['v', 'A', 't', 'v', 'A', 't']
            ],
        ),
        (   # test 5
            [2, 2, 1, 2, 1, 1, 2, 1],
            [3, 1, 2, 1, 1, 0, 3, 1],
            [
                ['-', '-', 't', '-', '-', '-', '-', '-'],
                ['t', '-', '-', 't', '-', '-', '-', 't'],
                ['-', 't', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', 't'],
                ['-', 't', 't', '-', '-', '-', '-', '-'],
                ['-', '-', '-', 't', '-', 't', '-', '-'],
                ['t', '-', '-', '-', '-', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', 't']
            ],
            [
                ['A', 'v', 't', 'v', 'v', 'v', 'v', 'A'],
                ['t', 'v', 'A', 't', 'A', 'v', 'v', 't'],
                ['A', 't', 'v', 'v', 'v', 'v', 'v', 'v'],
                ['v', 'v', 'A', 'v', 'v', 'v', 'A', 't'],
                ['A', 't', 't', 'v', 'v', 'v', 'v', 'v'],
                ['v', 'v', 'v', 't', 'v', 't', 'A', 'v'],
                ['t', 'A', 'v', 'A', 'v', 'v', 'v', 'v'],
                ['v', 'v', 'v', 'v', 'v', 'v', 'A', 't']
            ],
        ), 
        (   # test 6
            [7, 1, 8, 1, 8, 1, 6, 2, 7, 3, 4, 4, 4, 2, 5, 3, 3, 3, 5, 3],
            [4, 6, 4, 4, 2, 6, 3, 3, 5, 3, 4, 4, 3, 3, 6, 3, 5, 3, 4, 5],
            [
                ['-', '-', '-', '-', 't', '-', 't', '-', '-', '-', '-', 't', '-', '-', '-', '-', '-', '-', 't', '-'],
                ['t', '-', 't', '-', '-', '-', '-', '-', '-', '-', '-', '-', 't', '-', '-', 't', '-', '-', '-', '-'],
                ['-', '-', '-', '-', 't', '-', 't', '-', '-', '-', 't', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', 't', 't', 't', '-', '-', '-', '-', '-', 't', '-', '-', 't', '-', 't', '-', 't', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', 't', '-', '-', '-', '-', 't', '-', '-', '-', 't', '-', 't', '-', 't'],
                ['t', '-', '-', '-', '-', 't', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', 't', '-', 't', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', 't', 't', '-', '-', 't', '-'],
                ['t', '-', '-', '-', '-', 't', '-', '-', 't', '-', '-', '-', '-', 't', '-', '-', '-', 't', '-', '-'],
                ['-', 't', '-', '-', '-', '-', '-', 't', '-', '-', 't', 't', '-', '-', '-', '-', '-', '-', '-', 't'],
                ['-', '-', '-', 't', '-', '-', '-', '-', 't', '-', 't', '-', '-', '-', 't', 't', '-', '-', 't', '-'],
                ['t', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', 't', '-', '-'],
                ['-', '-', 't', '-', '-', 't', '-', '-', '-', 't', '-', '-', '-', '-', '-', '-', '-', 't', '-', '-'],
                ['-', '-', 't', '-', '-', '-', '-', '-', '-', '-', '-', '-', 't', '-', '-', '-', 't', '-', '-', 't'],
                ['-', '-', '-', '-', '-', '-', '-', '-', 't', '-', '-', '-', '-', '-', 't', '-', '-', '-', '-', '-'],
                ['-', '-', 't', '-', 't', '-', '-', 't', '-', '-', '-', '-', '-', '-', '-', '-', 't', '-', '-', '-'],
                ['-', '-', '-', '-', '-', '-', '-', 't', '-', 't', '-', '-', '-', 't', 't', '-', '-', '-', '-', 't'],
                ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', 't'],
                ['-', '-', '-', 't', 't', '-', '-', '-', '-', 't', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
                ['-', 't', 't', '-', '-', '-', '-', '-', 't', '-', '-', '-', '-', 't', '-', 't', '-', 't', '-', '-'],
                ['t', '-', '-', '-', '-', '-', 't', '-', '-', '-', '-', 't', '-', '-', '-', '-', '-', '-', '-', '-']
            ]
        ),        
    ]

    print(f'LEGEND: ')
    print(f'-: empty cell\nt: tree\nv: grass\nA: tent\n')
    print(f'SAMPLE TEST CASES: \n')
    for test_num in range(len(tests)):
        row_param = tests[test_num][0]
        col_param = tests[test_num][1]
        grid = tests[test_num][2]
        print(f'TEST {test_num}: ')
        print(f'Problem: ')
        print_board(row_param, col_param, grid)
        gc = GameController(grid, row_param, col_param)
        success = gc.play_game()
        cpu_ans = gc.grid
        print(f'Computer\'s Answer: ')
        print_board(row_param, col_param, cpu_ans)
        if len(tests[test_num]) <= 3:
            print(f'Correct Answer: NONE GIVEN')
            if success:
                print(f'Status: PASSED')
            else:
                print(f'Status: FAILED')
            print()
            continue
        cor_ans = tests[test_num][3]
        print(f'Correct Answer: ')
        print_board(row_param, col_param, cor_ans)
        is_correct = True
        for row in range(len(grid)):
            for col in range(len(grid)):
                if cor_ans[row][col] != cpu_ans[row][col]:
                    is_correct = False
                    break
        if is_correct and success:
            print(f'Status: PASSED')
        elif is_correct or success:
            print(f'Status: CHECK CODE & CORRECT ANSWER')
        else:
            print(f'Status: FAILED')
        print()
