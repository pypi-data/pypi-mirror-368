import pandas as pd
import os

def countryCode_values():
    """
    A ``pandas.Series`` of accepted (but not mandatory) values for ``countryCode`` values.

    Parameters
    ----------
        None

    Returns
    -------
        A ``pandas.Series`` of accepted (but not mandatory) values for ``countryCode`` values..
    
    Examples
    --------

    .. prompt:: python

        >>> corella.countryCode_values()

    .. program-output:: python -c "import corella;print(corella.countryCode_values())"
    """

    codes = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wikipedia_country_codes.csv')
    ccs = pd.read_csv(codes)
    return ccs['Code']