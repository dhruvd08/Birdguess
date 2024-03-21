import os
import random
import shelve

import PIL.Image
from PIL import Image, ImageFont, ImageDraw


class Img_data:

    def __init__(self, bg_color: tuple, fg_color: tuple):
        self.bg_color = bg_color
        self.fg_color = fg_color


color_comb = [Img_data((29, 113, 81), (246, 246, 233)),
              Img_data((175, 122, 31), (255, 255, 255)),
              Img_data((129, 66, 86), (242, 233, 225)),
              Img_data((113, 111, 53), (242, 233, 225)),
              Img_data((255, 249, 243), (65, 75, 59)),
              Img_data((140, 168, 124), (65, 75, 59))]


def get_img_path(id_: int) -> str:
    """
    Get image local path for the id_
    :param id_: Unique image identifier
    :return: Output image local path
    """
    if os.path.isfile(f'output/{id_}.png'):
        return f'output/{id_}.png'
    else:
        return None


def process(id_: int, word: list, chances_remaining: int) -> str:
    output_img_path = get_img_path(id_)

    if output_img_path is None:
        # random palette
        palette = random.choice(color_comb)

        with shelve.open(f'data/{id_}', flag='c') as db:
            db[f'{id_}'] = palette
    else:
        with shelve.open(f'data/{id_}', flag='c') as db:
            palette: Img_data = db[f'{id_}']

    print(palette.bg_color, palette.fg_color)

    # Create a blank image
    im = Image.new('RGBA', (1024, 1024), palette.bg_color)

    font = ImageFont.load_default(100)
    x_loc = 65
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
        x_loc += 65
        im = Image.alpha_composite(im, txt)

    white_bg = Image.new('RGBA', (1024, 300), color='white')
    Image.Image.paste(im, white_bg, box=(0, 724))

    with Image.open(f'chances/{chances_remaining}.png', 'r').convert('RGBA').resize((300, 300),
                                                                                    PIL.Image.NEAREST) as chances:
        Image.Image.paste(im, chances, (0, 724))

    im.save(f'output/{id_}.png')
    return f'output/{id_}.png'


# bird = ['_', '_', '_', 'N', 'G', 'E', '*', 'M', 'I', 'N', 'I', 'V', 'E', 'T']
# bird1 = ['B', 'L', 'A', 'C', 'K', '*', 'C', 'H', 'I', 'N', 'N', 'E', 'D',
#          '*', 'L', 'A', 'U', 'G', 'H', 'I', 'N', 'G', 'T', 'H', 'R', 'U', 'S', 'H']
# bird2 = ['B', 'L', 'A', 'C', 'K', '*', 'C', 'R', 'O', 'W', 'N', 'E', 'D',
#          '*', 'N', 'I', 'G', 'H', 'T', '*', 'H', 'E', 'R', 'O', 'N']
# bird3 = ['H', 'I', 'M', 'A', 'L', 'A', 'Y', 'A', 'N', '*', 'W', 'E', 'D', 'G', 'E',
#          '*', 'B', 'I', 'L', 'L', 'E', 'D', '*', 'W', 'R', 'E', 'N', '*',
#          'B', 'A', 'B', 'B', 'L', 'E', 'R']
# bird4 = ['S', 'H', 'I', 'K', 'R', 'A']
# bird5 = ['S', 'H', 'O', 'R', 'T', '*', 'T', 'O', 'E', 'D', '*', 'S', 'N', 'A', 'K', 'E',
#          '*', 'E', 'A', 'G', 'L', 'E']
# process(id_=1,
#         word=bird,
#         chances_remaining=5)
