from .line import Line
import numpy as np
from scipy.ndimage import gaussian_filter, convolve
from scipy.optimize import least_squares
from scipy.stats import binned_statistic
import logging

# Testing
import matplotlib.pyplot as plt

log = logging.getLogger(f"{__package__}.{__name__}")


VERT_KERNEL = np.array([
    [-1, 0, 1],
    [-1, 0, 1],
    [-1, 0, 1],
])

HORZ_KERNEL = np.array([
    [-1, -1, -1],
    [0, 0, 0],
    [1, 1, 1],
])

OVERSAMPLING = 10


def fit_line(img: np.ndarray, sigma=5, edge_threshold=0.75) -> Line:
    img = img.copy()
    img -= img.min()
    img = img / img.max()

    blurred = gaussian_filter(img, sigma)

    convs = [
        convolve(blurred, HORZ_KERNEL),
        convolve(blurred, -HORZ_KERNEL),
        convolve(blurred, VERT_KERNEL),
        convolve(blurred, -VERT_KERNEL),
    ]

    i = np.argmax([conv.sum() for conv in convs])
    conv = convs[i]

    if i in [0, 1]:
        log.debug("Horizontal edge detected.")
    else:
        log.debug("Vertical edge detected.")

    conv = conv / conv.max()

    i, j = np.where(conv > edge_threshold)

    def err(X):
        line = Line(X[0], X[1])

        return [line.dist((j[n], i[n])) for n in range(len(i))]
    
    line_guess = Line.from_points((j[0], i[0]), (j[-1], i[-1]))
    X = least_squares(err, (line_guess.slope, line_guess.intercept))

    line = Line(*X.x)

    if False:
        plt.figure(1)
        plt.imshow(conv)

        x = np.linspace(150, 225)
        plt.plot(x, x * line.slope + line.intercept)

        plt.show()
    
    return line


def img_to_LSF(img: np.ndarray, line: Line, dist_from_line=10):

    ROWS, COLS = np.indices(img.shape)

    x = np.array([line.signed_dist((x, y)) for x, y in zip(COLS.flatten(), ROWS.flatten())])
    y = img[ROWS.flatten(), COLS.flatten()]

    i = np.argsort(x)
    x = x[i]
    y = y[i]

    # Resample
    x2 = np.arange(x.min(), x.max(), 1 / OVERSAMPLING)
    y2 = binned_statistic(x, y, bins=x2)[0]

    y2 = y2[np.abs(x2[1:]) < dist_from_line]
    x2 = x2[np.abs(x2) < dist_from_line]

    dy = np.diff(y2)

    return x2, y2, dy


def LSF_to_MTF(lsf):

    dy = np.diff(lsf)

    fs = OVERSAMPLING  # samples / pixel

    Y = np.fft.fft(dy)

    f = np.linspace(0, fs, len(Y))

    # Nyquist is where f = 0.5
    #
    # 2 samples / cycle 
    # 2 pixels / cycle
    # Implies
    # 0.5 cycles / pixel

    # Normalize f to Nyquist (in other words, 1.0 will by Nyquist frequency)
    f /= 0.5

    Yabs = np.abs(Y)
    Yabs = Yabs[f <= 1.0]
    Yabs /= Yabs[0]
    f = f[f <= 1.0]

    return f, Yabs