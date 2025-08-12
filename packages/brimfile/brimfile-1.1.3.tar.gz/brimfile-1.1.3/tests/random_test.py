import sys
import os

import numpy as np
from matplotlib.pyplot import imshow

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import brimfile as brim

filename = r'/Users/bevilacq/Downloads/zebrafish_ECM_SBS.brim.zip'
f = brim.File(filename)

# get the first data group in the file
d = f.get_data()


# get the metadata 
md = d.get_metadata()
all_metadata = md.all_to_dict()


ar = d.get_analysis_results()

# get the image of the shift quantity for the average of the Stokes and anti-Stokes peaks
img, px_size = ar.get_image(brim.Data.AnalysisResults.Quantity.Shift, brim.Data.AnalysisResults.PeakType.average)

imshow(np.squeeze(img))

# get the spectrum in the image at a specific pixel (coord)
coord = (0, 3, 4)
PSD, frequency, PSD_units, frequency_units = d.get_spectrum_in_image(coord)    

f.close()