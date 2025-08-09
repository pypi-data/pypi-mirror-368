import mvulib
import matlab
import numpy as np
import time
from scipy.sparse import csr_matrix

class Mvu:
    _library_instance=None
    
    def __init__(self, n_neighbors=5, angles=0, maxiter=150, verbose=True):
        
        self.n_neighbors=n_neighbors
        self.angles=angles
        self.maxiter=maxiter
        self.verbose=verbose
        
        self.n_samples=None
        self.n_features=None
        
        self.adjacency_matrix=None
        self.kernel=None
        self.cost=None
        
        self.eigenvalues=None
        self._Y=None
        self.n_components=None
        self.embedding=None
        
        self.reconstruction_error=None
        self.reconstruction_error_rel=None
        
        self.n_constraints=None
        self.iter=None
        self.feasratio=None
        self.numerr=None
        self.pinf=None
        self.dinf=None
        
    def initialize():
        if not Mvu._library_instance:
            Mvu._library_instance=mvulib.initialize()
            
    def terminate():
        if Mvu._library_instance:
            Mvu._library_instance.terminate()
            Mvu._library_instance=None
            
    def __str__(self):
        return f"n_neighbors={self.n_neighbors}, angles={self.angles},"+\
               f" maxiter={self.maxiter}"

    def fit(self, X):
        if self.verbose:
            print(title_sep)
            
        start=time.time()
        
        lib=None
        if Mvu._library_instance:
            lib=Mvu._library_instance
        else:
            lib=mvulib.initialize()

        n, d=X.shape
        self.n_samples=n
        self.n_features=d

        if self.verbose:
            print(f"Parameters:\nn_samples={n}\nn_features={d}"+\
                  f"\nn_neighbors={self.n_neighbors}"+\
                  f"\nangles={self.angles}\nmaxiter={self.maxiter}")
            
        XIn=matlab.double(np.ascontiguousarray(X), size=(n,d))
        kIn=matlab.double([self.n_neighbors], size=(1,1))
        anglesStrIn="angles"
        anglesIn=matlab.double([self.angles], size=(1,1))
        maxIterStrIn="maxiter"
        maxIterIn=matlab.double([self.maxiter], size=(1,1))

        if self.verbose:
            print("Solving problem...")

        YOut, infoOut=lib.mvu(XIn, kIn, anglesStrIn, anglesIn, maxIterStrIn, maxIterIn,  nargout=2)
        if self.verbose:
            print("Problem solved!")

        self._Y=np.array(YOut)
        self.cost=infoOut["cost"]
        self.eigenvalues=np.array(infoOut["eigvals"])
        self.n_constraints=int(infoOut["constr"])
        self.iter=int(infoOut["iter"])
        self.feasratio=infoOut["feasratio"]
        self.numerr=int(infoOut["numerr"])
        self.pinf=int(infoOut["pinf"])
        self.dinf=int(infoOut["dinf"])
        rows=np.array(infoOut["rAdj"]).flatten()-1
        cols=np.array(infoOut["cAdj"]).flatten()-1
        self.adjacency_matrix=csr_matrix((np.repeat(1, len(rows)), (rows, cols)), shape=(n,n), dtype="int")
        self.kernel=np.array(infoOut["K"])

        self.n_components=None
        self.embedding=None
        self.reconstruction_error=None
        self.reconstruction_error_rel=None

        if not Mvu._library_instance:
            lib.terminate()

        finish=time.time()
        time_taken=round(finish-start, 2)

        if self.verbose:
            print(f"Execution of Mvu took {time_taken} seconds.")
            print(sep)
        return self

    def transform(self, p):
        if self._Y is None:
            raise Exception("Call Mvu.fit prior to calling transform!")
        self.n_components=p
        self.embedding=self._Y[:, 0:p]
        cost_kmds=np.sum(self.eigenvalues[p:]**2)
        self.reconstruction_error=np.sqrt(cost_kmds)
        self.reconstruction_error_rel=self.reconstruction_error/np.sqrt(cost_kmds+np.sum(self.eigenvalues[:p]**2))
        return self.embedding

    def fit_transform(self, X, p):
        return self.fit(X).transform(p)

    def summarize(self):
        print(sep)
        print(f"\nSolver Summary:\n\nn_constraints={self.n_constraints}"+\
              f"\niter={self.iter}\nfeasratio={self.feasratio}"+\
              f"\npinf={self.pinf}\ndinf={self.dinf}\nnumerr={self.numerr}\n")
        print(f"Mvu Summary:\n\ncost={self.cost}\nn_components={self.n_components}"+\
              f"\nreconstruction_error={self.reconstruction_error}"+\
              f"\nreconstruction_error_rel={self.reconstruction_error_rel}\n")
        print(sep)

sep="================================================================="
title_sep="============================== Mvu =============================="
