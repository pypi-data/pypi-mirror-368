from .check_scientificName import check_scientificName
from .common_functions import check_for_dataframe,check_if_all_args_empty,check_all_columns_values

def use_scientific_name(dataframe=None,
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
            A column name (``str``) denoting all your scientific names.
        taxonRank: ``str``
            A column name (``str``) denoting the rank of your scientific names (species, genus etc.)
        scientificNameAuthorship: ``str``
            A column name (``str``) denoting who originated the scientific name.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='use_scientific_name')
    
    mapping = {
        scientificName: 'scientificName',
        taxonRank: 'taxonRank',
        scientificNameAuthorship: 'scientificNameAuthorship'
    }

    accepted_formats = {
        scientificName: [str],
        taxonRank: [str],
        scientificNameAuthorship: [str]
    }

    values = ['scientificName','taxonRank','scientificNameAuthorship']

    # check if all args are empty
    check_if_all_args_empty(dataframe=dataframe,func='use_scientific_name',keys=mapping.keys(),values=values)

    # check column names and values
    dataframe,mapping = check_all_columns_values(dataframe=dataframe,mapping=mapping,accepted_formats=accepted_formats)

    # rename all necessary columns
    dataframe = dataframe.rename(columns=mapping)

    # check values
    errors = check_scientificName(dataframe=dataframe)
                    
    # return errors if there are any; otherwise, 
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe 