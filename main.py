import http
import random
import time
import json
import requests
from data import species
from flask import Flask, request

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
    """
    input_params{'msg_body': 'ttt', 'player_id': 4, 'player_name': 'Simba', 'msg_id': 1710389065,
    'player_country_code': 'IN'}
    header{'webhook-key': 'fa64f9edd0351f4238d7cbfa5b8e1c12e148aa1629bdceefe639bee8b93a2d5d'}
     """
    content = request.json
    print(content)

    if (request.headers.get('webhook-key')
            == 'fa64f9edd0351f4238d7cbfa5b8e1c12e148aa1629bdceefe639bee8b93a2d5d'):
        if content['msg_body'] == 'bg':
            location_vise_species = []
            for sp in species.keys():
                if content['player_country_code'] in species[sp]['countries']:
                    location_vise_species.append(sp)

            chosen_species: str = random.choice(location_vise_species)
            letters = ['_' if letter.lower() in alphabets else ' ' for letter in chosen_species]
            game_id = str(int(time.time()))
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
            send('TEXT', ''.join(letters), content['player_id'])
        elif content['msg_body'].lower() in [alphabet for alphabet in alphabets]:
            with open(f'/home/shreedave/Birdguess/data/{content["player_id"]}') as f:
                game_id = f.read()
            with open(f'/home/shreedave/Birdguess/player_data/{game_id}.json') as f:
                current_game = json.load(fp=f)
            entered_alphabet: str = content['msg_body'].lower()
            lives = current_game['lives']
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
            else:
                send('TEXT', 'That\'s wrong, you lose a life.', content['player_id'])
                lives -= 1
            with open(f'/home/shreedave/Birdguess/player_data/{game_id}.json', mode='w') as f:
                new_game = {
                    'game_id': game_id,
                    'species': current_game['species'],
                    'status': 'in_progress',
                    'lives': lives,
                    'letters': current_game['letters']
                }
                json.dump(obj=new_game, fp=f)
        else:
            send('TEXT', f'"{content["msg_body"]}" is not in the alphabetic order.', content['player_id'])
        return str(http.HTTPStatus.OK.value)
    else:
        return str(http.HTTPStatus.BAD_REQUEST.value)


@app.route('/')
def hello():
    return 'hello world'


if __name__ == '__main__':
    app.run()
