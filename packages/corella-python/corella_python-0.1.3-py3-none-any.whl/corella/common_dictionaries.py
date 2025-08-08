import uuid

REQUIRED_DWCA_TERMS = {
    "Australia": ["scientificName", "eventDate", "basisOfRecord"], #occurrenceID, catalogNumber, recordNumber
    "ALA": ["scientificName", "eventDate", "basisOfRecord"],
}

ID_REQUIRED_DWCA_TERMS = {
    "Australia": ["occurrenceID", "catalogNumber", "recordNumber"], 
    "ALA": ["occurrenceID", "catalogNumber", "recordNumber"],
}

GEO_REQUIRED_DWCA_TERMS = {
    "Australia": ['decimalLatitude','decimalLongitude','geodeticDatum'], #'coordinateUncertaintyInMeters','coordinatePrecision'], 
    "ALA": ['decimalLatitude','decimalLongitude','geodeticDatum','coordinateUncertaintyInMeters','coordinatePrecision'],
}

NAME_MATCHING_TERMS = {
    "Australia": ["scientificName","scientificNameAuthorship","vernacularName","rank","species","genus","family","order","classs","phylum","kingdom"],
    "ALA": ["scientificName","scientificNameAuthorship","vernacularName","rank","species","genus","family","order","classs","phylum","kingdom"]
}

TAXON_TERMS = {
    "Australia": ["scientificName","vernacularName","genus","family","order","classs","phylum","kingdom"], #"rank","species",
    "ALA": ["scientificName","vernacularName","genus","family","order","classs","phylum","kingdom"] #"rank","species",
}
'''
        'records_with_taxonomy_count': 'records_with_taxonomy_count',
        'records_with_recorded_by_count': 'records_with_recorded_by_count',
'''

required_columns_event = [
    "eventDate",
    "parentEventID",
    "eventID",
    "Event",
    "samplingProtocol"
]

continents = ["Africa","Antarctica","Asia","Europe","North America","Oceania","South America"]

unique_messages = {
    'organismQuantity': 'The organismQuantity must be a string, and must give a quantity to measurement type.',
    'organismQuantityType': 'The organismQuantity must be a string, and must give context to the field organismQuantity.'
}

REPORT_TERMS = {
    "Australia": {
        'record_type': 'record_type',
        'record_count': 'record_count',
        'record_error_count': 'record_error_count',
        'errors': 'Errors',
        'warnings': 'Warnings',
        'all_required_columns_present': 'all_required_columns_present',
        'missing_columns': 'missing_columns',
        'column_counts': 'column_counts',
        'records_with_temporal_count': 'records_with_temporal_count',
        'taxonomy_report': 'taxonomy_report',
        'coordinates_report': 'coordinates_report',
        'datetime_report': 'datetime_report',
        'vocab_reports': 'vocab_reports',
        'incorrect_dwc_terms': 'incorrect_dwc_terms'
    }
}

formats = {
    str: 'str',
    int: 'int',
    float: 'float',
    bool: 'bool',
    uuid.UUID: 'uuid',
    uuid.SafeUUID: 'uuid',
    list: 'list'
}