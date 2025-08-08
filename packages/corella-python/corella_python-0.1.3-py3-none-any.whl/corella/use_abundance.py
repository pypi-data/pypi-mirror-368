from .check_abundance import check_abundance
from .common_functions import check_for_dataframe,check_if_all_args_empty,check_all_columns_values

def use_abundance(dataframe=None,
                  individualCount=None,
                  organismQuantity=None,
                  organismQuantityType=None):
    """
    Checks for location information, as well as uncertainty and coordinate reference system.  
    Also runs data checks on coordinate validity.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        individualCount: ``str``
            A column name (``str``) that contains your individual counts (should be whole numbers).
        organismQuantity: ``str`` or 
            A column name (``str``) that contains a description of your individual counts.
        organismQuantityType: ``str`` 
            A column name (``str``) that describes what your organismQuantity is.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.
    """

    # raise a ValueError if no dataframe is provided
    check_for_dataframe(dataframe=dataframe,func='use_abundance')
    
    # column renaming dictionary
    renaming_map = {
        individualCount: 'individualCount',
        organismQuantity: 'organismQuantity',
        organismQuantityType: 'organismQuantityType',
    }

    # manually set values for function
    values = ['individualCount','organismQuantity','organismQuantityType']

    # check if all args are empty
    check_if_all_args_empty(dataframe=dataframe,func='use_abundance',keys=renaming_map.keys(),values=values)

    # denote accepted formats
    accepted_formats = {
        individualCount: [int],
        organismQuantity: [int],
        organismQuantityType: [str],
    }

    # check all columns and values to see if they need to be renamed or replaced
    dataframe,mapping = check_all_columns_values(dataframe=dataframe,mapping=renaming_map,accepted_formats=accepted_formats)

    # rename all necessary columns
    dataframe = dataframe.rename(columns=mapping)

    # check errors in data
    errors = check_abundance(dataframe=dataframe,errors=[])
    
    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe