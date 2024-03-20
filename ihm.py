import os
import shelve

import PIL.Image
from PIL import Image, ImageFont, ImageDraw
import random


class Box:

    def __init__(self, box_loc, box):
        self.box_loc = box_loc
        self.box = box


class Img_data:

    def __init__(self, boxes):
        self.boxes = boxes


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


def process(id_: int, word: list,
            chances_remaining: int, source_img_path: str) -> str:
    """
    Image processing for hm
    :param id_: Unique id to identify the image. It will be used in the output image file name.
    :param word: A list that tells letters to be displayed.
    Examples;
        crow with 'o' filled in will have
            ['-','-','o','-']
        orange minivet with 'e', 'i' filled in will have
            ['-','-','-',:'-','-','-','e', '*','-','i','-','i','-','e','-']
    :param chances_remaining:
    :param source_img_path: Original image local path. Ideally, put it under 'imgs' folder
    :return: Output image local path
    """
    output_img_path = get_img_path(id_)
    box_size = 64
    if output_img_path is None:
        # Its a new game - Create a blank image and store pixel data
        blank_img = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))

        with Image.open(source_img_path, 'r').convert('RGBA') as im:
            boxes = []
            left, upper, right, lower = 0, 0, box_size, box_size
            for row in range(int(1024 / box_size)):
                for col in range(int(1024 / box_size)):
                    boxes.append(Box((left, upper), im.crop((left, upper, right, lower))))
                    left += box_size
                    right += box_size

                left = 0
                right = box_size
                upper += box_size
                lower += box_size

            with shelve.open(f'data/{id_}', flag='c') as db:
                db[f'{id_}'] = Img_data(boxes)
            Image.Image.paste(im, blank_img, (0, 0))
    else:
        # Ongoing game - update image
        with shelve.open(f'data/{id_}', flag='c') as db:
            stored_img_data: Img_data = db[f'{id_}']

        no_of_boxes_to_display = int((1024 / box_size) * (1024 / box_size) * 0.03)
        if no_of_boxes_to_display > len(stored_img_data.boxes):
            no_of_boxes_to_display = len(stored_img_data.boxes)

        with Image.open(output_img_path, mode='r').convert('RGBA') as im:
            for i in range(no_of_boxes_to_display):
                random_box: Box = random.choice(stored_img_data.boxes)
                im.paste(random_box.box, random_box.box_loc)
                box_idx = stored_img_data.boxes.index(random_box)
                stored_img_data.boxes.pop(box_idx)

        with shelve.open(f'data/{id_}', flag='c') as db:
            db[f'{id_}'] = stored_img_data

    # Clear existing text
    label = Image.new('RGBA', (900, 150), 'white')
    im.paste(label, (0, 1024, 900, 1174))
    font = ImageFont.load_default(50)
    x_loc = 60
    y_loc = 1100
    space_loc = 0
    second_line = False
    for letter in word:
        txt = Image.new('RGBA', im.size, (255, 255, 255, 0))
        d = ImageDraw.Draw(txt)
        if letter == '*':
            space_loc = word.index('*', space_loc + 1)
            if space_loc > 12 and not second_line:
                # Next line
                y_loc += 60
                x_loc = 20
                second_line = True
            letter = ''
        d.text((x_loc, y_loc), letter, fill='black', anchor='mb', font=font)
        x_loc += 40
        im = Image.alpha_composite(im, txt)

    with Image.open(f'chances/{chances_remaining}.png', 'r').convert('RGBA').resize((150, 150),
                                                                                    PIL.Image.NEAREST) as chances:
        Image.Image.paste(im, chances, (860, 1040))

    im.save(f'output/{id_}.png')
    return f'output/{id_}.png'


# bird = ['O', 'R', 'A', 'N', 'G', 'E', '*', 'M', 'I', 'N', 'I', 'V', 'E', 'T']
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
#         word=bird4,
#         chances_remaining=3, source_img_path='imgs/orange_minivet_org.png')
