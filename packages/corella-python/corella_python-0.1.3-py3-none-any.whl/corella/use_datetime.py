import datetime
import pandas as pd
from .check_datetime import check_datetime
from .common_functions import check_for_dataframe,check_if_all_args_empty,check_all_columns_values

def use_datetime(dataframe=None,
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
            A column name (``str``) denoting the column with the dates of the events, or a ``str`` or 
            ``datetime.datetime`` object denoting the date of the event.
        year: ``str`` or ``int``
            A column name (``str``) denoting the column with the dates of the events, or an ``int`` denoting
            the year of the event.
        month: ``str`` or ``int``
            A column name (``str``) denoting the column with the dates of the events, or an ``int`` denoting
            the month of the event.
        day: ``str`` or ``int``
            A column name (``str``) denoting the column with the dates of the events, or an ``int`` denoting
            the day of the event.
        eventTime: ``str``
            A column name (``str``) denoting the column with the dates of the events, or a ``str`` denoting
            the time of the event.
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
    """

    # raise a ValueError if no dataframe is provided
    check_for_dataframe(dataframe=dataframe,func='use_datetime')

    # mapping column names
    mapping = {
        eventDate: 'eventDate',
        year: 'year', 
        month: 'month',
        day: 'day',
        eventTime: 'eventTime'
    }

    # accepted formats for inputs
    accepted_formats = {
        eventDate: [datetime.datetime,str],
        year: [str,int], 
        month: [str,int],
        day: [str,int],
        eventTime: [datetime.datetime,str]
    }

    values = ['eventDate','year','month','day','eventTime']

    # check if all arguments are empty
    check_if_all_args_empty(dataframe=dataframe,func='use_datetime',keys=mapping.keys(),values=values)
    
    # check all columns and values
    dataframe,mapping = check_all_columns_values(dataframe=dataframe,mapping=mapping,accepted_formats=accepted_formats)

    # rename all necessary columns
    dataframe = dataframe.rename(columns=mapping)

    # add option to convert strings to datetime
    if string_to_datetime:
        # specify which of day,month,year is first
        if yearfirst:
            dataframe['eventDate'] = pd.to_datetime(dataframe['eventDate'],yearfirst=yearfirst)
        elif dayfirst:
            dataframe['eventDate'] = pd.to_datetime(dataframe['eventDate'],dayfirst=dayfirst)
        else:
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