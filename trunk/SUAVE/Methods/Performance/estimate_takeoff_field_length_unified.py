## @ingroup Methods-Performance
# estimate_balanced_field_length.py
#
# Created: June 2019, M. Kruger
# Modified:

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
import SUAVE
from SUAVE.Core import Data, Units

# Package imports
import numpy as np

# ----------------------------------------------------------------------
#  Compute field length required for takeoff
# ----------------------------------------------------------------------

## @ingroup Methods-Performance
def estimate_takeoff_field_length_unified(vehicle, analyses, results, airport, obst_height=15.2):
    """ Estimate takeoff field length for unified propsys energy network
        Some parts based on existing estimate_take_off_field_length method

    Source:
    Raymer, D.,
    2012.
    Aircraft Design: A Conceptual Approach
    Fifth Edition.
    American Institute of Aeronautics and Astronautics, Inc.

    Inputs:
    vehicle
    analyses
    airport
    obst_height     [m]

    Outputs:
    takeoff_field_length    [m]

    Properties Used:
    N/A
    """

    # ==============================================
    # Unpack
    # ==============================================
    atmo            = analyses.base.atmosphere
    altitude        = airport.altitude * Units.ft
    delta_isa       = airport.delta_isa
    mass_to         = vehicle.mass_properties.takeoff
    reference_area  = vehicle.reference_area
    PKtot           = vehicle.PKtot
    AR              = vehicle.wings.main_wing.aspect_ratio
    e               = vehicle.wings.main_wing.span_efficiency
    mu_rol          = airport.rolling_resistance_free

    # ==============================================
    # Computing atmospheric conditions
    # ==============================================
    atmo_values       = atmo.compute_values(altitude,delta_isa)
    conditions        = SUAVE.Analyses.Mission.Segments.Conditions.Aerodynamics()

    rho = atmo_values.density
    sea_level_gravity = atmo.planet.sea_level_gravity

    # ==============================================
    # Determining vehicle maximum lift coefficient
    # ==============================================
    try:   # aircraft maximum lift informed by user
        maximum_lift_coefficient = vehicle.maximum_lift_coefficient_takeoff
    except:
        raise ValueError("No maximum lift coefficient specified")

    # ==============================================
    # Computing stall speed
    # ==============================================
    Vstall = (2.0 * mass_to * sea_level_gravity * rho  / (rho * reference_area * maximum_lift_coefficient)) ** 0.5

    # Ground roll
    Vi = 0.0
    Vf = Vto = 1.1 * Vstall
    CLr = 0.1
    CD0r = 1.2 * results.mission.segments['climb'].conditions.aerodynamics.drag_breakdown.parasite.total[0]
    Kr = 1 / (np.pi * e * AR)

    T_g = PKtot / (1 / np.sqrt(2) * Vto)

    KA = rho / (2 * vehicle.wing_loading) * (mu_rol * CLr - CD0r - Kr * CLr**2)
    KT = (T_g / (mass_to * sea_level_gravity)) - mu_rol
    sg = (1 / (2 * sea_level_gravity * KA)) * np.log((KT + KA * Vf**2) / (KT + KA * Vi**2))

    # Transition
    Vt = 1.15 * Vstall
    R = Vt**2 / (0.2 * sea_level_gravity)
    Tt = PKtot / Vt
    L_D = 0.8 * results.mission.segments['climb'].conditions.aerodynamics.lift_coefficient[0] /\
        results.mission.segments['climb'].conditions.aerodynamics.drag_coefficient[0]
    gamma_climb = np.arcsin(Tt / (mass_to * sea_level_gravity) - (1 / L_D))
    st = R * (Tt / (mass_to * sea_level_gravity) - (1 / L_D))
    ht = R * (1 - np.cos(gamma_climb))

    if ht > obst_height:
        st = np.sqrt(R**2 - (R - obst_height)**2)
        sc = 0
    else:
        sc = (obst_height - ht) / np.tan(gamma_climb)

    return sg + st + sc
