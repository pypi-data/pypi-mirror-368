import pandas as pd
from tabulate import tabulate
from .get_dwc_noncompliant_terms import get_dwc_noncompliant_terms
from .check_abundance import check_abundance
from .check_basisOfRecord import check_basisOfRecord
from .check_coordinates import check_coordinates
from .check_datetime import check_datetime
from .check_events import check_events
from .check_locality import check_locality
from .check_occurrenceIDs import check_occurrenceIDs
from .check_scientificName import check_scientificName

def check_data(occurrences=None,
               events=None,
               max_num_errors=5,
               print_report=True):
        """
        Checks whether or not the data in your occurrences complies with
        Darwin Core standards.

        Parameters
        ----------
            dataframe: ``pandas.DataFrame``
                The ``pandas.DataFrame`` that contains your data to check.

        Returns
        -------
            Raises a ``ValueError`` if something is not valid.
        
        Examples
        --------
        Suggest a workflow for a small dataset

        .. prompt:: python

            import pandas as pd
            import corella
            df = pd.DataFrame({'species': ['Callocephalon fimbriatum', 'Eolophus roseicapilla'], 'latitude': [-35.310, '-35.273'], 'longitude': [149.125, 149.133], 'eventDate': ['14-01-2023', '15-01-2023'], 'status': ['present', 'present']})
            corella.check_data(occurrences=df)
            
        .. program-output:: python -c "import pandas as pd;import corella;df = pd.DataFrame({'species': ['Callocephalon fimbriatum', 'Eolophus roseicapilla'], 'latitude': [-35.310, '-35.273'], 'longitude': [149.125, 149.133], 'eventDate': ['14-01-2023', '15-01-2023'], 'status': ['present', 'present']});print(corella.check_data(occurrences=df))"
    """

        # First, check if a dataframe is provided
        if occurrences is None and events is None:
            raise ValueError("Please provide a dataframe to this function.")

        # initialise errors 
        errors = []

        # initialise unicode symbols
        check_mark = u'\u2713'
        cross_mark = u'\u2717'

        # data
        compliance_dwc_standard = True

        # first, check for all terms that are not compliant
        vocab_check = []
        for df in [occurrences,events]:
            if df is not None:
                vocab_check_temp = get_dwc_noncompliant_terms(dataframe = df)
                vocab_check += vocab_check_temp
        
        # do vocab check 
        if len(vocab_check) > 0:
            compliance_dwc_standard = False
            terms_to_check = []
            for df in [occurrences,events]:
                if df is not None:
                    terms_to_check += [x for x in df.columns if x not in vocab_check]
        else:
            terms_to_check = list(occurrences.columns)

        # initialise table
        data_table = {
             'Number of Errors': [0 for x in range(len(terms_to_check))],
             'Pass/Fail': [check_mark for x in range(len(terms_to_check))],
             'Column name': list(terms_to_check)
        }

        # run all checks on occurrences
        if occurrences is not None:
            for f in [check_abundance,check_basisOfRecord,check_coordinates,check_datetime,check_locality,check_occurrenceIDs,check_scientificName]:
                errors_f = f(dataframe=occurrences)
                if type(errors_f) is list:
                    errors += errors_f

        # run all checks on events
        if events is not None:
            for f in [check_events,check_datetime]:
                errors_f = f(dataframe=events)
                if type(errors_f) is list:
                    errors += errors_f
        
        # print out message to screen
        for i,cname in enumerate(data_table['Column name']):
            if any(cname in x for x in errors):
                data_table['Number of Errors'][i] += 1
                data_table['Pass/Fail'][i] = cross_mark
        
        if print_report:
        
            df_data_table = pd.DataFrame(data_table)
            print(tabulate(df_data_table, showindex=False, headers=df_data_table.columns))
            print()

            print("\n══ Results ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\n")
            print()
            total_errors = df_data_table['Number of Errors'].sum()
            total_passes = df_data_table[df_data_table['Pass/Fail'] == check_mark].value_counts().sum()
            print('Errors: {} | Passes: {}'.format(total_errors,total_passes))
            print()
            if not compliance_dwc_standard:
                print("{} Data does not meet minimum Darwin core requirements".format(cross_mark))
                print("Use corella.suggest_workflow()\n")
            else:
                print("{} Data meets minimum Darwin core requirements".format(check_mark))
            
            # Loop over column names that have errors
            num_errors = 0
            for i,cname in enumerate(data_table['Column name']):
                if data_table['Number of Errors'][i] > 0:
                    print('── Error in {} ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────\n'.format(cname))
                    errors = [x for x in errors if cname in x]
                    for e in errors:
                        print(e)
                        num_errors += 1
                        if num_errors >= max_num_errors:
                            break 
                    print()
        else:
            if df_data_table['Number of Errors'].sum() == 0 and compliance_dwc_standard:
                return True
            return False