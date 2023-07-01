from PIL import Image
import pillow_avif


def convert_avif_to_png():
    # img = Image.open('img.avif')
    # rgb_im = im.convert('RGB')
    # rgb_im.save('audacious.jpg')
    # img.save('img.jpg')

    im = Image.open("img.avif")
    rgb_im = im.convert('RGB')
    rgb_im.save('audacious.jpg')


if __name__ == '__main__':
    convert_avif_to_png()
