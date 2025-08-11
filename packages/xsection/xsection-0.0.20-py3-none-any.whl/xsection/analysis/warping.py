import numpy as np
from shps.solve.laplace import laplace_neumann
from shps.solve.poisson import poisson_neumann


class WarpingAnalysis:
    def __init__(self, model, materials=None):
        self.model = model
        self.nodes = model.nodes
        self.elems = model.elems
        self._materials = materials

        self._solution = None
        self._warping  = None
        self._centroid = None
        self._shear_center = None

        self._nn = None
        self._mm = None 
        self._ww = None
        self._vv = None
        self._nm = None
        self._mw = None
        self._mv = None
        self._nv = None

    def translate(self, vect):
        return WarpingAnalysis(self.model.translate(vect))

    def section_tensor(self, twist=None, shear=None):

        External, Constrained, Uniform, Neglected = range(4)

        def constraints(shear, twist):
            nwm = 3
            P  = np.eye(6+2*nwm)
            Pa = np.zeros((3,3))
            Pe = np.zeros((3,6))

            if twist == Constrained or twist == Uniform:
                Pa[0,0] = Pe[0,3] = 1

            if shear == Constrained or shear == Uniform:
                Pa[1,1] = Pe[1,1] = 1
                Pa[2,2] = Pe[2,2] = 1


            P[9:12,0:6] = Pe
            P[9:12,9:12] = np.eye(3) - Pa
            P = P[:, ~(P == 0).all(axis=0)][~(P == 0).all(axis=1),:]

            return P

        cnn = self.cnn()
        cmm = self.cmm()
        cnm = self.cnm()
        cnw = self.cnw()
        cnv = self.cnv()
        cmw = self.cmw()
        cmv = self.cmv()
        cvv = self.cvv()
        cww = self.cww()

        owv =  np.zeros((3,3))
        ACA =  np.block([[cnn  , cnm,   cnw,   cnv],
                         [cnm.T, cmm,   cmw,   cmv],
                         [cnw.T, cmw.T, cww,   owv],
                         [cnv.T, cmv.T, owv.T, cvv]])
        
        if twist is None:
            twist = External
        if shear is None:
            shear = External
        P = constraints(shear, twist)
        BCBP = (ACA@P)[:, ~(P == 0).all(axis=0)]
        PBCBP = (P@BCBP)[~(P == 0).all(axis=1),:]
        return PBCBP

    def cnn(self):
        if self._nn is not None:
            return self._nn
        e = np.ones(len(self.model.nodes))
        EA = self.model.inertia(e,e, weight="e")
        GA = self.model.inertia(e,e, weight="g")
        self._nn = np.array([[EA,  0,  0],
                             [ 0, GA,  0],
                             [ 0,  0, GA]])
        return self._nn

    def cmm(self):
        if self._mm is not None:
            return self._mm 

        y,z = self.model.nodes.T
        izy = self.model.inertia(z,y, weight="g")
        izz = self.model.inertia(y,y, weight="e")
        iyy = self.model.inertia(z,z, weight="e")
        self._mm = np.array([[izz+iyy,   0,    0],
                             [   0   , iyy, -izy],
                             [   0   ,-izy,  izz]])
        return self._mm

    def cww(self):
        """
        \\int \\varphi \\otimes \\varphi
        """
        if self._ww is None:
            w = self.solution()
            Iw = self.model.inertia(w, w, weight="e")
            self._ww = np.array([[Iw, 0, 0],
                                 [ 0, 0, 0],
                                 [ 0, 0, 0]])
        return self._ww

    def cvv(self):
        if self._vv is None:
            # w = self.warping()
            w = self.solution()
            Iww = self.model.energy(w, w, weight="g")
            self._vv = np.array([[Iww, 0.0, 0.0],
                                 [0.0, 0.0, 0.0],
                                 [0.0, 0.0, 0.0]])
        return self._vv


    def cnm(self):
        if self._nm is not None:
            return self._nm
        y,z = self.model.nodes.T
        e  = np.ones(len(self.model.nodes))
        EQy = self.model.inertia(e,z, weight="e")
        EQz = self.model.inertia(e,y, weight="e")
        GQy = self.model.inertia(e,z, weight="g")
        GQz = self.model.inertia(e,y, weight="g")
        self._nm = np.array([[ 0,  EQy, -EQz],
                             [-GQy,  0,    0],
                             [ GQz,  0,    0]])
        return self._nm


    def cmw(self):
        if self._mw is not None:
            return self._mw
        y,z =  self.model.nodes.T
        w = self.solution()
        iwy = self.model.inertia(w,z)
        iwz = self.model.inertia(w,y)
        self._mw = np.array([[  0,  0, 0],
                             [ iwy, 0, 0],
                             [-iwz, 0, 0]])
        return self._mw

    def cmv(self):
        if self._mv is not None:
            return self._mv

        w = self.solution()

        yz  = self.model.nodes
        cxx = self.model.curl(yz, w)
        self._mv = np.array([[cxx, 0.0, 0.0],
                             [0.0, 0.0, 0.0],
                             [0.0, 0.0, 0.0]])
        return self._mv


    def css(self):
        w = self.solution()

        u = poisson_neumann(
            self.model.nodes,
            self.model.elems,
            load_fun = w
        )
        return self.model.inertia(u,w)

    def cnv(self):
        if self._nv is not None:
            return self._nv
        w = self.solution()

        i = np.zeros_like(self.model.nodes)
        i[:,1] = -1
        # i[:,0] = 1
        cxy = self.model.curl(i, w)
        # i[:,1] = 1
        # i[:,0] = 0
        i[:,0] = 1
        i[:,1] = 0
        cxz = self.model.curl(i, w)
        self._nv = np.array([[0.0, 0.0, 0.0],
                             [cxy, 0.0, 0.0],
                             [cxz, 0.0, 0.0]])
        return self._nv


    def cnw(self, ua=None)->float:
        # Normalizing Constant = -warpIntegral / A
        c = 0.0

        if ua is not None:
            for i,elem in enumerate(self.model.elems):
                area = self.model.cell_area(i)
                c += sum(ua[elem.nodes])/3.0 * area

        return np.array([[ c , 0.0, 0.0], 
                         [0.0, 0.0, 0.0],
                         [0.0, 0.0, 0.0]])


    def solution(self):
        """
        # We should have 
        #   self.model.inertia(np.ones(nf), warp) ~ 0.0
        """
        if self._solution is None:
            # self._solution = laplace_neumann(self.model.nodes, self.model.elems)
            self._solution = poisson_neumann(self.model.nodes, self.model.elems)
            cnw = self.cnw(self._solution)[0,0]
            cnn = self.cnn()[0,0]
            self._solution -= cnw/cnn

        return self._solution
    

    def centroid(self):
        if self._centroid is not None:
            return self._centroid
        A = self.cnn()[0,0]
        cnm = self.cnm()
        Qy = cnm[0,1] # int z
        Qz = cnm[2,0] # int y
        self._centroid = np.array((float(Qz/A), float(Qy/A)))
        return self._centroid

    def shear_center(self):
        if self._shear_center is not None:
            return self._shear_center

        cmm = self.translate(-self.centroid()).cmm()
        # cmm = self.cmm()

        I = np.array([[ cmm[1,1],  cmm[1,2]],
                      [ cmm[2,1],  cmm[2,2]]])

        _, iwy, iwz = self.cmw()[:,0]
        # _, iwz, iwy = -cen.cmw()
        ysc, zsc = np.linalg.solve(I, [iwy, iwz])
        self._shear_center = np.array((
            float(ysc), #-c[0,0], 
            float(zsc), #+c[1,0]
        )) #+ self.centroid()
        return self._shear_center

    def warping(self):
        if self._warping is not None:
            return self._warping

        w = self.solution() 
        # w = self.translate(-self.centroid()).solution()

        y,   z = self.model.nodes.T
        cy, cz = self.centroid()
        yc = y - cy 
        zc = z - cz
        sy, sz = self.shear_center()
        # sy = -sy 
        # sz = -sz
        # w =  w + np.array([ys, -zs])@self.model.nodes.T
        w = w + sy*zc - sz*yc

        self._warping = w

        return self._warping


    def torsion_constant(self):
        """
        Compute St. Venant's constant.
        """
        # J = Io + Irw
        return self.cmm()[0,0] + self.cmv()[0,0]

        nodes = self.model.nodes
        J  = 0
        for i,elem in enumerate(self.model.elems):
            ((y1, y2, y3), (z1, z2, z3)) = nodes[elem.nodes].T

            z23 = z2 - z3
            z31 = z3 - z1
            z12 = z1 - z2
            y32 = y3 - y2
            y13 = y1 - y3
            y21 = y2 - y1

            u1, u2, u3 = warp[elem.nodes]

            # Element area
            area = self.model.cell_area(i)

            # St. Venant constant
            Czeta1  = ( u2*y1 * y13 + u3 *  y1 * y21 + u1 * y1*y32 - u3 * z1 * z12 - u1*z1 * z23 - u2*z1*z31)/(2*area)
            Czeta2  = (u2*y13 *  y2 + u3 *  y2 * y21 + u1 * y2*y32 - u3 * z12 * z2 - u1*z2 * z23 - u2*z2*z31)/(2*area)
            Czeta3  = (u2*y13 *  y3 + u3 * y21 *  y3 + u1 * y3*y32 - u3 * z12 * z3 - u1*z23 * z3 - u2*z3*z31)/(2*area)
            Czeta12 = 2*y1*y2 + 2*z1*z2
            Czeta13 = 2*y1*y3 + 2*z1*z3
            Czeta23 = 2*y2*y3 + 2*z2*z3
            Czeta1s =   y1**2 +   z1**2
            Czeta2s =   y2**2 +   z2**2
            Czeta3s =   y3**2 +   z3**2
            J += ((Czeta1+Czeta2+Czeta3)/3. \
                + (Czeta12+Czeta13+Czeta23)/12. \
                + (Czeta1s+Czeta2s+Czeta3s)/6.)*area

        return float(J)

