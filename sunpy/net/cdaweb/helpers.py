import requests

from astropy.table import Table

from .cdaweb import _CDAS_BASEURL, _CDAS_HEADERS, _DATAVIEW


def get_observatory_groups():
    """
    Get a list of observatory IDs for each observatory in CDAWeb.

    An observatory group is typically a single mission, which can contain
    multiple observatories, e.g. for the STEREO observatory group there are two
    observatories, STEREO-A and STEREO-B.

    Returns
    -------
    astropy.table.Table

    Examples
    --------
    >>> from sunpy.net.cdaweb import get_observatory_groups
    >>>
    >>> groups = get_observatory_groups() #doctest: +REMOTE_DATA
    >>> groups['Group'] #doctest: +REMOTE_DATA
        <Column name='Group' dtype='str55' length=75>
                        ACE
                      AMPTE
        ...
                    Voyager
                       Wind
    >>> groups.loc['STEREO'] #doctest: +REMOTE_DATA
    <Row index=62>
    Group                                  Observatories
    str55                                      str518
    ------ -----------------------------------------------------------------------------
    STEREO 'Ahead', 'Behind', 'STA', 'STB', 'STEREO', 'STEREOA', 'STEREOB', 'sta', 'stb'
    """
    # Get a list of files for a given dataset between start and end times
    url = '/'.join([
        _CDAS_BASEURL,
        'dataviews', _DATAVIEW,
        'observatoryGroups'
    ])
    response = requests.get(url, headers=_CDAS_HEADERS)
    obs_groups = response.json()

    names = [obs['Name'] for obs in obs_groups['ObservatoryGroupDescription']]
    obs_ids = [obs['ObservatoryId'] for obs in obs_groups['ObservatoryGroupDescription']]
    # Join all IDs into a single string
    obs_ids = ["'" + "', '".join(id) + "'" for id in obs_ids]

    t = Table([names, obs_ids],
              names=['Group', 'Observatories'])
    t.add_index('Group')
    return t


def get_datasets(observatory):
    """
    Get a list of datasets for a given observatory.

    Parameters
    ----------
    observatory : str
        Observatory name.

    Returns
    -------
    astropy.table.Table

    Examples
    --------
    >>> from sunpy.net.cdaweb import get_datasets
    >>>
    >>> datasets = get_datasets('STEREOA') #doctest: +REMOTE_DATA
    >>> datasets['Id'] #doctest: +REMOTE_DATA
        <Column name='Id' dtype='str17' length=5>
         STA_L1_SWEA_SPEC
               STA_L1_HET
        STA_L1_IMPACT_HKP
           STA_LB_MAG_RTN
            STA_LB_IMPACT
    >>> datasets.loc['STA_L1_HET']['Label'] #doctest: +REMOTE_DATA
        'STEREO Ahead IMPACT/HET Level 1 Data. - J. Luhmann (UCB/SSL)'
    >>> datasets.loc['STA_L1_HET'][['Start', 'End']] #doctest: +REMOTE_DATA
        <Row index=1>
             Start                     End
             str24                    str24
    ------------------------ ------------------------
    2006-12-01T00:00:53.000Z 2021-07-31T23:59:30.000Z
    """
    # Get a list of files for a given dataset between start and end times
    url = '/'.join([
        _CDAS_BASEURL,
        'dataviews', _DATAVIEW,
        'datasets'
    ])
    url = f'{url}?observatory={observatory}'
    response = requests.get(url, headers=_CDAS_HEADERS)
    datasets = response.json()['DatasetDescription']

    ids = [dataset['Id'] for dataset in datasets]
    instruments = [', '.join(dataset['Instrument']) for dataset in datasets]
    labels = [dataset['Label'] for dataset in datasets]
    stimes = [dataset['TimeInterval']['Start'] for dataset in datasets]
    etimes = [dataset['TimeInterval']['End'] for dataset in datasets]

    t = Table([ids, instruments, labels, stimes, etimes],
              names=['Id', 'Instruments', 'Label', 'Start', 'End'])
    t.add_index('Id')
    return t
