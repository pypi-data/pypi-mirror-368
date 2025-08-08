from .check_abundance import check_abundance
from .common_functions import check_for_dataframe,set_data_workflow

def set_abundance(dataframe=None,
                  individualCount=None,
                  organismQuantity=None,
                  organismQuantityType=None):
    """
    Checks for location information, as well as uncertainty and coordinate reference system.  
    Also runs data checks on coordinate validity.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        individualCount: ``str``
            A column name that contains your individual counts (should be whole numbers).
        organismQuantity: ``str``
            A column name that contains a number or enumeration value for the quantity of organisms.  
            Used together with ``organismQuantityType`` to provide context.
        organismQuantityType: ``str`` 
            A column name or phrase denoting the type of quantification system used for ``organismQuantity``.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_abundance vignette <../../html/corella_user_guide/independent_observations/set_abundance.html>`_
    """

    # raise a ValueError if no dataframe is provided
    check_for_dataframe(dataframe=dataframe,func='set_abundance')
    
    # column renaming dictionary
    mapping = {
        'individualCount': individualCount ,
        'organismQuantity': organismQuantity,
        'organismQuantityType': organismQuantityType,
    }

    # denote accepted formats
    accepted_formats = {
        'individualCount': [int,float,list],
        'organismQuantity': [int,float,list],
        'organismQuantityType': [str,list],
    }

    # manually set values for function
    variables = [individualCount,organismQuantity,organismQuantityType]
    values = ['individualCount','organismQuantity','organismQuantityType']

    # set all values in dataframe
    dataframe = set_data_workflow(func='set_abundance',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)

    # check errors in data
    errors = check_abundance(dataframe=dataframe,errors=[])
    
    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe