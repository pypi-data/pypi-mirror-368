import datetime
import pandas as pd
from .check_datetime import check_datetime
from .common_functions import check_for_dataframe,set_data_workflow

def set_datetime(dataframe=None,
                 eventDate=None,
                 year=None,
                 month=None,
                 day=None,
                 eventTime=None,
                 string_to_datetime=False,
                 yearfirst=True,
                 dayfirst=False,
                 time_format='%H:%m:%S'):
    """
    Checks for time information, such as the date an occurrence occurred.  Also runs checks 
    on the validity of the format of the date.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check
        eventDate: ``str``
            A column name or value with the date or date + time of the observation/event.
        year: ``str`` or ``int``
            A column name or value with the year the observation/event.
        month: ``str`` or ``int``
            A column name or value with the month the observation/event.
        day: ``str`` or ``int``
            A column name or value with the day the observation/event.
        eventTime: ``str``
            A column name or value with the time the observation/event.  Date + time information 
            for observations is accepted in ``eventDate``.
        string_to_datetime: ``logical``
            An argument that tells ``corella`` to convert dates that are in a string format to a ``datetime`` 
            format.  Default is ``False``.
        yearfirst: ``logical``
            An argument to specify whether or not the day is first when converting your string to datetime.  
            Default is ``True``.
        dayfirst: ``logical``
            An argument to specify whether or not the day is first when converting your string to datetime.  
            Default is ``False``.
        time_format: ``str``
            A ``str`` denoting the original format of the dates that are being converted from a ``str`` to a 
            ``datetime`` object.  Default is ``'%H:%m:%S'``.

    Returns
    -------
        ``pandas.DataFrame`` with the updated data.

    Examples
    ----------
        `set_datetime vignette <../../html/corella_user_guide/independent_observations/set_datetime.html>`_
    """

    # check for dataframe
    check_for_dataframe(dataframe=dataframe,func='set_datetime')

    # mapping of column names and variables
    mapping = {
        'eventDate': eventDate,
        'year': year, 
        'month': month,
        'day': day,
        'eventTime': eventTime
    }

    # accepted data formats for each argument
    accepted_formats = {
        'eventDate': [datetime.datetime,str],
        'year': [str,int], 
        'month': [str,int],
        'day': [str,int],
        'eventTime': [datetime.datetime,str]
    }

    # specify variables and values for set_data_workflow()
    variables = [eventDate,year,month,day,eventTime]
    values = ['eventDate','year','month','day','eventTime']

    # set column names and values specified by user
    dataframe = set_data_workflow(func='set_datetime',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)

    # add option to convert strings to datetime
    if string_to_datetime:
        
        # specify which of day,month,year is first
        dataframe['eventDate'] = pd.to_datetime(dataframe['eventDate'],dayfirst=dayfirst,yearfirst=yearfirst)

        # check for event time
        if 'eventTime' in dataframe.columns:
            dataframe['eventTime'] = pd.to_datetime(dataframe['eventTime'],format=time_format).dt.time
    
    # check format
    errors = check_datetime(dataframe=dataframe,errors=[])
    
    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe