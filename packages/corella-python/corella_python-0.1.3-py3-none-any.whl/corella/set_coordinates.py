from .common_dictionaries import GEO_REQUIRED_DWCA_TERMS
from .check_coordinates import check_coordinates
from .common_functions import check_for_dataframe,set_data_workflow

def set_coordinates(dataframe=None,
                    decimalLatitude=None,
                    decimalLongitude=None,
                    geodeticDatum=None,
                    coordinateUncertaintyInMeters=None,
                    coordinatePrecision=None):
    """
    Checks for location information, as well as uncertainty and coordinate reference system.  
    Also runs data checks on coordinate validity.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        decimalLatitude: ``str``
            A column name that contains your latitudes (units in degrees).
        decimalLongitude: ``str``
            A column name that contains your longitudes (units in degrees).
        geodeticDatum: ``str`` 
            A column name or a ``str`` with he datum or spatial reference system 
            that coordinates are recorded against (usually "WGS84" or "EPSG:4326"). 
            This is often known as the Coordinate Reference System (CRS). If your 
            coordinates are from a GPS system, your data are already using WGS84.
        coordinateUncertaintyInMeters: ``str``, ``float`` or ``int`` 
            A column name (``str``) or a ``float``/``int`` with the value of the 
            coordinate uncertainty. ``coordinateUncertaintyInMeters`` will typically 
            be around ``30`` (metres) if recorded with a GPS after 2000, or ``100`` 
            before that year.
        coordinatePrecision: ``str``, ``float`` or ``int``
            Either a column name (``str``) or a ``float``/``int`` with the value of the 
            coordinate precision. ``coordinatePrecision`` should be no less than 
            ``0.00001`` if data were collected using GPS.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_coordinates vignette <../../html/corella_user_guide/independent_observations/set_coordinates.html>`_
    """

    # raise a ValueError if no dataframe is provided
    check_for_dataframe(dataframe=dataframe,func='set_coordinates')

    # mapping of column names and variables
    mapping = {
        'decimalLatitude': decimalLatitude,
        'decimalLongitude': decimalLongitude, 
        'geodeticDatum': geodeticDatum,
        'coordinatePrecision': coordinatePrecision,
        'coordinateUncertaintyInMeters': coordinateUncertaintyInMeters
    }

    # accepted data formats for each argument
    accepted_formats = {
        'decimalLatitude': [float],
        'decimalLongitude': [float], 
        'geodeticDatum': [str],
        'coordinatePrecision': [float,int],
        'coordinateUncertaintyInMeters': [float,int]
    }

    # specify variables and values for set_data_workflow()
    variables = [decimalLatitude,decimalLongitude,geodeticDatum,coordinatePrecision,coordinateUncertaintyInMeters]
    values = ['decimalLatitude','decimalLongitude','geodeticDatum','coordinatePrecision','coordinateUncertaintyInMeters']

    # set column names and values specified by user
    dataframe = set_data_workflow(func='set_coordinates',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)

    # check all required variables
    errors = check_coordinates(dataframe=dataframe,errors=[])

    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe