import http
import random
import time
import json
import requests
from data import species
from flask import Flask, request, send_file
import ihm

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

    response = requests.post(url=endpoint, json=input_params, headers=header).json()
    print(response)


@app.route('/notify-wh', methods=['POST'])
def notify():
    content = request.json
    print(content)

    if (request.headers.get('webhook-key')
            == 'fa64f9edd0351f4238d7cbfa5b8e1c12e148aa1629bdceefe639bee8b93a2d5d'):
        print('checking if game is over')
        try:
            with open(f'/home/shreedave/Birdguess/data/{content["player_id"]}') as f:
                game_id = f.read()
            with open(f'/home/shreedave/Birdguess/player_data/{game_id}.json') as f:
                current_game = json.load(fp=f)
        except FileNotFoundError:
            cont = True
        else:
            cont = False
            if current_game['status'] == 'over' and content['msg_body'].lower() != 'bg':
                print('game is over and player did not send "bg"')
                send('TEXT', 'Send "bg" to start a new game.', content['player_id'])
                with open(f'/home/shreedave/Birdguess/player_data/{game_id}.json', mode='w') as f:
                    new_game = {
                        'game_id': game_id,
                        'species': current_game['species'],
                        'status': current_game['status'],
                        'lives': current_game['lives'],
                        'letters': current_game['letters']
                    }
                    json.dump(obj=new_game, fp=f)
                    return str(http.HTTPStatus.OK.value)
            else:
                cont = True

        if content['msg_body'] == 'bg' and cont:
            print('player sent "bg"')
            location_vise_species = []
            for sp in species.keys():
                if content['player_country_code'] in species[sp]['countries']:
                    location_vise_species.append(sp)

            chosen_species: str = random.choice(location_vise_species)
            print('decided species')
            letters = ['_' if letter.lower() in alphabets else ' ' for letter in chosen_species]
            game_id = str(int(time.time()))
            ihm.process(int(game_id), [letter if not letter == ' ' else '*' for letter in letters], 6,
                        '/home/shreedave/Birdguess/imgs/orange-minivet.png')
            with open(f'/home/shreedave/Birdguess/data/{content["player_id"]}', mode='w') as f:
                f.write(f'{game_id}')
            with open(f'/home/shreedave/Birdguess/player_data/{game_id}.json', mode='w') as f:
                new_game = {
                    'game_id': game_id,
                    'species': [letter for letter in chosen_species],
                    'status': 'in_progress',
                    'lives': 6,
                    'letters': letters
                }
                json.dump(obj=new_game, fp=f)
            print('made game_id and game')
            # send('TEXT', ' '.join(letters), content['player_id'])
            send('IMAGE', f'https://shreedave.pythonanywhere.com/games/img/{game_id}', content['player_id'])
        elif content['msg_body'].lower() in [alphabet for alphabet in alphabets] and cont:
            with open(f'/home/shreedave/Birdguess/data/{content["player_id"]}') as f:
                game_id = f.read()
            with open(f'/home/shreedave/Birdguess/player_data/{game_id}.json') as f:
                current_game = json.load(fp=f)
            status: str = current_game['status']
            lives: int = current_game['lives']
            ihm.process(int(game_id), [letter if not letter == ' ' else '*' for letter in current_game['letters']], lives,
                        '/home/shreedave/Birdguess/imgs/orange-minivet.png')
            if status == 'in_progress':
                entered_alphabet: str = content['msg_body'].lower()
                if entered_alphabet.upper() in current_game['letters']:
                    send('TEXT', f'You have already placed that alphabet.', content['player_id'])
                    return str(http.HTTPStatus.OK.value)
                elif entered_alphabet in current_game['species']:
                    indexs = []
                    for i, let in enumerate(current_game['species']):
                        if let == entered_alphabet:
                            indexs.append(i)
                    for ind in indexs:
                        current_game['letters'][ind] = entered_alphabet.upper()
                    # send('TEXT', ' '.join(current_game['letters']), content['player_id'])
                    send('IMAGE', f'https://shreedave.pythonanywhere.com/games/img/{game_id}', content['player_id'])
                    if '_' not in current_game['letters']:
                        status = 'over'
                        send('TEXT', 'You got it right!!', content['player_id'])
                else:
                    lives -= 1
                    send('TEXT', f'That\'s wrong, you lost a chance. '
                                 f'Now you have {lives}/6 chances left. ', content['player_id'])
                    if lives == 0:
                        status = 'over'
                        send('TEXT', 'You have no chances left. Game over.', content['player_id'])
            elif status == 'over':
                send('TEXT', 'Send "bg" to start a new game.', content['player_id'])
            with open(f'/home/shreedave/Birdguess/player_data/{game_id}.json', mode='w') as f:
                new_game = {
                    'game_id': game_id,
                    'species': current_game['species'],
                    'status': status,
                    'lives': lives,
                    'letters': current_game['letters']
                }
                json.dump(obj=new_game, fp=f)
            return str(http.HTTPStatus.OK.value)
        elif cont:
            send('TEXT', f'"{content["msg_body"]}" is not in the alphabetic order.', content['player_id'])
        return str(http.HTTPStatus.OK.value)
    else:
        return str(http.HTTPStatus.BAD_REQUEST.value)


@app.route('/games/img/<game_id>')
def game_img(game_id: str):
    return send_file(f'output/{game_id}.png')


if __name__ == '__main__':
    app.run()
