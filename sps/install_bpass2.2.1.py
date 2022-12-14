"""
Download BPASS v2.2.1 and convert to HDF5 synthesizer grid.
"""

import os
from hoki import load
import numpy as np
from utils import write_data_h5py, write_attribute, add_log10Q
import gdown
import tarfile
import h5py
from scipy import integrate

from unyt import h, c
from synthesizer.sed import calculate_Q






model_url = {}
model_url['bpass-v2.2.1_chab100-bin'] = "https://drive.google.com/file/d/1az7_hP3RDovr-BN9sXgDuaYqOZHHUeXD/view?usp=sharing"
model_url['bpass-v2.2.1_chab300-bin'] = "https://drive.google.com/file/d/1JcUM-qyOQD16RdfWjhGKSTwdNfRUW4Xu/view?usp=sharing"
# model_url[''] = ""
# model_url[''] = ""
# model_url[''] = ""
# model_url[''] = ""
# model_url[''] = ""



# --- this links our model naming pattern to the bpass naming. Unfortunately due to inconsistency this is tricky to do via a function.



def download_data(model):

    if model in model_url.keys():
        filename = gdown.download(model_url[model], quiet=False, fuzzy=True)
        return filename
    else:
        print('ERROR: no url for that model')

def untar_data(model):

    model_dir = f'{synthesizer_data_dir}/input_files/bpass/{model}'
    tar = tarfile.open(f'{synthesizer_data_dir}/input_files/bpass/{model}.tar.gz')
    tar.extractall(path = model_dir)
    tar.close()
    # os.remove(f'{model}.tar.gz')


def make_grid(model, bs='bin'):


    model_ = model.split('_')

    version = model_[1]

    imf = model_[2:]
    if type(imf) == list:
        imf = '_'.join(imf)

    hms = imf[-3:]#
    imf_ = imf[:-3]
    imf_ = imf_.replace('_', '')
    imf_ = imf_.replace('imf','')

    model_name = f'bpass-{version}-{bs}_{imf_}-{hms}' # this is the name of the ultimate HDF5 file

    print(model, imf, model_name)

    out_filename = f'{grid_dir}/{model_name}.h5' # this is the full path to the ultimate HDF5 grid file


    input_dir = f'{parent_model_dir}/{model}'

    # --- ccreate metallicity grid and dictionary
    Zk_to_Z = {'zem5': 0.00001, 'zem4': 0.0001, 'z001': 0.001, 'z002': 0.002, 'z003': 0.003, 'z004': 0.004, 'z006': 0.006, 'z008': 0.008, 'z010': 0.01, 'z014': 0.014, 'z020': 0.020, 'z030': 0.030, 'z040': 0.040}
    Z_to_Zk = {k:v for v, k in Zk_to_Z.items()}
    Zs = np.sort(np.array(list(Z_to_Zk.keys())))
    log10Zs = np.log10(Zs)

    zk = Z_to_Zk[Zs[0]]

    # --- get ages
    fn_ = f'{input_dir}/starmass-{bs}-{imf}.{zk}.dat.gz'
    starmass = load.model_output(fn_)
    log10ages = starmass['log_age'].values

    # --- get wavelength grid
    fn_ = f'{input_dir}/spectra-{bs}-{imf}.{zk}.dat.gz'
    spec = load.model_output(fn_)
    wavelengths = spec['WL'].values # \AA
    nu = 3E8/(wavelengths*1E-10)

    nZ = len(log10Zs)
    na = len(log10ages)

    stellar_mass = np.zeros((na,nZ))
    remnant_mass = np.zeros((na,nZ))
    log10Q = np.zeros((na,nZ)) # the ionising photon production rate
    spectra = np.zeros((na, nZ, len(wavelengths)))


    for iZ, Z in enumerate(Zs):

        zk = Z_to_Zk[Z]

        # --- get remaining and remnant fraction
        fn_ = f'starmass-{bs}-{imf}.{zk}.dat.gz'
        starmass = load.model_output(f'{input_dir}/{fn_}')
        stellar_mass[:, iZ] = starmass['stellar_mass'].values/1E6
        remnant_mass[:, iZ] = starmass['remnant_mass'].values/1E6

        # --- get spectra
        fn_ = f'spectra-{bs}-{imf}.{zk}.dat.gz'
        spec = load.model_output(f'{input_dir}/{fn_}')

        for ia, log10age in enumerate(log10ages):

            spec_ = spec[str(log10age)].values # Lsol AA^-1 10^6 Msol^-1

            # --- convert from Llam to Lnu
            spec_ /= 1E6 # Lsol AA^-1 Msol^-1
            spec_ *= (3.826e33)  # erg s^-1 AA^-1 Msol^-1
            spec_ *= wavelengths/nu # erg s^-1 Hz^-1 Msol^-1
            spectra[ia, iZ, :] = spec_

            # --- calcualte ionising photon luminosity
            log10Q[ia, iZ] = np.log10(calculate_Q(wavelengths, spec_))



    write_data_h5py(out_filename, 'star_fraction', data=stellar_mass, overwrite=True)
    write_attribute(out_filename, 'star_fraction', 'Description',
                    'Two-dimensional remaining stellar fraction grid, [age,Z]')

    write_data_h5py(out_filename, 'remnant_fraction', data=remnant_mass, overwrite=True)
    write_attribute(out_filename, 'remnant_fraction', 'Description',
                    'Two-dimensional remaining remnant fraction grid, [age,Z]')

    write_data_h5py(out_filename, 'spectra/stellar', data=spectra, overwrite=True)
    write_attribute(out_filename, 'spectra/stellar', 'Description',
                    'Three-dimensional spectra grid, [Z,Age,wavelength]')
    write_attribute(out_filename, 'spectra/stellar', 'Units', 'erg s^-1 Hz^-1')

    write_data_h5py(out_filename, 'log10Q', data=log10Q, overwrite=True)
    write_attribute(out_filename, 'log10Q', 'Description',
                        'Two-dimensional ionising photon production rate grid, [age,Z]')

    write_data_h5py(out_filename, 'log10ages', data=log10ages, overwrite=True)
    write_attribute(out_filename, 'log10ages', 'Description',
            'Stellar population ages in log10 years')
    write_attribute(out_filename, 'log10ages', 'Units', 'log10(yr)')

    write_data_h5py(out_filename, 'metallicities', data=Zs, overwrite=True)
    write_attribute(out_filename, 'metallicities', 'Description',
            'raw abundances')
    write_attribute(out_filename, 'metallicities', 'Units', 'dimensionless [log10(Z)]')

    write_data_h5py(out_filename, 'log10metallicities', data=log10Zs, overwrite=True)
    write_attribute(out_filename, 'log10metallicities', 'Description',
            'raw abundances in log10')
    write_attribute(out_filename, 'log10metallicities', 'Units', 'dimensionless [log10(Z)]')

    write_data_h5py(out_filename, 'spectra/wavelength', data=wavelengths, overwrite=True)
    write_attribute(out_filename, 'spectra/wavelength', 'Description',
            'Wavelength of the spectra grid')
    write_attribute(out_filename, 'spectra/wavelength', 'Units', 'AA')









if __name__ == "__main__":

    synthesizer_data_dir = os.getenv('SYNTHESIZER_DATA')
    parent_model_dir = f'{synthesizer_data_dir}/input_files/bpass/'
    grid_dir = f'{synthesizer_data_dir}/grids'


    models = ['bpass_v2.2.1_imf100_100', 'bpass_v2.2.1_imf100_300', 'bpass_v2.2.1_imf135_100', 'bpass_v2.2.1_imf135_300', 'bpass_v2.2.1_imf135all_100', 'bpass_v2.2.1_imf170_100', 'bpass_v2.2.1_imf170_300', 'bpass_v2.2.1_imf_chab100',  'bpass_v2.2.1_imf_chab300']

    # models = ['bpass_v2.2.1_imf100_100']


    for model in models:

        print('-'*40)
        print(model)

        # download_data(model)
        # untar_data(model)
        make_grid(model)
