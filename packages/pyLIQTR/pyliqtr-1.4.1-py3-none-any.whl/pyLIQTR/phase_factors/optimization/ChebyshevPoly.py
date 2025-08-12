"""
Copyright (c) 2024 Massachusetts Institute of Technology 
SPDX-License-Identifier: BSD-2-Clause
"""
import numpy                as np
import scipy.special        as sfn



class ChebyshevPoly:



    def __init__(self,coeffs=None,parity=None):

        self.N                 =  None
        self.deg               =  None
        self.coeffs            =  None
        self.parity            =  parity
        self.type              =  None

        if (coeffs is not None):
            self.coeffs           = coeffs
            self.N                = len(coeffs)
            self.deg              = self.N - 1
            self.parity           = parity





    def set_type(self,string):

        self.type = string
        return





    def set_parity(self,parity):

        self.parity = parity
        return





    def zero_poly(self,N,parity=None):

        self.N      = N
        self.deg    = N-1
        self.coeffs = np.zeros(N)

        if (parity is not None):
            self.parity = parity
        else:
            self.parity = N % 2

        return






    def set_coeffs(self,cfs_set,terms="all",parity=None):

        if (terms == "all"):
            self.coeffs = cfs_set
            self.parity = parity
            self.N      = len(cfs_set)
            self.deg    = self.N - 1
        elif (terms == "even"):
            N_cf = 2*len(cfs_set)
            self.coeffs[0:N_cf:2] = cfs_set
        elif (terms == "odd"):
            N_cf = 2*len(cfs_set)+1
            self.coeffs[1:N_cf:2] = cfs_set
        else:
            print("Invalid term specification. Must be even, odd, or all.")

        return

    # 
    # def coeffs(self):
    #     return(self.coeffs)

    def evens(self):
        return(self.coeffs[0:self.N:2])

    def odds(self):
        return(self.coeffs[1:self.N:2])


    def set_evens(self,cfs_set):

        N_cf = 2*len(cfs_set)

        # need to ultimately check and make sure coefficients will fit
        # into the target array, make sure array exists, etc.

        self.coeffs[0:N_cf:2] = cfs_set
        return





    def set_odds(self,cfs_set):

        N_cf = 2*len(cfs_set)+1

        # need to ultimately check and make sure coefficients will fit
        # into the target array, make sure array exists, etc.
        self.coeffs[1:N_cf:2] = cfs_set
        return






    def coeffs(self,coeffs=None,parity=None):

        # do we really want parity to be defined?  shouldn't we just assume
        # it is none if the value of parity is None or or otherwise?

        cflag = (coeffs is not None)
        pflag = (parity is not None)

        if (cflag and pflag):
            self.N       =  len(coeffs)
            self.deg     =  N-1
            self.coeffs  =  coeffs
            self.parity  =  parity

        elif (not (cflag and pflag)):
            print("\nCoefficients and parity are required for a ChebyshevPoly.\n")
            exit()

        else:
            return (self.coeffs)






    def eval(self,x,terms=None):


        ### really should split this out into itself and its mpmath variant,
        ### so it is available for user manipualation - and just put a
        ### wrapper here for eval (can also have it evaluate for cosh terms)

        x     = self._handle_scalar(x)      # Transforms scalar input to a 0-d numpy array

        fx    = np.zeros(len(x))      # Store evaluation of of f(x)
        acx   = np.arccos(x)          # Arccos appearing in Chebyshev terms

        ## Evaluates only even or odd terms in the expansion, assuming
        ## that the list of coefficients contains both even and odd parity
        ## terms.
        ##
        if ((terms is not None) and (self.parity not in [0,1])):

            if   (terms == 0):
                for k in range(0,self.N,2):
                    fx += self.coeffs[k] * np.cos(k*acx)
            elif (terms == 1):
                for k in range(1,self.N,2):
                    fx += self.coeffs[k] * np.cos(k*acx)
            else:
                for k in range(0,self.N):
                    fx += self.coeffs[k] * np.cos(k*acx)

        ## For a Chebyshev polynomial with a defnite parity we evaluate terms
        ## assuming that coefficients all correspond to terms with that parity.
        ##
        else:

            if (self.parity == 0):
                for k in range(0,self.N):
                    fx += self.coeffs[k] * np.cos((2*k)*acx)
            elif (self.parity == 1):
                for k in range(0,self.N):
                    fx += self.coeffs[k] * np.cos((2*k+1)*acx)
            else:
                for k in range(0,self.N):
                    fx += self.coeffs[k] * np.cos(k*acx)

        return(fx)




    def _handle_scalar(self,x):

        x = np.asarray(x)

        if x.ndim == 0:
            x = x[np.newaxis]

        return(x)


    def write_poly(self,filename):

        return




    def read_poly(self,filename):

        return










################################################################################
###
###   DATACLASS     eval_chebyshev(x, coeffs, parity)
###
################################################################################
###
###   DESCRIPTION
###
###      Evaluate the approximation to a function f(x) of parity <parity>
###      as defined by a Chebyshev expansion with coefficients <coeffs>.  The
###      array <coeffs> is assumed to contain terms for both even and odd
###      parity.
###
###   ARGUMENTS
###
###      x       =   value or array of values for function evaluation
###      coeffs  =   array of coefficients defining the Chebyshev expansion
###      parity  =   parity of the polynomial to evaluate (i.e., nonzero
###                  coefficents to include in the sum):
###
###                           0   ->   even terms
###                           1   ->   odd terms
###                           2   ->   all terms
###
###   RETURNS
###
###      N/A
###
###   REQUIRES
###
###      fx  =   value of function evaluated at point(s) x
###

def eval_chebyshev(x, coeffs, parity):


    x     = handle_scalar(x)      # Transforms scalar input to a 0-d numpy array

    N_cfs = len(coeffs)           # Number of coefficients defining f(x)
    fx    = np.zeros(len(x))      # Store evaluation of of f(x)
    acx   = np.arccos(x)          # Arccos appearing in Chebyshev terms

    if   (parity == 0):
        for k in range(0,N_cfs,2):
            fx += coeffs[k] * np.cos(k*acx)
    elif (parity == 1):
        for k in range(1,N_cfs,2):
            fx += coeffs[k] * np.cos(k*acx)
    else:
        for k in range(0,N_cfs):
            fx += coeffs[k] * np.cos(k*acx)

    return(fx)





################################################################################
###
###   DATACLASS     eval_chebyshev_strict(x, coeffs, parity)
###
################################################################################
###
###   DESCRIPTION
###
###      Evaluate the approximation to a function f(x) of parity <parity>
###      as defined by a Chebyshev expansion with coefficients <coeffs>.  The
###      array <coeffs> is assumed to only contain coefficients corresponding
###      to the parity <parity>.
###
###   ARGUMENTS
###
###      x       =   value or array of values for function evaluation
###      coeffs  =   array of coefficients defining the Chebyshev expansion
###      parity  =   parity of the polynomial terms to evaluate:
###
###                           0   ->   even terms
###                           1   ->   odd terms
###
###   RETURNS
###
###      N/A
###
###   REQUIRES
###
###      fx  =   value of function evaluated at point(s) x
###

def eval_chebyshev_strict(x, coeffs, parity):


    x     = handle_scalar(x)      # Transforms scalar input to a 0-d numpy array

    N_cfs = len(coeffs)           # Number of coefficients defining f(x)
    fx    = np.zeros(len(x))      # Array to store evaluation of of f(x)
    acx   = np.arccos(x)          # Arccos appearing in Chebyshev terms


    if (parity == 0):
        for k in range(0,N_cfs):
            fx += coeffs[k] * np.cos((2*k)*acx)
    else:
        for k in range(0,N_cfs):
            fx += coeffs[k] * np.cos((2*k+1)*acx)

    return(fx)