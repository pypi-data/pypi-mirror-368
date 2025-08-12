import argparse
import mtf
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import logging

log = logging.getLogger(__package__)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('input_image')
    parser.add_argument('--gui-roi', action='store_true', default=False)
    parser.add_argument('--roi', help="Specify in quotes as you would slice a matrix. E.g. \"200:400, 50:150\"")
    parser.add_argument('--log-level', default='info', choices=['info', 'warning', 'error', 'debug'])
    args = parser.parse_args()

    log.setLevel(args.log_level.upper())
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter("%(name)s:%(levelname)s:%(message)s"))
    log.addHandler(sh)

    log.info(f"args: {args}")

    img = np.array(Image.open(args.input_image))

    if args.gui_roi:
        f = plt.figure()
        plt.imshow(img)
        tmp = np.array(plt.ginput(2))
        args.roi = f"{tmp[:, 1].min().round().astype(int)}:{tmp[:, 1].max().round().astype(int)}, {tmp[:, 0].min().round().astype(int)}:{tmp[:, 0].max().round().astype(int)}"
        log.info(f"ROI set to: \"{args.roi}\"")

    if args.roi is not None:
        log.info(f"Cropping to roi of \"{args.roi}\"")
        row, col = args.roi.split(",")
        roi_slice = (slice(*map(int, row.split(":"))), slice(*map(int, col.split(":"))))
        img = img[roi_slice]

    line = mtf.fit_line(img)
    x, y, dy = mtf.img_to_LSF(img, line)
    f, MTF = mtf.LSF_to_MTF(y)

    plt.figure()
    plt.imshow(img)

    _, ax = plt.subplots(2, 1)
    ax[0].plot(x, y)
    ax[1].plot(x[1:], dy)

    plt.figure()
    plt.plot(f, MTF)
    plt.title(f"MTF at Ny / 2: {np.interp(0.5, f, MTF) * 100:.1f} %")
    plt.grid(True)
    plt.gca().set_ylim((0, 1))
    plt.gca().set_xlim((0, 1))

    plt.show()