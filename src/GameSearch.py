from src.GameState import  GameState
import time

class GameSearch:

    def __init__(self, MaxDepth, ):

        self.MaxDepth   = MaxDepth

        self.Best       = None

    def search(self, game_state, depth=1):

        # Candidate is a directionary containing a 'score' and a 'column' (added later)

        Candidate = {'score': 0}

        # decide if it is a machine or human move (odd means machine move)
        if (depth % 2 == 1):

            # computer move set best to a low score
            Best = {'score': -10000000}
            disc = 1

        else:
            # human move set best to a high score
            Best = {'score': +10000000}
            disc = -1

        for col in game_state.getLegalActions():

            new_state = GameState(game_state)
            new_state.addCounter(disc, col)

            new_state_score = new_state.score

            if new_state.is_terminal() is not None:

                Candidate['score']  = new_state_score
                Candidate['column'] = col

            # if not leaf node (DepthMax not reached, test for termination of recursion
            elif (depth < self.MaxDepth) and (len(new_state.getLegalActions()) > 0 ):

                Candidate = self.search(new_state, depth + 1)


            # maximum depth of requested lookahead reached so just evaluate
            else:

                Candidate['score'] = new_state_score
                Candidate['column'] = col

            if (depth % 2 == 1):

                # Machine - so candidate needs to be higher than Best

                if Candidate['score'] > Best['score']:
                    Best['score'] = Candidate['score']
                    Best['column'] = col


            else:

                # Human - so candidate needs to be lower than Best

                if Candidate['score'] < Best['score']:
                    Best['score'] = Candidate['score']
                    Best['column'] = col

            #print(new_state, Best, Candidate)

        return Best


    def alpha_beta_search(self, game_state, depth=1, alpha=-100000000, beta=100000000):

      #  time.sleep(0.0000001)

        counter =  1 if depth % 2 == 1 else -1
        min_max =  1 if depth % 2 == 1 else -1 # 1 means MAX and -1 means MIN

        if game_state.is_terminal() or (depth == self.MaxDepth):

            return  {'score': game_state.score, 'column': 99}

        else:

            Best = {'score': -20000000 * min_max}

            for action in game_state.getLegalActions():

                successor = GameState(game_state)
                successor.addCounter(counter, action)

                Candidate = self.alpha_beta_search(successor, depth + 1, alpha, beta)

                if min_max ==  1:

                    if Candidate['score'] > Best['score']: Best = {'score':  Candidate['score'], 'column':action}

                    if Candidate['score'] > beta: return Best

                    alpha = max(alpha, Candidate['score'])

                if min_max == -1:

                    if Candidate['score'] < Best['score']: Best = {'score':  Candidate['score'], 'column':action}

                    if Candidate['score'] < alpha: return Best

                    beta = min(beta, Candidate['score'])



           # print(min_max, Best, Candidate, alpha, beta)

        self.Best = Best

        return Best
