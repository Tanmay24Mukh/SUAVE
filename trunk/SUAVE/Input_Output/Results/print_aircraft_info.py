## @ingroup Input_Output-Results
# print_aircraft_info.py

# Created: M. Kruger
# Updated:

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------
import datetime
from .identify_architecture import identify_arch

# ----------------------------------------------------------------------
#  Print output file with weight breakdown
# ----------------------------------------------------------------------
## @ingroup Input_Output-Results
def print_aircraft_info(vehicle, filename = 'aircraft_info.dat'):
    """
    Prints breakdown of important high-level aircraft parameters

    Assumptions:
    N/A

    Source:
    N/A

    Inputs:
    vehicle
    filename (optional)  <string> Determines the name of the saved file

    Outputs:
    filename              Saved file with name as above

    Properties Used:
    N/A
    """
    #unpack
    # propsys = vehicle.propulsors.unified_propsys
    # propsys_info = vehicle.propulsors.unified_propsys.info
    # nr_fans_mech = propsys_info.nr_fans_mech
    # nr_fans_elec = propsys_info.nr_fans_elec
    # nr_turbines = propsys.nr_turbines

    # start printing
    fid = open(filename,'w')   # Open output file
    fid.write('Output file with high level aircraft parameters\n\n') #Start output printing
    fid.write(' WING:\n')
    fid.write(' Wing span [m]   = {}\n'.format(vehicle.wings.main_wing.spans.projected))
    fid.write(' Wing area [m^2] = {}\n'.format(vehicle.wings.main_wing.areas.reference))
    fid.write(' ------------------------\n')
    fid.write(' Horizontal tail:\n')
    fid.write(' Tail span [m]   = {}\n'.format(vehicle.wings.horizontal_stabilizer.spans.projected))
    fid.write(' Tail area [m^2] = {}\n'.format(vehicle.wings.horizontal_stabilizer.areas.reference))
    fid.write(' ------------------------\n')
    fid.write(' Vertical tail:\n')
    fid.write(' Tail span [m]   = {}\n'.format(vehicle.wings.vertical_stabilizer.spans.projected))
    fid.write(' Tail area [m^2] = {}\n'.format(vehicle.wings.vertical_stabilizer.areas.reference))
    fid.write(' ------------------------\n')
    fid.write(' PROPULSION SYSTEM:\n')
    fid.write(' Battery mass [kg]   = {}\n'.format(vehicle.propulsors.unified_propsys.battery.mass_properties.mass))
    fid.write(' Battery volume [m^3]   = {}\n'.format(vehicle.propulsors.unified_propsys.battery.max_energy / vehicle.propulsors.unified_propsys.battery.specific_volume))
    fid.write(' ------------------------\n')
    fid.write(' WING LOADING:\n')
    fid.write(' Wing loading [kg/m^2] = {}\n'.format(vehicle.wing_loading))
    # Print timestamp
    fid.write('\n'+ 43*'-'+ '\n' + datetime.datetime.now().strftime(" %A, %d. %B %Y %I:%M:%S %p"))
    # done
    fid.close

# ----------------------------------------------------------------------
#   Module Test
# ----------------------------------------------------------------------
if __name__ == '__main__':
    print(' Error: No test defined ! ')
