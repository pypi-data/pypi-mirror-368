"""
This module provides utility functions and error classes to support safe and
consistent handling of inputs throughout the plot-misc codebase. It includes
mechanisms for enforcing type constraints, checking object shapes and content,
and raising informative exceptions when expectations are not met.

Classes
-------
InputValidationError
    A custom exception raised when validation of a parameter fails.

Error_MSG
    A container of templated error messages for validation routines.

Functions
---------
is_type(param, types, param_name=None)
    Verifies that a parameter is an instance of a given type or set of types.

is_df(df)
    Confirms whether an object is a pandas DataFrame.

are_columns_in_df(df, expected_columns, warning=False)
    Checks that specific column names exist in a DataFrame.

is_series_type(column, types)
    Confirms all elements of a Series or DataFrame match a specified type.

same_len(object1, object2, object_names=None)
    Validates that two objects have the same length.

string_to_list(object)
    Wraps strings in a list; leaves other objects unchanged.

"""

import inspect
import warnings
import pandas as pd
from typing import (
    Any,
    Type,
    Set,
)
from packaging import version


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class InputValidationError(Exception):
    """
    Custom exception for signalling input validation failures.
    """
    pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# error messages
class Error_MSG(object):
    """
    Container for predefined error message templates.
    
    Attributes
    ----------
    MISSING_DF : str
        Message template for missing values in a DataFrame.
    INVALID_STRING : str
        Message for invalid string values.
    INVALID_EXACT_LENGTH : str
        Message for enforcing exact list or array length.
    """
    MISSING_DF = '`{}` contains missing values.'
    INVALID_STRING = '`{}` should be limited to `{}`.'
    INVALID_EXACT_LENGTH = '`{}` needs to contain exactly {} elements, not {}.'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _get_param_name(param:Any) -> str | None:
    """
    Attempt to infer the variable name of a parameter from the caller's scope.
    """
    frame = inspect.currentframe().f_back.f_back
    param_names =\
        [name for name, value in frame.f_locals.items() if value is param]
    return param_names[0] if param_names else None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def is_type(param: Any, types: tuple[Type] | Type,
            param_name: str | None = None,) -> bool:
    """
    Checks if a given parameter matches any of the supplied types
    
    Parameters
    ----------
    param : `any`
        Object to test.
    types: `type` or `tuple` [`type`]
        Expected type(s) of the object.
    param_name : `str` or `None`
        Name of the parameter. Will attempt to infer the parameter name if set
        to `NoneType`.
    
    Returns
    -------
    bool
        True if type matches.
    
    Raises
    ------
    InputValidationError
        If the parameter does not match any of the expected types.
    """
    if not isinstance(param, types):
        if param_name is None:
            param_name = _get_param_name(param)
        else:
            warnings.warn('`param_name` will be depricated.',
                          DeprecationWarning,
                          stacklevel=2,
                          )
        raise InputValidationError(
            f"Expected any of [{types}], "
            f"got {type(param)}; Please see parameter: `{param_name}`."
        )
    return True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def is_df(df: Any) -> bool:
    """
    Check if objects is a pd.DataFrame.
    
    Parameters
    ----------
    df : `Any`
        Object to test.
    
    Returns
    -------
    bool
        True if the object is a DataFrame.
    
    Raises
    ------
    InputValidationError
        If the object is not a DataFrame.
    """
    return is_type(df, pd.DataFrame)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# NOTE add test for expected_columns being a str and that it raises an error
# with the intact tsring rather than each letter individually.
def are_columns_in_df(
    df: pd.DataFrame, expected_columns: list[str] | str, warning: bool=False,
) -> bool:
    """
    Check if all expected columns are present in a given pandas.DataFrame.
    
    Parameters
    ----------
    df : `pandas.DataFrame`
        DataFrame to test.
    expected_columns: `str` or `list` [`str`]
        Expected column name(s). For easy of use any `None` entries will be
        filtered out before applying the test.
    warning : bool, default False
        raises a warning instead of an error.
    
    Returns
    -------
    bool
        True if all columns are present, False if missing and `warning=True`.
    
    Raises
    ------
    InputValidationError
        If any columns are missing and `warning=False`.
    """
    # constant
    message = "The following columns are missing from the pandas.DataFrame: {}"
    res = True
    # filtering out any potential None names
    expected_columns = string_to_list(expected_columns)
    expected_columns = [c for c in expected_columns if c is not None]
    # tests
    expected_columns_set: Set[str] = set(expected_columns) if isinstance(
        expected_columns, list
    ) else set([expected_columns])
    missing_columns = expected_columns_set - set(df.columns)
    # return
    if missing_columns:
        if warning == False:
            raise InputValidationError(
                message.format(missing_columns)
            )
        else:
            warnings.warn(
                message.format(missing_columns)
            )
            res = False
    return res


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def is_series_type(column: pd.Series | pd.DataFrame, types: tuple[Type] | Type,
                   ) -> bool:
    """
    Check whether each element of a Series or DataFrame matches a given type.
    
    Parameters
    ----------
    column : `pd.Series` or `pd.DataFrame`
        Data structure to validate.
    types : `type` or `tuple` [`tupe`]
        Allowed types for individual elements.
    
    Returns
    -------
    bool
        True if all elements match given types.
    
    Raises
    ------
    InputValidationError
        If any element fails the type check.
    
    Notes
    -----
    Instead of testing the dtypes, the function will look over each
        element and test these individually.
    """
    # check input
    is_type(column, (pd.DataFrame, pd.Series))
    # run tests
    if isinstance(column, pd.Series):
        [is_type(col, types) for col in column]
    elif isinstance(column, pd.DataFrame):
        if version.parse('2.0.3') <= version.parse(pd.__version__):
            # iteritems got depricated.
            column.iteritems = column.items
        for _, col in column.items():
            [is_type(co, types) for co in col]
    # return
    return True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def same_len(object1: Any, object2: Any, object_names: list[str] | None = None,
             ) -> bool:
    """
    Assert that two objects have the same length.
    
    Parameters
    ----------
    object1 : Any
        First object.
    object2 : Any
        Second object.
    object_names : list of str, optional
        Names of the two objects (for error message).
    
    Returns
    -------
    bool
        True if lengths match.
    
    Notes
    -----
    both object1 and object2 should have a `len` method.
    
    Raises
    ------
    ValueError
        If lengths do not match or `object_names` is invalid.
    """
    n1 = len(object1)
    n2 = len(object2)
    if object_names is None:
        object_names = ['object1', 'object2']
    elif len(object_names) !=2:
        raise ValueError('`object_names` should be `NoneType` or contain '
                         'two strings')
    # the actual test
    if n1 != n2:
        raise ValueError("The length of `{0}`: {1}, does not match the length "
                         "of `{2}`: {3}.".format(object_names[0], n1,
                                               object_names[1], n2)
                         )
    return True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def string_to_list(object:Any) -> Any | list[str]:
    """
    Checks if `object` is a string and wraps this in a list, returns the
    original object if it is not a string.
    
    Parameters
    ----------
    object : Any
        Object to check.
    
    Returns
    -------
    list[str] or Any
        List if input is string; otherwise the input unchanged.
    """
    if isinstance(object, str):
        return [object]
    else:
        return object

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def number_to_list(object:Any) -> Any | list[str]:
    """
    Checks if `object` is a float or int and wraps this in a list, returns the
    original object if it is not a string.
    
    Parameters
    ----------
    object : Any
        Object to check.
    
    Returns
    -------
    list[str] or Any
        List if input is string; otherwise the input unchanged.
    """
    if isinstance(object, (int, float)):
        return [object]
    else:
        return object

