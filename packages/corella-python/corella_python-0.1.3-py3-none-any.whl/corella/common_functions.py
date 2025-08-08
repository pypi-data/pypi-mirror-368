import pandas as pd
import numpy as np
import datetime
from .common_dictionaries import formats
from pandas.api.types import is_numeric_dtype,is_string_dtype,is_datetime64_any_dtype

def set_data_workflow(func=None,
                      dataframe=None,
                      mapping=None,
                      variables=None,
                      values=None,
                      accepted_formats=None):

    # check if all args are empty
    check_if_all_args_empty(dataframe=dataframe,func=func,keys=variables,values=values)

    # check column names and values
    dataframe,mapping = check_all_columns_values(dataframe=dataframe,mapping=mapping,accepted_formats=accepted_formats)

    # rename all necessary columns
    dataframe = dataframe.rename(columns=mapping)

    return dataframe

def snake_to_camel_case(list_of_words=None):
    """
    Changes snake case to camel case.

    Parameters
    ----------
        list_of_words: ``list``
            list of words to switch case

    Returns
    -------
        New list with the changed case
    """
    new_list = []
    for w in list_of_words:
        term = w.lower().split("_")
        for i in range(len(term)):
            term[i] = term[i].capitalize()
        new_list.append("".join(term))
    return new_list

def check_is_string(dataframe=None,
                    column_name=None,
                    errors=None):
    """
    Checks whether or not your chosen column has data with the string type.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            dataframe with data to check
        column_name: ``str``
            name of column to check
        errors: ``list``
            current list of errors

    Returns
    -------
        ``errors``: ``list``
            updated list of errors
    """
    if not is_string_dtype(dataframe[column_name]):
        errors.append('the {} column must be a string.'.format(column_name))
    return errors

def check_is_numeric(dataframe=None,
                     column_name=None,
                     errors=None):
    """
    Checks whether or not your chosen column has data with the numeric type.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            dataframe with data to check
        column_name: ``str``
            name of column to check
        errors: ``list``
            current list of errors

    Returns
    -------
        ``errors``: ``list``
            updated list of errors
    """
    if (not is_numeric_dtype(dataframe[column_name])) and (not type(dataframe[column_name].dtypes) in [np.dtypes.Int64DType,np.dtypes.Int32DType]):
        other_formats = list(set(type(x) for x in dataframe[column_name]))
        if (len(other_formats) > 1 )| (not is_numeric_dtype(other_formats[0])):
            errors.append('the {} column must be numeric.'.format(column_name))
    return errors

def check_is_datetime(dataframe=None,
                     column_name=None,
                     errors=None):
    """
    Checks whether or not your chosen column has data with the numeric type.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            dataframe with data to check
        column_name: ``str``
            name of column to check
        errors: ``list``
            current list of errors

    Returns
    -------
        ``errors``: ``list``
            updated list of errors
    """

    if not is_datetime64_any_dtype(dataframe[column_name]):
        other_formats = list(set(type(x) for x in dataframe[column_name]))
        if (len(other_formats) > 1 )| (other_formats[0] is not datetime.time):
            errors.append('the {} column must be in datetime format.'.format(column_name))
    return errors

def swap_error_message(errors=None,
                       orig_message=None,
                       new_message=None):
    """
    Swaps generic error with custom error message

    Parameters
    ----------
        errors: ``list``
            list of errors to check for messages
        orig_message: ``str``
            original message in ``errors`` list
        new_message: ``str``
            new message in place of ``orig_message``

    Returns
    -------
        updated list of errors
    """
    if orig_message in errors:
        index = errors.index(orig_message)
        errors[index] = new_message
    return errors

def get_bor_values():
    """
    Gets current valid values for ``basisOfRecord``

    Parameters
    ----------
        None

    Returns
    -------
        A list of valid ``basisOfRecord`` terms 
    """
    temp = pd.read_table('https://raw.githubusercontent.com/gbif/parsers/dev/src/main/resources/dictionaries/parse/basisOfRecord.tsv').dropna()
    terms = list(set(temp['PRESERVED_SPECIMEN']))
    terms = snake_to_camel_case(terms)
    return terms

def check_for_dataframe(dataframe=None,
                        func=None):

    if dataframe is None:
        raise ValueError('Please provide a dataframe to {}().'.format(func))
    elif dataframe.empty:
        raise ValueError('You provided an empty dataframe.  Please provide one with data.')
    
def check_if_all_args_empty(dataframe=None,
                            func=None,
                            keys=None,
                            values=None):
    
    if all([v not in values for v in dataframe.columns]):
        if all([v is None for v in keys]):
            raise ValueError("No Darwin Core arguments supplied to `{}()`.  See dir(corella.{}()) for valid arguments.".format(func,func))
        
def check_all_columns_values(dataframe=None,
                             mapping=None,
                             accepted_formats=None):
    # loop over all variables with following logic:
    # 1. check if var is None
    # 2. If var is not none, and not in the column names, assume user has given us a value for the column and add it; 
    #        delete entry in dictionary, as column does not need to be renamed 

    # make a copy of the dictionary to return
    mapping_to_return = mapping.copy()
    
    # loop over mapping keys
    for key in mapping.keys():
        if mapping[key] is not None:
            if key not in dataframe.columns:
                if type(mapping[key]) is str and mapping[key] in dataframe.columns:
                    pass
                elif type(mapping[key]) in accepted_formats[key] and type(mapping[key]) is not bool:
                    if (type(mapping[key]) is not str) or (mapping[key] not in dataframe.columns):
                        dataframe[key] = mapping[key]
                        del mapping_to_return[key]
                elif type(mapping[key]) in accepted_formats[key] and type(mapping[key]) is bool:
                    del mapping_to_return[key]
                else:
                    f = [formats[x] for x in accepted_formats[key]]
                    if len(f) > 1:
                        raise ValueError("Only type(s) {} is accepted for {}".format(",".join(f),key))
                    else:
                        raise ValueError("Only type(s) {} is accepted for {}".format(f[0],key))

    # invert dict for renaming
    mapping_to_return_inverted = dict(map(reversed, mapping_to_return.items()))

    # return dataframe and column mappings for renaming
    return dataframe,mapping_to_return_inverted