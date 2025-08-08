from .check_license import check_license
from .common_functions import check_for_dataframe,set_data_workflow

def set_license(dataframe=None,
                license=None,
                rightsHolder=None,
                accessRights=None):
    """
    Checks for location information, as well as uncertainty and coordinate reference system.  
    Also runs data checks on coordinate validity.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        license: ``str``
            A column name or value denoting a legal document giving official 
            permission to do something with the resource. Must be provided as a 
            url to a valid license.
        rightsHolder: ``str``
            A column name or value denoting the person or organisation owning or 
            managing rights to resource.
        accessRights: ``str``
            A column name or value denoting any access or restrictions based on 
            privacy or security.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_license vignette <../../html/corella_user_guide/independent_observations/set_license.html>`_
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='set_license')
    
    # mapping of column names and variables
    mapping = {
        'license': license ,
        'rightsHolder': rightsHolder,
        'accessRights': accessRights,
    }

    # accepted data formats for each argument
    accepted_formats = {
        'license': [str,list],
        'rightsHolder': [str,list],
        'accessRights': [str,list],
    }

    # specify variables and values for set_data_workflow()
    variables = [license,rightsHolder,accessRights]
    values = ['license','rightsHolder','accessRights']

    # set column names and values specified by user
    dataframe = set_data_workflow(func='set_license',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)

    # check values
    errors = check_license(dataframe=dataframe,errors=[])
    
    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe