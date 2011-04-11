# BSD Licence
# Copyright (c) 2011, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

"""
Catalogs the test data available on esg-dev1.

"""

DAP_BASES = [
    'http://esg-dev1.badc.rl.ac.uk:8081/ta_20101129',
    'http://esg-dev1.badc.rl.ac.uk:8080/thredds/dodsC/test_data/ta_20101129',
    'http://esg-dev1.badc.rl.ac.uk:8080/opendap/ta_20101129',
    ]

DATA_FILES =  [
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_197812010600-197901010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_197901010600-198001010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198001010600-198101010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198101010600-198201010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198201010600-198301010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198301010600-198401010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198401010600-198501010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198501010600-198601010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198601010600-198701010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198701010600-198801010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198801010600-198901010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_198901010600-199001010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199001010600-199101010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199101010600-199201010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199201010600-199301010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199301010600-199401010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199401010600-199501010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199501010600-199601010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199601010600-199701010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199701010600-199801010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199801010600-199901010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_199901010600-200001010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_200001010600-200101010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_200101010600-200201010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_200201010600-200301010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_200301010600-200401010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_200401010600-200501010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_200501010600-200601010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_200601010600-200701010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_200701010600-200801010000.nc',
    'ta_6hrPlev_HadGEM2-ES_piControl_r1i1p1_200801010600-200901010000.nc',
]

def make_dataset_list(base_url):
    """
    Yields a list of URLs relative to base_url
    for the test data.

    """
    base_url = base_url.rstrip('/')
    for d in DATA_FILES:
        yield '%s/%s' % (base_url, d)

