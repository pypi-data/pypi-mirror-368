from .check_locality import check_locality
from .common_functions import check_for_dataframe,check_if_all_args_empty,check_all_columns_values

def use_locality(dataframe=None,
                 continent = None,
                 country = None,
                 countryCode = None,
                 stateProvince = None,
                 locality = None):
    """
    Checks for additional location information, such as country and countryCode.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        continent: ``str``
            Either a column name (``str``) or a string denoting one of the seven continents.
        country: ``str`` or ``pandas.Series``
            Either a column name (``str``) or a string denoting the country.
        countryCode: ``str`` or ``pandas.Series``
            Either a column name (``str``) or a string denoting the countryCode.
        stateProvince: ``str`` or ``pandas.Series``
            Either a column name (``str``) or a string denoting the state or province.
        locality: ``str`` or ``pandas.Series``
            Either a column name (``str``) or a string denoting the locality.
    Returns
    -------
        ``pandas.DataFrame`` with the updated data.
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='use_locality')

    # create a dictionary of names for renaming
    mapping = {
        continent: 'continent',
        country: 'country',
        countryCode: 'countryCode',
        stateProvince: 'stateProvince',
        locality: 'locality'
    }

    accepted_formats = {
        continent: [str],
        country: [str],
        countryCode: [str],
        stateProvince: [str],
        locality: [str]
    }

    # specify values
    values = ['continent','country','countryCode','stateProvince','locality']

    # check if all args are empty
    check_if_all_args_empty(dataframe=dataframe,func='use_locality',keys=mapping.keys(),values=values)

    # check column names and values
    dataframe,mapping = check_all_columns_values(dataframe=dataframe,mapping=mapping,accepted_formats=accepted_formats)

    # rename all necessary columns
    dataframe = dataframe.rename(columns=mapping)
    
    # get errors in data
    errors = check_locality(dataframe=dataframe)

    # return errors if there are any; otherwise, 
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe