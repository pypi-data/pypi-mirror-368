from .check_multimedia import check_multimedia
from .common_functions import check_for_dataframe,set_data_workflow

def set_multimedia(dataframe=None,
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
    check_for_dataframe(dataframe=dataframe,func='set_multimedia')

    # set string names for all options
    mapping = {
        'occurrenceID': occurrenceID,
        'identifier': identifier,
        'eventID': eventID,
        'type': type,
        'format': format,
        'references': references,
        'title': title,
        'description': description,
        'created': created,
        'creator': creator,
        'license': license
    }

    # set accepted formats for all options
    accepted_formats = {
        'occurrenceID': [str],
        'identifier': [str],
        'eventID': [str],
        'type': [str],
        'format': [str],
        'references': [str],
        'title': [str],
        'description': [str],
        'created': [str],
        'creator': [str],
        'license': [str],
    }

    # specify values
    variables = [occurrenceID,identifier,eventID,type,format,references,title,description,created,creator,license]
    values = ['occurrenceID','identifier','eventID','type','format','references','title','description','created','creator','license']

    dataframe = set_data_workflow(func='set_multimedia',dataframe=dataframe,mapping=mapping,variables=variables,
                                  values=values,accepted_formats=accepted_formats)

    # check all required variables
    errors = check_multimedia(dataframe=dataframe,errors=[])

    # return errors if there are any; otherwise, return dataframe
    if len(errors) > 0:
        raise ValueError("There are some errors in your data.  They are as follows:\n\n{}".format('\n'.join(errors)))
    return dataframe