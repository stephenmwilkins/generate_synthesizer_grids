
""" This reads in a cloudy grid of models and creates a new SPS grid including the various outputs """


from scipy import integrate
import os
import shutil
from synthesizer.utils import read_params
from synthesizer.cloudy_sw import read_wavelength, read_continuum, default_lines, read_lines
from synthesizer.sed import calculate_Q
import argparse
import numpy as np
import h5py

#
# from unyt import c, h

h = 6.626E-34
c = 3.E8


synthesizer_data_dir = os.getenv('SYNTHESIZER_DATA')

path_to_grids = f'{synthesizer_data_dir}/grids'
path_to_cloudy_files = f'{synthesizer_data_dir}/cloudy'


# cloudy_models = ['cloudy-v17.03_log10Uref-2']  # --- the cloudy grid
#
# sps_grids = [
#     'bc03_chabrier03',
#     'bpass-v2.2.1-bin_100-100',
#     'bpass-v2.2.1-bin_100-300',
#     'bpass-v2.2.1-bin_135-100',
#     'bpass-v2.2.1-bin_135-300',
#     'bpass-v2.2.1-bin_135all-100',
#     'bpass-v2.2.1-bin_170-100',
#     'bpass-v2.2.1-bin_170-300',
#     'fsps-v3.2_Chabrier03',
#     'bpass-v2.2.1-bin_chab-100',
#     'bpass-v2.2.1-bin_chab-300',
#     'maraston-rhb_kroupa',
#     'maraston-rhb_salpeter',
#     'bc03-2016-Stelib_chabrier03',
#     'bc03-2016-BaSeL_chabrier03',
#     'bc03-2016-Miles_chabrier03',
# ]

# sps_grids = [f'fsps-v3.2_imf3:{imf3:.1f}' for imf3 in np.arange(1.5, 3.1, 0.1)]


sps_grids = ['bpass-v2.2.1-bin_chab-300']
cloudy_models = [f'cloudy-v17.03_log10Uref{log10U:.1f}' for log10U in np.arange(-4, 1.1, 0.5)]


for sps_model in sps_grids:

    print('-'*50)
    print(sps_model)

    for cloudy_model in cloudy_models:

        print(cloudy_model)
        print(f'{path_to_cloudy_files}/{sps_model}_{cloudy_model}/')

        # --- open the original SPS model grid
        fn = f'{path_to_grids}/{sps_model}.h5'
        hf = h5py.File(fn, 'r')

        # --- short hand for later
        metallicities = hf['metallicities']
        log10ages = hf['log10ages']

        nZ = len(metallicities)  # number of metallicity grid points
        na = len(log10ages)  # number of age grid points

        i = 1
        for iZ, Z in enumerate(metallicities):
            for ia, log10age in enumerate(log10ages):

                infile = f'{path_to_cloudy_files}/{sps_model}_{cloudy_model}/{ia}_{iZ}'

                try:
                    spec_dict = read_continuum(infile, return_dict=True)
                except:
                    print(f'qsub -t {i} run_grid.job')

                i += 1

                # if not os.path.isfile(infile+'.cont'):  # attempt to open run.
                #
                #     print(ia, iZ)
