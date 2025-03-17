import random
import copy

class TeekoPlayer:
    """An object representation for an AI game player for the game Teeko."""
    
    board = [[' ' for _ in range(5)] for _ in range(5)]
    pieces = ['b', 'r']

    def __init__(self):
        """Initializes a TeekoPlayer object by randomly selecting red or black as its piece color."""
        self.my_piece = random.choice(self.pieces)
        self.opp = self.pieces[0] if self.my_piece == self.pieces[1] else self.pieces[1]

    def run_challenge_test(self):
        """
        Determines if the challenge AI will be tested.
        Set to True for challenge testing or False for standard tests.
        """
        return True

    # define the successor finding function
    def succ(self, state):
        successors = []

        count_b = 0
        count_r = 0
        coordinates_b = []
        coordinates_r = []
        empty = []
        for row in range(5):
            for column in range(5):
                if state[row][column] == 'b':
                    count_b += 1
                    coordinates_b.append([row, column])
                elif state[row][column] == 'r':
                    count_r += 1
                    coordinates_r.append([row, column])
                else:
                    empty.append([row, column])
        # check if drop phase
        if count_b+count_r < 8:
            for row in range(5):
                for col in range(5):
                    if state[row][col] == ' ':
                        new_state = copy.deepcopy(state)
                        new_state[row][col] = self.my_piece
                        successors.append(new_state)
        else:
            for row in range(5):
                for col in range(5):
                    if state[row][col] == self.my_piece:
                        for move in [(-1, 0), (1, 0), (0, -1), (0, 1), (1, -1), (-1, 1), (-1, -1), (1, 1)]:
                            new_row = row + move[0]
                            new_col = col + move[1]
                            # check if in right bounds
                            if 0 <= new_row < 5 and 0 <= new_col < 5:
                                if state[new_row][new_col] == ' ':
                                    new_state = copy.deepcopy(state)
                                    new_state[new_row][new_col] = self.my_piece
                                    new_state[row][col] = ' '
                                    successors.append(new_state)
        return successors
    
    def heuristic_game_value(self, state):
        eval = self.game_value(state)
        if eval != 0:
            return eval

        result = 0
        # ---
        for row in state:
            for col in range(2):
                if row[col] == self.my_piece:
                    for i in range(4):
                        if row[col+i] == self.my_piece:
                            result+=1
                elif row[col] == self.opp:
                    for i in range(4):
                        if row[col+i]==self.my_piece:
                            result-=1
        # |
        for col in range(5):
            # only 2 so doesn't go out of range
            for row in range(2):
                line = []
                for i in range(row, row+4):
                    line.append(state[i][col])
                if line[0] == self.my_piece:
                    result+=line.count(self.my_piece)
                elif line[0] == self.opp:
                    result-=line.count(self.opp)

        # \
        for row in range(2):
            for col in range(2):
                line = []
                for i in range(4):
                    line.append(state[row+i][col+i])
                if line[0] == self.my_piece:
                    result+=line.count(self.my_piece)
                elif line[0] == self.opp:
                    result-=line.count(self.opp)
        # /
        for row in range(2):
            for col in range(3, 5):
                line = []
                for i in range(4):
                    line.append(state[row+i][col-i])
                if line[0] == self.my_piece:
                    result+=line.count(self.my_piece)
                elif line[0] == self.opp:
                    result-=line.count(self.opp)
        # []
        for row in range(4):
            for col in range(4):
                box = [state[row][col], state[row + 1][col], state[row][col + 1], state[row + 1][col + 1]]
                if box.count(self.my_piece) == 3 and box.count(self.opp) == 0:
                    result+=box.count(self.my_piece)*5
                elif box.count(self.opp) == 3 and box.count(self.my_piece) == 0:
                    result-=box.count(self.opp)*5
        # normalize by dividing by max score
        result = result/352
        # make sure does not exceed boundaries
        return max(-1, min(1, result))
    

    def max_value(self, state, depth, maxTurn):
        # base case
        if depth == 3 or self.game_value(state) != 0:
            return [self.heuristic_game_value(state), state]
        
        successors = self.succ(state)
        if maxTurn:
            # find the max best move
            m = [-999999, None]
            for succ_state in successors:
                v = [self.max_value(succ_state, depth+1, False)[0], succ_state]
                if v[0] > m[0]:
                    m = v
            return m
        else:
            # find the min best move
            m = [999999, None]
            for succ_state in successors:
                v = [self.max_value(succ_state, depth+1, True)[0], succ_state]
                if v[0] < m[0]:
                    m = v
            return m

    def make_move(self, state):
        """
        Selects a (row, col) space for the next move. 
        
        Args:
            state (list of lists): The current state of the game board.
        
        Returns:
            list: A list of move tuples [(row, col), (source_row, source_col)].
                  For drop phase, it contains only [(row, col)].
        """
        # find w
        count_b = 0
        count_r = 0
        coordinates_b = []
        coordinates_r = []
        empty = []
        for row in range(5):
            for column in range(5):
                if state[row][column] == 'b':
                    count_b += 1
                    coordinates_b.append([row, column])
                elif state[row][column] == 'r':
                    count_r += 1
                    coordinates_r.append([row, column])
                else:
                    empty.append([row, column])
        if count_b + count_r == 8:
            drop_phase = False
        else:
            drop_phase = True

        move = []

        result = self.max_value(state, 0, True)[1]

        if drop_phase:
            # determine the row and column of the move
            for row in range(5):
                for col in range(5):
                    if result[row][col] != state[row][col]:
                        move = [(row, col)]
        else:
            # find the position of the move
            for row in range(5):
                for col in range(5):
                    if state[row][col] == ' ' and result[row][col] == self.my_piece:
                        # find where the piece came from by checking if there is no longer a piece somewhere
                        if row+1 < 5 and state[row+1][col] != ' ' and result[row+1][col] == ' ':
                            move = [(row, col), (row+1, col)]
                        elif col+1 < 5 and state[row][col+1] != ' ' and result[row][col+1] == ' ':
                            move = [(row, col), (row, col+1)]
                        elif row-1 >= 0 and state[row-1][col] != ' ' and result[row-1][col] == ' ':
                            move = [(row, col), (row-1, col)]
                        elif col-1 >= 0 and state[row][col-1] != ' ' and result[row][col-1] == ' ':
                            move = [(row, col), (row, col-1)]
                        elif row+1 < 5 and col+1 < 5 and state[row+1][col+1] != ' ' and result[row+1][col+1] == ' ':
                            move = [(row, col), (row+1, col+1)]
                        elif row-1 >=0 and col-1 >= 0 and state[row-1][col-1] != ' ' and result[row-1][col-1] == ' ':
                            move = [(row, col), (row-1, col-1)]
                        elif row-1 >=0 and col+1 <5 and state[row-1][col+1] != ' ' and result[row-1][col+1] == ' ':
                            move = [(row, col), (row-1, col+1)]
                        elif row+1 <5 and col-1 >= 0 and state[row+1][col-1] != ' ' and result[row+1][col-1] == ' ':
                            move = [(row, col), (row+1, col-1)]

        return move

    def opponent_move(self, move):
        """
        Validates the opponent's move against the internal board representation.

        Args:
            move (list): A list of move tuples [(row, col), (source_row, source_col)].
        """
        if len(move) > 1:
            source_row, source_col = move[1]
            if source_row is not None and self.board[source_row][source_col] != self.opp:
                self.print_board()
                print(move)
                raise Exception("You don't have a piece there!")
            if abs(source_row - move[0][0]) > 1 or abs(source_col - move[0][1]) > 1:
                self.print_board()
                print(move)
                raise Exception('Illegal move: Can only move to an adjacent space')
        if self.board[move[0][0]][move[0][1]] != ' ':
            raise Exception("Illegal move detected")

        self.place_piece(move, self.opp)

    def place_piece(self, move, piece):
        """
        Modifies the board representation using the specified move and piece.
        
        Args:
            move (list): A list of move tuples [(row, col), (source_row, source_col)].
            piece (str): The piece ('b' or 'r') to place on the board.
        """
        if len(move) > 1:
            self.board[move[1][0]][move[1][1]] = ' '
        self.board[move[0][0]][move[0][1]] = piece

    def print_board(self):
        """Formatted printing for the board."""
        for row in range(len(self.board)):
            line = f"{row}: " + " ".join(self.board[row])
            print(line)
        print("   A B C D E")

    def game_value(self, state):
        """
        Checks the current board status for a win condition.
        
        Args:
            state (list of lists): The current or successor state of the game board.
        
        Returns:
            int: 1 if this player wins, -1 if the opponent wins, 0 otherwise.
        """
        # Check horizontal wins
        for row in state:
            for i in range(2):
                if row[i] != ' ' and row[i] == row[i+1] == row[i+2] == row[i+3]:
                    return 1 if row[i] == self.my_piece else -1

        # Check vertical wins
        for col in range(5):
            for i in range(2):
                if state[i][col] != ' ' and state[i][col] == state[i+1][col] == state[i+2][col] == state[i+3][col]:
                    return 1 if state[i][col] == self.my_piece else -1

        # Check \ diagonal wins
        for x in range(2):
            for y in range(2):
                if state[x][y] != ' ' and state[x][y] == state[x+1][y+1] == state[x+2][y+2] == state[x+3][y+3]:
                    return 1 if state[x][y] == self.my_piece else -1

        # Check / diagonal wins
        for y in range(3, 5):
            for x in range(0, 2):
                if state[x][y] != ' ' and state[x][y] == state[x-1][y-1] == state[x-2][y-2] == state[x-3][y-3]:
                    return 1 if state[x][y] == self.my_piece else -1
        # Check box wins
        for x in range(4):
            for y in range(4):
                if state[x][y] != ' ' and state[x][y] == state[x+1][y+1] == state[x+1][y] == state[x][y+1]:
                    return 1 if state[x][y] == self.my_piece else -1

        return 0  # No winner yet

############################################################################
#
# THE FOLLOWING CODE IS FOR SAMPLE GAMEPLAY ONLY
#
############################################################################
def main():
    print('Playing the game...')
    ai = TeekoPlayer()
    piece_count = 0
    turn = 0

    # Drop phase
    while piece_count < 8 and ai.game_value(ai.board) == 0:
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(f"{ai.my_piece} moved at {chr(move[0][1] + ord('A'))}{move[0][0]}")
        else:
            ai.print_board()
            print(f"{ai.opp}'s turn")
            move_made = False
            while not move_made:
                player_move = input("Move (e.g. B3): ")
                if len(player_move) == 2 and player_move[0] in "ABCDE" and player_move[1] in "01234":
                    try:
                        ai.opponent_move([(int(player_move[1]), ord(player_move[0]) - ord("A"))])
                        move_made = True
                    except Exception as e:
                        print(e)

        piece_count += 1
        turn = (turn + 1) % 2

    # Move phase
    while ai.game_value(ai.board) == 0:
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(f"{ai.my_piece} moved from {chr(move[1][1] + ord('A'))}{move[1][0]}")
            print(f" to {chr(move[0][1] + ord('A'))}{move[0][0]}")
        else:
            ai.print_board()
            print(f"{ai.opp}'s turn")
            move_made = False
            while not move_made:
                move_from = input("Move from (e.g. B3): ")
                move_to = input("Move to (e.g. B3): ")
                if len(move_from) == 2 and move_from[0] in "ABCDE" and move_from[1] in "01234" and \
                   len(move_to) == 2 and move_to[0] in "ABCDE" and move_to[1] in "01234":
                    try:
                        ai.opponent_move([
                            (int(move_to[1]), ord(move_to[0]) - ord("A")),
                            (int(move_from[1]), ord(move_from[0]) - ord("A"))
                        ])
                        move_made = True
                    except Exception as e:
                        print(e)

        turn = (turn + 1) % 2

    ai.print_board()
    if ai.game_value(ai.board) == 1:
        print("AI wins! Game over.")
    else:
        print("You win! Game over.")

if __name__ == "__main__":
    main()
