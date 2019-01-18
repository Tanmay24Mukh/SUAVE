# @ingroup Methods-Weights-Correlations-Propulsion
# unified_propsys.py
#
# Created:  Oct 2018, M. Kruger
# Modified:

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
from SUAVE.Core import Units
from SUAVE.Methods.Power_Balance.calculate_powers import calculate_powers

# package imports
import numpy as np

# ----------------------------------------------------------------------
#   Unified Propulsion System
# ----------------------------------------------------------------------

# @ingroup Methods-Weights-Correlations-Propulsion


def unified_propsys(mdotm, mdote, PKtot, Ebat, Pbat_max, fL, fS, weight_factor=1):
    """ Calculate the weight of the entire propulsion system

    Assumptions:
            N/A

    Source:
        Kruger, Michael, et al.
        "Electrified Aircraft Trade-Space Exploration."
        2018 Aviation Technology, Integration, and Operations Conference.
        2018.

    Inputs:
            mdotm - array of mechanical fan mass flows [kg/s]
            mdote - array of electrical fan mass flows [kg/s]
            PKtot - Total installed PK [W]
            fL    - Load electrification factor [-]
            fS    - Source electrification factor [-]

    Outputs:
            weight - weight of the full propulsion system [kg]

    Properties Used:
            N/A
    """
    # Sizing constants from LEARN. FIXME - Some of these should maybe be specified in inputs
    Kcore = 45.605
    Kfan = 1.2972
    Knace = 4.5641
    cmnace = 1.0
    c_core = 400.0 * Units['kJ/kg']
    pm_mot = 8.0 * Units['hp/lb']
    pm_pe = 10.0 * Units['hp/lb']
    pm_tms = 8.0 * Units['hp/lb']
    e_sbat = 500.0 * Units['Wh/kg']  # battery specific energy
    p_sbat = 2985.0 * Units['W/kg']  # battery specific power

    # Constants FIXME - Some of these should maybe be specified in inputs
    # Assumed efficiencies
    eta_fan = 0.9  # Fan
    eta_mot = 0.95  # Motor
    eta_pe  = 0.98  # Power electronics
    eta_bat = 0.5  # For sizing condition battery is at max power, thus eta = 0.5

    # Fan and nacelle weights
    m_fanm = (Kfan * mdotm**1.2).sum()
    m_nacm = (cmnace * Knace * mdotm).sum()
    m_fane = (Kfan * mdote**1.2).sum()
    m_nace = (cmnace * Knace * mdote).sum()

    # Calculate powers  NOTE - Negative values set to zero
    [PKe, PKm, PfanE, PfanM, Pmot, Pinv, Pbat, Pturb, Pgenmot, Pconv, Plink] = \
    calculate_powers(PKtot, fS, fL, eta_pe, eta_mot, eta_fan)

    mdot_core = Pturb / c_core

    m_core        = Kcore * mdot_core**1.2
    m_prop_mot    = Pmot / pm_mot
    m_pe_prop_mot = Pinv / pm_pe
    m_gen         = Pgenmot / pm_mot
    m_pe_link     = Pconv / pm_pe

    # Size battery based on power or energy
    # Power
    m_bat_p = Pbat / (p_sbat * eta_bat)
    # Energy
    m_bat_e = Ebat / e_sbat

    m_bat = np.max([m_bat_p, m_bat_e])

    mprop = m_core + m_fanm + m_fane + m_nacm + m_nace + m_prop_mot + m_pe_prop_mot + \
            m_bat + m_gen + m_pe_link

    # Thermal management system
    q_bat  = (1.0 - eta_bat) * Pbat
    q_gen  = (1.0 - eta_mot) * Pgenmot
    q_conv = (1.0 - eta_pe) * Pconv
    q_inv  = (1.0 - eta_pe) * Pinv
    q_mot  = (1.0 - eta_mot) * Pmot
    
    q_tot  = q_bat + q_gen + q_conv + q_inv + q_mot

    mass_tms = q_tot / pm_tms

    mass_propsys = (mprop + mass_tms) * weight_factor

    return mass_propsys