import numpy as np
from PIL import Image
import seam_carving
from rembg.bg import remove
import cv2
from io import BytesIO

import time


from app.core.graph import resize_image


if __name__ == '__main__':
    # measure time
    start = time.time()
    width = 1000
    height = 500
    bytes_io = resize_image(Image.open(f"input/ratatouille_{width}_{height}_in.jpg"), width, height)
    end = time.time()
    print(f"Time taken: {end - start:.4f}")
    with open(f'output/ratatouille_{width}_{height}_gen_out_bytes.jpg', 'wb') as f:
        f.write(bytes_io)
