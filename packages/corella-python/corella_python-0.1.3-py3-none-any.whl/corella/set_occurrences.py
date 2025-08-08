from .add_eventID_occurrences import add_eventID_occurrences
from .add_unique_IDs import add_unique_IDs
from .check_occurrences import check_occurrences
from .common_functions import check_for_dataframe,set_data_workflow

def set_occurrences(dataframe=None,
                    occurrenceID=None,
                    catalogNumber=None,
                    recordNumber=None,
                    basisOfRecord=None,
                    sep='-',
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
        occurrenceID: ``str``, ``bool`` or ``list``
            You can provide 3 types of arguments to ``occurrenceID``:
            - ``str``: rename the column of interest to ``occurrenceID``
            - ``bool``: generate random UUIDs
            - ``list``: generate composite ids.  If you want either sequential numbers or 
                        random UUIDs added, use the keywords ``"sequential"`` or ``"random"``
                        to your 
            *Note*: Every occurrence should have an occurrenceID entry. Ideally, IDs should be 
            persistent to avoid being lost in future updates. They should also be unique, both within 
            the dataset, and (ideally) across all other datasets.
        catalogNumber: ``str`` or ``bool``
            See ``occurrenceID``
        recordNumber: ``str`` or ``bool``
            See ``occurrenceID``
        sep: ``char``
            Separation character for composite IDs.  Default is ``-``.
        basisOfRecord: ``str``
            Either a column name (``str``) or a valid value for ``basisOfRecord`` to add to 
            the dataset.  For values of ``basisOfRecord``, it only accepts ``camelCase``, for consistency with field 
            ``"humanObservation"``, ``"machineObservation"``, ``"livingSpecimen"``, ``"preservedSpecimen"``, ``"fossilSpecimen"``, ``"materialCitation"``
        occurrenceStatus: ``str``
            Either a column name (``str``) or a valid value for ``occurrenceStatus`` to add to 
            the dataset.  Valid values are ``"present"`` or ``"absent"``
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

    Examples
    ----------
        `set_occurrences vignette <../../html/corella_user_guide/independent_observations/set_occurrences.html>`_
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='set_occurrences')
    
    # check for events for adding event ID
    if add_eventID:
        check_for_dataframe(dataframe=events,func='set_occurrences')

    # mapping of column names and variables
    mapping = {
        'occurrenceID': occurrenceID,
        'catalogNumber': catalogNumber,
        'recordNumber': recordNumber,
        'basisOfRecord': basisOfRecord,
        'occurrenceStatus': occurrenceStatus
    }

    # accepted data formats for each argument
    accepted_formats = {
        'occurrenceID': [str,list,bool],
        'catalogNumber': [str],
        'recordNumber': [str],
        'basisOfRecord': [str],
        'occurrenceStatus': [str]
    }

    # specify variables and values for set_data_workflow()
    variables = [occurrenceID,catalogNumber,recordNumber,basisOfRecord,occurrenceStatus]
    values = ['occurrenceID','catalogNumber','recordNumber','basisOfRecord','occurrenceStatus']

    # if user wants a random or sequential ID
    for id in ['occurrenceID','catalogNumber','recordNumber']:
        if type(mapping[id]) is str or type(mapping[id]) is list:
            if mapping[id] in ['random','sequential'] or any(x in ['random','sequential'] for x in mapping[id]):
                values.remove(id)
                variables.remove(mapping[id])
                del mapping[id]
                del accepted_formats[id]

    if any(x in ['random','sequential'] for x in [occurrenceID,catalogNumber,recordNumber]):
        if not all(mapping[x] is None for x in mapping):
            # set column names and values specified by user
            dataframe = set_data_workflow(func='set_occurrences',dataframe=dataframe,mapping=mapping,variables=variables,
                                          values=values,accepted_formats=accepted_formats)
    else:
        dataframe = set_data_workflow(func='set_occurrences',dataframe=dataframe,mapping=mapping,variables=variables,
                                      values=values,accepted_formats=accepted_formats)

    # check if unique occurrence IDs need to be added
    if (type(occurrenceID) in [str,bool,list] and 'occurrenceID' not in dataframe.columns): 
        dataframe = add_unique_IDs(column_name='occurrenceID',sep=sep,column_info=occurrenceID,
                                   dataframe=dataframe)
    if (type(catalogNumber) in [str,bool,list] and 'catalogNumber' not in dataframe.columns): 
        dataframe = add_unique_IDs(column_name='catalogNumber',sep=sep,column_info=catalogNumber,
                                   dataframe=dataframe)
    if (type(recordNumber)  in [str,bool,list] and 'recordNumber' not in dataframe.columns): 
        dataframe = add_unique_IDs(column_name='recordNumber',sep=sep,column_info=recordNumber,
                                   dataframe=dataframe)
        
    # check if we are adding eventID to occurrences
    if type(add_eventID) is bool and add_eventID:
        dataframe = add_eventID_occurrences(occurrences=dataframe,events=events,eventType=eventType)
        
    # check data
    errors = check_occurrences(dataframe=dataframe,errors=[])
    
    # return errors if there are any; otherwise, 
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe