import pygame
import multiprocessing as mp

from src.Display    import Display
from src.Display    import Counter
from src.GameState  import GameState
from src.GameSearch import GameSearch



class BackgroundThinker():

    def __init__(self, status, qInput, qOutput):

        self.status  = status
        self.qInput  = qInput
        self.qOutput = qOutput

        while self.status['GameState'] != 'Quit':

            if not self.qInput.empty():

                (player, game_state) = self.qInput.get()

                game_state = game_state if player.counter == 1 else game_state.swap_player()

                agent = GameSearch(player.searchdepth)

                column = agent.alpha_beta_search(game_state)['column']

                self.qOutput.put(column)


class Player():

    def __init__(self, number, counter, type, state, colour, searchdepth):

        self.number      = number
        self.counter     = counter
        self.type        = type
        self.state       = state
        self.colour      = colour
        self.searchdepth = searchdepth
        self.thinking    = False

    def _computer_move(self, game_state, qQuestion, qAnswer):

        column = -1

        if not self.thinking:

            self.thinking = True

            self.state = 'Thinking'

            qQuestion.put((self, game_state))

        if self.thinking and not qAnswer.empty():

            column = qAnswer.get()

            self.thinking = False

        return column


    def _human_move(self, display, game_state, events):

        counterGroup = display.backgroundGroup
        dragGroup    = display.foregroundGroup
        status       = display.status

        counterColumn = -1

        pos = pygame.mouse.get_pos()

        x, y = pos

        for event in events:

            if event.type == pygame.MOUSEBUTTONDOWN:

                # Check to see if picking up a new counter or continuing to drag an already dragged counter
                if (len(dragGroup) > 0) :

                    check_group = dragGroup

                else:
                    check_group = counterGroup

                # Check to see if counter is the right colour and the from the top of the pile (correct turn)
                # If the checkGroup is dragGroup the counter is removed and replaced into dragGroup
                for counter in check_group:

                    if counter.rect.collidepoint(pos) and counter.player == self.counter and counter.number == status['Turn']:
                        counterGroup.remove(counter)
                        dragGroup.add(counter)
                        self.state = 'Dragging'

            if event.type == pygame.MOUSEMOTION and len(dragGroup) > 0 and self.state == 'Dragging':

                for counter in dragGroup:

                    counter.rect.x = min(max(x - counter.radius, 0),1000 - 2 * counter.radius)

                    counter.rect.y = min(max(y - counter.radius, 800 * 0.15), 800 - 2 * counter.radius)

            if (event.type == pygame.MOUSEBUTTONUP):

                # If counter was being dragged, and it has been dropped in the 'drop zone' then change the game state
                # and drop the counter into the board.

                if  len(dragGroup) > 0:

                    checkDrop, counterRow = False, 0

                    for counter in dragGroup:

                        if (y < 1000 * 0.30 - counter.radius) and (x > 800 * 0.20 + counter.radius) and (
                                x < 1000 * 0.80 + counter.radius):

                            columnDistance = 10000

                            for i in game_state.getLegalActions():

                                columnX = display.board_pos[0] + display.board.columnCoords[i]

                                if abs(x - columnX) < columnDistance:
                                    columnDistance = abs(x - columnX)

                                    counterColumn = i

                                    checkDrop = True

                                    counterRow = game_state.next_row(counterColumn)

                            dragGroup.remove(counter)
                            counterGroup.add(counter)

                            self.state = 'Dropping'

                    else:
                        self.state = 'Dropped'



        return counterColumn


    def take_turn(self, display, game_state, qQuestion, qAnswer, events):

        if self.type == 'Computer':

            return self._computer_move(game_state, qQuestion, qAnswer)

        if self.type == 'Human':

            return self._human_move(display, game_state, events)




class Connect4():

    def __init__(self, width, height):

        pygame.init()

        # create dictionary used to manage the app and control the flow of the game
        self.status = {'GameState': 'Playing', 'Turn': 1, 'Player': -1 }


        #set up multithreading mode and queues
        mp.set_start_method('spawn')
        self.qQuestion = mp.Queue()
        self.qAnswer   = mp.Queue()
        self.thinker = mp.Process(target=BackgroundThinker, args=(self.status, self.qQuestion, self.qAnswer))
        self.thinker.start()

        #create colour dictionary
        colours    = {'Red': (200, 0, 0), 'Yellow': (200, 200, 0), 'Blue': (0, 0, 200), 'Green': (0, 200, 0), 'Background': (100, 100, 100), 'Black': (0, 0, 0), 'Transparent': (1, 1, 1)}

        self.players = [Player(1, -1, 'Human',    'Waiting', 'Yellow', 3),
                        Player(2,  1, 'Computer', ''       , 'Red',    3)]

        # create sprite groups and sprites for the counters

        self.dragGroup    = pygame.sprite.Group()
        self.counterGroup = pygame.sprite.Group()

        for i in range(21, 0, -1):

            for player in self.players:

                counter = Counter(player=player.counter, number=i, colour=colours[player.colour], width=width, height=height, status=self.status, colours = colours)

                counter.rect.x = counter.home[0] - counter.radius

                counter.rect.y = counter.home[1] + height * 0.6 - counter.radius

                self.counterGroup.add(counter)

        self.game_state = GameState()


        self.display = Display(status = self.status, width = width, height = height, colours = colours,
                               counterGroup = self.counterGroup, dragGroup = self.dragGroup)




    def MainLoop(self):

        while self.status['GameState'] != 'Quit':

            if self.status['GameState'] ==  'Reset': self.game_state = GameState()

            events = pygame.event.get()

            self.display.update(status=self.status, players = self.players, events=events)

            playerIndex = max(self.status['Player'], 0)

            slider = self.display.sliders[playerIndex].getValue()

            player = self.players[playerIndex]

            column = player.take_turn(self.display, self.game_state, self.qQuestion, self.qAnswer, events)

            if column >= 0 and column < 99:

                row = self.game_state.addCounter(player.counter, column)

                for counter in self.counterGroup:

                    if counter.player == self.status['Player'] and counter.number == self.status['Turn']:

                        counter.dest = self.display.calcCoords(column, row)

                player.state = 'Playing ' + str(column)

                self.status['Turn'] = self.status['Turn'] + 1 if self.status['Player'] == 1 else self.status['Turn']
                self.status['Player'] = -1 * self.status['Player']

            elif column ==99:

                if self.game_state.score < 2000: text = 'Yellow Win!'
                elif self.game_state.score > 2000: text = 'Red Win!'
                else: text = 'Draw'

                print(text)

        self.thinker.kill()







