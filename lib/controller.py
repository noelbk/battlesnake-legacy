from lib.game.engine import Engine
from lib.game.models import Game, GameState


def create_game(snakes, width, height):
    game = Game(width=width, height=height)
    game.insert()

    # Create the first GameState
    game_state = Engine.create_game_state(game)

    # Init the first GameState
    Engine.add_snakes_to_board(game_state, snakes)
    Engine.add_random_food_to_board(game_state)

    # Save the first GameState
    game_state.insert()

    print '----------------------------'
    print game
    print game_state.to_string()
    print '----------------------------'

    return (game, game_state)


def next_turn(game, moves):
    game_states = GameState.find({'game_id': game._id})

    if len(game_states) > 0:
        game_state = game_states[0]
        next_game_state = Engine.resolve_moves(game_state, moves)
        next_game_state.insert()

        print game_state.to_string()
        print '----------------------------'
        print next_game_state.to_string()
        print '----------------------------'

        return next_game_state
    else:
        raise Exception('No GameStates found for %s' % game)