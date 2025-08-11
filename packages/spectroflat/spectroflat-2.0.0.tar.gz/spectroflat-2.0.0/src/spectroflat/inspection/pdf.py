# -*- coding: utf-8 -*-
"""
Module to provide helper methods / constants for matplotlib PDF reports
"""
from typing import Union

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.axes_grid1 import make_axes_locatable

#: A4 landscape format in inches
A4_LANDSCAPE = (11.69, 8.27)
#: A4 portrait format in inches
A4_PORTRAIT = (8.27, 11.69)
#: Margins in %
MARGINS = {'L': 0.07, 'T': 0.05, 'R': 0.05, 'B': 0.05}
#: Margin in % for (Left, Bottom, Right, Top) for tight_layout
TIGHT_MARGIN = (0, 0.05, 1, 1)


def text_page(pdf: PdfPages, content: Union[str, list], ha: str = "center", font_size: int = 10, weight: str = 'normal',
              vpos: tuple = (0.5, 0.5), footer_txt: str = None, page_size: tuple = A4_PORTRAIT):
    """
    Helper method to add a text page to a given PdfPages object

    ## Params
    - pdf: The PdfPages object to extend
    - content: The text content for the page
    - ha: horizontal alignment of the text
    - pos: vertical position (only used if content is a string)
    - footer: Optional footer text
    - page_size: Size of the page in inches.
    """
    page = plt.figure(figsize=page_size)
    page.clf()
    if isinstance(content, str):
        page.text(vpos[0], vpos[1], content.expandtabs(),
                  transform=page.transFigure, size=font_size, ha=ha, fontweight=weight)
    else:
        space = (1 - MARGINS['T'] - MARGINS['B'])
        line_height = space / len(content)
        for i in range(len(content)):
            page.text(MARGINS['L'], 1 - MARGINS['T'] - line_height * i, content[i].expandtabs(),
                      transform=page.transFigure, size=font_size, ha=ha, fontweight=weight)
    if footer_txt is not None:
        footer(page, footer_txt, size=10)
    pdf.savefig()
    plt.close()


def footer(page, content: str, size: int = 9):
    page.text(0.5, 0.02, content, transform=page.transFigure, size=size, ha='center')


def table_page(pdf: PdfPages, col_labels: list, row_values: list, loc: str = 'center', font_size: int = 9,
               color: list = None, footer_txt: str = None, page_size: tuple = A4_LANDSCAPE):
    """
    Helper method to add a table page to a given PdfPages object

    ## Params
    - pdf: The PdfPages object to extend
    - col_labels: list of column labels (formatted strings)
    - row_values: 2-D list wih row values (formatted strings)
    - page_size: Size of the page in inches.
    """
    fig, ax = plt.subplots(figsize=page_size)
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')
    tab = ax.table(cellText=row_values, colLabels=col_labels, loc=loc, cellLoc=loc, colLoc=loc,
                   fontsize=font_size, cellColours=color)
    tab.auto_set_font_size(False)
    tab.auto_set_column_width(col=list(range(len(col_labels))))
    if footer_txt is not None:
        footer(fig, footer_txt, size=10)
    fig.tight_layout()
    pdf.savefig()
    plt.close()


def cbar(fig, axis, colors, size: str = '3%', extend=None, label=None) -> None:
    divider = make_axes_locatable(axis)
    cax = divider.append_axes("right", size=size, pad=0.03)
    fig.colorbar(colors, cax=cax, extend=extend, label=label)
