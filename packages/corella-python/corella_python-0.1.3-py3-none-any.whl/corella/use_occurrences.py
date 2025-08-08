from .add_eventID_occurrences import add_eventID_occurrences
from .add_unique_IDs import add_unique_IDs
from .check_occurrences import check_occurrences
from .common_functions import check_for_dataframe,check_if_all_args_empty,check_all_columns_values

def use_occurrences(dataframe=None,
                    occurrenceID=None,
                    catalogNumber=None,
                    recordNumber=None,
                    basisOfRecord=None,
                    occurrenceStatus=None,
                    errors=[],
                    add_eventID=False,
                    events=None,
                    eventType=None):
    """
    Checks for unique identifiers of each occurrence and how the occurrence was recorded.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        occurrenceID: ``str`` or ``bool``
            Either a column name (``str``) or ``True`` (``bool``).  If a column name is 
            provided, the column will be renamed.  If ``True`` is provided, unique identifiers
            will be generated in the dataset.
        catalogNumber: ``str`` or ``bool``
            Either a column name (``str``) or ``True`` (``bool``).  If a column name is 
            provided, the column will be renamed.  If ``True`` is provided, unique identifiers
            will be generated in the dataset.
        recordNumber: ``str`` or ``bool``
            Either a column name (``str``) or ``True`` (``bool``).  If a column name is 
            provided, the column will be renamed.  If ``True`` is provided, unique identifiers
            will be generated in the dataset.
        basisOfRecord: ``str``
            Either a column name (``str``) or a valid value for ``basisOfRecord`` to add to 
            the dataset.
        occurrenceStatus: ``str``
            Either a column name (``str``) or a valid value for ``occurrenceStatus`` to add to 
            the dataset.
        errors: ``list``
            ONLY FOR DEBUGGING: existing list of errors.
        add_eventID: ``logic``
            Either a column name (``str``) or a valid value for ``occurrenceStatus`` to add to 
            the dataset.
        events: ``pd.DataFrame``
            Dataframe containing your events.
        eventType: ``str``
            Either a column name (``str``) or a valid value for ``eventType`` to add to 
            the dataset.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='use_occurrences')
    
    # check for events for adding event ID
    if add_eventID:
        check_for_dataframe(dataframe=events,func='use_occurrences')

    # column renaming dictionary
    mapping = {
        occurrenceID: 'occurrenceID',
        catalogNumber: 'catalogNumber',
        recordNumber: 'recordNumber',
        basisOfRecord: 'basisOfRecord',
        occurrenceStatus: 'occurrenceStatus'
    }

    accepted_formats = {
        occurrenceID: [str,bool], #uuid.UUID
        catalogNumber: [str],
        recordNumber: [str],
        basisOfRecord: [str],
        occurrenceStatus: [str]
    }

    values = ['occurrenceID','catalogNumber','recordNumber','basisOfRecord','occurrenceStatus']

    # check if all arguments are empty
    check_if_all_args_empty(dataframe=dataframe,func='use_occurrences',keys=mapping.keys(),values=values)

    # check column names and values
    dataframe,mapping = check_all_columns_values(dataframe=dataframe,mapping=mapping,accepted_formats=accepted_formats)

    # rename all necessary columns
    dataframe = dataframe.rename(columns=mapping)
    
    # check if unique occurrence IDs need to be added
    if (type(occurrenceID) is bool):
        dataframe = add_unique_IDs(column_name='occurrenceID',dataframe=dataframe)

    if type(add_eventID) is bool and add_eventID:
        dataframe = add_eventID_occurrences(occurrences=dataframe,events=events,eventType=eventType)

    # check data
    errors = check_occurrences(dataframe=dataframe,errors=[])
    
    # return errors if there are any; otherwise, 
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe