"""
solve the problem 

div grad u = v  in Domain
(grad u) n = 0  on Boundary

"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
import multiprocessing as mp
from functools import partial
from time import perf_counter

try:
    from pypardiso import spsolve as _spsolve
    _PARDISO = True
except ModuleNotFoundError:
    from scipy.sparse.linalg import spsolve as _spsolve
    _PARDISO = False

try:
    from numba import njit as jit 
    from numba import prange
    jit(lambda x: x**2)(1.0)  # test if numba is available

except ModuleNotFoundError:
    prange = range
    def jit(*_, **__):
        def _decorator(func):
            return func
        return _decorator



def _assemble_triplet(conn, ke, rows, cols, data):
    """
    Append COO triplets for a 1-dof-per-node element
    """
    for a, i in enumerate(conn):
        for b, j in enumerate(conn):
            rows.append(i)
            cols.append(j)
            data.append(ke[a, b])


@jit(cache=True, fastmath=True, nogil=True)
def _assemble_matrix(Ka, ke, conn, ndf):
    nne = len(conn)
    for a in range(nne):
        ia = conn[a] * ndf
        for b in range(nne):
            ib = conn[b] * ndf
            Ka[ia:ia+ndf, ib:ib+ndf] += ke[a*ndf:(a+1)*ndf,b*ndf:(b+1)*ndf]


@jit(cache=True, fastmath=True, nogil=True)
def _assemble_vector(Fa, fe, conn, ndf):
    nne = len(conn)
    for a in range(nne):
        ia = conn[a] * ndf
        Fa[ia:ia+ndf] += fe[a*ndf:(a+1)*ndf]


def _wrap_elem(nodes, elem_map, load_fun, elem):
    xyz = nodes[elem.nodes].T
    me, ke, fe = elem_map[elem.shape](xyz)
    if load_fun is not None:
        fe = load_fun(xyz, elem.nodes)
    return elem, (me, ke, fe)


class T3:
    """Linear (3-node) triangle for Poisson/Laplace."""

    @staticmethod
    @jit(cache=True, fastmath=True)
    def elem(xyz):
        ((y1, y2, y3), (z1, z2, z3)) = xyz

        z12, z23, z31 = z1-z2, z2-z3, z3-z1
        y32, y13, y21 = y3-y2, y1-y3, y2-y1

        area = 0.5 * ((y2 - y1) * (z3 - z1) - (y3 - y1) * (z2 - z1))

        me = area/12 * (np.eye(3) + np.ones((3, 3)))

        k11 =  y32**2 + z23**2
        k12 =  y13*y32 + z23*z31
        k13 =  y21*y32 + z12*z23
        k22 =  y13**2 + z31**2
        k23 =  y13*y21 + z12*z31
        k33 =  y21**2 + z12**2
        ke  = 1/(4.0*area) * np.array([[k11, k12, k13],
                                       [k12, k22, k23],
                                       [k13, k23, k33]])

        fe =  1/6. * np.array([
              (y1*y32 - z1*z23) + (y2*y32 - z2*z23) + (y3*y32 - z3*z23),
              (y1*y13 - z1*z31) + (y2*y13 - z2*z31) + (y3*y13 - z3*z31),
              (y1*y21 - z1*z12) + (y2*y21 - z2*z12) + (y3*y21 - z3*z12)])
        return me, ke, fe


class T6:
    """Quadratic (6-node) triangle for Poisson/Laplace."""

    @staticmethod
    @jit(cache=True, fastmath=True)
    def elem(xyz): # (2,6) array: rows=(y,z)
        # quick geometry (use only corner nodes)
        y, z = xyz[:, :3]
        area = 0.5 * ((y[1]-y[0])*(z[2]-z[0]) - (y[2]-y[0])*(z[1]-z[0]))
        if area == 0.0:
            raise ValueError("Degenerate triangle")

        beta  = np.array([y[1]-y[2], y[2]-y[0], y[0]-y[1]])
        gamma = np.array([z[2]-z[1], z[0]-z[2], z[1]-z[0]])
        gradL = np.vstack((beta, gamma)) / (2.0*area)     # (2,3)

        # 3-point Gauss rule
        gp = np.array([[1/6, 1/6, 2/3],
                       [1/6, 2/3, 1/6],
                       [2/3, 1/6, 1/6]])
        w  = np.full(3, 1/3)

        ke = np.zeros((6, 6))
        for (L1, L2, L3), wt in zip(gp, w):
            gradN = np.zeros((6, 2))

            # vertex nodes
            gradN[0] = (4*L1 - 1)*gradL[:, 0]
            gradN[1] = (4*L2 - 1)*gradL[:, 1]
            gradN[2] = (4*L3 - 1)*gradL[:, 2]
            # midside nodes
            gradN[3] = 4*(L2*gradL[:, 0] + L1*gradL[:, 1])
            gradN[4] = 4*(L3*gradL[:, 1] + L2*gradL[:, 2])
            gradN[5] = 4*(L3*gradL[:, 0] + L1*gradL[:, 2])

            ke += wt*area * (gradN @ gradN.T)

        me = (area / 180.0) * np.array(
            [[ 6, -1, -1,  0,  0,  0],
             [-1,  6, -1,  0,  0,  0],
             [-1, -1,  6,  0,  0,  0],
             [ 0,  0,  0, 32, 16, 16],
             [ 0,  0,  0, 16, 32, 16],
             [ 0,  0,  0, 16, 16, 32]])
        fe = np.zeros(6)
        return me, ke, fe



_GaussQ4 = [
#   ((0.0, 0.0), 1.0)
    ((-1/np.sqrt(3), -1/np.sqrt(3)), 1.0),
    (( 1/np.sqrt(3), -1/np.sqrt(3)), 1.0),
    (( 1/np.sqrt(3),  1/np.sqrt(3)), 1.0),
    ((-1/np.sqrt(3),  1/np.sqrt(3)), 1.0),
]

class Q4:

    @staticmethod
    @jit(cache=True, fastmath=True)
    def elem(xyz):
        pass
        

        



def poisson_neumann_(
    nodes,
    elements,
    materials=None,
    elem_fun=None,       # e.g.  pick_elem or T3.elem or T6.elem
    load_fun=None,       # as before
    threads=6,
    chunk=200,
    fix_node=0,
    fix_value=1.0):

    if elem_fun is None:
        elem_fun = T3.elem # pick_elem

    if load_fun is not None:
        load_fun = body_force(load_fun)

    # if load_fun is None:
    #     load_fun = body_force(np.array([0.0, 0.0]))

    ndf = 1
    ndof_total = ndf * len(nodes)
    Ka = np.zeros((ndof_total, ndof_total))
    Fa = np.zeros(ndof_total)


    tic = perf_counter()
    with mp.Pool(threads) as pool:
        for elem, (me, ke, fe) in pool.imap_unordered(
                partial(_wrap_elem, nodes, elem_fun, load_fun),
                elements,
                chunk):
            _assemble_matrix(Ka, ke, elem.nodes, ndf)
            _assemble_vector(Fa, fe, elem.nodes, ndf)

    print(f"Assembly took {perf_counter() - tic:.3f} seconds")

    tic = perf_counter()
    fixed  = np.array([fix_node * ndf])
    free   = np.setdiff1d(np.arange(ndof_total), fixed)

    Pf = Fa[free] - Ka[np.ix_(free, fixed)].ravel()*fix_value
    Kf = Ka[np.ix_(free, free)]
    Uf = np.linalg.solve(Kf, Pf)
    print(f"Solving took {perf_counter() - tic:.3f} seconds")

    u = np.empty(ndof_total)
    u[free]  = Uf
    u[fixed] = fix_value
    return u


def poisson_neumann(
        nodes,
        elements,
        materials=None,
        elem_fun=None,
        load_fun=None,
        threads=6,
        chunk=200,
        fix_node=None,
        fix_value=1.0,
        verbose=False
):
    if elem_fun is None:
        elem_fun = T3.elem           # or pick_elem for mixed T3/T6


    elem_map = {
            'T3': T3.elem,
            'Q4': Q4.elem,
    }

    if load_fun is not None and not callable(load_fun):
        load_fun = body_force(load_fun)

    ndf          = 1
    ndof_total   = ndf * len(nodes)
    rows, cols, data = [], [], []
    Fa           = np.zeros(ndof_total)

    #
    tic = perf_counter()
    with mp.Pool(threads) as pool:
        for elem, (_, ke, fe) in pool.imap_unordered(
                partial(_wrap_elem, nodes, elem_map, load_fun),
                elements,
                chunk):

            if elem.group is not None and materials is not None:
                assert materials[elem.group] != 0
                ke *= materials[elem.group]

            _assemble_triplet(elem.nodes, ke, rows, cols, data)
            _assemble_vector(Fa, fe, elem.nodes, ndf)

    if verbose:
        print(f"Assembly   : {perf_counter() - tic:6.3f} s")

    # build sparse CSR
    K = sp.coo_matrix(
            (data, (rows, cols)), shape=(ndof_total, ndof_total)
        ).tocsr()

    #
    # Dirichlet fix
    #
    if fix_node is None:
        fix_node = 0
    tic = perf_counter()
    fixed  = np.array([fix_node * ndf])
    free   = np.setdiff1d(np.arange(ndof_total), fixed)

    Pf = Fa[free] - K[free][:, fixed].toarray().ravel() * fix_value
    Kf = K[free][:, free]

    #
    # Solve
    #
    Uf = _spsolve(Kf, Pf)

    if verbose:
        print(f"Solve      : {perf_counter() - tic:6.3f} s "
            f"({ 'PARDISO' if _PARDISO else 'SuperLU' })")

    #
    u = np.empty(ndof_total)
    u[free]  = Uf
    u[fixed] = fix_value
    return u

def pick_elem(xyz):
    return T3.elem(xyz) if xyz.shape[1] == 3 else T6.elem(xyz)



# def body_force(f):
#     def _load(xyz, conn):
#         area = 0.5*abs(np.linalg.det(np.vstack((xyz, np.ones(xyz.shape[1])))))
#         return area * f[conn] / xyz.shape[1] * np.ones(xyz.shape[1])
#     return _load
def _body_force_kernel(xyz, conn, f_nodal):
    """
    Nodal load vector for a body force specified at nodes.
    For linear triangles use the exact formula
        fe_i = A/12 * (2*f_i + f_j + f_k)
    """
    area  = 0.5 * abs(np.linalg.det(np.vstack((xyz, np.ones(xyz.shape[1])))))
    f_i, f_j, f_k = f_nodal[conn]
    return area / 12.0 * np.array([2*f_i + f_j + f_k,
                                   f_i + 2*f_j + f_k,
                                   f_i + f_j + 2*f_k])


def body_force(f_nodal):
    """
    Parameters
    ----------
    f_nodal : (nNodes,) array_like
        Scalar body-force value at every global node.

    Returns
    -------
    load_fun : callable (xyz, conn) -> fe
        Suitable for `solve_poisson_2d(..., load_fun=...)`.
    """
    return partial(_body_force_kernel, f_nodal=np.asarray(f_nodal))