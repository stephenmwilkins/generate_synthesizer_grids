

import os
import gdown


grid_url = {}

grid_url['bpass-v2.2.1-bin_chab-300'] = 'https://drive.google.com/file/d/135XvWyz06DgU0_uMzczB4_Azy4DC7bOH/view?usp=share_link'
grid_url['bpass-v2.2.1-bin_chab-300_cloudy-v17.03_log10Uref-2'] = 'https://drive.google.com/file/d/1iJTi0ciskqsV6kL5ObbRV4orQ0xnKqvI/view?usp=share_link'
grid_url['pillars.png'] = 'https://drive.google.com/file/d/1cfAF9ULT2cV_k3-roDsUO9MMdr8RbunV/view?usp=share_link'


if __name__ == "__main__":

    output_dir = '../../synthesizer/synthesizer/data/grids/'

    grids = ['bpass-v2.2.1-bin_chab-300', 'bpass-v2.2.1-bin_chab-300_cloudy-v17.03_log10Uref-2']
    grids = ['pillars.png']

    for grid in grids:

        if len(grid.split('.')) > 1:
            gdown.download(grid_url[grid], output=f'{output_dir}/{grid}', quiet=False, fuzzy=True)
        else:
            gdown.download(
                grid_url[grid], output=f'{output_dir}/{grid}.h5', quiet=False, fuzzy=True)
