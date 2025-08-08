import pandas as pd

def basisOfRecord_values():
    """
    A ``pandas.Series`` of accepted (but not mandatory) values for ``basisOfRecord`` values.

    Parameters
    ----------
        None

    Returns
    -------
        A ``pandas.Series`` of accepted (but not mandatory) values for ``basisOfRecord`` values..
    
    Examples
    --------

    .. prompt:: python

        >>> corella.basisOfRecord_values()

    .. program-output:: python -c "import corella;print(corella.basisOfRecord_values())"
    """
    return pd.DataFrame({'basisOfRecord values': ["humanObservation",
                                                  "machineObservation",
                                                  "livingSpecimen",
                                                  "preservedSpecimen",
                                                  "fossilSpecimen",
                                                  "materialCitation"]})