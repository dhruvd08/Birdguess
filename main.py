import http
import importlib
import random
import time
import requests
from dbmodel import GameDBO
from flask import Flask, request, send_file
import ihm_lite
import dbmanager

home_path = '/home/shreedave/Birdguess/'
# home_path = ''

local = False

app = Flask(__name__)
alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
             'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
             'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
             'y', 'z']


def send(msg_type: str, msg: str, to: int):
    endpoint = 'https://foresthut.pythonanywhere.com/messages/message'

    input_params = {
        'msg_id': str(int(time.time())),
        'msg_body': msg,
        'msg_type': msg_type,
        'player_id': to
    }

    header = {
        'api-key': 'fa64f9edd0351f4238d7cbfa5b8e1c12e148aa1629bdceefe639bee8b93a2d5d'
    }

    try:
        response = requests.post(url=endpoint, json=input_params, headers=header, timeout=1).json()
    except:
        pass


def process_input(user_input, game: GameDBO):
    got_right = False

    if user_input.lower() in alphabets:
        if user_input.upper() in game.current_letters:
            send('TEXT', f'You have already placed that alphabet.', game.player_id)
        elif user_input.lower() in game.word:
            indexs = []
            for i, let in enumerate(game.word):
                if let == user_input:
                    indexs.append(i)
            for ind in indexs:
                game.current_letters[ind] = user_input.upper()

            if '_' not in game.current_letters:
                got_right = True
                send("TEXT", 'You got it right! Here\'s your card.', game.player_id)
                send('IMAGE',
                     f'https://shreedave.pythonanywhere.com/species/img/'
                     f'{game.cmd}/'
                     f'{"".join(game.word).replace(" ", "-")}',
                     game.player_id)
                game.status = 'done'
                ihm_lite.process(int(game.id),
                                 [letter if not letter == ' ' else '*' for letter in game.current_letters],
                                 game.lives)
            dbmanager.update_game(game_id=game.id, current_letters=''.join(game.current_letters),
                                  status=game.status)
        else:
            game.lives -= 1

            if game.lives == 0:
                game.status = 'over'

            dbmanager.update_lives(game_id=game.id, lives=game.lives, status=game.status)

        if not got_right:
            ihm_lite.process(int(game.id),
                             [letter if not letter == ' ' else '*' for letter in game.current_letters],
                             game.lives)
            if local:
                print(f'IMAGE, https://shreedave.pythonanywhere.com/games/img/{game.id}, {game.player_id}')
            else:
                send('IMAGE', f'https://shreedave.pythonanywhere.com/games/img/{game.id}', game.player_id)
    else:
        send('TEXT', 'Enter a valid alphabet between a-z.', game.player_id)


@app.route('/notify-wh', methods=['POST'])
def notify():
    if (request.headers.get('webhook-key')
            == 'fa64f9edd0351f4238d7cbfa5b8e1c12e148aa1629bdceefe639bee8b93a2d5d'):
        commands = ['wgb', 'wgm']

        content = request.json
        command = content['msg_body'].lower()
        player_id = int(content['player_id'])
        if command in commands:
            list_of_words = importlib.import_module(command).words
            print(list_of_words)
            word_id: int = random.randint(1, len(list_of_words))
            word = list_of_words[word_id - 1][str(word_id)]['word']
            letters = ['_' if letter.lower() in alphabets else '*' for letter in word]

            new_game = GameDBO(player_id=int(player_id), status='in_progress', cmd=command,
                               word_id=int(word_id), word=word, lives=6, current_letters=''.join(letters))
            dbmanager.create_game(g=new_game)
            game: GameDBO = dbmanager.get_latest_game_by_player_id(player_id=player_id)
            print(game.current_letters)
            ihm_lite.process(game.id, game.current_letters, chances_remaining=game.lives)
            if local:
                print(f'IMAGE, https://shreedave.pythonanywhere.com/games/img/{game.id}, {player_id}')
            else:
                send('IMAGE', f'https://shreedave.pythonanywhere.com/games/img/{game.id}', player_id)


        else:
            game: GameDBO = dbmanager.get_latest_game_by_player_id(player_id)
            print(game.current_letters)
            if game.status == 'over' or game.status == 'done':
                send('TEXT', f'Send "{game.cmd}" to start a new game.', player_id)
                return str(http.HTTPStatus.OK)
            elif game.status == 'in_progress':
                process_input(command, game)

        return str(http.HTTPStatus.OK)
    else:
        return str(http.HTTPStatus.BAD_REQUEST)


@app.route('/games/img/<game_id>')
def game_img(game_id: str):
    return send_file(f'{home_path}output/{game_id}.png')


@app.route('/species/img/<group>/<species_name>')
def bird_img(group: str, species_name: str):
    return send_file(f'{home_path}imgs/{group}/{species_name}.png')


if __name__ == '__main__':
    app.run()
