## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
# parasite_drag_total.py
#
# Created:  Jan 2014, T. Orra
# Modified: Jan 2016, E. Botero
#           Jul 2017, M. Clarke

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np

# ----------------------------------------------------------------------
#  Total Parasite Drag
# ----------------------------------------------------------------------

## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
def parasite_total(state,settings,geometry):
    """Sums component parasite drag

    Assumptions:
    None

    Source:
    None

    Inputs:
    geometry.reference_area                             [m^2]
    geometry.wings.areas.reference                      [m^2]
    geometry.fuselages.areas.front_projected            [m^2]
    geometry.propulsors.number_of_engines               [Unitless]
    geometry.propulsors.nacelle_diameter                [m]
    conditions.aerodynamics.drag_breakdown.
      parasite[wing.tag].parasite_drag_coefficient      [Unitless]
      parasite[fuselage.tag].parasite_drag_coefficient  [Unitless]
      parasite[propulsor.tag].parasite_drag_coefficient [Unitless]


    Outputs:
    total_parasite_drag                                 [Unitless]

    Properties Used:
    N/A
    """

    # unpack
    conditions             = state.conditions
    wings                  = geometry.wings
    fuselages              = geometry.fuselages
    propulsors             = geometry.propulsors
    vehicle_reference_area = geometry.reference_area
   
    #compute parasite drag total
    total_parasite_drag = 0.0
   
    # from wings
    for wing in wings.values():
        parasite_drag = conditions.aerodynamics.drag_breakdown.parasite[wing.tag].parasite_drag_coefficient
        conditions.aerodynamics.drag_breakdown.parasite[wing.tag].parasite_drag_coefficient = parasite_drag * wing.areas.reference/vehicle_reference_area
        total_parasite_drag += parasite_drag * wing.areas.reference/vehicle_reference_area

    # from fuselage
    for fuselage in fuselages.values():
        if fuselage.tag == 'fuselage_bwb':
            continue
        parasite_drag = conditions.aerodynamics.drag_breakdown.parasite[fuselage.tag].parasite_drag_coefficient
        conditions.aerodynamics.drag_breakdown.parasite[fuselage.tag].parasite_drag_coefficient = parasite_drag * fuselage.areas.front_projected/vehicle_reference_area
        total_parasite_drag += parasite_drag * fuselage.areas.front_projected/vehicle_reference_area

    # from propulsors
    if propulsors.values()[0]['arch_tag'] == 'conventional': # conventional propulsors
        for propulsor in propulsors.values():
            ref_area = np.pi / 4.0 * propulsor.nacelle_diameter**2
            parasite_drag = conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient
            conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient  = parasite_drag * ref_area/vehicle_reference_area * propulsor.number_of_engines
            total_parasite_drag += parasite_drag * ref_area/vehicle_reference_area * propulsor.number_of_engines
    elif propulsors.values()[0]['arch_tag'] == 'unified': # unified model
        for propulsor in propulsors.values():
            ref_area_mech = np.pi / 4.0 * propulsor.mech_nac_dia**2.0
            ref_area_elec = np.pi / 4.0 * propulsor.elec_nac_dia**2.0
            parasite_drag_mech = \
                conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient_mech            
            parasite_drag_elec = \
                conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient_elec
            conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient_mech  = parasite_drag_mech * ref_area_mech / vehicle_reference_area * propulsor.number_of_engines_mech
            conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient_elec  = parasite_drag_elec * ref_area_elec / vehicle_reference_area * propulsor.number_of_engines_elec
            conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient = \
                conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient_mech + \
                conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient_elec            
            total_parasite_drag += conditions.aerodynamics.drag_breakdown.parasite[propulsor.tag].parasite_drag_coefficient
    else:
        raise Exception('Propulsion network should have arch_tag set to either "conventional" or "unified"')

    # from pylons
    try:
        parasite_drag = conditions.aerodynamics.drag_breakdown.parasite['pylon'].parasite_drag_coefficient
    except:
        parasite_drag = 0. # not currently available for supersonics

    total_parasite_drag += parasite_drag

    # dump to conditions
    state.conditions.aerodynamics.drag_breakdown.parasite.total = total_parasite_drag

    return total_parasite_drag