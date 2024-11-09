import pygame

import pygame_widgets
from   pygame_widgets.slider import Slider
from   pygame_widgets.button import Button


class Board(pygame.surface.Surface):

    def  __init__(self, **kwargs):

        width   = kwargs['width']
        height  = kwargs['height']
        colours = kwargs['colours']

        super().__init__((width, height))

        self.set_colorkey(colours['Transparent'])

        frame = pygame.Rect(0, 0, width, height)

        self.columnCoords = [0, 0, 0, 0, 0, 0, 0]
        self.rowCoords    = [0, 0, 0, 0, 0, 0]

        pygame.draw.rect(self, colours['Blue'], frame)

        self.holeRadius   = int(width / 20)
        self.holeSpacing  = int(width / 8)

        for i in range(7):

            self.columnCoords[i] = self.holeSpacing * (i + 1)

            for j in range(6):

                self.rowCoords[5 - j] =  int(self.holeSpacing * (j + 0.8))

                pygame.draw.circle(self, colours['Transparent'], (self.holeSpacing * (i + 1), self.holeSpacing * (j + .8)), self.holeRadius, 0)

class Counter(pygame.sprite.Sprite):

    def  __init__(self, **kwargs):

        super().__init__()

        self.colour  = kwargs['colour']
        self.width   = kwargs['width']
        self.height  = kwargs['height']
        self.player  = kwargs['player']
        self.number  = kwargs['number']
        self.status  = kwargs['status']
        self.colours = kwargs['colours']

        self.radius     = self.width * 0.03

        self.sideRail    = self.width * 0.85  if self.player == 1 else self.width * 0.15
        self.topRail     = self.height * 0.20
        self.bottomRail  = self.height * 0.91

        colourBorder = self.colours['Black']
        colourDisk   = self.colour

        self.image  = pygame.Surface((self.radius * 2, self.radius * 2))

        self.image.set_colorkey(self.colours['Transparent'])

        pygame.draw.rect(self.image, self.colours['Transparent'], (0, 0, self.radius * 2, self.radius * 2))

        pygame.draw.circle(self.image, colourDisk,   (self.radius, self.radius), self.radius, 0)
        pygame.draw.circle(self.image, colourBorder, (self.radius, self.radius), self.radius, 2)

        self.rect = self.image.get_rect()

        self.speed = (0, 1)

        self.home   = (self.sideRail, 0.25 * self.width + self.number * 15)
        self.dest   = (self.sideRail, 0.25 * self.width + self.number * 15)

    def move(self):

        moved = False

        rail = self.bottomRail if self.status['GameState'] == 'Reset' else self.topRail

        displaced = (self.dest[0] - self.rect.x - self.radius, self.dest[1] - self.rect.y )

        if displaced[0] != 0:                                                   # counter has wrong x position

            if self.rect.y == rail:                                             # counter on one of the rails

                self.speed = (-1,0) if displaced[0] < 0 else (1,0)              # move towards correct x column

            else:                                                               # move counter towards the rail

                if   self.rect.y > rail: self.speed = (0,-1)
                elif self.rect.y < rail: self.speed = (0, 1)

                else:                                                           # on rail so move toward x
                    if self.rect.x > self.sideRail:   self.speed = (-1, 0)
                    elif self.rect.x < self.sideRail: self.speed = (1, 0)

        else:                                                                   # x position is correct

                if    self.rect.y > self.dest[1] - self.radius: self.speed = ( 0,-1)
                elif  self.rect.y < self.dest[1] - self.radius: self.speed = ( 0, 1)
                else: self.speed = (0, 0)


        self.rect.x = self.rect.x + self.speed[0]
        self.rect.y = self.rect.y + self.speed[1]

        if self.speed[0] != 0 or self.speed[1] != 0: moved = True

        return moved

class Display():

    def __init__(self, **kwargs):

        # Create the window and set the class variables

        self.width           = kwargs['width']
        self.height          = kwargs['height']
        self.colours         = kwargs['colours']
        self.status          = kwargs['status']
        self.backgroundGroup = kwargs['counterGroup']
        self.foregroundGroup = kwargs['dragGroup']

        # Create the window
        self.window  = pygame.display
        self.window.set_caption('Connect 4')
        self.surface = self.window.set_mode((self.width, self.height))


        #create the background and the board Rect and Surface objects
        self.board = Board(width=self.width * 0.6, height=self.height * 0.6, colours=self.colours)
        self.background = pygame.Rect( 0, 0, self.width, self.height )
        self.board_pos  = (self.width * 0.2, self.height * 0.3)

        #   create widgets for game control
        self.slidersPreChange = [0, 1]

        self.sliders = [ Slider(self.surface, (self.width * 0.1), 50, 30, 20, handleColour=(1, 0, 0), handleRadius=10, min=0, max=1, step=1, initial=0),
                         Slider(self.surface, (self.width * 0.6), 50, 30, 20, handleColour=(1, 0, 0), handleRadius=10, min=0, max=1, step=1, initial=1)]

        self.searchdepth = [ Slider(self.surface, (self.width * 0.1), 80, 120, 20, handleColour=(1, 0, 0), handleRadius=10, min=2, max=10, step=1, initial=6),
                             Slider(self.surface, (self.width * 0.6), 80, 120, 20, handleColour=(1, 0, 0), handleRadius=10, min=2, max=10, step=1, initial=6)]

        self.buttons = [ Button(self.surface, (self.width * 0.4) ,               100, 150, 50, text='New Game', fontSize=30, inactiveColour=self.colours['Green'], onClick=self.new_game),
                         Button(self.surface, (self.width * 0.85), self.height * 0.9, 100, 50, text='Quit',     fontSize=30, inactiveColour=self.colours['Red']  , onClick=self.quit)]

        self.window.update()

    def quit(self):

        self.status['GameState'] = 'Quit'

    def new_game(self):

        self.status['GameState'] = 'Reset'
        self.status['Player']    = -1
        self.status['Turn']      = 1

        for counter in self.backgroundGroup: counter.dest = counter.home



    def move_counters(self):

        moved = False

        for counter in self.backgroundGroup:

            if counter.move(): moved = True

        return moved

    def calcCoords(self, counterColumn, counterRow):

        Xcoord = self.board_pos[0] + self.board.columnCoords[counterColumn]

        Ycoord = self.board_pos[1] + self.board.rowCoords[counterRow]

        return (Xcoord, Ycoord)




    def update(self, **kwargs):

        events = kwargs['events']
        players = kwargs['players']
        status = kwargs['status']

        x, y = pygame.mouse.get_pos()

        if status['GameState'] == 'Reset':

            status['GameState'] = '' if not self.move_counters() else 'Reset'

        self.move_counters()

        pygame.draw.rect(self.surface, self.colours['Background'], self.background)

        pygame_widgets.update(events)

        self.backgroundGroup.draw(self.surface)

        self.surface.blit(self.board, self.board_pos)

        player_type = lambda slider: 'Human' if slider.getValue() == 0 else 'Computer'

        for i, slider in enumerate(self.sliders):

            # change player description if slider toggle switched

            players[i].type = player_type(self.sliders[i])
            players[i].searchdepth = self.searchdepth[i].getValue()


            # check to see if the slider value has changed
         #   if self.sliders[i].getValue() != self.slidersPreChange:
         #       self.slidersPreChange = self.sliders[i].getValue()

        texts = [
            {'Message': players[0].type, 'Position': ((self.width * 0.05) + 100, 40), 'Size': (120, 36)},
            {'Message': players[1].type, 'Position': ((self.width * 0.55) + 100, 40), 'Size': (120, 36)},
            {'Message': players[0].state, 'Position': ((self.width * 0.05) +  70, 120), 'Size': (120, 36)},
            {'Message': players[1].state, 'Position': ((self.width * 0.55) +  70, 120), 'Size': (120, 36)}
        ]

        for text in texts:

            render = pygame.font.SysFont('arial', 32).render(text['Message'], False, self.colours['Black'], self.colours['Background'])
            textRect = render.get_rect()
            textRect.topleft = text['Position']
            self.surface.blit(render, textRect)


        self.foregroundGroup.draw(self.surface)

        self.window.update()

        return status


