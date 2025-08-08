from .common_functions import check_is_string,check_for_dataframe

def check_occurrenceStatus(dataframe=None,
                           errors=[]):
    """
    Checks whether or not you have valid values for the ``occurrenceStatus`` 
    column, which are ``PRESENT``, ``ABSENT``, ``present``, ``absent``.

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
    check_for_dataframe(dataframe=dataframe,func='check_occurrenceStatus')
    
    # check basisOfRecord values
    if 'occurrenceStatus' in dataframe.columns:
        errors = check_is_string(dataframe=dataframe,column_name='occurrenceStatus',errors=errors)
        terms = ['PRESENT','ABSENT','present','absent']
        if not all(x in terms for x in dataframe['occurrenceStatus']):
            errors.append("There are invalid occurrenceStatus values.  Valid values are {}".format(', '.join(terms)))
    
    # return errors or None if no errors
    if len(errors) > 0:
        return errors
    return dataframe