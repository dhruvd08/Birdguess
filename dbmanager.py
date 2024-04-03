import os

import sqlalchemy
from sqlalchemy import text

from dbmodel import GameDBO

sqlalchemy_database_uri = "mysql://{username}:{password}@{hostname}/{databasename}".format(
    username=os.environ['MYSQL_DB_USER'],
    password=os.environ['MYSQL_DB_PWD'],
    hostname=os.environ['MYSQL_DB_HOST_ADDRESS'],
    databasename=os.environ['MYSQL_DB_NAME'],
)
engine = sqlalchemy.create_engine(sqlalchemy_database_uri)


def letters_to_array(c_letters: str):
    c_letters = c_letters.replace('[', '').replace(']', '')
    c_letters = list(c_letters)
    return c_letters


def to_game(gme):
    return GameDBO(
        id=gme.id,
        current_letters=letters_to_array(gme.current_letters),
        cmd=gme.cmd,
        word_id=gme.word_id,
        word=gme.word,
        lives=gme.lives,
        status=gme.status,
        player_id=gme.player_id,
        created_date=gme.created_date,
        updated_date=gme.updated_date
    )


def create_game(g: GameDBO):
    session = engine.connect()
    session.execute(text(f"insert into games (player_id, status, cmd, word_id, word, lives, current_letters) "
                         f"values ({g.player_id}, '{g.status}', '{g.cmd}', {g.word_id}, '{g.word}', {g.lives}, '{g.current_letters}')"))
    session.commit()
    session.close()


def update_game(game_id, current_letters, status):
    session = engine.connect()
    session.execute(text(f"update games set current_letters = '{current_letters}',"
                         f"status = '{status}' "
                         f"where id = {game_id}"))
    session.commit()
    session.close()


def update_lives(game_id, lives, status):
    session = engine.connect()
    session.execute(text(f"update games set lives = {lives},"
                         f"status = '{status}'"
                         f"where id = {game_id}"))
    session.commit()
    session.close()


def get_game(game_id) -> GameDBO:
    session = engine.connect()
    g: GameDBO = session.execute(text(f"select * from games where id={game_id}")).first()
    session.close()
    return to_game(g)


def get_game_by_player_id(player_id):
    session = engine.connect()
    result = session.execute(text(f"select * from games where player_id={player_id}")).all()
    session.close()
    games = []
    for row in result:
        games.append({'id': row[0], 'player_id': row[1], 'status': row[2], 'command': row[3],
                      'word_id': row[4], 'word': row[5], 'lives': row[6], 'current_letters': row[7],
                      'created_on': row[8], 'updated_on': row[9]})
    return games


def get_latest_game_by_player_id(player_id):
    session = engine.connect()
    result = session.execute(text(f"select * from games where player_id={player_id}")).all()
    session.close()
    games = []
    for row in result:
        games.append({'id': row[0], 'player_id': row[1], 'status': row[2], 'command': row[3],
                      'word_id': row[4], 'word': row[5], 'lives': row[6], 'current_letters': letters_to_array(row[7]),
                      'created_on': row[8], 'updated_on': row[9]})
    return games[-1]


def get_game_by_command(command):
    session = engine.connect()
    result = session.execute(text(f"select * from games where group='{command}'")).all()
    session.close()
    games = []
    for row in result:
        games.append({'id': row[0], 'player_id': row[1], 'status': row[2], 'command': row[3],
                      'word_id': row[4], 'word': row[5], 'lives': row[6], 'current_letters': row[7],
                      'created_on': row[8], 'updated_on': row[9]})
    return games


def get_game_by_player_id_and_status(player_id, status):
    session = engine.connect()
    result = session.execute(text(f"select * from games where player_id={player_id} and status='{status}'")).all()
    session.close()
    games = []
    for row in result:
        games.append({'id': row[0], 'player_id': row[1], 'status': row[2], 'command': row[3],
                      'word_id': row[4], 'word': row[5], 'lives': row[6], 'current_letters': row[7],
                      'created_on': row[8], 'updated_on': row[9]})
    return games


def player_has_completed_the_word(player_id, word) -> bool:
    session = engine.connect()
    result = session.execute(text(f"select * from games where player_id={player_id} "
                                  f"and word='{word}' and status='DONE'")).all()
    session.close()
    if result:
        return True
    else:
        return False


# letters = '______'
# print(str(letters))
# g = GameDBO(player_id=2, cmd='wgb', status='NEW', word_id=4, word='Shikra', current_letters=str(letters))
# create_game(g)
#
# letters = 'SHIKRA'
# g = GameDBO(id=1, player_id=2, status='DONE', word='Shikra', current_letters=str(letters))
# update_game(g)
#
# print(get_game(1).current_letters)
# print(get_game_by_player_id(2))

# print(get_game_by_player_id_and_status(2, 'IN_PROGRESS'))
# print(player_has_completed_the_word(2, 'Shikra'))
