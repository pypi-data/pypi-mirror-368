from .common_functions import check_is_string

def check_taxonomy(dataframe=None,
                   errors=[]):
    """
    Checks whether or not the following columns are in string format:

    - ``kingdom``
    - ``phylum``
    - ``class``
    - ``order``
    - ``family``
    - ``genus``
    - ``specificEpithet``
    - ``vernacularName``

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

    # check the type of variable for all scientific name associated variables
    for item in ['kingdom','phylum','class','order','family','genus','specificEpithet','vernacularName']:
        if item in dataframe.columns:
            errors = check_is_string(dataframe=dataframe,column_name=item,errors=errors)

    # return either errors or None
    if errors is not None:
        return errors
    return None