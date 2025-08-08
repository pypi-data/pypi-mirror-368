from .common_functions import check_is_numeric,check_is_string,check_for_dataframe
from .common_dictionaries import GEO_REQUIRED_DWCA_TERMS
from pandas.api.types import is_numeric_dtype

def check_coordinates(dataframe=None,
                      errors=[]):
    """
    Checks the following fields:

    - ``decimalLatitude``
    - ``decimalLongitude``
    - ``geodeticDatum``
    - ``coordinateUncertaintyInMeters``
    - ``coordinatePrecision``

    It will check if all the above fields (except ``geodeticDatum``) are numeric.  
    It will also check if ``geodeticDatum`` is a string.  

    For ``decimalLatitude`` and ``decimalLongitude``, it will check if they are 
    between -90 and 90, and between -180 and 180, respectively.  It will then 
    check if ``coordinateUncertaintyInMeters`` and ``coordinatePrecision`` are 
    above 0.

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

    # First, check if a dataframe is provided
    check_for_dataframe(dataframe=dataframe,func='check_coordinates')
    
    # required terms
    terms_to_check = GEO_REQUIRED_DWCA_TERMS["Australia"] + ['coordinatePrecision','coordinateUncertaintyInMeters']

    # check data types for location data
    for c in terms_to_check:
        if c in dataframe.columns:
            
            # first, check for numeric columns
            if c in ['decimalLatitude','decimalLongitude','coordinatePrecision','coordinateUncertaintyInMeters']:
                errors = check_is_numeric(dataframe=dataframe,column_name=c,errors=errors)

            # then, check for string columns
            if c == 'geodeticDatum': 
                errors = check_is_string(dataframe=dataframe,column_name=c,errors=errors)
                
    # set ranges for easy looping
    ranges = {
        'decimalLatitude': [-90,90],
        'decimalLongitude': [-180,180]
    }

    # check for both lat and long
    if not all(x in dataframe.columns for x in ['decimalLatitude','decimalLongitude']):
        errors.append('You need to provide both decimalLatitude and decimalLongitude')

    # check if there were errors for decimalLatitude and decimalLongitude
    if not any(x in errors for x in ['decimalLatitude','decimalLongitude','coordinateUncertaintyInMeters','coordinatePrecision']):

        # check range of lat/long are correct
        for var in ['decimalLatitude','decimalLongitude','coordinateUncertaintyInMeters','coordinatePrecision']:

            # check for any entries that aren't valid
            if var in dataframe.columns and is_numeric_dtype(dataframe[var]):

                if var in ['decimalLatitude','decimalLongitude']:
                    valid_count = dataframe[var].astype(float).between(ranges[var][0], ranges[var][1], inclusive='both').sum()
                    if valid_count < len(dataframe[var]):
                        errors.append("There are some invalid {} values.  They should be between {} and {}.".format(var,ranges[var][0],ranges[var][1]))
          
                else:
                    valid_count_df = dataframe[var] > 0
                    valid_count = valid_count_df.sum()

                    # return errors
                    if valid_count < len(dataframe[var]):
                        errors.append("There are some invalid {} values.  They should be above 0.".format(var))
          
    # return errors
    if errors is not None:
        return errors
    return None
