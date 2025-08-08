from .common_functions import check_is_string
import uuid

def check_individual_traits(dataframe=None,
                            errors=[]):
    
    # check if dataframe is provided an argument
    if dataframe is None:
        raise ValueError("Please provide a dataframe")

    # check the type of variable for all scientific name associated variables
    for item in ['individualID','lifeStage','sex','vitality','reproductiveCondition']:
        if item in dataframe.columns:
            if item == 'individualID':
                other_formats = list(set(type(x) for x in dataframe[item]))
                if len(other_formats) == 1:
                    if (other_formats[0] not in [uuid.UUID,str]):
                        errors.append('the individualID column must either be a string or a uuid.')
                else:
                    if any(x not in [uuid.UUID,str] for x in other_formats):
                        errors.append('the datasetID column must either be a string or a uuid.')
            else:
                errors = check_is_string(dataframe=dataframe,column_name=item,errors=errors)

    # return either errors or None
    if errors is not None:
        return errors
    return None