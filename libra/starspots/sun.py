"""
Methods for drawing from the sunspot latitude and radius distribution
"""
import numpy as np
import astropy.units as u


__all__ = ['draw_random_sunspot_latitudes', 'draw_random_sunspot_radii']


@u.quantity_input(theta=u.rad, phi=u.rad)
def rtp_to_edge(radius, theta, phi, n_points=1000):
    """
    Use the haversine formula to compute the boundary lat/lon coordinates for a
    circular spot centered on ``(theta, phi)``, with radius ``radius` in units
    of the stellar radius.

    Parameters
    ----------
    radius : float
        Spot radius [R_star]
    theta : `~astropy.units.Quantity`
        Spot theta coord (90 deg - latitude)
    phi : `~astropy.units.Quantity`
        Spot phi coord (longitude)
    n_points : int
        Number of points to include in the circle boundary

    Returns
    -------
    lat : `~astropy.units.Quantity`
        Latitudes of spot boundary
    lon : `~astropy.units.Quantity`
        Longitudes of spot boundary
    """
    lat1 = np.pi/2 - theta.to(u.rad).value
    lon1 = phi.to(u.rad).value
    d = radius

    thetas = np.linspace(0, -2*np.pi, n_points)[:, np.newaxis]

    lat = np.arcsin(np.sin(lat1) * np.cos(d) + np.cos(lat1) *
                    np.sin(d) * np.cos(thetas))
    dlon = np.arctan2(np.sin(thetas) * np.sin(d) * np.cos(lat1),
                      np.cos(d) - np.sin(lat1) * np.sin(lat))
    lon = ((lon1 - dlon + np.pi) % (2*np.pi)) - np.pi
    return lat*u.rad, lon*u.rad


def generate_random_coord(n=1):
    """
    Generate random latitude/longitude pairs, of length ``n``.
    """
    random_longitude = 2*np.pi*np.random.rand(n)
    random_z = 2*np.random.rand(n) - 1
    random_latitude = np.arcsin(random_z)
    result = np.vstack([random_latitude, random_longitude]).T * u.rad

    if result.shape[0] == 1:
        return result[0]
    return result


def sunspot_distribution(latitude, mean_latitude=15):
    """
    Approximate un-normalized probability distribution of sunspots at
    ``latitude`` near activity maximum on the Sun.

    Parameters
    ----------
    latitude : `~numpy.ndarray`
        Latitude

    mean_latitude : float
        Mean active latitude in degrees

    Returns
    -------
    p : `~numpy.ndarray
        Probability (un-normalized)
    """
    return np.exp(-0.5 * (abs(latitude) - mean_latitude)**2 / 6**2)


def sunspot_latitude_inverse_transform(x, mean_latitude=15):
    """
    Use inverse transform sampling to randomly draw spot latitudes from the
    sunspot latitude distribution, for a uniform random variate ``x`` on the
    range [0,1).

    Parameters
    ----------
    x : `~np.ndarray` or float
        Uniform random variate on [0, 1)

    Returns
    -------
    lat : `~astropy.units.Quantity`
        Latitude of a sunspot drawn from the sunspot latitude distribution.
    """
    lats = np.linspace(-88, 88, 1000)
    prob = np.cumsum(sunspot_distribution(lats, mean_latitude=mean_latitude))
    prob /= np.max(prob)
    return np.interp(x, prob, lats) * u.deg


def draw_random_sunspot_latitudes(n, mean_latitude=15):
    """
    Draw one or more random samples from the sunspot latitude distribution.

    Parameters
    ----------
    n : int
        Number of random sunspot latitudes to draw

    Returns
    -------
    lat : `~astropy.units.Quantity`
        Latitude of a sunspot drawn from the sunspot latitude distribution.
    """
    return sunspot_latitude_inverse_transform(np.random.rand(n),
                                              mean_latitude=mean_latitude)


def sunspot_umbral_area_distribution(log_area_uhem):
    """
    Approximate log-normal distribution of sunspot umbral areas
    """
    return np.exp(-0.5 * (log_area_uhem - 4.1)**2 / 1.0**2)


def sunspot_umbral_area_inverse_transform(x):
    """
    Use inverse transform sampling to randomly draw spot areas from the
    sunspot umbral area distribution, for a uniform random variate ``x`` on the
    range [0,1).

    Parameters
    ----------
    x : `~np.ndarray` or float
        Uniform random variate on [0, 1)

    Returns
    -------
    umbral_areas : `~numpy.ndarray`
        Umbral area(s) of sunspot(s) drawn from the sunspot umbral area
        distribution.
    """
    log_areas_uhem = np.linspace(0, 9, 1000)
    prob = np.cumsum(sunspot_umbral_area_distribution(log_areas_uhem))
    prob /= np.max(prob)
    return np.interp(x, prob, log_areas_uhem)


def draw_random_sunspot_radii(n):
    """
    Draw one or more random samples from the sunspot radius distribution.

    Parameters
    ----------
    n : int
        Number of random sunspot radii to draw

    Returns
    -------
    rspot_rstar : `~numpy.ndarray`
        Radii of a sunspots drawn from the sunspot radius distribution,
        in units of stellar radii.
    """
    umbral_areas_uhem = sunspot_umbral_area_inverse_transform(np.random.rand(n))
    total_to_umbral_area = 5  # ratio of total spot area to area in umbra
    rspot_rstar = np.sqrt(1e-6 * 2 * total_to_umbral_area * umbral_areas_uhem)
    return rspot_rstar