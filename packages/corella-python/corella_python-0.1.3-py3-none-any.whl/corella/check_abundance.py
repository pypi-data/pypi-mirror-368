from .check_occurrenceStatus import check_occurrenceStatus
from .common_dictionaries import unique_messages
from .common_functions import check_is_numeric,check_is_string,swap_error_message

def check_abundance(dataframe=None,
                    errors=[]):
    """
    Checks the following columns:

    - ``individualCount``
    - ``organismQuantity``
    - ``organismQuantityType``

    For ``individualCount``, it will check if this is a numeric column.  If 
    ``occurrenceStatus`` is in the data, it will check if there are mismatches 
    between the two columns (i.e. if ``individualCount`` is greater than 0, but 
    the ``occurrenceStatus`` is marked as ``absent``.)

    For ``organismQuantity`` and ``organismQuantityType``, it will check if both 
    columns are present and both are strings.

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

    # first, check if individual count is numeric
    if 'individualCount' in dataframe.columns:
        errors = check_is_numeric(dataframe=dataframe,column_name='individualCount',errors=errors)

        # now, do checks for occurrenceStatus
        if 'occurrenceStatus' in dataframe.columns:
            errors_occstatus = check_occurrenceStatus(dataframe=dataframe,errors=errors)
            if type(errors_occstatus) is list:
                errors += errors_occstatus
            if any(dataframe[dataframe['individualCount'] == 0]):
                zeroes = dataframe.loc[dataframe['individualCount'] == 0]
                if not zeroes.empty:
                    wrong_statuses = zeroes[zeroes['occurrenceStatus'].isin(['PRESENT','present'])]
                    if not wrong_statuses.empty:
                        errors.append('Some of your individual counts are 0, yet the occurrence status is set to present.  Please change occurrenceStatus to ABSENT')

    accepted_types = {
        'organismQuantity': [int],
        'organismQuantityType': [str]
    }

    # first, check if both organismQuantity and organismQuantityType are present; if not, add error message
    if any(x in dataframe.columns for x in ['organismQuantity','organismQuantityType']):
        if not set(dataframe.columns).issuperset(['organismQuantity','organismQuantityType']):
            errors.append('You must include both organismQuantity and organismQuantityType.')

        # now, check each individually
        for var in ['organismQuantity','organismQuantityType']:
            if var in dataframe.columns:
                if var == 'organismQuantity':
                    errors = check_is_numeric(dataframe=dataframe,column_name=var,errors=errors)
                else:
                    errors = check_is_string(dataframe=dataframe,column_name=var,errors=errors)
                    errors = swap_error_message(errors=errors,
                                                orig_message='the {} column must be a {}.'.format(var,accepted_types[var]),
                                                new_message=unique_messages[var])
    
    # return errors
    if errors is not None:
        return errors
    return None