from .check_scientificName import check_scientificName
from .common_functions import check_for_dataframe,set_data_workflow

def set_scientific_name(dataframe=None,
                        scientificName=None,
                        taxonRank=None,
                        scientificNameAuthorship=None):
    """
    Checks for the name of the taxon you identified is present.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        scientificName: ``str``
            A column name (``str``) denoting all full scientific names in the lower level taxonomic rank 
            that can be determined.
        taxonRank: ``str``
            A column name (``str``) denoting the taxonomic rank of your scientific 
            names (species, genus etc.)
        scientificNameAuthorship: ``str``
            A column name (``str``) denoting the authorship information for ``scientificName``.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_scientific_name vignette <../../html/corella_user_guide/independent_observations/set_scientific_name.html>`_
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='set_scientific_name')
    
    # mapping of column names and variables
    mapping = {
        'scientificName': scientificName,
        'taxonRank': taxonRank,
        'scientificNameAuthorship': scientificNameAuthorship
    }

    # accepted data formats for each argument
    accepted_formats = {
        'scientificName': [str],
        'taxonRank': [str],
        'scientificNameAuthorship': [str]
    }

    # specify variables and values for set_data_workflow()
    variables = [scientificName,taxonRank,scientificNameAuthorship]
    values = ['scientificName','taxonRank','scientificNameAuthorship']

    # set column names and values specified by user
    dataframe = set_data_workflow(func='set_taxonomy',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)

    # check values
    errors = check_scientificName(dataframe=dataframe)
                    
    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe 