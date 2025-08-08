import pandas as pd
from .add_unique_IDs import add_unique_IDs
from .common_functions import check_for_dataframe

def generate_eventID_parentEventID(dataframe=None,
                                   event_hierarchy=None,
                                   sep='-',
                                   eventID='random'):
    # first, check for dataframe
    check_for_dataframe(dataframe=dataframe,func='generate_eventID_parentEventID')

    # then, check for event hierarchy
    if event_hierarchy is None:
        raise ValueError('Please provide an event_hierarchy to use_events.')
    
    if 'eventType' not in dataframe.columns:
        raise ValueError("Please ensure that you have an eventType column so the event hierarchy can correctly be assigned.")
    
    # now, generate all events in the event hierarchy
    new_dataframe = pd.DataFrame()
    for i,row in dataframe.iterrows():
        temp_df = pd.concat([dataframe.iloc[[i]]]*3,ignore_index=True)
        for key in event_hierarchy.keys():
            if 0 not in event_hierarchy.keys():
                temp_df.at[key-1,'eventType'] = event_hierarchy[key]
            else:
                temp_df.at[key,'eventType'] = event_hierarchy[key]
        new_dataframe=pd.concat([new_dataframe,temp_df],ignore_index=True)

    # after generating all events, generate all eventIDs
    new_dataframe = add_unique_IDs(dataframe=new_dataframe,column_name='eventID',
                                   column_info=eventID,sep=sep)
    
    # now, link all events together via the parentEventID column
    new_dataframe.insert(1,'parentEventID',['' for i in list(range(new_dataframe.shape[0]))])
    for i,row in new_dataframe.iterrows():
        if i == 0 or i % len(event_hierarchy.keys()) == 0:
            pass
        else:
            new_dataframe.at[i,'parentEventID'] = new_dataframe.loc[i-1]['eventID']

    # return dataframe
    return new_dataframe