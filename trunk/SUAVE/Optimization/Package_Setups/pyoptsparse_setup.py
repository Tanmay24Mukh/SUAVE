## @ingroup Optimization-Package_Setups
# pyopt_setup.py
#
# Created:  Aug 2018, E. Botero
# Modified: Mar 2019, M. Kruger

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
import numpy as np
from SUAVE.Optimization import helper_functions as help_fun

# ----------------------------------------------------------------------
#  Pyopt_Solve
# ----------------------------------------------------------------------

## @ingroup Optimization-Package_Setups
def Pyoptsparse_Solve(problem, solver='SNOPT', FD='single', sense_step=1.0E-6,  nonderivative_line_search=False):
    """ This converts your SUAVE Nexus problem into a PyOptsparse optimization problem and solves it.
        Pyoptsparse has many algorithms, they can be switched out by using the solver input. 

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        problem                   [nexus()]
        solver                    [str]
        FD (parallel or single)   [str]
        sense_step                [float]
        nonderivative_line_search [bool]

        Outputs:
        outputs                   [list]

        Properties Used:
        None
    """      
   
    # Have the optimizer call the wrapper
    mywrap = lambda x:PyOpt_Problem(problem,x)
   
    inp = problem.optimization_problem.inputs
    obj = problem.optimization_problem.objective
    con = problem.optimization_problem.constraints
   
    if FD == 'parallel':
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        myrank = comm.Get_rank()      
   
    # Instantiate the problem and set objective

    try:
        import pyoptsparse as pyOpt
    except:
        raise ImportError('No version of pyOptsparse found')
        
    
    opt_prob = pyOpt.Optimization('SUAVE',mywrap)
    for ii in range(len(obj)):
        opt_prob.addObj(obj[ii,0])    
       
    # Set inputs
    nam = inp[:,0] # Names
    ini = inp[:,1] # Initials
    bnd = inp[:,2] # Bounds
    scl = inp[:,3] # Scale
    typ = inp[:,4] # Type
   
    # Pull out the constraints and scale them
    bnd_constraints = help_fun.scale_const_bnds(con)
    scaled_constraints = help_fun.scale_const_values(con,bnd_constraints)
    x   = ini/scl
   
    for ii in range(0,len(inp)):
        lbd = (bnd[ii][0]/scl[ii])
        ubd = (bnd[ii][1]/scl[ii])
        #if typ[ii] == 'continuous':
        vartype = 'c'
        #if typ[ii] == 'integer':
            #vartype = 'i'
        opt_prob.addVar(nam[ii],vartype,lower=lbd,upper=ubd,value=x[ii])
       
    # Setup constraints  
    for ii in range(0,len(con)):
        name = con[ii][0]
        edge = scaled_constraints[ii]
       
        if con[ii][1]=='<':
            opt_prob.addCon(name, upper=edge)
        elif con[ii][1]=='>':
            opt_prob.addCon(name, lower=edge)
        elif con[ii][1]=='=':
            opt_prob.addCon(name, lower=edge,upper=edge)

    # Finalize problem statement and run
    print(opt_prob)
   
    if solver == 'SNOPT':
        opt = pyOpt.SNOPT()
        CD_step = (sense_step**2.)**(1./3.)  #based on SNOPT Manual Recommendations
        opt.setOption('Function precision', sense_step**2)
        opt.setOption('Difference interval', sense_step)
        opt.setOption('Central difference interval', CD_step)
        opt.setOption('Central difference interval', CD_step)
        opt.setOption('Major optimality tolerance', sense_step)
        
    elif solver == 'SLSQP':
        opt = pyOpt.SLSQP()
        # opt.setOption('ACC', sense_step**2)  # Default
        opt.setOption('ACC', 1e-16)  # Default
         
    elif solver == 'FSQP':
        opt = pyOpt.FSQP()
        
    elif solver == 'PSQP':
        opt = pyOpt.PSQP()  
        
    elif solver == 'NSGA2':
        opt = pyOpt.NSGA2(pll_type='POA')
        opt.setOption('PopSize', 20)
        opt.setOption('maxGen', 5)
    
    elif solver == 'ALPSO':
        #opt = pyOpt.pyALPSO.ALPSO(pll_type='DPM') #this requires DPM, which is a parallel implementation
        opt = pyOpt.ALPSO()
        # opt.setOption('SwarmSize', 10)
        # opt.setOption('maxOuterIter', 3)
        # opt.setOption('maxInnerIter', 6)
        # opt.setOption('minInnerIter', 3)

    elif solver == 'CONMIN':
        opt = pyOpt.CONMIN() 
        
    elif solver == 'IPOPT':
        opt = pyOpt.IPOPT()  
    
    elif solver == 'NLPQLP':
        opt = pyOpt.NLQPQLP()     
    
    elif solver == 'NLPY_AUGLAG':
        opt = pyOpt.NLPY_AUGLAG()       
        
    if nonderivative_line_search==True:
        opt.setOption('Nonderivative linesearch')
    if FD == 'parallel':
        outputs = opt(opt_prob, sens='FD',sensMode='pgc')
        
    elif solver == 'SNOPT':
        # outputs = opt(opt_prob, sens='FD', sensStep = sense_step, storeHistory='snopt.hist', hotStart='ALPSO.hist')
        outputs = opt(opt_prob, sens='FD', sensStep = sense_step, storeHistory='snopt.hist')

    elif solver == 'SLSQP':
        # outputs = opt(opt_prob, sens='FD', sensStep = sense_step, hotStart='NSGA2.hist')
        outputs = opt(opt_prob, sens='FD', sensStep=sense_step)
  
    elif solver == 'ALPSO':
        outputs = opt(opt_prob, storeHistory='ALPSO.hist')

    elif solver == 'NSGA2':
        outputs = opt(opt_prob, storeHistory='NSGA2.hist')

    else:
        outputs = opt(opt_prob)        
   
    return outputs


# ----------------------------------------------------------------------
#  Problem Wrapper
# ----------------------------------------------------------------------

## @ingroup Optimization-Package_Setups
def PyOpt_Problem(problem,xdict):
    """ This wrapper runs the SUAVE problem and is called by the PyOpt solver.
        Prints the inputs (x) as well as the objective values and constraints.
        If any values produce NaN then a fail flag is thrown.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        problem   [nexus()]
        x         [array]

        Outputs:
        obj       [float]
        cons      [array]
        fail      [bool]

        Properties Used:
        None
    """      
   
    x = []
    
    for key, val in xdict.items():
        x.append(float(val))
        
   
    obj   = problem.objective(x)
    const = problem.all_constraints(x).tolist()
    fail  = np.array(np.isnan(obj.tolist()) or np.isnan(np.array(const).any())).astype(int)
    
    funcs = {}
    
    for ii, obj in enumerate(obj):
        funcs[problem.optimization_problem.objective[ii,0]] = obj
        
    for ii, con in enumerate(const):
        funcs[problem.optimization_problem.constraints[ii,0]] = con

       
    print('Inputs')
    print(x)
    print('Obj')
    print(obj)
    print('Con')
    print(const)
   
    return funcs, fail

