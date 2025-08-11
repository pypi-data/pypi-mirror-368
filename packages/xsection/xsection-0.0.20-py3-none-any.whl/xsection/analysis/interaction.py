import xara
import numpy as np
# test_stress = lambda s: max(s) < 0.9*50*ksi
# test_stress = lambda s: min(s) > -0.9*50*ksi
# test_strain = lambda s: max(s) < 0.9*0.003
# test_strain = lambda s: min(s) > -0.9*0.003

class _SectionInterface:
    def __init__(self, section, shape, materials):

        if isinstance(materials, dict):
            materials = [materials]

        self._model = None
        self._materials = materials
        self._section = section
        self._shape = shape

        self._is_shear = "shear" in self._section.lower()


    def initialize(self):
        if self._model is not None:
            self._model.wipe()

        self._model = _create_model(self._section, self._shape, self._materials)
        model = self._model

        self._model.invoke("section", 1, ["update 0 0 0 0 0 0;"])


    def getStressResultant(self, e, commit=True):
        eps, kap = map(float, e)
        stress = self._model.invoke("section", 1, [
                        f"update  {eps} 0 0 0 0 {kap};",
                         "stress"
        ] + (["commit"] if commit else []))
        if self._is_shear:
            return np.array(stress)[[0, 5]]
        else:
            return np.array(stress)[[0, 3]]


    def getSectionTangent(self):
        tangent = self._model.invoke("section", 1, [
                        "tangent"
        ])

        n = int(np.sqrt(len(tangent)))
        Ks = np.array(tangent).reshape(n,n)
        return Ks


def _solve_eps(sect, kap, axial: float, eps0, tol=1e-8, maxiter=15, time=0.0):
    # Newton-Raphson iteration
    eps = eps0
    s = sect.getStressResultant([eps, kap], False)
    for i in range(maxiter):
        if abs(s[0] - axial) < tol:
            return eps
        s = sect.getStressResultant([eps, kap], False)
        eps -= (s[0] - axial)/sect.getSectionTangent()[0,0]
    
    print(f"Warning: {maxiter} iterations reached, r = {s[0] - axial}, {time = }")
    return None

    return eps


def _analyze(s, P, dkap, nstep):
    s.initialize()
    k0 = 0.0

    kap = 0
    if eo := _solve_eps(s,  k0,  P,  0.0):
        e0 = _solve_eps(s,  k0,  P,  eo)
    else:
        e0 = 0.0

    PM = [
        s.getStressResultant([e0, k0], True)
    ]
    if e1 := _solve_eps(s, k0+dkap, P, e0):
        PM.append(s.getStressResultant([e1, k0+dkap], True))

        e = e0
        kap = 2*dkap
        for _ in range(nstep):
            # if abs(PM[-1][1]) < 0.995*abs(PM[-2][1]):
            #     break
            e = _solve_eps(s, kap, P, e)
            if e is None:
                break
            PM.append(s.getStressResultant([e, kap], True))
            kap += dkap
    return PM, kap




def _create_model(section, shape, materials):

    model = xara.Model(ndm=3, ndf=6)

    if isinstance(materials, dict):
        materials = [materials]

    shear = "shear" in section.lower()
    for i,mat in enumerate(materials):
        if shear:
            m = mat
            model.nDMaterial(m["type"], i+1, **{k: v for k, v in m.items() if k not in {"name", "type"}})
        else:
            m = mat
            model.uniaxialMaterial(m["type"], i+1, **{k: v for k, v in m.items() if k not in {"name", "type"}})

    model.section(section, 1, GJ=1e3)
    for i in range(len(materials)):
        for fiber in shape.create_fibers(warp=shear, group=i):
            model.fiber(**fiber, material=i+1, section=1)

    # Define two nodes at (0,0)
    model.node(1, (0, 0, 0))
    model.node(2, (0, 0, 0))

    # Fix all degrees of freedom except axial and bending
    model.fix(1, (1, 1, 1,  1, 1, 1))
    model.fix(2, (0, 1, 1,  1, 1, 0))

    # Create element
    model.element("zeroLengthSection", 1, (1, 2), 1)

    return model

def _analyze_direction(model,
                       direction,
                       maxK, numIncr,
                       initial=None
                       ):
    """
    Arguments
       axialLoad -- axial load applied to section (negative is compression)
       maxK      -- maximum curvature reached during analysis
       numIncr   -- number of increments used to reach maxK (default 100)
    """
    if initial is not None:
        # Define constant axial load
        model.pattern("Plain", 1, "Constant", loads={2: initial})

        # Define analysis
        model.system("BandGeneral")
        model.numberer("Plain")
        model.constraints("Plain")
        model.test("NormUnbalance", 1.0e-8, 20, 0)
        model.algorithm("Newton")
        model.integrator("LoadControl", 0.0)
        model.analysis("Static")

        # Do one analysis for constant axial load
        model.analyze(1)

    # Define reference moment
    model.pattern("Plain", 2, "Linear")
    model.load(2, direction, pattern=2)

    # Compute curvature increment
    dK = maxK/numIncr

    # Use displacement control at node 2 for section analysis
    model.integrator("DisplacementControl", 2, 6, dK, 1, dK, dK)

    MK = []
    for i in range(numIncr):

        # Get moment and curvature
        M = model.eleResponse(1, "force")[5]
        k = model.nodeDisp(2, 6)

        MK.append([-M, k])

        # Evaluate step
        if model.analyze(1) != 0:
            break

    return MK


class SectionInteraction:
    def __init__(self, section, axial):
        self.axial = axial
        self._section = section

    def moment_curvature(self):

        # test = lambda m: m.eleResponse(1, "section", "fiber", (0.0, 0.0), "stress")[0] < 0.9*50*ksi

        for N in self.axial:
            model = _create_model(*self._section)
            M, k = zip(*_analyze_direction(model,  (0,0,0,  0,0,1), 
                                           0.005, 200, 
                                           initial=[N,0,0,   0,0,0]))
            yield N, M, k

    def create_model(self):
        return _create_model(*self._section)


    def surface2(self, nstep = 30, incr=5e-6):
        import matplotlib.pyplot as plt
        import numpy as np
        fig, ax = plt.subplots(1,2, sharey=True, constrained_layout=True)
        sect = _SectionInterface(*self._section)
        axial = self.axial

        # Curvature increment
        dkap = incr
        s = sect
        for P in axial:
            PM, kmax = _analyze(s, P, dkap, nstep)

            p, m = zip(*PM)

            ax[0].scatter(np.linspace(0.0, kmax, len(m)), m, s=0.2)

            ax[1].scatter(p, m, s=0.2)

        ax[0].set_xlabel("Curvature, $\\kappa$")
        ax[0].set_ylabel("Moment, $M(\\varepsilon, \\kappa)$")
        ax[1].set_xlabel("Axial force, $P$")
        # ax[1].set_ylabel("Moment, $M$")

        # plt.show()

