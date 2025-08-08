from tabulate import tabulate
import pandas as pd
from .common_dictionaries import ID_REQUIRED_DWCA_TERMS,GEO_REQUIRED_DWCA_TERMS
from .get_dwc_noncompliant_terms import get_dwc_noncompliant_terms

# df = pd.DataFrame({'species': ["Callocephalon fimbriatum", "Eolophus roseicapilla"], 'latitude': [-35.310, "-35.273"], 'longitude': [149.125, 149.133], 'eventDate': ["14-01-2023", "15-01-2023"], 'status': ["present", "present"]})

def suggest_workflow(occurrences=None,
                     events=None):
    """
    Suggests a workflow to ensure your data conforms with the pre-defined Darwin Core standard.

    Parameters
    ----------
        dataframe: ``pandas.DataFrame``
            The ``pandas.DataFrame`` that contains your data to check.

    Returns
    -------
        A printed report detailing presence or absence of required data.

    Examples
    --------
        Suggest a workflow for a small dataset

        .. prompt:: python

            import pandas as pd
            import corella
            df = pd.DataFrame({'species': ['Callocephalon fimbriatum', 'Eolophus roseicapilla'], 'latitude': [-35.310, '-35.273'], 'longitude': [149.125, 149.133], 'eventDate': ['14-01-2023', '15-01-2023'], 'status': ['present', 'present']})
            corella.suggest_workflow(dataframe=df)
            
        .. program-output:: python -c "import pandas as pd;import corella;df = pd.DataFrame({'species': ['Callocephalon fimbriatum', 'Eolophus roseicapilla'], 'latitude': [-35.310, '-35.273'], 'longitude': [149.125, 149.133], 'eventDate': ['14-01-2023', '15-01-2023'], 'status': ['present', 'present']});corella.suggest_workflow(occurrences=df)"
    """
    if occurrences is None and events is None:
        raise ValueError("Please provide at least an occurrences dataframe.")

    # set up dictionary for printing results
    required_terms_occurrence = {
        "Type": ["Identifier (at least one)",
                 "Record type",
                 "Scientific name",
                 "Location",
                 "Date/Time"],
        "Matched term(s)": ['-','-','-','-','-'],
        "Missing term(s)": [' OR '.join(ID_REQUIRED_DWCA_TERMS["Australia"]),
                            'basisOfRecord',
                            'scientificName',
                            GEO_REQUIRED_DWCA_TERMS["Australia"],
                            'eventDate']
    }

    if events is not None:
        required_terms_occurrence["Type"].append("Associated event ID")
        required_terms_occurrence["Matched term(s)"].append('-')
        required_terms_occurrence["Missing term(s)"].append('eventID')

    # set up dictionary for events
    required_terms_event = {
        "Type": ["Identifier",
                 "Linking identifier",
                 "Type of Event",
                 "Name of Event",
                 "How data was acquired",
                 "Date of Event"],
        "Matched term(s)": ['-','-','-','-','-','-'],
        "Missing term(s)": ['eventID',
                            'parentEventID',
                            'eventType',
                            'Event',
                            'samplingProtocol',
                            'eventDate']
    }

    # declare lists before loop
    unmatched_dwc_terms = []
    matched_dwc_terms = []

    # get matching and nonmatching terms
    for df in [occurrences,events]:
        if df is not None:
            unmatched_dwc_terms_temp = get_dwc_noncompliant_terms(dataframe=df)
            unmatched_dwc_terms += unmatched_dwc_terms_temp
            matched_dwc_terms += list(filter(lambda x: x not in unmatched_dwc_terms, list(df.columns)))

    # set terms for looping over
    terms_occurrence = [
        ID_REQUIRED_DWCA_TERMS["Australia"],
        'basisOfRecord',
        'scientificName',
        GEO_REQUIRED_DWCA_TERMS["Australia"],
        'eventDate'
    ]

    # set terms for looping over
    terms_events = [
        'eventID',
        'parentEventID',
        'eventType',
        'Event',
        'samplingProtocol',
        'eventDate'
    ]

    # loop over all terms to compile what the person has in the dataframe
    if occurrences is not None:
        for i,t in enumerate(terms_occurrence):
            if type(t) is list and i == 0:
                if any(map(lambda v: v in ID_REQUIRED_DWCA_TERMS["Australia"],list(occurrences.columns))):
                    column_present = list(map(lambda v: v in ID_REQUIRED_DWCA_TERMS["Australia"],list(occurrences.columns)))
                    true_indices = column_present.index(True)
                    if type(true_indices) is list:
                        required_terms_occurrence["Matched term(s)"][i] = ', '.join(list(occurrences.columns)[true_indices])
                    else:
                        required_terms_occurrence["Matched term(s)"][i] = list(occurrences.columns)[true_indices]
                    required_terms_occurrence["Missing term(s)"][i] = '-'
            elif type(t) is list and i == 3:
                
                # check for required location terms
                location_names = []
                for name in terms_occurrence[i]:
                    if name in occurrences.columns:
                        location_names.append(name)                
                
                # check which required terms are present
                if len(location_names) == 0:
                    location_names = ['-']
                elif len(location_names) == len(required_terms_occurrence["Missing term(s)"][i]):
                    required_terms_occurrence["Missing term(s)"][i] = ['-']
                else:
                    for name in location_names:
                        required_terms_occurrence["Missing term(s)"][i].remove(name)

                # set variables for display table
                required_terms_occurrence["Matched term(s)"][i] = ', '.join(location_names)
                required_terms_occurrence["Missing term(s)"][i] = ', '.join(required_terms_occurrence["Missing term(s)"][i])
            else:
                if t in list(occurrences.columns):
                    required_terms_occurrence["Matched term(s)"][i] = t
                    required_terms_occurrence["Missing term(s)"][i] = '-'

    # if events is not None, check for terms
    if events is not None:
        for i,t in enumerate(terms_events):
            if t in list(events.columns):
                required_terms_event["Matched term(s)"][i] = t
                required_terms_event["Missing term(s)"][i] = '-'

    # print results
    print("\n── Darwin Core terms ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────")
    print("\n── All DwC terms ──")
    # change to include events, multimedia and emof
    if occurrences is not None and events is not None:
        length = len(occurrences.columns) + len(events.columns)
    elif events is not None:
        length = len(events.columns)
    else:
        length = len(occurrences.columns)
    print("\nMatched {} of {} column names to DwC terms:\n".format(len(matched_dwc_terms),length))
    print("{} Matched: {}".format(u'\u2713',', '.join(matched_dwc_terms)))
    print("{} Unmatched: {}".format(u'\u2717',', '.join(unmatched_dwc_terms)))
    if occurrences is not None:
        print("\n── Minimum required DwC terms occurrences ──\n")
        terms_occ = pd.DataFrame(required_terms_occurrence)
        print(tabulate(terms_occ, showindex=False, headers=terms_occ.columns))
    if events is not None:
        print("\n── Minimum required DwC terms events ──\n")
        terms_event = pd.DataFrame(required_terms_event)
        print(tabulate(terms_event, showindex=False, headers=terms_event.columns))
    print("\n── Suggested workflow ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────")
    # occurrences
    if list(required_terms_occurrence["Missing term(s)"]) == ['-','-','-','-','-']:
        print("\nCongratulations! You have the required Darwin Core terms for occurrences. Use corella.check_occurrences() to check whether your data is also Darwin Core compliant.")
    elif occurrences is not None:
        print("\n── Occurrences ──\n")
        print("To make your occurrences Darwin Core compliant, use the following workflow:\n")
        if required_terms_occurrence["Matched term(s)"][0] == '-' or required_terms_occurrence["Matched term(s)"][1] == '-':
            print("corella.set_occurrences()")
        if required_terms_occurrence["Matched term(s)"][2] == '-':
            print("corella.set_scientific_name()")
        if required_terms_occurrence["Missing term(s)"][3] != '-':
            print("corella.set_coordinates()")
        if required_terms_occurrence["Matched term(s)"][4] == '-':
            print("corella.set_datetime()")    
        print("\nAdditional functions: set_abundance(), set_collection(), set_individual_traits(), set_license(), set_locality(), set_taxonomy()")
    
    # events
    if list(required_terms_event["Missing term(s)"]) == ['-','-','-','-','-','-']:
        print("\nCongratulations! You have the required Darwin Core terms for events. Use corella.check_events() to check whether your data is also Darwin Core compliant.")
    elif events is not None:
        print("\n── Events ──\n")
        print("To make your events Darwin Core compliant, use the following workflow:\n")
        if not all(x != '-' for x in required_terms_event["Matched term(s)"][0:5]):
            print("corella.set_events()")
        if required_terms_event["Matched term(s)"][5] == '-':
            print("corella.set_datetime()")    