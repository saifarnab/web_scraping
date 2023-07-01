from PIL import Image
import pillow_avif


def convert_avif_to_png():
    img = Image.open('img.avif')
    img.save('img.png')


if __name__ == '__main__':
    convert_avif_to_png()
