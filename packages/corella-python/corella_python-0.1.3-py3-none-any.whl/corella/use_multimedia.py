from .check_multimedia import check_multimedia
from .common_functions import check_for_dataframe,check_if_all_args_empty,check_all_columns_values

def use_multimedia(dataframe=None,
                   occurrenceID=None,
                   identifier=None,
                   eventID=None,
                   type=None,
                   format=None,
                   references=None,
                   title=None,
                   description=None,
                   created=None,
                   creator=None,
                   license=None):
    
    # raise a ValueError if no dataframe is provided
    check_for_dataframe(dataframe=dataframe,func='use_multimedia')

    # set string names for all options
    mm_options = {
        occurrenceID: 'occurrenceID',
        identifier: 'identifier',
        eventID: 'eventID',
        type: 'type',
        format: 'format',
        references: 'references',
        title: 'title',
        description: 'description',
        created: 'created',
        creator: 'creator',
        license: 'license'
    }

    # set accepted formats for all options
    accepted_formats = {
        occurrenceID: [str],
        identifier: [str],
        eventID: [str],
        type: [str],
        format: [str],
        references: [str],
        title: [str],
        description: [str],
        created: [str],
        creator: [str],
        license: [str],
    }

    # specify values
    values = ['occurrenceID','identifier','eventID','type','format','references','title','description','created','creator','license']

    # check if all arguments are empty
    check_if_all_args_empty(dataframe=dataframe,func='use_multimedia',keys=mm_options.keys(),values=values)
    
    # check all column values to see if they are a column name or can be assigned a value
    dataframe,mapping = check_all_columns_values(dataframe=dataframe,mapping=mm_options,accepted_formats=accepted_formats)

    # rename all necessary columns
    dataframe = dataframe.rename(columns=mapping)

    # check all required variables
    errors = check_multimedia(dataframe=dataframe,errors=[])

    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe