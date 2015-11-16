# estimate_landing_field_length.py
#
# Created:  Tarik, Carlos, Celso, Jun 2014
# Modified: M. Vegh Apr. 2015

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

#SUAVE Imports
import SUAVE
from   SUAVE.Core            import Data
from   SUAVE.Core            import Units

# package imports
import numpy as np

# ----------------------------------------------------------------------
#  Compute field length required for landing
# ----------------------------------------------------------------------
def estimate_landing_field_length(vehicle,analyses,airport):
    """ SUAVE.Methods.Performance.estimate_landing_field_length(vehicle,config,airport):
        Computes the landing field length for a given vehicle condition in a given airport

        Inputs:
            vehicle	 - SUAVE type vehicle

            config   - data dictionary with fields:
                Mass_Properties.landing    - Landing weight to be evaluated
                S                          - Wing Area
                Vref_VS_ratio              - Ratio between Approach Speed and Stall speed
                                             [optional. Default value = 1.23]
                maximum_lift_coefficient   - Maximum lift coefficient for the config
                                             [optional. Calculated if not informed]

    airport   - SUAVE type airport data, with followig fields:
                atmosphere                  - Airport atmosphere (SUAVE type)
                altitude                    - Airport altitude
                delta_isa                   - ISA Temperature deviation


        Outputs:
            landing_field_length            - Landing field length


        Assumptions:
      		- Landing field length calculated according to Torenbeek, E., "Advanced
    Aircraft Design", 2013 (equation 9.25)
            - Considering average aav/g values of two-wheel truck (0.40)
    """
   
    # ==============================================
        # Unpack
    # ==============================================
    atmo            = analyses.base.atmosphere
    altitude        = airport.altitude * Units.ft
    delta_isa       = airport.delta_isa
    weight          = vehicle.mass_properties.landing
    reference_area  = vehicle.reference_area
    try:
        Vref_VS_ratio = config.Vref_VS_ratio
    except:
        Vref_VS_ratio = 1.23

    # ==============================================
    # Computing atmospheric conditions
    # ==============================================
    conditions0       = atmo.compute_values(0.)
    atmo_values       = atmo.compute_values(altitude)
    conditions        =SUAVE.Analyses.Mission.Segments.Conditions.Aerodynamics()
    p                 = atmo_values.pressure
    T                 = atmo_values.temperature
    rho               = atmo_values.density
    a                 = atmo_values.speed_of_sound
    mu                = atmo_values.dynamic_viscosity
                      
    p0                = conditions0.pressure
    T0                = conditions0.temperature
    rho0              = conditions0.density
    a0                = conditions0.speed_of_sound
    mu0               = conditions0.dynamic_viscosity
    T_delta_ISA       = T + delta_isa
    sigma_disa        = (p/p0) / (T_delta_ISA/T0)
    rho               = rho0 * sigma_disa
    a_delta_ISA       = atmo.fluid_properties.compute_speed_of_sound(T_delta_ISA)
    mu                = 1.78938028e-05 * ((T0 + 120) / T0 ** 1.5) * ((T_delta_ISA ** 1.5) / (T_delta_ISA + 120))
    sea_level_gravity = atmo.planet.sea_level_gravity
   
    # ==============================================
    # Determining vehicle maximum lift coefficient
    # ==============================================
    
    try:   # aircraft maximum lift informed by user
        maximum_lift_coefficient = vehicle.maximum_lift_coefficient
    except:
        # Using semi-empirical method for maximum lift coefficient calculation
        from SUAVE.Methods.Aerodynamics.Fidelity_Zero.Lift import compute_max_lift_coeff

        
        conditions.freestream=Data()
        conditions.freestream.density   = rho
        conditions.freestream.dynamic_viscosity = mu
        conditions.freestream.velocity  = 90. * Units.knots
        
        try:
            maximum_lift_coefficient, induced_drag_high_lift =   compute_max_lift_coeff(vehicle,conditions)
            vehicle.maximum_lift_coefficient                 =   maximum_lift_coefficient
            
        except:
            raise ValueError, "Maximum lift coefficient calculation error. Please, check inputs"
    # ==============================================
    # Computing speeds (Vs, Vref)
    # ==============================================
    stall_speed  = (2 * weight * sea_level_gravity / (rho * reference_area * maximum_lift_coefficient)) ** 0.5
    Vref         = stall_speed * Vref_VS_ratio
    
    # ========================================================================================
    # Computing landing distance, according to Torenbeek equation
    #     Landing Field Length = k1 + k2 * Vref**2
    # ========================================================================================

    # Defining landing distance equation coefficients
    try:
        landing_constants = config.landing_constants # user defined
    except:  # default values - According to Torenbeek book
        landing_constants = np.zeros(3)
        landing_constants[0] = 250.
        landing_constants[1] =   0.
        landing_constants[2] =  2.485  / sea_level_gravity  # Two-wheels truck : [ (1.56 / 0.40 + 1.07) / (2*sea_level_gravity) ]
##        landing_constants[2] =   2.9725 / sea_level_gravity  # Four-wheels truck: [ (1.56 / 0.32 + 1.07) / (2*sea_level_gravity) ]

    # Calculating landing field length
    landing_field_length = 0.
    for idx,constant in enumerate(landing_constants):
        landing_field_length += constant * Vref**idx
    
    
    # return
    return landing_field_length
