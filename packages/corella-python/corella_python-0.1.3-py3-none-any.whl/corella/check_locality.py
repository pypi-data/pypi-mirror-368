import os
import pandas as pd
from .common_dictionaries import continents
from .common_functions import check_is_string

def check_locality(dataframe=None,
                   errors=[]):
    """
    Checks the following fields:

    - ``continent``
    - ``country``
    - ``countryCode``
    - ``stateProvince``
    - ``locality``

    It will check if all the above fields are strings.    

    It will also check if the ``continent``, ``country`` and ``countryCode`` 
    column values are correct (valid country and country codes are found at 
    https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check.
        errors: ``str``
            A list of previous errors (used when you're doing multiple checks).

    Returns
    -------
        A ``list`` of errors; else, return the ``dataframe``.
    """
    
    # check if dataframe is provided an argument
    if dataframe is None:
        raise ValueError("Please provide a dataframe")
    
    # get country codes for checking
    country_codes = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wikipedia_country_codes.csv'))

    # column names for easy looping
    column_names = {
        'country': 'Country name',
        'countryCode': 'Code'
    }

    # loop over all variables
    for var in ['continent','country','countryCode','stateProvince','locality']:
        if var in dataframe.columns:
            errors = check_is_string(dataframe=dataframe,column_name=var,errors=errors)
            in_column = any(var in x for x in errors)
            if var == 'continent' and not in_column:
                if not set(continents).issuperset(dataframe[var]):
                    errors.append('Some of your continents are incorrect.  Accepted values are:\n\n{}'.format(', '.join(continents)))
            elif (var == 'country' or var == 'countryCode') and not in_column:
                if not set(country_codes[column_names[var]]).issuperset(dataframe[var]):
                    errors.append('Some of your {} are incorrect.  Accepted values are found on Wikipedia: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2'.format(var))
            
    # return errors
    if errors is not None:
        return errors
    return None