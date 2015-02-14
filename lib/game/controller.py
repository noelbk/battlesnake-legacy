
import time

from lib.game.engine import Engine
from lib.caller import AsyncCall
from lib.game.models import Game, GameState


def _log(msg):
    print "[controller] %s" % str(msg)


def start_game(game_id, manual):
    game = Game.find_one({'_id': game_id})

    if not game:
        raise Exception('Could not find game %s' % game_id)

    if manual:
        game.state = Game.STATE_MANUAL
        game.save()
    else:
        game.state = Game.STATE_READY
        game.save()

    return game


def create_game(snake_urls, width, height, turn_time):
    game = Game(width=width, height=height, turn_time=turn_time)

    # Fetch snakes
    start_urls = [('%s/start' % url) for url in snake_urls]
    responses = AsyncCall(
        payload={
            'game_id': game.id
        },
        urls=start_urls,
        timeout=game.turn_time
    ).start()

    snakes = []
    for snake_url in snake_urls:
        for url, response in responses.items():
            if response is None:
                # FREAK OUT
                raise Exception('failed to contact snake: %s' % url)

            if url.startswith(snake_url):
                snakes.append({
                    'url': snake_url,
                    'color': response['color'],
                    'id': response['name'],
                    'name': response['name'],
                    'taunt': response['taunt']
                })

    game.insert()

    # Create the first GameState
    game_state = Engine.create_game_state(game.id, game.width, game.height)

    # Init the first GameState
    Engine.add_snakes_to_board(game_state, snakes)
    Engine.add_random_food_to_board(game_state)

    # Save the first GameState
    game_state.insert()

    return (game, game_state)


def get_moves(game_state, timeout):
    urls = []
    for snake in game_state.snakes:
        urls.append('%s/move' % snake['url'])

    payload = {
        'game_id': game_state.game_id,
        'turn': game_state.turn,
        'board': game_state.board,
        'snake': game_state.snakes
    }

    responses = AsyncCall(payload, urls, timeout).start()

    moves = []

    for snake in game_state.snakes:
        for url, response in responses.items():
            if response is None:
                # Too bad for that snake. Engine should keep it moving
                # in current direction
                _log('%s timed out' % snake['id'])
                continue

            if url.startswith(snake['url']):
                moves.append({
                    'snake_id': snake['id'],  # Don't trust id from response
                    'move': response['move']
                })
    return moves


def next_turn(game):
    game_states = GameState.find({'game_id': game.id})

    if len(game_states) > 0:
        game_state = game_states[0]
        moves = get_moves(game_state, game.turn_time)
        next_game_state = Engine.resolve_moves(game_state, moves)
        next_game_state.insert()

        return next_game_state
    else:
        raise Exception('No GameStates found for %s' % game)


def run_game(game):
    if game.state != Game.STATE_READY:
        raise Exception("Controller tried to run game that wasn't ready")

    game.state = Game.STATE_PLAYING
    game.save()

    new_game_state = None

    # We have exclusive game access now
    _log('starting game: %s' % game.id)

    while game.state != Game.STATE_DONE:
        start_time = time.time()

        # moves = fetch_moves_async

        try:
            new_game_state = next_turn(game)
        except Exception as e:
            _log('failed to insert game state for %s: %s' % (game.id, e))
            break

        _log('finished turn: %s' % new_game_state)

        if new_game_state.is_done():
            game.state = Game.STATE_DONE
            game.save()
        else:
            # Wait at least
            elasped_time = time.time() - start_time
            sleep_for = max(0, float(game.turn_time) - elasped_time)
            _log('sleeping for %.2f: %s' % (sleep_for, new_game_state.id))
            time.sleep(sleep_for)

    _log('done: %s' % new_game_state)
