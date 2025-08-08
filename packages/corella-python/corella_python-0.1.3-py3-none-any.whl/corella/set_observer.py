from .check_observer import check_observer
from .common_functions import check_for_dataframe,set_data_workflow

def set_observer(dataframe=None,
                 recordedBy=None,
                 recordedByID=None):
    """
    Checks for the name of the taxon you identified is present.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        recordedBy: ``str``
            A column name or name(s) of people, groups, or organizations responsible 
            for recording the original occurrence. The primary collector or observer should be 
            listed first.
        recordedByID: ``str``
            A column name or the globally unique identifier for the person, people, groups, or organizations 
            responsible for recording the original occurrence.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_observer vignette <../../html/corella_user_guide/independent_observations/set_observer.html>`_
    """
    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='set_scientific_name')
    
    # mapping of column names and variables
    mapping = {
        'recordedBy': recordedBy,
        'recordedByID': recordedByID,
    }

    # accepted data formats for each argument
    accepted_formats = {
        'recordedBy': [str],
        'recordedByID': [str],
    }

    # specify variables and values for set_data_workflow()
    variables = [recordedBy,recordedByID]
    values = ['recordedBy','recordedByID']

    # set column names and values specified by user
    dataframe = set_data_workflow(func='set_taxonomy',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)

    # check values
    errors = check_observer(dataframe=dataframe)
                    
    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe 