import numpy as np
import matplotlib
import pandas as pd
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import animation, rc
from IPython.display import HTML
import pgmpy as pgm
from sklearn.decomposition import PCA

matplotlib.rcParams['figure.figsize'] = [12, 9]


def scatter_3d(data, title='', dpi=200, markersize=2, rcParams=matplotlib.rcParams):
    matplotlib.rcParams['figure.dpi'] = dpi
    matplotlib.rcParams = rcParams

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(title)
    ax.plot(*data, linestyle="", marker="o", markersize=markersize)

    return ax


def anim_scatter_3d(data, title='', markersize=2, az_start=0., az_end=90., frames=100, embed_limit=30., dpi=200,
                    rcParams=matplotlib.rcParams):
    matplotlib.rcParams["animation.embed_limit"] = embed_limit
    matplotlib.rcParams['figure.dpi'] = dpi
    matplotlib.rcParams = rcParams

    def update_graph(i):
        az = (az_end - az_start) / frames * i
        ax.azim = az_start + az
        return graph,

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(title)
    graph, = ax.plot(*data, linestyle="", marker="o", markersize=markersize)

    anim = matplotlib.animation.FuncAnimation(fig, update_graph, frames=frames, interval=40, blit=True)

    return HTML(anim.to_html5_video())
