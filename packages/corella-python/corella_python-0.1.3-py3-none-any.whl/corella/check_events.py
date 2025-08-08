from .common_functions import check_is_numeric,check_is_string,check_for_dataframe

def check_events(dataframe=None,
                 errors=[]):
    """
    Checks the following fields:

    - ``eventID``
    - ``parentEventID``
    - ``eventType``
    - ``Event``
    - ``samplingProtocol``

    It will check if all the above fields are either numeric or ``str``    

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
    check_for_dataframe(dataframe=dataframe,func='check_events')

    # check values 
    for item in ['eventID','parentEventID','eventType''Event','samplingProtocol']:
        if item in dataframe.columns:
            if item in ['eventID','parentEventID']:
                temp_errors = check_is_string(dataframe=dataframe,column_name=item,errors=errors)
                if len(temp_errors) > 0:
                    temp_errors2 = check_is_numeric(dataframe=dataframe,column_name=item,errors=errors)
                    if len(temp_errors2) > 0:
                        errors.append('{} column needs to be either a string or numeric.'.format(item))
            else:
                temp_errors = check_is_string(dataframe=dataframe,column_name=item,errors=errors)
                errors += temp_errors
            
    # return errors if there are any; else, return None if everything is ok  
    if errors is not None:
        return errors  
    return None