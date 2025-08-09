"""
Named constants for use throughout the plot-misc package.

This module provides collections of string constants grouped by their
functional context. These constants are intended to ensure consistency
in labelling, plotting, and data management across modules.
"""


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CLASS_NAME = '__CLASS_NAME'

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# an alias to int or float type hint
Real = int | float

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Forest plot
class ForestNames(object):
    """
    Constants used by forest.py
    """
    s_col                          = 's_col'
    c_col                          = 'c_col'
    a_col                          = 'a_col'
    g_col                          = 'g_col'
    y_col                          = 'y_axis'
    forest_data                    = 'data'
    strata_del                     = 'strata_del'
    group_del                      = 'group_del'
    order_col                      = 'order'
    min                            = 'min'
    max                            = 'max'
    mean                           = 'mean'
    fontweight                     = 'bold'
    kwargs                         = 'kwargs'
    span                           = 'span'
    ESTIMATE                       = 'estimate'
    LOWER_BOUND                    = 'lower_bound'
    UPPER_BOUND                    = 'upper_bound'
    PVALUE                         = 'p-value'
    CI                             = 'confidence_interval'
    data_table                     = 'data_table'
    EmpericalSupport_Coverage      = 'coverage'
    EmpericalSupport_Compatability = 'compatibility'
    EmpericalSupportResults        = 'results_'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Utils Names
class UtilsNames(object):
    """
    Constants used by utils.utils.py
    """
    value_input        = 'curated_matrix_value'
    annot_input        = 'curated_matrix_annotation'
    annot_star         = 'matrix_star'
    annot_pval         = 'matrix_pvalue'
    annot_effect       = 'matrix_point_estimate'
    value_point        = 'curated_matrix_point_estimate_value'
    value_original     = 'crude_point_estimate'
    source_data        = 'source_data'
    mat_point          = 'point'
    mat_pvalue         = 'pvalue'
    mat_index          = 'id'
    mat_exposure       = 'exposure'
    mat_outcome        = 'outcome'
    mat_exposure_list  = ['IL2ra', 'IP10', 'SCF', 'TRAIL']
    mat_outcome_list   = ['HDL-C', 'LDL-C']
    mat_annot_star     = 'star'
    mat_annot_pval     = 'pvalues'
    mat_annot_point    = 'point_estimates'
    mat_annot_none     = '`NoneType`'
    roc_false_positive = 'false_positive'
    roc_sensitivity    = 'sensitivity'
    roc_threshold      = 'threshold'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NamesDecisionCurves(object):
    '''
    Names used by the DecisionCurve class in machine_learning.py
    '''
    TP_RATE      = 'True positive rate'
    FP_RATE      = 'False positive rate'
    THRESHOLD    = 'Threshold'
    ALL_MODEL    = 'All model'
    NONE_MODEL   = 'None model'
    MODEL        = 'model'
    NETBENEFIT   = 'Net benefit'
    HARM         = 'harm'
    COL          = 'col'
    LTY          = 'lty'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NamesIncidenceMatrix(object):
    """
    Names used by incidencematrix.py
    """
    AXIS_X       = 'x'
    AXIS_Y       = 'y'
    AXIS_B       = 'both'
    GRID_POS_B   = 'centre'
    GRID_POS_O   = 'outline'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NamesMachineLearnig(object):
    '''
    Names used by machinelearning.py
    '''
    DATA           = 'data'
    CI_COLOUR      = 'ci_colour'
    CI_LINEWIDTH   = 'ci_linewidth'
    DOT_COLOUR     = 'dot_colour'
    DOT_MARKER     = 'dot_marker'
    LINE_COLOUR    = 'line_colour'
    LINE_LINEWIDTH = 'line_linewidth'
    LINE_LINESTYLE = 'line_linestyle'

