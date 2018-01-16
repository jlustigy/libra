from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import os
from astropy.io import fits
import astropy.units as u

__all__ = ['Spectrum1D', 'NIRSpecSpectrum2D']

bg_path = os.path.join(os.path.dirname(__file__), os.pardir, 'data', 'etc',
                       'image_detector.fits')


class Spectrum1D(object):
    def __init__(self, wavelength, flux, error=None, header=None):
        self.wavelength = wavelength
        self.flux = flux
        self.error = error
        self.header = header

    def plot(self, ax=None):
        if ax is None:
            ax = plt.gca()

        ax.plot(self.wavelength, self.flux)

        return ax

    @u.quantity_input(new_wavelengths=u.m)
    def interp_flux(self, new_wavelengths):
        f = interp1d(self.wavelength.value, self.flux, kind='linear',
                     bounds_error=False, fill_value=0)
        interped_fluxes = f(new_wavelengths)

        if hasattr(self.flux, 'unit') and self.flux.unit is not None:
            return interped_fluxes * self.flux.unit
        return interped_fluxes


class NIRSpecSpectrum2D(object):
    def __init__(self):
        self.image = fits.getdata(bg_path)
