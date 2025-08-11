import matplotlib.pyplot as plt
import numpy as np

from .pdf import A4_PORTRAIT, A4_LANDSCAPE, PdfPages, cbar


def plt_state_imgs(img: np.array, pdf: PdfPages, title='', clim=None):
    states = img.shape[0]
    extend = None if clim is None else 'both'
    if states == 1:
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=A4_LANDSCAPE)
        im = _add_img_plot(ax, img[0], clim=clim)
        cbar(fig, ax, im, extend=extend)
    elif states < 9:
        fig, axs = plt.subplots(ncols=2, nrows=states // 2, sharex='col', sharey='row', figsize=A4_LANDSCAPE)
        j = 0
        for s in range(states):
            i = 0 if s % 2 == 0 else 1
            im = _add_img_plot(axs[i][j], img[s], state=s, clim=clim)
            cbar(fig, axs[i][j], im, extend=extend)
            j += i
    else:
        fig, axs = plt.subplots(ncols=3, nrows=states // 3, sharex='col', sharey='row', figsize=A4_PORTRAIT)
        j = 0
        for s in range(states):
            i = s % 3
            im = _add_img_plot(axs[j][i], img[s], state=s)
            cbar(fig, axs[j][i], im, extend=extend)
            if i == 2:
                j += 1
    fig.suptitle(title)
    fig.tight_layout()
    pdf.savefig()
    plt.close()


def _add_img_plot(ax, img: np.array, state: int = None, clim=None):
    state = 'Average' if state is None else f'State #{state}'
    # ax.set_title(f'[{state}] MEAN:{img.mean():.2e} MIN:{img.min():.2e}\nMAX:{img.max():.2e} STD:{img.std():.2e}')
    ax.set_title(f'[{state}]')
    ax.set_xlabel(r'$\lambda$ [px]')
    ax.set_ylabel('y [px]')
    if clim is None:
        return ax.imshow(img, cmap='gray')
    if clim == 'sigma':
        m = img.mean()
        s = img.std()
        return ax.imshow(img, cmap='gray', clim=[m - s, m + s])
    return ax.imshow(img, cmap='gray', clim=clim)


def plt_img(img: np.array, pdf: PdfPages, title: str = '', roi: tuple = None, clim=None):
    fig, ax = plt.subplots(nrows=1, figsize=A4_LANDSCAPE)
    fig.suptitle(title)
    c = ax.imshow(img, cmap='gray', clim=clim)
    if roi is not None:
        ax.axvline(x=roi[1].start, linestyle='--')
        ax.axvline(x=roi[1].stop, linestyle='--')
        ax.axhline(y=roi[0].start, linestyle='--')
        ax.axhline(y=roi[0].stop, linestyle='--')
    cbar(fig, ax, c, extend=None if clim is None else 'both')
    ax.set_xlabel(r'$\lambda$ [px]')
    ax.set_ylabel('y [px]')
    fig.tight_layout()
    pdf.savefig()
    plt.close()


def plt_adjustment_comparison(original: np.array, desmiled: np.array, pdf: PdfPages, window: int = 230, roi=None):
    """
    Plot a cutout of selected rows from the original and the smile-corrected image.
    The plot shows window//2 pixels around the strongest line in the original.

    :param original: The original image
    :param desmiled: The desmiled image
    :param pdf: The PdfPages object to save the figure to
    :param window: Windows size in px
    :param roi: region of interest, if any
    """
    if roi is not None:
        original = original[roi]
        desmiled = desmiled[roi]
    brow = original.shape[0] // 3
    mrow = original.shape[0] // 2
    wcenter = original[mrow].argmin()
    wsize = window // 2
    xlim = [wcenter - wsize, wcenter + wsize]
    fig, ax = plt.subplots(nrows=2, figsize=A4_PORTRAIT)
    fig.suptitle(f'Correction result ({window} px around strongest line)')
    ax[0].set_title(f'Original')
    ax[0].plot(original[brow], label='top+margin')
    ax[0].plot(original[mrow], label='middle')
    ax[0].plot(original[-brow], label='bottom-margin')
    ax[0].set_xlim(xlim)
    ax[1].set_title(f'Corrected (selected rows)')
    ax[1].plot(desmiled[brow])
    ax[1].plot(desmiled[mrow])
    ax[1].plot(desmiled[-brow])
    ax[1].set_xlim(xlim)
    fig.legend()
    fig.tight_layout()
    pdf.savefig()
    plt.close()


def plt_spatial_comparison(original: np.array, corrected: np.array, pdf: PdfPages, roi: tuple = None):
    fig, ax = plt.subplots(nrows=2, sharex='all', figsize=A4_LANDSCAPE)
    fig.suptitle(f'Spatial average before and after correction')
    ax[0].set_ylabel('Original')
    ax[1].set_ylabel('Corrected')
    ax[1].set_xlabel('Spatial dimension [px]')
    roi = (slice(None, None), slice(None, None)) if roi is None else roi
    for s in range(original.shape[0]):
        ax[0].plot(original[s][roi].mean(axis=1))
        ax[1].plot(corrected[s][roi].mean(axis=1))
    fig.tight_layout()
    pdf.savefig()
    plt.close()


def plt_std_of_consecutive_hard_flats(data: list, pdf: PdfPages) -> None:
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=A4_LANDSCAPE)
    ax.plot(data)
    ax.grid(True)
    fig.suptitle("Standard deviation of two consecutive hard flats")
    fig.tight_layout()
    pdf.savefig()
    plt.close()


def plt_selected_lines(data: np.array, lines: list, pdf: PdfPages, roi: tuple = None) -> None:
    fig, ax = plt.subplots(nrows=1, figsize=A4_LANDSCAPE)
    ax.set_title(f'Selected lines for fitting')
    ax.plot(data)
    for line in lines:
        li = line if roi is None else line + roi[1].start
        ax.axvline(x=li, linestyle='--')
    ax.set_xlim([0, len(data)])
    ax.set_xlabel(r'$\lambda$ [px]')
    ax.set_ylabel('Counts')
    fig.tight_layout()
    pdf.savefig()
    plt.close()
