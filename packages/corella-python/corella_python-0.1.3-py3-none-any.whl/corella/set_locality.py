from .check_locality import check_locality
from .common_functions import check_for_dataframe,set_data_workflow

def set_locality(dataframe=None,
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
            Valid values are: ``"Africa"``, ``"Antarctica"``, ``"Asia"``, ``"Europe"``, ``"North America"``, ``"Oceania"``, ``"South America"``
        country: ``str`` or ``pandas.Series``
            Either a column name (``str``) or a string denoting a valid country name.  See ``country_codes``.
        countryCode: ``str`` or ``pandas.Series``
            Either a column name (``str``) or a string denoting a valid country code.  See ``country_codes``.
        stateProvince: ``str`` or ``pandas.Series``
            Either a column name (``str``) or a string denoting a sub-national region.
        locality: ``str`` or ``pandas.Series``
            Either a column name (``str``) or a string containing a specific description of a location or place.
    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_locality vignette <../../html/corella_user_guide/independent_observations/set_locality.html>`_
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='set_locality')

    # mapping of column names and variables
    mapping = {
        'continent': continent,
        'country': country,
        'countryCode': countryCode,
        'stateProvince': stateProvince,
        'locality': locality
    }

    # accepted data formats for each argument
    accepted_formats = {
        'continent': [str],
        'country': [str],
        'countryCode': [str],
        'stateProvince': [str],
        'locality': [str]
    }

    # specify variables and values for set_data_workflow()
    variables = [continent,country,countryCode,stateProvince,locality]
    values = ['continent','country','countryCode','stateProvince','locality']

    # set column names and values specified by user
    dataframe = set_data_workflow(func='set_locality',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)
    
    # get errors in data
    errors = check_locality(dataframe=dataframe)

    # return errors if there are any; otherwise, 
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe