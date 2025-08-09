"""
General utilities for figure formatting and annotation.

This module provides a set of utilities to support custom figure creation,
axis annotation, matrix formatting, and heatmap generation. It includes
helpers for label placement, axis tick control, annotation styling, and
matrix-based effect/p-value processing for visualisation.

Classes
-------
MatrixHeatmapResults
    A results container for curated matrices used in annotated heatmaps.

MidpointNormalize
    A custom normalisation class that centres colour maps on a specified
    midpoint, useful for diverging data.

Functions
---------
annotate_axis_midpoints(ax, labels, axis='y', gap=6, offset=None, ...)
    Annotates midpoints between tick marks on an axis when regular gaps
    are detected.
    
calc_angle_points(x, y, radians=False)
    Calculates the angle between two points in degrees or radians.
    
calc_matrices(data, exposure_col, outcome_col, point_col='point',
    pvalue_col='pvalue', ...)
    Creates effect and p-value matrices for heatmap plotting, including
    optional annotation styles and NA masking.
    
calc_mid_point(x, y)
    Computes the midpoint between two Cartesian coordinates.
    
change_ticks(ax, ticks, labels=None, axis='x', log=False)
    Updates axis tick locations and labels, with optional log scaling.
    
adjust_labels(annotations, axis, min_distance=0.1)
    Adjusts overlapping annotation text to improve legibility.
    
plot_span(start_span, stop_span, ax, horizontal=True, **kwargs)
    Adds a vertical or horizontal span to a matplotlib axis.
    
segment_labelled(x, y, ax, label=None, ...)
    Plots a line segment with optional endpoints and midpoint label,
    aligned to segment orientation.
    
"""

import re
import warnings
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.path as mpath
import numbers
from typing import (
    Any,
    Literal,
    Optional,
)

from plot_misc.constants import (
    UtilsNames,
    Real,
    CLASS_NAME,
)
from plot_misc.errors import (
    is_type,
    InputValidationError,
    Error_MSG,
)
from plot_misc.utils.formatting import _nlog10_func

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Class
class Results(object):
    '''
    A general results class
    '''
    # /////////////////////////////////////////////////////////////////////////
    # Initiation the class
    # NOTE include * to force all named arguments to be named (no positional)
    # args when calling innit.
    def __init__(self,*, set_args: list[str], **kwargs:Any):
        """
        Initialise a `Results` instance.
        
        Raises
        ------
        AttributeError
            If an unrecognised keyword is provided.
        """
        SET_ARGS = '_setargs'
        setattr(self,SET_ARGS, set_args)
        # now set values
        for k in kwargs.keys():
            if k not in getattr(self, SET_ARGS):
                raise AttributeError("unrecognised argument '{0}'".format(k))
        # Loops over `SET_ARGS`, assigns the kwargs content to name `s`.
        # if argument is missing in kwargs, print a warning.
        for s in getattr(self, SET_ARGS):
            try:
                setattr(self, s, kwargs[s])
            except KeyError:
                warnings.warn("argument '{0}' is set to 'None'".format(s))
                setattr(self, s, None)
    # /////////////////////////////////////////////////////////////////////////
    def __str__(self) -> str:
        # assigns a back up name if clas_name is not provided
        CLASS_NAME_ = getattr(self, CLASS_NAME, type(self).__name__)
        return f"A `{CLASS_NAME_}` results class."
    # /////////////////////////////////////////////////////////////////////////
    def __repr__(self) -> str:
        CLASS_NAME_ = getattr(self, CLASS_NAME, type(self).__name__)
        args = getattr(self, '_setargs')
        parts = []
        # join the keys and values
        for arg in args:
            # skip
            if arg == CLASS_NAME:  # pragma: no cover
                continue
            # format value
            value = getattr(self, arg, None)
            if isinstance(value, float):
                formatted = f"{value:.3f}"
                # check for confidnece intervals
            elif (
                isinstance(value, (list, tuple)) and\
                all(isinstance(v, numbers.Real) for v in value) and\
                len(value) == 2
            ):
                formatted = f"[{value[0]:.3f}, {value[1]:.3f}]"
                if isinstance(value, tuple):
                    formatted = f"({value[0]:.3f}, {value[1]:.3f})"
                    
                # check for array like objects
            elif isinstance(value, (list, tuple, np.ndarray, pd.Series)):
                formatted = self._repr_summary(value)
            else:
                formatted = repr(value)
            parts.append(f"  {arg}={formatted}")
        # return a pretty string
        body = "\n".join(parts)
        return f"{CLASS_NAME_}\n{body}\n"
    # /////////////////////////////////////////////////////////////////////////
    def _repr_summary(self, value, max_items=6, precision=3, ):
        """A repr summary for array like objects"""
        if isinstance(value, np.ndarray):
            array_str = np.array2string(
                value,
                precision=precision,
                threshold=max_items,
                edgeitems=3,
                suppress_small=True
            )
            # Indent continuation lines
            indent_str = ' ' * 2
            lines = array_str.splitlines()
            if len(lines) > 1:  # pragma: no cover
                indented_array = (f"\n{indent_str}  ").join(lines)
            else:
                indented_array = lines[0]
            return (
                f"array({indented_array}, shape={value.shape}, "
                f"dtype={value.dtype})"
            )
        elif isinstance(value, (list, tuple)):
            sample = value[:max_items]
            suffix = ", ..." if len(value) > max_items else ""
            items = ', '.join(repr(v) for v in sample)
            return f"{type(value).__name__}([{items}{suffix}])"
        elif isinstance(value, pd.Series):
            sample = value.iloc[:max_items].tolist()
            suffix = ", ..." if len(value) > max_items else ""
            return (f"Series([{', '.join(repr(v) for v in sample)}{suffix}], "
                    f"name={value.name})")
        return repr(value)  # pragma: no cover

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MatrixHeatmapResults(Results):
    '''
    Results container for annotated heatmap matrices returned by
    `calc_matrices`.
    
    This object holds curated and raw matrix representations of effect
    estimates and p-values, along with their corresponding annotation layers
    (e.g. stars, point estimates, or p-values). It is designed for flexible
    visualisation and post-processing in heatmap plots.
    
    Attributes
    ----------
    crude_point_estimate : `pd.DataFrame`
        The raw matrix of point estimates without formatting or masking.
    curated_matrix_annotation : `pd.DataFrame`
        The corresponding annotation matrix (e.g. stars or point estimates),
        suitable for overlaying on the heatmap (strings).
    curated_matrix_point_estimate_value : `pd.DataFrame`
        The same shape as `curated_matrix_value`, but containing the original
        (unlogged) point estimates, masked where needed.
    curated_matrix_value : `pd.DataFrame`
        The final heatmap matrix with signed -log10(p-values), possibly NA-masked
        and suitable for plotting (numeric).
    matrix_point_estimate : `pd.DataFrame`
        A matrix of formatted point estimates as strings, with non-significant
        values masked.
    matrix_pvalue : `pd.DataFrame`
      A matrix of signed -log10(p-values), unmasked (floats).
    matrix_star : `pd.DataFrame`
      A matrix showing stars for significant values and empty strings otherwise.
    source_data : `pd.DataFrame`
        The input dataframe passed to `calc_matrices`, stored for provenance
        or further post hoc checks.
    '''
    SET_ARGS = [
        UtilsNames.value_input,
        UtilsNames.annot_input,
        UtilsNames.annot_star,
        UtilsNames.annot_pval,
        UtilsNames.annot_effect,
        UtilsNames.value_original,
        UtilsNames.value_point,
        UtilsNames.source_data,
    ]
    # /////////////////////////////////////////////////////////////////////////
    # Initiation the class
    def __init__(self, **kwargs):
        super().__init__(set_args=self.SET_ARGS, **kwargs)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MidpointNormalize(mpl.colors.Normalize):
    """
    Normalise colour values around a central midpoint.
    
    This custom normalisation class is useful for diverging colour maps where
    the colour scale should be centred around a meaningful reference point
    (e.g., zero or no effect). It maps the midpoint to 0.5 in the [0, 1]
    normalised scale and interpolates values linearly between vmin, vcenter,
    and vmax.
    
    Useful for visualising signed values (e.g., log-fold changes, residuals,
    differences) with symmetric colour gradients.
    
    Parameters
    ----------
    vmin : `float` or `NoneType`
        Minimum data value that maps to 0.0 on the colour scale.
    vmax : `float` or `NoneType`
        Maximum data value that maps to 1.0 on the colour scale.
    vcenter : `float` or `NoneType`
        Central value that maps to 0.5 on the colour scale.
    clip : `bool`, default False
        If True, data outside vmin/vmax is clipped to the endpoints.
    
    Methods
    -------
    inverse(value)
        Inverts a normalised value from the [0, 1] scale back to the original
        data scale.
    """
    def __init__(self, vmin:float | None = None, vmax:float | None = None,
                 vcenter:float | None = None, clip:bool=False):
        # check input
        is_type(clip, (type(None), bool))
        # assign to self
        self.vcenter = vcenter
        super().__init__(vmin, vmax, clip)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __call__(self, value:float, clip:bool | None = None):
        is_type(clip, (type(None), bool))
        # Note also that we must extrapolate beyond vmin/vmax
        if clip is None:
            clip = self.clip  # honour the value passed to __init__
        else:
            value = np.clip(value, self.vmin, self.vmax)
        x, y = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1.]
        return np.ma.masked_array(np.interp(value, x, y,
                                            left=-np.inf, right=np.inf))
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def inverse(self, value):
        y, x = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1]
        return np.interp(value, x, y, left=-np.inf, right=np.inf)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# Functions

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _update_kwargs(update_dict:dict[Any, Any], **kwargs:Optional[Any],
            ) -> dict[Any, Any]:
    """
    Merge keyword arguments with override priority.
    
    Updates a dictionary of keyword arguments, giving precedence to entries
    in `update_dict` over any duplicates in `kwargs`.
    
    Parameters
    ----------
    update_dict : `dict` [`any`, `any`]
        Dictionary of key-value pairs that take precedence.
    **kwargs
        Arbitrary keyword arguments.
    
    Returns
    -------
    dict
        A merged dictionary where keys in `update_dict` override those in
        `kwargs`.
    
    Examples
    --------
    >>> _update_kwargs(update_dict={'c': 'black'}, c='red', alpha = 0.5)
    {'c': 'black', 'alpha': 0.5}
    """
    new_dict = {**kwargs, **update_dict}
    # returns
    return new_dict

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _dict_string_argument(partial_match:str, dict_string:dict[Any, str],
                          context:dict[Any,Any],
                          ) -> dict[Any,Any]:
    """
    Evaluate matching string values in a dictionary using runtime context.
    
    For each string value in `dict_string` that matches `partial_match`,
    evaluate the string in the given `context` and assign the result back
    to the corresponding key.
    
    Parameters
    ----------
    partial_match : `str`
        Regex pattern to match string values.
    dict_string : `dict` ['any', 'str']
        Dictionary with values to evaluate conditionally.
    context : `dict` ['any', 'any']
        Dictionary providing variable context for evaluation.
    
    Returns
    -------
    dict
        Dictionary with evaluated values substituted in place.
    
    Examples
    --------
    >>> row=[1, 2]
    >>> dict_string={'obj1': 'row[0]', 'obj2' : 2}
    >>> new_dict = _dict_string_argument('row', dict_string,
                                         context={'row':row})
    {'obj1': 1, 'obj2': 2}
    """
    # testing input
    is_type(partial_match, str)
    is_type(dict_string, dict)
    # evaluting object
    for key, value in dict_string.items():
        if isinstance(value, str) and re.match(partial_match, value):
            dict_string[key] = eval(value, context)
    # return stuf
    return dict_string

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def plot_span(start_span:Real, stop_span:Real, ax:plt.Axes,
              horizontal:bool=True, **kwargs:Optional[Any],
              ):
    """
    Add a horizontal or vertical span to a matplotlib axis.
    
    Parameters
    ----------
    start_span: `float`
        The coordinate to start the span.
    stop_span: `float`
        The coordinate to end the span.
    ax : `plt.Axes`
            Axes object to annotate.
    horizontal : `bool`, default `True`
        Whether to use axhspan or axvspan.
    **kwargs
        Additional keyword arguments passed to `ax.axhspan` or `ax.axvspan`.
    
    Returns
    -------
    None
    """
    is_type(start_span, (int, float))
    is_type(stop_span, (int, float))
    is_type(ax, plt.Axes)
    is_type(horizontal, bool)
    # horizontal or vertical
    if horizontal == True:
        span = ax.axhspan
    else:
        span = ax.axvspan
    # plot
    span(start_span, stop_span, **kwargs)
    # return
    return None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def change_ticks(ax:plt.Axes, ticks:list[str], labels:list[str] | None = None,
                 axis:Literal['x','y']='x', log:bool=False):
    '''
    Update tick locations and labels for a given axis.
    
    Takes an axis and changes the ticks labels and location. If `labels` is
    set to `None`, it will use `ticks` for both the location and the labels.
    
    Parameters
    ----------
    ax : `plt.Axes`
        The axis to modify.
    ticks : `list` [`float` | `int`]
        A list of ticks marks which will be used for the position and labels
    labels : `list` [`str`]
        If supplied use these labels instead of re-using `ticks`.
    log: `bool`, default `False`
        If True, apply `np.log` to the tick locations before placing.
    
    Returns
    -------
    None
    
    Raises
    ------
    ValueError
        If `labels` is provided and its length differs from `ticks`, or if
        `axis` is not one of {'x', 'y'}.'''
    # check input
    is_type(ticks, list)
    is_type(labels, (list, type(None)))
    is_type(axis, str)
    is_type(log, bool)
    if axis in ['y', 'x'] == False:
        raise ValueError('`axis` is limited to `x` or `y`.')
    # set labels
    if isinstance(labels, list):
        if not len(labels) == len(ticks):
            raise ValueError('`labels` and `ticks` have distinct number of '
                             'entries.')
        # set the actual labels
        tick_labels = labels
    else:
        tick_labels = ticks
    # do we need to transform the location
    if log == True:
        tick_location = np.log(ticks)
    else:
        tick_location = ticks
    # work on xaxis
    if axis == 'x':
        try:
            ax.xaxis.set_ticks(tick_location)
            ax.xaxis.set_ticklabels(tick_labels)
        except AttributeError as e:
            raise e
    # work on yaxis
    if axis == 'y':
        try:
            ax.yaxis.set_ticks(tick_location)
            ax.yaxis.set_ticklabels(tick_labels)
        except AttributeError as e:
            raise e
    # done

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _extract(data:pd.DataFrame, exposure_col:str, outcome_col:str,
            point_col:str, pvalue_col:str, dropna:bool=False,
            **kwargs:Optional[Any],
            ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract point estimate and p-value matrices from long-format data.
    
    This function takes a long-format DataFrame and returns two pivot tables:
    one for point estimates and one for p-values. These are indexed by
    outcome and columned by exposure.
    
    Parameters
    ----------
    data : `pd.DataFrame`
        Input data in long format with the required columns.
    exposure_col : `str`
        Name of the column representing exposure variables.
    outcome_col : `str`
        Name of the column representing outcome variables.
    point_col : `str`
        Name of the column containing point estimates.
    pvalue_col : `str`
        Name of the column containing p-values.
    dropna : `bool`, default `False`
        Set to `True` to remove columns with any missing data.
        
    Returns
    -------
    point_mat : pd.DataFrame
        Matrix with point estimates.
    pvalue_mat : pd.DataFrame
        Matrix with p-values.
    
    Raises
    ------
    ValueError
        If the point and p-value matrices have mismatched shapes.
    """
    ### subsetting
    # making sure we do not change the original `data`
    data = data.copy()
    ### getting estimates
    point = data[[point_col, exposure_col, outcome_col]].copy()
    pvalue = data[[pvalue_col, exposure_col, outcome_col]].copy()
    ### matrix
    point_mat = point.pivot_table(index=[outcome_col],
                      columns = exposure_col,
                      values = point_col,
                      dropna=dropna,
                      **kwargs,
                      )
    pvalue_mat = pvalue.pivot_table(index=[outcome_col],
                      columns = exposure_col,
                      values = pvalue_col,
                      dropna=dropna,
                      **kwargs,
                      )
    ### check the shape are correct
    if not point_mat.shape == pvalue_mat.shape:
        raise ValueError('P-value and point estimate matrices have different'
                         'shapes')
    else:
        return point_mat, pvalue_mat

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _format_matrices(effect:pd.DataFrame, pval:pd.DataFrame, sig:float,
                     log:bool=True, ptrun:Real=16, digits:str='3',
                     symbol:str='★') -> tuple[pd.DataFrame,
                                                pd.DataFrame,
                                                pd.DataFrame,
                                                pd.DataFrame,
                                                pd.DataFrame,
                                                ]:
    """
    Format effect and p-value matrices for heatmap visualisation.

    Applies masking, rounding, annotation, and -log10 transformation to p-values,
    returning both numeric and string matrices for plotting.
    
    Parameters
    ----------
    effect : `pd.DataFrame`
        Matrix of effect estimates as floats.
    pval : `pd.DataFrame`
        Matrix of p-values as floats.
    sig : `float`
        The significance p-value cut-off either bounded between 0 and 1,
        or -log10 transformed.
    log : `bool`, default is `True`
        should the `pval` matrix be -log10 transformed.
    ptrun : `float` or `int`, default 16
        Truncation threshold for p-values.
    digits : `str`, default `3`
        the number of significant digits the effect matrix should be rounded.
    symbol : `str`, default `★`
        the unicode symbol used to flag significant findings.
    
    Returns
    -------
    pval : pd.DataFrame
        Signed p-value matrix (numeric).
    effect : pd.DataFrame
        Masked effect matrix with rounded string entries.
    star : pd.DataFrame
        Star annotation matrix for significant results.
    pvalstring : pd.DataFrame
        Masked p-value string matrix for annotation.
    effect_float : pd.DataFrame
        Raw effect matrix without masking.
    """
    
    # checking input
    if len(digits) > 1:
        raise ValueError("`digits` must be interpretable as a single integer, "
                         f"got: {digits}.")
    # taking the log10
    if log == True:
        pval_full = _nlog10_func(pval, ptrun)
    else:
        pval_full = pval.copy()
    # rounding
    dig = '{:.'+digits+'f}'
    pval = pval_full.round(int(float(digits)))
    dir = np.sign(effect)
    # simply stoaring the float matrix
    effect_float = effect.copy()
    # formatting
    if pd.__version__ < '2.1.0':
        effect = effect.applymap(dig.format).copy()
    else:
        effect = effect.map(dig.format).copy()
    # scaling
    pval = dir * pval
    # if log == True use larger than
    if log == True:
        # if not significant set to empty
        effect[pval_full < sig] = '.'
        effect = effect.astype('str')
        # adding stars
        star = effect.copy()
        star[pval_full >= sig] = symbol
        # pvalues
        pvalstring = effect.copy()
        pvalstring[pval_full >= sig] = pval[pval_full >= sig].astype('str')
        # if log != True use smaller than
    else:
        # if not significant set to empty
        effect[pval_full > sig] = '.'
        effect = effect.astype('str')
        # adding stars
        star = effect.copy()
        star[pval_full <= sig] = symbol
        # pvalues
        pvalstring = effect.copy()
        pvalstring[pval_full <= sig] = pval[pval_full <= sig].astype('str')
    
    # returning
    return pval, effect, star, pvalstring, effect_float

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calc_matrices(data:pd.DataFrame,
                  exposure_col:str,
                  outcome_col:str,
                  point_col:str='point',
                  pvalue_col:str='pvalue',
                  alpha:Real=-1*np.log10(0.05),
                  sig_numbers:int=2,
                  ptrun:Real=16,
                  annotate:str | None='star',
                  without_log:bool=False,
                  mask_na:bool=True,
                  **kwargs:Optional[Any],
                  ) -> MatrixHeatmapResults:
    """
    Generate value and annotation matrices for clustered heatmap visualisation.
    
    This function transforms a long-format DataFrame into heatmap-ready matrices
    based on statistical results. The output includes both numeric matrices
    (e.g. signed -log10(p-values)) and string annotations (e.g. significance
    stars, p-values, or effect sizes).
    
    Arguments
    ---------
    data : `pd.DataFrame`
        Long-format dataframe containing exposure, outcome, point estimate,
        and p-value columns.
    exposure_col : `str`
        Column name indicating the exposure variable.
    outcome_col : `str`
        Column name indicating the outcome variable.
    point_col : `str`, default `point`
        Column name with point estimates.
    pvalue_col : `str`, default 'pvalue'
        Column name with p-values. Note p-values are expected to range between
        0 and 1.
    alpha : `float` or `int`, default `-1*np.log(0.05)`
        The significance cut-off.
    sig_numbers : `int`, default 2
        The number of significant numbers the cell annotations should have.
    ptrun : `float` or `int`, default 16
        P-values smaller than 10^(-ptrun) are truncated.
    annotate : `str`, default 'star'
        Annotation style to return. Options:
        - 'star': significance stars
        - 'pvalues': raw or transformed p-values
        - 'pointestimates': formatted effect estimates
        - None: returns only numeric matrix without annotations
    without_log : `bool`, default `False`
        If the p-value should `NOT` be -log10 converted.
    mask_na : `bool`, default `True`
        If you want to mask missing results (e.g., replacing NAs by 0 or 1)
    **kwargs
        All other arguments are forwarded to `_extract`.
    
    Returns
    -------
    MatrixHeatmapResults
    
    Raises
    ------
    ValueError
        If `annotate` is not one of the supported values.
    """
    #### check input
    is_type(data, pd.DataFrame)
    is_type(exposure_col, str)
    is_type(outcome_col, str)
    is_type(point_col, str)
    is_type(pvalue_col, str)
    is_type(alpha, (int, float))
    is_type(sig_numbers, int)
    is_type(without_log, bool)
    is_type(mask_na, bool)
    ### subsetting data
    point_mat, pvalue_mat = _extract(data,
                                     exposure_col=exposure_col,
                                     outcome_col=outcome_col,
                                     point_col=point_col,
                                     pvalue_col=pvalue_col,
                                     **kwargs,
                                     )
    ### formatting data
    values, annot_effect, annot_star, annot_pval, values_point =\
        _format_matrices(
            point_mat, pvalue_mat, sig=alpha,
            ptrun=ptrun, digits=str(sig_numbers),
            log=without_log == False,
        )
    ### selecting the annotation to use
    if annotate == UtilsNames.mat_annot_star:
        annot = annot_star
    elif annotate == UtilsNames.mat_annot_pval:
        annot = annot_pval
    elif annotate == UtilsNames.mat_annot_point:
        annot = annot_effect
    elif annotate is None:
        annot = pd.DataFrame().reindex_like(values)
        annot.fillna('', inplace=True)
    else:
        raise ValueError('Incorrect `annotate` value supplied '
                         'Please use: {}'.\
                         format([UtilsNames.mat_annot_star,
                                 UtilsNames.mat_annot_pval,
                                 UtilsNames.mat_annot_point,
                                 UtilsNames.mat_annot_none,
                                 ]
                                ))
    ### drop or mask NAs
    if mask_na == False:
        drop_c = values.isna().any(axis = 0) == False
        drop_r = values.isna().any(axis = 1) == False
        values_input = values.loc[drop_r, drop_c]
        annot_input = annot.loc[drop_r, drop_c]
        # Mask with zero if logged
    elif without_log == False:
        values_input = values.fillna(0, inplace=False)
        annot_input = annot.fillna('.', inplace=False)
        annot_input[annot_input == 'nan'] = '.'
        # Mask with one if not
    else:
        values_input = values.fillna(1, inplace=False)
        annot_input = annot.fillna('.', inplace=False)
        annot_input[annot_input == 'nan'] = '.'
    ### Return
    res = {UtilsNames.value_input: values_input,
           UtilsNames.annot_input: annot_input,
           UtilsNames.annot_star: annot_star,
           UtilsNames.annot_pval: annot_pval,
           UtilsNames.annot_effect: annot_effect,
           UtilsNames.value_original: values,
           UtilsNames.value_point: values_point,
           UtilsNames.source_data: data,
           }
    return MatrixHeatmapResults(**res)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOTE see if this can be used for volcano as well
def adjust_labels(annotations:list, axis:plt.Axes,
               min_distance:Real=0.1):
    """
    Adjust positions of overlapping annotations to prevent collision.
    
    Iteratively checks all pairs of annotation objects and shifts them apart
    if their positions are within `min_distance` of one another.
    
    Parameters
    ----------
    annotations : `list` [`mpl.text.Annotation`]
        List of matplotlib ax.annotate objects.
    axis : `plt.Axes`
        The axis where annotations are drawn.
    min_distance : `float` or `int`, default 0.1
        Minimum allowable distance between annotations in data coordinates.
    
    Returns
    -------
    None
    """
    # type checking
    is_type(min_distance, (int, float))
    # plotting
    for i, ann1 in enumerate(annotations):
        for j, ann2 in enumerate(annotations):
            if i != j:
                # Get positions of annotations
                pos1 = axis.transData.inverted().transform(
                    axis.transData.transform(ann1.get_position())
                )
                pos2 = axis.transData.inverted().transform(
                    axis.transData.transform(ann2.get_position())
                )
                # Calculate distance between annotations
                vertical_distance = abs(pos1[1] - pos2[1])
                horizontal_distance = abs(pos1[0] - pos2[0])
                # Adjust positions if annotations overlap
                if vertical_distance < min_distance and\
                        horizontal_distance < min_distance:
                    if pos1[1] < pos2[1]:
                        pos1 = (pos1[0], pos2[1] - min_distance)
                    else:
                        pos2 = (pos2[0], pos1[1] - min_distance)
                    ann1.set_position(pos1)
                    ann2.set_position(pos2)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calc_mid_point(x:list[float] | tuple[float, float],
                   y:list[float] | tuple[float, float],
                   ) -> tuple[float, float]:
    """
    Takes two points and returns the Cartesian coordinates of the point in
    the middle of these two points.
    
    Parameters
    ----------
    x: `list` or `tuple` of two floats
        The x-coordinates of the two points.
    y: `list` or `tuple` of two floats
        The y-coordinates of the two points.
    
    Returns
    -------
    tuple of two floats
        returns coordinate of the point between `x` and `y`.
    
    Raises
    ------
    InputValidationError
        If either `x` or `y` do not contain exactly two elements.
    """
    # input
    is_type(x, (list,tuple))
    is_type(y, (list,tuple))
    if len(x) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'x',str(2), str(len(x))))
    if len(y) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'y',str(2), str(len(x))))
    # calculates the mid point
    x_mid = sum(x)/2
    y_mid = sum(y)/2
    # return
    return x_mid, y_mid

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def calc_angle_points(x:list[float] | tuple[float, float],
                      y:list[float] | tuple[float, float],
                      radians:bool=False,
                      ) -> float:
    '''
    Calculate the angle between two points, returns an angle between 0 and
    360 degrees.
    
    Parameters
    ----------
    x : `list` or `tuple` of two floats
        The x-coordinates of the two points.
    y : `list` or `tuple` of two floats
        The y-coordinates of the two points.
    radians : `bool`, default `False`
        returns the angle in radians instead of degrees.
    
    Returns
    -------
    float
        Angle in degrees (0–360) or radians.
    
    Raises
    ------
    InputValidationError
        If either `x` or `y` do not contain exactly two elements.
    '''
    # input
    is_type(radians, bool)
    is_type(x, (list,tuple))
    is_type(y, (list,tuple))
    if len(x) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'x',str(2), str(len(x))))
    if len(y) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'y',str(2), str(len(x))))
    # get the angle
    delta_x = x[1] - x[0]
    delta_y = y[1] - y[0]
    slope=delta_y/delta_x
    angle_radians = np.arctan(slope)
    # convert radians to degrees
    angle_degrees_original = np.degrees(angle_radians)
    # ensure the angle is between 0 and 360 degrees
    angle = (angle_degrees_original + 360) % 360
    # get the principal angle
    if radians == True:
        angle = np.radians(angle)
    # return
    return angle

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def segment_labelled(
    x:tuple[float, float], y:tuple[float, float], ax:plt.Axes,
    label: str | None = None,
    endpoints_marker: str | mpath.Path=mpath.Path.unit_circle(),
    endpoints_size:Real=8, endpoints_c:str='orangered', segment_c='black',
    label_fontsize:Real=10, label_background_c='white',
    overrule_angle: Real | None = None,
    calc_angle_after_trans:bool=True,
    kwargs_segment:dict[Any, Any]={},
    kwargs_text:dict[Any, Any]={},
) -> plt.Axes:
    """
    Plots a line segment between two points, and optionally annotates the
    midpoint with a `label` string.
    
    Parameters
    ----------
    x : `list` or `tuple` of two floats
        The x-coordinates of the two points.
    y : `list` or `tuple` of two floats
        The y-coordinates of the two points.
    label : `str`
        The string which be plotted on top of the line segment. Set to
        `NoneType` to not plot anything.
    ax : `plt.axes`
        The matplotlib axis.
    endpoints_marker : `str`, default `unit_circle`
        The marker of the line segment endpoints.
    endpoints_size : `float` or `int`, default 30
        The marker size.
    endpoints_c : `str`, default `orangered`
        The marker colour.
    segment_c : `str`, default `black`
        The segment line colour
    label_fontsize : `float` or `int`, default 20
        The label font size.
    label_background_c : `str`, default `white`
        The label background colour.
    overrule_angle : `float` or `int`, default `NoneType`
        Use this to overrule the internally calculated angle against which the
        label will be plotted.
    calc_angle_after_trans : `bool`, default `True`
        Whether to apply a `ax.transData.transform_point` transformation before
        calculating the angle the text needs to be plotted on.
    kwargs_*_dict : `dict`, default empty dict
        Optional arguments supplied to the various plotting functions:
            kwargs_segment --> ax.plot
            kwargs_text    --> ax.text
    
    Returns
    -------
    matplotlib.axes.Axes
        The modified axis with the line segment.
    """
    # ################### input
    is_type(x, (list,tuple))
    is_type(y, (list,tuple))
    is_type(ax, plt.Axes)
    is_type(label, (type(None),str))
    # is_type(endpoints_marker, str)
    is_type(endpoints_size, (int, float))
    is_type(endpoints_c, str)
    is_type(label_fontsize, (int, float))
    is_type(label_background_c, str)
    is_type(overrule_angle, (type(None), float, int))
    if len(x) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'x',str(2), str(len(x))))
    if len(y) != 2:
        raise InputValidationError(Error_MSG.INVALID_EXACT_LENGTH.format(
            'y',str(2), str(len(x))))
    # ################### get mid point and angle
    mid_coordinates=calc_mid_point(x=x, y=y)
    if overrule_angle is None:
        # do we need to apply a transformation first
        if calc_angle_after_trans == True:
            p1 = list(ax.transData.transform_point((x[0], y[0])))
            p2 = list(ax.transData.transform_point((y[0], y[1])))
            x_trans=[p1[0], p2[0]]
            y_trans=[p1[1], p2[1]]
        else:
            x_trans = x
            y_trans = y
        text_angle=calc_angle_points(x=x_trans, y=y_trans)
    else:
        text_angle=overrule_angle
    # ################### plot line segment
    new_segment_kwargs = _update_kwargs(update_dict=kwargs_segment,
                                        c=segment_c,
                                        markersize=endpoints_size,
                                        marker=endpoints_marker,
                                        markerfacecolor=endpoints_c,
                                        linestyle='-'
                                        )
    ax.plot(x, y,
            **new_segment_kwargs)
    # ################### plot label
    if label is not None:
        new_label_kwargs = _update_kwargs(update_dict=kwargs_text,
                                          va='center', ha='center',
                                          backgroundcolor=label_background_c,
                                          fontsize=label_fontsize,
                                          rotation=text_angle,
                                          )
        ax.text(mid_coordinates[0], mid_coordinates[1], label,
                **new_label_kwargs,
                )
    # ################### return
    return ax

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def annotate_axis_midpoints(ax:plt.Axes, labels:list[str],
                            axis:Literal['x','y']='y',
                            gap:Real=6,
                            offset:Real | None = None,
                            padding:Real = 0.0,
                            start_label:dict[str, float] | None = None,
                            end_label:dict[str, float] | None = None,
                            text_kwargs:dict[str, any] | None = None,
                            text_kwargs_start:dict[str, any] | None = None,
                            text_kwargs_end:dict[str, any] | None = None,
                            ) -> plt.Axes:
    """
    Identifies gaps between axes label positions and annotates the midpoints
    with user supplied labels.
    
    Parameters
    ----------
    ax : `plt.Axes`
        The axis to annotate.
    labels : `list` [`str`]
        A list of labels for each midpoint.
    axis : {'x', 'y'}, default 'y'
        Which axis to analyse and annotate.
    gap : `int` or `float`, default 6
        The exact space between tick values to trigger annotation.
    offset : float, default `NoneType`
        The position of the label **orthogonal to the axis**, given in **axes
        coordinates** (0 = bottom/left of axis, 1 = top/right). Negative values
        place the label outside the axis bounds. Defaults to:
            - -0.01 for `axis='y'` (left of y-axis)
            - -0.02 for `axis='x'` (below x-axis)
    padding : float, default 0.0
        The padding on the requested axis in original units. Only applied to
        `labels` supplied strings.
    start_label : `dict` [`str`, `float`], default `NoneType`
        Optional label before the first detected gap. Format should be:
        `{"label text": position}` where position is the coordinate orthogonal
        to the axis (in axes coordinates).
    end_label : `dict` [`str`, `float`], default `NoneType`
        Optional label after the last detected gap. Same format as `start_label`.
    text_kwargs : `dict` [`str`, `any`]
        Extra keyword arguments for `ax.text()` (e.g. fontweight).
    
    Returns
    -------
    plt.Axes
        The updated axis with added midpoint annotations.
    
    Raises
    ------
    IndexError
        If number of `labels` does not match the number of detected gaps.
    ValueError
        If `axis` is not either 'x' or 'y'.
    """
    # ### check input
    is_type(ax, plt.Axes)
    is_type(axis, str)
    is_type(labels, list)
    is_type(gap, (int, float))
    is_type(offset, (type(None), int, float))
    is_type(start_label, (type(None), dict))
    is_type(end_label, (type(None), dict))
    if axis in ['y', 'x'] == False:
        raise ValueError('`axis` is limited to `x` or `y`.')
    # setting defaults
    if offset is None:
        offset = -0.01 if axis == 'y' else -0.02
    # initialise empty dict
    text_kwargs = text_kwargs or {}
    text_kwargs_start = text_kwargs_start or {}
    text_kwargs_end = text_kwargs_end or {}
    # #### Extract tick positions and labels from the chosen axis, and define
    # a label placement function with appropriate axis transform
    if axis == 'y':
        ticks = ax.get_yticks()
        # make sure the axis y-axis is mapped to 0-1 range instead of the
        # original units, the x-axis is unaffected..
        transform = ax.get_yaxis_transform()
        # updating kwargs
        new_kwargs = _update_kwargs(
            update_dict=text_kwargs, ha='right', va='center',
            transform=transform)
        new_kwargs_start = _update_kwargs(
            update_dict=text_kwargs_start, ha='right', va='top',
            transform=transform)
        new_kwargs_end = _update_kwargs(
            update_dict=text_kwargs_end, ha='right', va='bottom',
            transform=transform)
        # the actual function
        place_text = lambda pos, spine_coord, label, kwargs: ax.text(
            x=spine_coord, y=pos, s=label, **kwargs)
    else:
        ticks = ax.get_xticks()
        # same as above.
        transform = ax.get_xaxis_transform()
        # updating kwargs
        new_kwargs = _update_kwargs(
            update_dict=text_kwargs, va='top', ha='center', transform=transform)
        new_kwargs_start = _update_kwargs(
            update_dict=text_kwargs_start, va='top', ha='left',
            transform=transform)
        new_kwargs_end = _update_kwargs(
            update_dict=text_kwargs_end, va='top', ha='right',
            transform=transform)
        # the actual function
        place_text = lambda pos, spine_coord, label, kwargs: ax.text(
            x=pos, y=spine_coord, s=label, **kwargs)
    #  #### Identify exact-sized gaps
    gap_indices = [
        i for i in range(len(ticks) - 1)
        if abs(ticks[i + 1] - ticks[i]) == gap
    ]
    n_expected = len(gap_indices)
    if isinstance(labels, list) and len(labels) != n_expected:
        raise IndexError(
            f"Expected {n_expected} labels for gap = {gap}, "
            f"but received {len(labels)}."
        )
    # #### Adding optional start label
    if start_label:
        label_s, spine_coord_s = list(start_label.items())[0]
        place_text(spine_coord_s, offset, label_s, new_kwargs_start)
    # ##### Midpoint labels
    for j, i in enumerate(gap_indices):
        mid = (ticks[i] + ticks[i + 1]) / 2
        label_text = labels(j) if callable(labels) else labels[j]
        place_text(mid+padding, offset, label_text, new_kwargs)
    # #### Adding optional end label
    if end_label:
        # mid_e = (ticks[i + 1] + ticks[-1]) / 2
        label_e, spine_coord_e = list(end_label.items())[0]
        place_text(spine_coord_e, offset, label_e, new_kwargs_end)
    # #### return
    return ax

