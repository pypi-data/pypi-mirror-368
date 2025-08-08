from .common_functions import get_bor_values,check_is_string,check_for_dataframe

def check_basisOfRecord(dataframe=None,
                        errors=[]):
    """
    Checks whether or not your ``basisOfRecord`` column values are valid.

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
    check_for_dataframe(dataframe=dataframe,func='check_basisOfRecord')

    # check basisOfRecord values
    if 'basisOfRecord' in dataframe.columns:
        errors = check_is_string(dataframe=dataframe,column_name='basisOfRecord',errors=errors)
        terms = get_bor_values()
        if not set(terms).issuperset(set(dataframe['basisOfRecord'])):
            errors.append("There are invalid basisOfRecord values.  Valid values are {}".format(', '.join(terms)))

    # return errors or None if no errors
    if len(errors) > 0:
        return errors
    return dataframe