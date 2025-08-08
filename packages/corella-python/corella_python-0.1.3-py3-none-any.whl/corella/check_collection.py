from .common_functions import check_is_string
import uuid

def check_collection(dataframe=None,
                     errors=[]):
    """
    Checks whether or not the following columns are present and in the correct format:

    - ``datasetID``
    - ``datasetName``
    - ``catalogNumber``

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
    for item in 'datasetID','datasetName','catalogNumber':
        if item in dataframe.columns:
            if item == 'datasetID':
                other_formats = list(set(type(x) for x in dataframe[item]))
                if len(other_formats) == 1:
                    if (other_formats[0] not in [uuid.UUID,str]):
                        errors.append('the datasetID column must either be a string or a uuid.')
                else:
                    if any(x not in [uuid.UUID,str] for x in other_formats):
                        errors.append('the datasetID column must either be a string or a uuid.')
            else:
                errors = check_is_string(dataframe=dataframe,column_name=item,errors=errors)

    # return either errors or None
    if errors is not None:
        return errors
    return None