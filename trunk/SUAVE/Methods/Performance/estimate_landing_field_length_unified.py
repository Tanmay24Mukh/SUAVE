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
def estimate_landing_field_length_unified(vehicle, analyses, results, airport, mass_fuel, obst_height=15.2):
    """ Estimate landing field length for unified propsys energy network
        Some parts based on estimate_takeoff_field_length_unified

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
    landing_field_length                   [m]

    Assumptions:
    Idle thrust is 10% of total thrust at touchdown speed

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
    mu_brake        = airport.rolling_resistance_brake

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
        maximum_lift_coefficient = vehicle.maximum_lift_coefficient_landing
    except:
        raise ValueError("Maximum lift coefficient calculation error. Please, check inputs")

    # ==============================================
    # Computing stall speed
    # ==============================================
    Vstall = (2.0 * mass_to * sea_level_gravity * rho / (rho * reference_area * maximum_lift_coefficient)) ** 0.5

    mass_land = mass_to - mass_fuel

    # Approach
    Vf = 1.23 * Vstall
    gamma_app = np.deg2rad(3)
    R = Vf**2 / (0.2 * sea_level_gravity)
    hf = R * (1 - np.cos(gamma_app))
    sa = (obst_height - hf) / np.tan(gamma_app)

    # Flare    
    Tf = 0.1 * PKtot / Vf
    L_D = 0.8 * results.mission.segments['descent'].conditions.aerodynamics.lift_coefficient[0] /\
        results.mission.segments['descent'].conditions.aerodynamics.drag_coefficient[0]
    sf = R * (Tf / (mass_land * sea_level_gravity) - (1 / L_D))

    if sf < 0:
        sf = 0

    hf = R * (1 - np.cos(gamma_app))

    if hf > obst_height:
        sf = np.sqrt(R**2 - (R - obst_height)**2)
        sa = 0
    else:
        sa = (obst_height - hf) / np.tan(gamma_app)

    # Ground roll
    Vi = Vtd = 1.15 * Vstall
    Vf = 0.0
    CLr = 0.1
    CD0r = 1.2 * results.mission.segments['descent'].conditions.aerodynamics.drag_breakdown.parasite.total[0]
    Kr = 1 / (np.pi * e * AR)

    T_g = 0.1 * PKtot / Vtd

    KA = rho / (2 * vehicle.wing_loading) * (mu_brake * CLr - CD0r - Kr * CLr**2)
    KT = (T_g / (mass_land * sea_level_gravity)) - mu_brake
    sg = (1 / (2 * sea_level_gravity * KA)) * np.log((KT + KA * Vf**2) / (KT + KA * Vi**2))
   
    return sa + sf + sg
