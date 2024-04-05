import os
import random
import shelve

import PIL.Image
from PIL import Image, ImageFont, ImageDraw

home_path = '/home/shreedave/Birdguess/'
# home_path = ''


class Img_data:

    def __init__(self, bg_color: tuple, fg_color: tuple, bg_img: str):
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.bg_img = bg_img


color_comb = [Img_data((29, 113, 81), (246, 246, 233), f'{home_path}imgs/bg_1.png'),
              Img_data((175, 122, 31), (255, 255, 255), f'{home_path}imgs/bg_2.png'),
              Img_data((129, 66, 86), (242, 233, 225),f'{home_path}imgs/bg_3.png'),
              Img_data((113, 111, 53), (242, 233, 225),f'{home_path}imgs/bg_4.png'),
              Img_data((255, 249, 243), (65, 75, 59),f'{home_path}imgs/bg_5.png'),
              Img_data((140, 168, 124), (65, 75, 59), f'{home_path}imgs/bg_6.png')]


def get_img_path(id_: int) -> str:
    """
    Get image local path for the id_
    :param id_: Unique image identifier
    :return: Output image local path
    """
    if os.path.isfile(f'{home_path}output/{id_}.png'):
        return f'{home_path}output/{id_}.png'
    else:
        return None


def process(id_: int, word: list, chances_remaining: int) -> str:
    output_img_path = get_img_path(id_)

    if output_img_path is None:
        # random palette
        palette = random.choice(color_comb)

        with shelve.open(f'{home_path}data/{id_}', flag='c') as db:
            db[f'{id_}'] = palette
    else:
        with shelve.open(f'{home_path}data/{id_}', flag='c') as db:
            palette: Img_data = db[f'{id_}']

    # Create a blank image
    # im = Image.new('RGBA', (1024, 1024), palette.bg_color)
    with Image.open(palette.bg_img).convert('RGBA') as im:
        font = ImageFont.load_default(100)
        x_loc = 60
        y_loc = 250
        for letter in word:
            txt = Image.new('RGBA', im.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(txt)
            if letter == '*':
                # Next line
                y_loc += 100
                x_loc = 0
                letter = ''
            d.text((x_loc, y_loc), letter, fill=palette.fg_color, anchor='mb', font=font)
            x_loc += 70
            im = Image.alpha_composite(im, txt)

        white_bg = Image.new('RGBA', (300, 300), color='white')
        Image.Image.paste(im, white_bg, box=(0, 724))

        with (Image.open(f'{home_path}chances/{chances_remaining}.png', 'r').convert('RGBA').resize((300, 300),
                                                                                         PIL.Image.NEAREST) as chances):
            Image.Image.paste(im, chances, (0, 724))

    im.save(f'{home_path}output/{id_}.png')
    return f'{home_path}output/{id_}.png'
