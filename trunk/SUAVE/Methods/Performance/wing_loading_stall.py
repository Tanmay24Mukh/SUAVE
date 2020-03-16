## @ingroup Methods-Performance
# wing_loading_stall.py
#
# Created: Oct 2019, M. Kruger
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
def wing_loading_stall(vehicle, analyses, airport):
    """ Estimate stall speed

    Source:
    Raymer

    Inputs:
    # vehicle
      fuel_fraction - Fraction of total wing volume usable for fuel storage

    Outputs:
    wing_fuel_vol                   [m^3]

    Properties Used:
    N/A
    """        

    # ==============================================
    # Unpack
    # ==============================================
    wing = vehicle.wings.main_wing
    t_c = wing.thickness_to_chord
    lambda_w = wing.sweeps.quarter_chord
    Sw = vehicle.reference_area
    AR = wing.aspect_ratio
    kQ = 0.95
    atmo            = analyses.base.atmosphere
    mass_to = vehicle.mass_properties.takeoff
    altitude        = airport.altitude * Units.ft
    delta_isa       = airport.delta_isa

    # ==============================================
    # Computing atmospheric conditions
    # ==============================================
    atmo_values       = atmo.compute_values(altitude,delta_isa)
    conditions        = SUAVE.Analyses.Mission.Segments.Conditions.Aerodynamics()
    
    p   = atmo_values.pressure
    T   = atmo_values.temperature
    rho = atmo_values.density
    a   = atmo_values.speed_of_sound
    mu  = atmo_values.dynamic_viscosity
    sea_level_gravity = atmo.planet.sea_level_gravity

    

    # ==============================================
    # Determining vehicle maximum lift coefficient
    # ==============================================
    try:   # aircraft maximum lift informed by user
        maximum_lift_coefficient = vehicle.maximum_lift_coefficient_takeoff
    except:
        # Using semi-empirical method for maximum lift coefficient calculation
        from SUAVE.Methods.Aerodynamics.Fidelity_Zero.Lift import compute_max_lift_coeff

        # Condition to CLmax calculation: 90KTAS @ 10000ft, ISA
        conditions  = atmo.compute_values(10000. * Units.ft)
        conditions.freestream=Data()
        conditions.freestream.density   = conditions.density
        conditions.freestream.dynamic_viscosity = conditions.dynamic_viscosity
        conditions.freestream.velocity  = 90. * Units.knots
        try:
            maximum_lift_coefficient, induced_drag_high_lift = compute_max_lift_coeff(vehicle,conditions)
            vehicle.maximum_lift_coefficient = maximum_lift_coefficient
        except:
            raise ValueError("Maximum lift coefficient calculation error. Please, check inputs")

    # ==============================================
    # Computing speeds (Vs, Vapp)
    # ==============================================
    Vstall = (2.0 * mass_to * sea_level_gravity * rho / (rho * Sw * maximum_lift_coefficient)) ** 0.5

    wing_loading_stall = 0.5 * rho * Vstall**2 * maximum_lift_coefficient
    
    return wing_loading_stall
