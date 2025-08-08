from .common_functions import check_for_dataframe,set_data_workflow
from .check_individual_traits import check_individual_traits
import uuid

def set_individual_traits(dataframe=None,
                          individualID=None,
                          lifeStage=None,
                          sex=None,
                          vitality=None,
                          reproductiveCondition=None):
    """
    Checks for location information, as well as uncertainty and coordinate reference system.  
    Also runs data checks on coordinate validity.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        individualID: ``str``
            A column name containing an identifier for an individual or named group of 
            individual organisms represented in the Occurrence. Meant to accommodate 
            resampling of the same individual or group for monitoring purposes. May be 
            a global unique identifier or an identifier specific to a data set.
        lifeStage: ``str``
            A column name containing the age, class or life stage of an organism at the time of occurrence.
        sex: ``str`` 
            A column name or value denoting the sex of the biological individual.
        vitality: ``str``
            A column name or value denoting whether an organism was alive or dead at the time of collection or observation.
        reproductiveCondition: ``str``
            A column name or value denoting the reproductive condition of the biological individual.
        
    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_individual_traits vignette <../../html/corella_user_guide/independent_observations/set_individual_traits.html>`_
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='set_individual_traits')

    # mapping of column names and variables
    mapping = {
        'individualID': individualID,
        'lifeStage': lifeStage,
        'sex': sex,
        'vitality': vitality,
        'reproductiveCondition': reproductiveCondition,
    }

    # accepted data formats for each argument
    accepted_formats = {
        'individualID': [uuid.UUID,str,list],
        'lifeStage': [str,list],
        'sex': [str,list],
        'vitality': [str,list],
        'reproductiveCondition': [str,list],
    }

    # specify variables and values for set_data_workflow()
    variables = [individualID,lifeStage,sex,vitality,reproductiveCondition]
    values = ['individualID','lifeStage','sex','vitality','reproductiveCondition']

    # set column names and values specified by user
    dataframe = set_data_workflow(func='set_individual_traits',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)
    
    # check values
    errors = check_individual_traits(dataframe=dataframe,errors=[])

    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe