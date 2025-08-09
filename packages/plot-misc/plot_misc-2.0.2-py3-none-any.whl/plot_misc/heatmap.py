"""
Heatmap drawing and annotation tools built on top of matplotlib and seaborn.

This module provides flexible functions to create and annotate heatmaps using
either `matplotlib` or `seaborn`, with extensive support for customisation and
publication-quality output. It includes functionality for standard heatmaps,
clustered heatmaps, and embedded annotations with control over grid styling,
tick labelling, and colourbar presentation.

Functions
---------
heatmap(data, row_labels, col_labels, ...)
    Draws a standard heatmap using matplotlib's `imshow`, with options for
    gridlines, tick formatting, and embedded colourbars.

annotate_heatmap(im, data=None, valfmt=None, ...)
    Adds text annotations to an existing heatmap image (AxesImage object),
    with configurable formatting and colour thresholding.

clustermap(data, cmap='Spectral', annot=None, ...)
    Wraps seaborn's `clustermap` with additional layout and styling options
    suitable for compact or publication figures.

Notes
-----
The base structure of the `heatmap` and `annotate_heatmap` functions is derived
from the example published in the official matplotlib gallery [1]_.

References
----------
.. [1] https://matplotlib.org/stable/gallery/images_contours_and_fields/image_annotated_heatmap.html
"""

# modules
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from plot_misc.utils.utils import _update_kwargs
from plot_misc.errors import (
    is_type,
)
from plot_misc.constants import Real
from typing import (
    Any,
    Optional,
)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def heatmap(data:pd.DataFrame | np.ndarray, row_labels:list[str] | np.ndarray,
            col_labels:list[str] | np.ndarray, grid_col:str='white',
            grid_linestyle:str='-', grid_linewidth:float=3,
            cbar_bool:bool=False, cbar_label:str="",
            ax:plt.Axes | None = None,
            grid_kw:dict[Any,Any] | None = None,
            cbar_kw:dict[Any,Any] | None = None,
            **kwargs:Optional[Any],
            ) -> tuple[matplotlib.image.AxesImage,
                       matplotlib.colorbar.Colorbar]:
    """
    Plot a heatmap with row and column labels using matplotlib.
    
    This function draws a heatmap using `imshow`, with options to configure
    grid lines, colourbars, and axis labels. It accepts both NumPy arrays
    and pandas DataFrames as input.
    
    Parameters
    ----------
    data : `pd.DataFrame` or `np.array`
        A 2D array of shape (M, N) containing the values to plot.
    row_labels : `list` [`str`] or `np.ndarray`
        A list or array of length M with the labels for the rows.
    col_labels : `list` [`str`] or `np.ndarray`
        A list or array of length N with the labels for the rows.
    grid_col : `str`, default 'white'
        The colour of the grid lines
    grid_linestyle : `str`, default '-'
        The linestyle of the grid lines
    grid_linewidth : `float`, default 3
        The width of the grid lines.
    cbar_bool : `bool`, default `False`
        If `True`, add a colourbar to the figure.
    cbar_label : `str`, default " "
        The label for the colorbar.
    ax : `plt.Axes` or `None`, default NoneType
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted. If
        not provided, use current axes or create a new one.
    grid_kw : `dict` [`str`,`any`] or `None`, default None
        A dictionary with arguments to `matplotlib.Axes.grid`.
    cbar_kw : `dict` [`str`, `any`] or `None`, default `None`
        A dictionary with arguments to `matplotlib.Figure.colorbar`.
    **kwargs : `any`
        All other arguments are forwarded to `imshow`.
    
    Returns
    -------
    im : `matplotlib.image.AxesImage`
        The heatmap image object.
    cbar : `matplotlib.colorbar.Colorbar` or `None`
        The colourbar object if `cbar_bool` is `True`, otherwise `None`.
    
    Notes
    -----
    The returned objects can be used to annotate the cells using for example
    `annotate_heatmap`.
    
    This function is adapted from the matplotlib gallery example [1]_.
    """
    
    # create a axes if needed
    if not ax:
        ax = plt.gca()
    # check input
    if isinstance(data, pd.DataFrame):
        matrix = data.copy().to_numpy()
    else:
        matrix = data
    # copy
    row_lab = row_labels
    col_lab = col_labels
    # check additional input
    is_type(row_lab, (list, np.array))
    is_type(col_lab, (list, np.array))
    is_type(cbar_label, str)
    # map None to dict
    grid_kw = grid_kw or {}
    cbar_kw = cbar_kw or {}
    # ### Plot the heatmap
    im = ax.imshow(matrix, **kwargs)
    # Create colorbar
    if cbar_bool == True:
        # NOTE if the kwargs for colobar is extended use `_update_kwargs
        cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
        cbar.ax.set_ylabel(cbar_label, rotation=-90, va="bottom")
    else:
        cbar = None
    # Show all ticks and label them with the respective list entries.
    ax.set_xticks(np.arange(matrix.shape[1]))
    ax.set_xticklabels(col_lab)
    ax.set_yticks(np.arange(matrix.shape[0]))
    ax.set_yticklabels(row_lab)
    # Let the horizontal axes labeling appear on top.
    # ax.tick_params(top=True, bottom=False,
    #                labeltop=True, labelbottom=False)
    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right",
             rotation_mode="anchor")
    # Turn spines off and create white grid.
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    # set tick marks
    ax.set_xticks(np.arange(matrix.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(matrix.shape[0]+1)-.5, minor=True)
    # grid
    new_grid_kwargs = _update_kwargs(
        update_dict=grid_kw, which="minor", color=grid_col,
                     linestyle=grid_linestyle, linewidth=grid_linewidth,
                     )
    ax.grid(**new_grid_kwargs)
    ax.tick_params(which="minor", bottom=False, left=False)
    # return stuff
    return im, cbar

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def annotate_heatmap(
    im:plt.Axes.imshow,
    data:pd.DataFrame | np.ndarray | None = None,
    valfmt:str | matplotlib.ticker.Formatter | None = None,
    textcolors:tuple[str,str] | list[str,str]=("black","white"),
    threshold: float | None = None,
    **kwargs:Optional[Any],
) -> list[plt.Text]:
    """
    Annotate each cell in a heatmap image with its value.
    
    This function adds text annotations to an existing `AxesImage` object,
    such as those created by the `heatmap` function. The text colour may
    be adjusted dynamically based on a threshold value and the image’s colour
    map.
    
    Parameters
    ----------
    im : `plt.Axes.imshow`
        The AxesImage to be labeled.
    data : `pd.DataFrame`, `np.array`, or `None`, default `Nonetype`
        A 2D numpy array of shape (M, N). If `None`, the function uses the
        array embedded in `im`.
    valfmt : `str`, `matplotlib.ticker.Formatter` or `None`, default `NoneType`
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}" - (note the `x` is needs
        to be included to represent the numerical), or be a
        `matplotlib.ticker.Formatter`.
    textcolors : `list` or `tuple` [`str`, `str`], default `('black', 'white')`
        A pair of colors.  The first is used for values below a threshold,
        the second for those above.
    threshold : `float` or `None`, default `NoneType`
        The absolute value in data units according to which the colors from
        textcolors are applied.  If None (the default) uses the middle of the
        colormap as separation.
    **kwargs : `any`
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    
    Returns
    -------
    texts : `list` of `matplotlib.text.Text`
        A list of text annotation objects added to the heatmap.
    """
    
    # mapping data to matrix
    values = im.get_array()
    if data is None:
        matrix = im.get_array()
    elif isinstance(data, pd.DataFrame):
        matrix = data.copy().to_numpy()
    else:
        matrix = data
    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        # this will value is matrix is a string
        try:
            threshold = im.norm(values.max())/2.
        except np.core._exceptions.UFuncTypeError:
            threshold = None
    # Set default alignment to center, but allow it to be
    # overwritten by text_kw.
    kw = _update_kwargs(update_dict=kwargs,
                        horizontalalignment="center",
                        verticalalignment="center",
                        )
    # Get the formatter in case a string is supplied
    if not valfmt is None:
        if isinstance(valfmt, str):
            valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)
    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            # only run if threshold exists
            if not threshold is None:
                kw.update(color=textcolors[int(im.norm(abs(values[i, j])) > threshold)])
            # format text or not
            if not valfmt is None:
                text = im.axes.text(j, i, valfmt(matrix[i, j], None), **kw)
            else:
                text = im.axes.text(j, i, matrix[i,j], **kw)
            texts.append(text)
    # returning stuff
    return texts

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def clustermap(data:pd.DataFrame,
               cmap:matplotlib.cm.get_cmap=matplotlib.colormaps.get_cmap('Spectral'),
               annot:pd.DataFrame | None = None,
               fsize:tuple[Real,Real]=(15, 15),
               linewidths:float=1.0,
               cpos: tuple[float] | None =(0.09, 0.02, 0.03, 0.10),
               annotsize:float=6, clab:str='', clabfs:float=7, fmt:str=".3",
               clabpos:str='left', clabtsize:float=5, xticklabsize:float=8,
               yticklabsize:float=6, yticks:bool=True, xticks:bool=True,
               cbar_dict_kw:dict[Any,Any] | None = None,
               tree_dict_kw:dict[Any,Any] | None = None,
               annot_dict_kw:dict[Any,Any] | None = None,
               clustermap_dict_kw:dict[Any,Any] | None = None,
               ) -> sns.matrix.ClusterGrid:
    """
    Plot a clustered heatmap using seaborn's clustermap API.
    
    Wraps `seaborn.clustermap` with additional controls for layout,
    annotation, and appearance. Allows clustering of both rows and columns
    and supports annotated values, tick styling, and custom colourbars.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        A datafarme of shape (M, N).
    fsize : `tuple` [`real`, `real`], default `(15, 15)`
        figure size in inches
    linewidths : `float`, default 1.0
        Width of the gridlines between cells.
    annot : `pd.DataFrame` or `None`, default `NoneType`
        An opional dataframe used for annotation.
    annotsize : `float`, default 6.0
        Font size for annotations, will be parsed to
        `matplotlib.axes.Axes.text`.
    fmt : `str`, default '.3'
        String formatting code to use when adding annotations.
    cmap : `matplotlib.colormaps`, default 'viridis'
        matplotlib colormaps
    cpos : `tuple` [`float`, `float`, `float`, `float`]
        Default (0.09,0.02.0.03,0.10). Position of the colourbar in figure
        coordinates: `(left, bottom, width, height)`. Set to `None` to disable
        the colourbar.
    clab : `str`, default ' '
        colour guide y-axis title.
    clabsf : `float`, default 7.0.
        Font size for the colourbar label.
    clabpos : `str`, `left`
        Position of the colourbar label (e.g., `'left'`, `'right'`).
    clabtsize : `float`, default 5.0
        Font size for the colourbar tick labels.
    xticklabsize : `float`, default 8.0
        Font size for x-axis tick labels.
    yticklabsize : `float`, default 6.0
        Font size for y-axis tick labels.
    yticks : `bool`, default `True`
        Whether to display y-axis tick marks.
    xticks : `bool`, default `True`
        Whether to display x-axis tick marks.
    cbar_dict_kw : `dict` [`any`, `any`], optional
        Keyword arguments passed to `Figure.colorbar()`.
    tree_dict_kw : `dict` [`any`, `any`], optional
        Keyword arguments passed to dendrogram tree plotting.
    annot_dict_kw : `dict` [`any`, `any`], optional
        Keyword arguments passed to annotation text formatting.
    clustermap_dict_kw : `dict` [`any`, `any`], optional
        Keyword arguments passed to `seaborn.clustermap()`.
    
    Returns
    -------
    cm : `seaborn.matrix.ClusterGrid`
        A seaborn cluster grid object with the full figure layout.
    """
    # #### constants
    # map None to dict
    cbar_dict_kw = cbar_dict_kw or {}
    tree_dict_kw = tree_dict_kw or {}
    annot_dict_kw = annot_dict_kw or {}
    clustermap_dict_kw = clustermap_dict_kw or {}
    # update keyword dictionaries
    annot_kw = _update_kwargs(update_dict=annot_dict_kw,
                              size=annotsize,
                              )
    clustermap_kw = _update_kwargs(update_dict=clustermap_dict_kw,
                                   fmt=fmt, linewidths=linewidths,
                                   figsize=(fsize[0], fsize[1]),
                                   cbar_pos=cpos, cmap=cmap,
                                   annot=annot,
                                   )
    # make figure
    cm = sns.clustermap(data,
                        cbar_kws=cbar_dict_kw,
                        tree_kws=tree_dict_kw,
                        annot_kws=annot_kw,
                        **clustermap_kw,
                        )
    # cbar labels
    cm.ax_cbar.axes.yaxis.set_label_text(clab, fontsize=clabfs)
    cm.ax_cbar.axes.yaxis.set_label_position(clabpos)
    cm.ax_cbar.tick_params(labelsize=clabtsize)
    # heatmap tick labels
    cm.ax_heatmap.set_xticklabels(cm.ax_heatmap.get_xmajorticklabels(),
                                   fontsize = xticklabsize)
    cm.ax_heatmap.set_yticklabels(cm.ax_heatmap.get_ymajorticklabels(),
                                   fontsize = yticklabsize)
    # removing axis labels
    cm.ax_heatmap.set_ylabel("")
    cm.ax_heatmap.set_xlabel("")
    # add both xy ticks
    cm.ax_heatmap.tick_params('both', reset=False, bottom=xticks, right=yticks)
    # return
    return cm

