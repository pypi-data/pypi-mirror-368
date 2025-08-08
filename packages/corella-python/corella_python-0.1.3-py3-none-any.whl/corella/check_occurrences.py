from .check_basisOfRecord import check_basisOfRecord
from .check_occurrenceIDs import check_occurrenceIDs
from .check_occurrenceStatus import check_occurrenceStatus

def check_occurrences(dataframe=None,
                      errors=[]):
    """
    This is meant to check your occurrence data for a few data columns:

    - ``basisOfRecord``
    - ``occurrenceID`` or ``catalogNumber`` or ``recordNumber``
    - ``occurrenceStatus``

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

    # first, check basisOfRecord for errors
    errors_bor = check_basisOfRecord(dataframe=dataframe,errors=[])
    if type(errors_bor) is list:
        errors += errors_bor

    # then, occurrenceIDs
    errors_occID = check_occurrenceIDs(dataframe=dataframe,errors=[])
    if type(errors_occID) is list:
        errors += errors_occID
    
    # then, abundance
    errors_status = check_occurrenceStatus(dataframe=dataframe,errors=[])
    if type(errors_status) is list:
        errors += errors_status

    # return any errors
    return errors