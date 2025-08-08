import pandas as pd
import numpy as np

def occurrence_terms():
    """
    A ``pandas.Series`` of accepted (but not mandatory) values for occurrence data.

    Parameters
    ----------
        None

    Returns
    -------
        A ``pandas.Series`` of accepted (but not mandatory) values for occurrence data.
    
    Examples
    --------

    .. prompt:: python

        >>> corella.occurrence_terms()

    .. program-output:: python -c "import corella;print(corella.occurrence_terms())"
    """

    # get raw terms from tdwg
    terms_versions_raw = pd.read_csv("https://raw.githubusercontent.com/tdwg/dwc/refs/heads/master/vocabulary/term_versions.csv")

    # only choose recommended terms, not deprecated
    terms_use = terms_versions_raw[(terms_versions_raw['status'] == 'recommended') & (terms_versions_raw['rdf_type'].str.contains('Property'))]

    # change 1.1, nan and terms values to 'Generic'
    organizedin = terms_use['organized_in'].copy()
    organizedin = organizedin.replace({'http://purl.org/dc/elements/1.1/': 'http://purl.org/dc/elements/Generic',
                                        np.nan: 'http://purl.org/dc/elements/Generic',
                                        'http://purl.org/dc/terms/': 'http://purl.org/dc/elements/Generic'})
    terms_use = terms_use.drop(columns=['organized_in'],axis=1)
    terms_use = pd.concat([terms_use,organizedin],axis=1)

    # drop duplicates
    terms_use = terms_use.drop_duplicates(subset='term_localName')

    # exclude values with IRI
    terms_use_final = terms_use[~terms_use['organized_in'].str.contains('UseWithIRI')].reset_index(drop=True)

    # return a pandas series of all the names
    return terms_use_final['term_localName']