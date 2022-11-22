import sys
import numpy as np
import fsps
from synthesizer.sed import convert_flam_to_fnu, calculate_Q
from utils import write_data_h5py, write_attribute


imf_key = {
    'Salpeter': 0,
    'Chabrier03': 1,
    'Kroupa01': 2,
}


def generate_grid(imf):
    """ Main function to create fsps grids used by synthesizer """

    model_name = f'fsps-v3.2_{imf}'
    out_filename = f'{grid_dir}/{model_name}.h5'

    # sfh = 0: ssp, zcontinuous = 0: use metallicity grid
    sp = fsps.StellarPopulation(imf_type=imf_key[imf])

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
        spec_ = sp.get_spectrum(zmet=iZ+1)[1]   # 2D array Lsol / AA
        for ia in range(na):

            flam = spec_[ia]  # Lsol / AA
            flam *= 3.826e33  # erg s^-1 AA^-1 Msol^-1

            fnu = convert_flam_to_fnu(lam, flam)
            spec[ia, iZ] = fnu

            log10Q[ia, iZ] = np.log10(calculate_Q(lam, fnu))

    write_data_h5py(fname, 'spectra/wavelength', data=lam, overwrite=True)
    write_attribute(fname, 'spectra/wavelength', 'Description',
                    'Wavelength of the spectra grid')
    write_attribute(fname, 'spectra/wavelength', 'Units', 'AA')

    write_data_h5py(fname, 'ages', data=ages, overwrite=True)
    write_attribute(fname, 'ages', 'Description',
                    'Stellar population ages years')
    write_attribute(fname, 'ages', 'Units', 'yr')

    write_data_h5py(fname, 'log10ages', data=log10ages, overwrite=True)
    write_attribute(fname, 'log10ages', 'Description',
                    'Stellar population ages in log10 years')
    write_attribute(fname, 'log10ages', 'Units', 'log10(yr)')

    write_data_h5py(fname, 'metallicities', data=metallicities, overwrite=True)
    write_attribute(fname, 'metallicities', 'Description',
                    'raw abundances')
    write_attribute(fname, 'metallicities', 'Units', 'dimensionless [Z]')

    write_data_h5py(fname, 'log10metallicities', data=log10metallicities, overwrite=True)
    write_attribute(fname, 'log10metallicities', 'Description',
                    'raw abundances in log10')
    write_attribute(fname, 'log10metallicities', 'Units', 'dimensionless [log10(Z)]')

    write_data_h5py(fname, 'log10Q', data=log10Q, overwrite=True)
    write_attribute(fname, 'log10Q', 'Description',
                    'Two-dimensional ionising photon production rate grid, [age,Z]')

    write_data_h5py(fname, 'spectra/stellar', data=spec, overwrite=True)
    write_attribute(fname, 'spectra/stellar', 'Description',
                    'Three-dimensional spectra grid, [age, metallicity, wavelength]')
    write_attribute(fname, 'spectra/stellar', 'Units', 'erg s^-1 Hz^-1')


if __name__ == "__main__":

    grid_dir = '/its/research/astrodata/highz/synthesizer/grids/'

    imfs = ['Salpeter', 'Chabrier03', 'Kroupa01']
    imfs = ['Salpeter']

    for imf in imfs:

        generate_grid(imf)
