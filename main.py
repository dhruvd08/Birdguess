import http
import random
import time
import json
import requests
from data import species
from flask import Flask, request

app = Flask(__name__)


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
            for key in species.keys():
                if species[key]['countries'] == content['player_country_code']:
                    location_vise_species.append(key)

            chosen_species: str = random.choice(location_vise_species)
            letters = [letter.upper() for letter in chosen_species]
            game_id = time.time()
            with open(f'data/{content["player_id"]}', mode='w') as f:
                f.write(f'{game_id}')
            with open(f'player_data/{game_id}.json', mode='w') as f:
                new_game = {
                    'game_id': game_id,
                    'species': chosen_species,
                    'status': 'new',
                    'letters': letters
                }
                json.dump(obj=new_game, fp=f)
            send('TEXT', ''.join(letters), content['player_id'])
        else:
            send('TEXT', f'Hello {content["player_name"]}! We will be live soon!', content['player_id'])
        return str(http.HTTPStatus.OK.value)
    else:
        return str(http.HTTPStatus.BAD_REQUEST.value)


if __name__ == '__main__':
    app.run()
