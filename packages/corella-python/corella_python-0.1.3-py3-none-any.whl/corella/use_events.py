import pandas as pd
from .check_events import check_events
from .common_functions import check_for_dataframe,check_if_all_args_empty,check_all_columns_values
from .generate_eventID_parentEventID import generate_eventID_parentEventID

def use_events(dataframe=None,
               eventID=None,
               parentEventID=None,
               eventType=None,
               Event=None,
               samplingProtocol=None,
               event_hierarchy=None):
    """
    Checks for event-specific information, such as how the data was collected, what type of 
    event it was, and names of events.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        eventID: ``str``
            A column name (``str``) that contains a unique ID for your event.
        parentEventID: ``str``
            A column name (``str``) that contains a unique ID belonging to an event below 
            it in the event hierarchy.
        eventType: ``str`` 
            A column name (``str``) or a ``str`` denoting what type of event you have.
        Event: ``str`` 
            A column name (``str``) or a ``str`` denoting the name of the event.
        samplingProtocol: ``str`` or 
            Either a column name (``str``) or a ``str`` denoting how you collected the data, 
            i.e. "Human Observation".
        event_hierarchy: ``dict``
            A dictionary containing a hierarchy of all events so they can be linked.  For example, 
            if you have a set of observations that were taken at a particular site, you can use the 
            dict {1: "Site Visit", 2: "Sample", 3: "Observation"}.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.
    """
    
    # first, check for data frame
    check_for_dataframe(dataframe=dataframe,func='use_events')

    # mapping column names
    mapping = {
        eventID: 'eventID',
        parentEventID: 'parentEventID', 
        eventType: 'eventType',
        Event: 'Event',
        samplingProtocol: 'samplingProtocol'
    }

    # accepted formats for inputs
    accepted_formats = {
        eventID: [str,bool],
        parentEventID: [str,bool], 
        eventType: [str],
        Event: [str],
        samplingProtocol: [str]
    }

    values = ['eventID','parentEventID','eventType','Event','samplingProtocol']

    # check if all arguments are empty
    check_if_all_args_empty(dataframe=dataframe,func='use_events',keys=mapping.keys(),values=values)
    
    # check all columns and values
    dataframe,mapping = check_all_columns_values(dataframe=dataframe,mapping=mapping,accepted_formats=accepted_formats)

    # rename all necessary columns
    dataframe = dataframe.rename(columns=mapping)

    # check for event_hierarchy
    if type(eventID) is bool:
        if parentEventID is None:
            print("parentEventID has not been provided, but will automatically be generated.")
            dataframe = generate_eventID_parentEventID(dataframe=dataframe,event_hierarchy=event_hierarchy)
        elif parentEventID in mapping:
            raise ValueError("a parentEventID column has been provided, but eventID has not. Please provide your eventID column.")
    elif not set(dataframe.columns).issuperset({'eventID','parentEventID'}) and event_hierarchy is None:
        raise ValueError("Please provide column names for eventID and parentEventID.  Or, provide an event_hierarchy dictionary for automatic ID generation.")
    elif event_hierarchy is not None and not set(dataframe.columns).issuperset({'eventID','parentEventID'}):
        dataframe=generate_eventID_parentEventID(dataframe=dataframe,event_hierarchy=event_hierarchy)
    else:
        pass

    # check for errors
    errors = check_events(dataframe=dataframe,errors=[])
    
    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe