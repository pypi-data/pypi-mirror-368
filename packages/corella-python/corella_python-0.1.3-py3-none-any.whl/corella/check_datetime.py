import datetime
from .common_functions import check_is_datetime,check_is_numeric,check_for_dataframe

def check_datetime(dataframe=None,
                   errors=[]):
    """
    Checks the following fields:

    - ``eventDate``
    - ``year``
    - ``month``
    - ``day``
    - ``eventTime``

    It will check if all the above fields (except ``geodeticDatum``) are either 
    numeric or ``datetime`` objects.    

    It will also check if all column values are valid (i.e. there's no 13th month, 
    25th hour etc.)

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
    check_for_dataframe(dataframe=dataframe,func='check_datetime')

    # first, raise an error if there is not an eventDate column
    if 'eventDate' not in dataframe.columns:
        errors.append('eventDate is a required field. Please ensure it is in your dataframe')

    # accepted ranges for dates and times
    ranges_datetimes = {
        'eventDate': [datetime.datetime.fromtimestamp(0),datetime.datetime.now()],
        'year': [0,datetime.datetime.now().year],
        'month': [1,12],
        'day': [1,31],
        'eventTime': [datetime.time(0,0,0),datetime.time(23,59,59)]
    }

    # check values 
    for var in ranges_datetimes.keys():

        # check if in columns
        if var in dataframe.columns:

            # check type of variable first
            if var in ['eventDate','eventTime']:
                errors = check_is_datetime(dataframe=dataframe,column_name=var,errors=errors)
            else:
                errors = check_is_numeric(dataframe=dataframe,column_name=var,errors=errors)
            
            # if the data type in column is correct, see if there are invalid values
            if not any(var in x for x in errors):
                valid_count = dataframe[var].between(ranges_datetimes[var][0], ranges_datetimes[var][1], inclusive='both').sum()
                if valid_count < len(dataframe[var]):
                    errors.append("There are some invalid {} values.  They should be between {} and {}.".format(var,ranges_datetimes[var][0],ranges_datetimes[var][1]))

    # return errors if there are any; else, return None if everything is ok  
    if errors is not None:
        return errors  
    return None