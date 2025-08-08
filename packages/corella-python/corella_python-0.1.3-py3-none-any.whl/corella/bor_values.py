import pandas as pd

def bor_values():

    return pd.DataFrame({'basisOfRecord values': ["humanObservation",
                                                  "machineObservation",
                                                  "livingSpecimen",
                                                  "preservedSpecimen",
                                                  "fossilSpecimen",
                                                  "materialCitation"]})