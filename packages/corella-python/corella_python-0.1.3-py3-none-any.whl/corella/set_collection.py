from .common_functions import check_for_dataframe,set_data_workflow
from .check_collection import check_collection
import uuid

def set_collection(dataframe=None,
                   datasetID=None,
                   datasetName=None,
                   catalogNumber=None):
    """
    Checks for location information, as well as uncertainty and coordinate reference system.  
    Also runs data checks on coordinate validity.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        datasetID: ``str``
            A column name or other string denoting the identifier for the set of data. May be a global unique 
            identifier or an identifier specific to a collection or institution.
        datasetName: ``str``
            A column name or other string identifying the data set from which the record was derived.
        catalogNumber: ``str`` 
            A column name or other string denoting a unique identifier for the record within the data set or collection.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_collection vignette <../../html/corella_user_guide/independent_observations/set_collection.html>`_
    """
    
    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='set_collection')
    
    # mapping of column names and variables
    mapping = {
        'datasetID': datasetID ,
        'datasetName': datasetName,
        'catalogNumber': catalogNumber,
    }

    # accepted data formats for each argument
    accepted_formats = {
        'datasetID': [type(uuid.uuid4()),str,list],
        'datasetName': [str,list],
        'catalogNumber': [str,list],
    }

    # specify variables and values for set_data_workflow()
    variables = [datasetID,datasetName,catalogNumber]
    values = ['datasetID','datasetName','catalogNumber']

    # set column names and values specified by user
    dataframe = set_data_workflow(func='set_collection',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)
    
    # check values
    errors = check_collection(dataframe=dataframe,errors=[])

    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe