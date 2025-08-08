from .common_functions import check_for_dataframe,set_data_workflow
from .check_taxonomy import check_taxonomy

def set_taxonomy(dataframe=None,
                 kingdom=None,
                 phylum=None,
                 taxon_class=None, 
                 order=None,
                 family=None,
                 genus=None,
                 specificEpithet=None,
                 vernacularName=None):
    """
    Adds extra taxonomic information.  Also runs checks on whether or not the names are the 
    correct data type.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        kingdom: ``str``,``list``
            A column name, kingdom name (``str``) or list of kingdom names (``list``).
        phylum: ``str``,``list``
            A column name, phylum name (``str``) or list of phylum names (``list``).
        taxon_class: ``str``,``list``
            A column name, class name (``str``) or list of class names (``list``).
        order: ``str``,``list``
            A column name, order name (``str``) or list of order names (``list``).
        family: ``str``,``list``
            A column name, family name (``str``) or list of family names (``list``).
        genus: ``str``,``list``
            A column name, genus name (``str``) or list of genus names (``list``).
        specificEpithet: ``str``,``list``
            A column name, specificEpithet name (``str``) or list of specificEpithet names (``list``).
            **Note**: If ``scientificName`` is *Abies concolor*, the ``specificEpithet`` is *concolor*.
        vernacularName: ``str``,``list``
            A column name, vernacularName name (``str``) or list of vernacularName names (``list``).

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_taxonomy vignette <../../html/corella_user_guide/independent_observations/set_taxonomy.html>`_
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='set_taxonomy')
    
    # specify variables and values for set_data_workflow()
    variables = [kingdom,phylum,taxon_class,order,family,genus,specificEpithet,vernacularName]
    values = ['kingdom','phylum','class','order','family','genus','specificEpithet','vernacularName']
    
    # mapping of column names and variables
    mapping = dict(zip(values,variables))
    
    # accepted data formats for each argument
    accepted_formats = {x:[str,list] for x in values}
    
    # set variables
    dataframe = set_data_workflow(func='set_taxonomy',dataframe=dataframe,variables=variables,
                                  mapping=mapping,values=values,accepted_formats=accepted_formats)

    # check values
    errors = check_taxonomy(dataframe=dataframe)

    # return errors if there are any; otherwise, 
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe