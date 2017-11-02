from __future__ import print_function

import sys
import time
import threading
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    Image = None
try:
    import cv2
except ImportError:
    cv2 = None
try:
    from wand.image import Image as WandImage
except ImportError:
    WandImage = None
try:
    from pgmagick import Image as PGImage, FilterTypes, Blob, Geometry
except ImportError:
    PGImage = None
try:
    from pyvips import Image as VipsImage
except ImportError:
    VipsImage = None


imagename = sys.argv[1]


def deferred_noop():
    time.sleep(.2)


def deferred_pillow():
    im = Image.open(imagename)
    im.resize((1024, 768), Image.BICUBIC)
    im.save(BytesIO(), format='jpeg', quality=85)


def deferred_opencv():
    im = cv2.imread(imagename)
    cv2.resize(im, (1024, 768), interpolation=cv2.INTER_AREA)
    cv2.imencode(".jpeg", im, [int(cv2.IMWRITE_JPEG_QUALITY), 85])


def deferred_wand():
    with WandImage(filename=imagename) as im:
        im.resize(1024, 768, 'catrom')
        im.compression_quality = 85
        im.format = 'jpeg'
        im.save(file=BytesIO())


def deferred_pgmagick():
    im = PGImage(imagename)

    im.filterType(FilterTypes.CatromFilter)
    im.zoom(Geometry(1024, 768))

    im.quality(85)
    im.magick('jpeg')
    im.write(Blob())


def deferred_vips():
    im = VipsImage.new_from_file(imagename)
    im.resize(0.4, kernel='cubic')
    im.write_to_buffer('.jpeg', Q=85)



def test_deferred(deferred):
    start = time.time()
    t = threading.Thread(target=deferred)
    t.start()
    n = 0

    while t.isAlive():
        time.sleep(.0001)
        n += 1

    print('>>> {:<20} time: {:1.3f}s  {:>4} switches'.format(
        deferred.__name__, time.time() - start, n))


test_deferred(deferred_noop)
if not Image is None:
    test_deferred(deferred_pillow)
if not cv2 is None:
    test_deferred(deferred_opencv)
if not WandImage is None:
    test_deferred(deferred_wand)
if not PGImage is None:
    test_deferred(deferred_pgmagick)
if not VipsImage is None:
    test_deferred(deferred_vips)
