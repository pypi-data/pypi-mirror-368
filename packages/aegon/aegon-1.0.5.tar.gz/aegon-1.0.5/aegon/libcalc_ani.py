time
import warnings
warnings.filterwarnings("ignore", message="cuaev not installed")
import os
import sys
import torchani
from ase.optimize import BFGS
import contextlib
from joblib import Parallel, delayed
#-------------------------------------------------------------------------------
eVtokcalpermol = 23.060548012069496
#-------------------------------------------------------------------------------
@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
#-------------------------------------------------------------------------------
def ANI_single(atoms, opt='ANI1ccx', preclist=[1E-03, 1E-04, 1E-05]):
    timein=time.strftime("%c")
    print('%s at %s' %(atoms.info['i'], timein))
    moleculeout=atoms.copy()
    for prec in preclist:
        with suppress_stdout():
            calculator = {
                'ANI1x':   torchani.models.ANI1x().ase(),
                'ANI1ccx': torchani.models.ANI1ccx().ase(),
                'ANI2x':   torchani.models.ANI2x().ase()
            }[opt]
        moleculeout.calc = calculator
        dyn = BFGS(moleculeout, logfile=None)
        dyn.run(fmax=prec, steps=200)
    energy = moleculeout.get_potential_energy()
    moleculeout.info['e'] = energy * eVtokcalpermol
    return moleculeout
#-------------------------------------------------------------------------------
def ANI(mol_list, n_jobs = 1, opt='ANI1ccx', preclist=[1E-03, 1E-04, 1E-05]):
    results = Parallel(n_jobs = n_jobs)(delayed(ANI_single)(mol, opt, preclist) for mol in mol_list)
    return results
#-------------------------------------------------------------------------------
