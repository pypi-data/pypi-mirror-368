import matplotlib.pyplot as plt
import numpy as np

from .pdf import A4_LANDSCAPE, cbar
from ..smile import OffsetMap, StateAligner


def plt_map(smap: OffsetMap, rows: tuple = (50, 550, -550, -50), state_aware: bool = True, pdf=None) -> None:
    """
    Generates a heatmap plot of the given smile offset map.
    Note: Will only plot the average for all states (e.g. the "squashed" version, without squashing the map)

    ### Params
    - smap: The `OffsetMap` to plot
    - rows: The row numbers to plot cuts through
    - title: The title of the plot
    """
    if smap.is_squashed():
        _omap_state_plot(smap.map, smap.error, rows, 'Squashed Offset Map', pdf)
    elif not state_aware:
        _omap_state_plot(smap.map[0], smap.error[0], rows, f'Offset Map for all states', pdf)
    else:
        for s in range(smap.map.shape[0]):
            _omap_state_plot(smap.map[s], smap.error[s], rows, f'Offset Map for state #{s}', pdf)


def _omap_state_plot(shifts: np.array, error: np.array, rows: tuple, title: str, pdf=None):
    colors = ['green', 'red', 'orange', 'purple', 'lime', 'pink', 'blue', 'yellow']
    fig, axs = plt.subplots(nrows=2, ncols=2, sharex='col', dpi=100, figsize=A4_LANDSCAPE)
    fig.suptitle(title)
    xes = range(shifts.shape[1])
    axs[0, 0].set_title(r'Offset per column in $\lambda$ direction')
    axs[0, 0].set_xlabel(r'column($\lambda$ [px])')
    axs[0, 0].set_ylabel('offset [px]')

    c = axs[0, 1].imshow(shifts, cmap='gray')
    cbar(fig, axs[0, 1], c, label='Offset [px]')
    axs[0, 1].set_title('Offset per pixel')
    axs[0, 1].set_xlabel(r'$\lambda$ [px]')
    axs[0, 1].set_ylabel('y [px]')
    for i in range(len(rows)):
        r = shifts.shape[0] + rows[i] if rows[i] < 0 else rows[i]
        axs[0, 0].plot(xes, shifts[r], label=f"row  {r}", color=colors[i])
        axs[0, 1].axhline(y=r, color=colors[i], linestyle='--', linewidth=0.5)
    axs[0, 0].legend()

    axs[1, 0].set_title(r'Error per column in $\lambda$ direction')
    axs[1, 0].set_xlabel(r'column($\lambda$ [px])')
    axs[1, 0].set_ylabel(r'$\chi^2$ Error')

    c = axs[1, 1].imshow(error, cmap='gray', clim=[0, 0.005])
    cbar(fig, axs[1, 1], c, label=r'$\chi^2$ Error', extend='both')
    axs[1, 1].set_title(r'$\chi^2$ error per pixel (clipped at 0.005)')
    axs[1, 1].set_xlabel(r'$\lambda$ [px]')
    axs[1, 1].set_ylabel('y [px]')
    for i in range(len(rows)):
        axs[1, 0].plot(xes, error[rows[i]], label=f"row  {rows[i]}", color=colors[i])
        r = error.shape[0] + rows[i] if rows[i] < 0 else rows[i]
        axs[1, 1].axhline(y=r, color=colors[i], linestyle='--', linewidth=0.5)

    fig.tight_layout()
    if pdf is not None:
        pdf.savefig()
        plt.close()
    else:
        plt.show()


def plt_state_alignment(sta: StateAligner, pdf) -> None:
    """
    Generates a line plot of the state alignment result

    ### Params
    - sta: The `StateAligner` whos result to plot
    """
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=A4_LANDSCAPE)
    fig.suptitle('Differential line positions compared to state 0')
    for i in range(1, len(sta.deltas)):
        ax.plot(sta.deltas[i]['x'], sta.deltas[i]['y'], label=f'State {i}')
    ax.set_xlabel('Line pos. [px]')
    ax.set_ylabel('Delta [px]')
    ax.legend()
    fig.tight_layout()
    pdf.savefig()
    plt.close()
