import sys
import numpy as np
import fsps
import os
from synthesizer.sed import convert_flam_to_fnu, calculate_Q
from utils import write_data_h5py, write_attribute


def generate_grid(imf_lower_limit=1):
    """ Main function to create fsps grids used by synthesizer
        this generates grids with different high-mass slopes while adopting the Kroupa imf as a base
    """

    model_name = f'fsps-v3.2_imfll:{imf_lower_limit:.1f}'
    out_filename = f'{grid_dir}/{model_name}.h5'

    # sfh = 0: ssp, zcontinuous = 0: use metallicity grid
    sp = fsps.StellarPopulation(imf_type=2, imf_lower_limit=imf_lower_limit)

    lam = sp.wavelengths  # units: Angstroms
    log10ages = sp.log_age  # units: log10(years)
    ages = 10**log10ages
    metallicities = sp.zlegend  # units: log10(Z)
    log10metallicities = np.log10(metallicities)

    na = len(log10ages)
    nZ = len(metallicities)

    log10Q = np.zeros((na, nZ))  # the ionising photon production rate
    spec = np.zeros((na, nZ, len(lam)))

    for iZ in range(nZ):
        print(iZ)
        spec_ = sp.get_spectrum(zmet=iZ+1)[1]   # 2D array Lsol / AA
        for ia in range(na):

            fnu = spec_[ia]  # Lsol / Hz
            fnu *= 3.826e33  # erg s^-1 Hz^-1 Msol^-1

            # fnu = convert_flam_to_fnu(lam, flam)
            spec[ia, iZ] = fnu

            log10Q[ia, iZ] = np.log10(calculate_Q(lam, fnu))

    write_data_h5py(out_filename, 'spectra/wavelength', data=lam, overwrite=True)
    write_attribute(out_filename, 'spectra/wavelength', 'Description',
                    'Wavelength of the spectra grid')
    write_attribute(out_filename, 'spectra/wavelength', 'Units', 'AA')

    write_data_h5py(out_filename, 'ages', data=ages, overwrite=True)
    write_attribute(out_filename, 'ages', 'Description',
                    'Stellar population ages years')
    write_attribute(out_filename, 'ages', 'Units', 'yr')

    write_data_h5py(out_filename, 'log10ages', data=log10ages, overwrite=True)
    write_attribute(out_filename, 'log10ages', 'Description',
                    'Stellar population ages in log10 years')
    write_attribute(out_filename, 'log10ages', 'Units', 'log10(yr)')

    write_data_h5py(out_filename, 'metallicities', data=metallicities, overwrite=True)
    write_attribute(out_filename, 'metallicities', 'Description',
                    'raw abundances')
    write_attribute(out_filename, 'metallicities', 'Units', 'dimensionless [Z]')

    write_data_h5py(out_filename, 'log10metallicities', data=log10metallicities, overwrite=True)
    write_attribute(out_filename, 'log10metallicities', 'Description',
                    'raw abundances in log10')
    write_attribute(out_filename, 'log10metallicities', 'Units', 'dimensionless [log10(Z)]')

    write_data_h5py(out_filename, 'log10Q', data=log10Q, overwrite=True)
    write_attribute(out_filename, 'log10Q', 'Description',
                    'Two-dimensional ionising photon production rate grid, [age,Z]')

    write_data_h5py(out_filename, 'spectra/stellar', data=spec, overwrite=True)
    write_attribute(out_filename, 'spectra/stellar', 'Description',
                    'Three-dimensional spectra grid, [age, metallicity, wavelength]')
    write_attribute(out_filename, 'spectra/stellar', 'Units', 'erg s^-1 Hz^-1')


if __name__ == "__main__":

    synthesizer_data_dir = os.getenv('SYNTHESIZER_DATA')
    grid_dir = f'{synthesizer_data_dir}/grids'
    print(grid_dir)

    for imf_lower_limit in [0.5, 1, 5, 10, 50]:
        print(imf_lower_limit)
        generate_grid(imf_lower_limit)
