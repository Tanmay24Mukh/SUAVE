## @ingroup Input_Output-Results
# print_SNOPT_summary.py

# Created: M. Kruger
# Updated:

def print_SNOPT_summary(filename = 'SNOPT_summary.out'):
    """Function reads and prints information from SNOPT summary file"""

    print('-------SNOPT output summary-------\n')

    linesList = [line.rstrip('\n') for line in open(filename)]

    converged = 0
    for i, line in enumerate(linesList):
        if 'SNOPTC EXIT' in line:
            print(line)
        if 'SNOPTC INFO' in line:
            print(line)
        if 'SNOPTC EXIT   0 -- finished successfully' in line:
            converged = 1

    print('---------------END---------------\n')

    return converged