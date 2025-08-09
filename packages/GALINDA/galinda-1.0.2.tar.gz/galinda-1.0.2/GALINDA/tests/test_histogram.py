# %%
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
import glob
import h5py
from matplotlib import rc
rc("animation", html = "html5")

from GALINDA import GALINDA

# %%
gal = GALINDA.Bubble("animation_data/", "m11h_star_coordinates")

gal.histogram(1) #change the input her eto test edge cases

print(len(gal.to_plot))
print(len(gal.binX))
print(len(gal.binY))