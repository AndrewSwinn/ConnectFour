# Class to contain the state of the window.
#
# A complete window takes 42 bytes to store.
#
# A gigabyte of memory should be able to store 25,500,000 window states.
#
# With a branching factor of 7 that gives a Breadth First tree depth of 8.7
#
# Yellow counters represented by -1
# Red counters represented by 1
#
# Board can only be changed using the addCounter method
#

import numpy as np

class GameState:

    def __init__(self, game_state=None):

        if game_state is None:

            self.board     = np.zeros((6, 7), dtype=np.int8)
            self.score     = 0
            self.game_over = None

        else:

            self.board     = np.copy(game_state.board)
            self.score     = game_state.score
            self.game_over = game_state.game_over

    def __str__(self):

        board = ""

        for row in range (5, -1, -1):

            for column in range (0, 7):

                counter = 'Y' if self.board[row, column] == -1 else ('R' if self.board[row, column] == 1 else '.')

                board = board + counter + ' '

            board = board + '\n'

        board = board + 'Score : ' + str(self.score) + '\n'

        return board

    def next_row(self, column):

        nextRow = max([-1] + [i for (i, j) in enumerate(self.board[:, column]) if j != 0]) + 1

        return nextRow

    def addCounter(self, counter, column):

        nextRow = self.next_row(column)

        self.board[nextRow, column] = counter

        self._evaluate_position()

        return nextRow

    def getLegalActions(self):

        legalActions = [i for (i, j) in enumerate(self.board[5,:]) if j == 0]

        return legalActions

    def swap_player(self):

        self.board = self.board * -1

        return self

    def _evaluate_position(self):

        RowMax = 6
        ColMax = 7

        # All Quads must be checked !!

        Value = 0  # Current evaluation

        # Rows: 4x6 = 24 in total
        for row in range(RowMax):
            for col in range(ColMax - 3):
                Value = Value + self._evaluate_quad(row, col, 0, 1)

        # Columns: 3 x 7 = 21 in total
        for row in range(RowMax - 3):
            for col in range(ColMax):
                Value = Value + self._evaluate_quad(row, col, 1, 0)

        # Down Diagonals: 3 x 4 = 12 in total
        for row in range(RowMax - 3):
            for col in range(ColMax - 3):
                Value = Value + self._evaluate_quad(row, col, 1, 1)

        # Up Diagonals: 3 x 4 = 12 in total
        for row in range(3, RowMax):
            for col in range(ColMax - 3):
                Value = Value + self._evaluate_quad(row, col, -1, 1)

        if len(self.getLegalActions()) == 0:

            self.game_over = 0

        self.score = Value

    def _evaluate_quad(self, Row, Col, DeltaRow, DeltaCol):

        RedCount = 0  # ' Generate Counts for Discs in Quad
        YellowCount = 0
        Rowel = Row  # Start at given grid coordinates
        ColEl = Col

        Score = 0;

        # calculate number of red and yellow tokens within the quad

        for Element in range(4):

            if self.board[Rowel, ColEl] == 1:

                RedCount += 1;

            elif self.board[Rowel, ColEl] == -1:

                YellowCount += 1;

            Rowel = Rowel + DeltaRow  # generate next quad element
            ColEl = ColEl + DeltaCol

        # Analyse

        if (RedCount > 0) and (YellowCount > 0):
            Score = 0;  # neutral quad -- nobody can win here

        elif (YellowCount > 0):

            if YellowCount == 1:

                Score = -1  # OK to start a new quad if nothing else available

            elif YellowCount == 2:

                Score = -10  # Two together is an advantage

            elif YellowCount == 3:

                Score = -100  # 3 together -- almost there

            elif YellowCount == 4:

                Score = -100000  # Winning position -- better than anything
                self.game_over = 1

        else:
            if RedCount == 1:

                Score = 1  # OK to start a new quad if nothing else available

            elif RedCount == 2:

                Score = 10  # Two together is an advantage

            elif RedCount == 3:

                Score = 100  # 3 together -- almost there

            elif RedCount == 4:

                Score = 100000  # Winning position -- better than anything

                self.game_over = -1

        # case of all empty quad is neutral (0) and handled implicitly
        #print("score at " + str(Row) + " and " + str(Col) + " is " + str(Score))
        return Score;

    def is_terminal(self):

        return False if self.game_over is None else True


