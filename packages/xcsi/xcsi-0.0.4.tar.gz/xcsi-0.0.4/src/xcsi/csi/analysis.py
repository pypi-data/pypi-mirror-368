from xcsi.csi import find_row, find_rows
from collections import defaultdict

def _apply_loads(csi, model, case: str=None):
    "LOAD CASE DEFINITIONS",
    "LOAD PATTERN DEFINITIONS",

    "JOINT LOADS - FORCE",
    "FRAME LOADS - DISTRIBUTED",
    "FRAME LOADS - GRAVITY",
    "FRAME LOADS - POINT",
    "CABLE LOADS - DISTRIBUTED",
    pass

class LoadPattern:
    def __init__(self, name, csi):
        self.name = name

        joint_sp = defaultdict(dict)
        for joint in find_rows(csi.get("JOINT LOADS - GROUND DISPLACEMENT", []),
                               LoadPat=name):
            for key in "U1", "U2", "U3", "R1", "R2", "R3":
                if key in joint:
                    joint_sp[joint["Joint"]][key] = joint[key]

        self._joint_sp = joint_sp


        joint_force = defaultdict(dict)
        for joint in find_rows(csi.get("JOINT LOADS - FORCE", []),
                               LoadPat=name):
            for key in "F1", "F2", "F3", "M1", "M2", "M3":
                if key in joint:
                    joint_force[joint["Joint"]][key] = joint[key]

        self._joint_force = joint_force

    def _add_frame_loads(self):
        name = self.name 
        csi = self._csi

        # Frame loads
        self._frame_loads = defaultdict(list)
        for assign in find_rows(csi.get("FRAME LOADS - DISTRIBUTED", []),
                               LoadPat=name):
            
            if assign.get("RelDistA", 0) != 0:
                raise ValueError("Relative distance not supported for distributed frame loads")
            if assign.get("RelDistB", 1) != 1:
                raise ValueError("Relative distance not supported for distributed frame loads")
            if assign.get("DistType", "RelDist") != "RelDist":
                raise ValueError("Only relative distance supported for distributed frame loads")
            
            try:
                direction = int(assign["Dir"]-1)
            except ValueError:
                raise ValueError(f"Unsupported direction {assign['Dir']} for frame load {assign['Frame']}")

            force = [0,0,0]
            moment = [0,0,0]
            if assign["Type"] == "Force":
                if assign["FOverLA"] != assign["FOverLB"]:
                    raise ValueError("FOverLA and FOverLB must be equal for distributed frame loads")
                
                force[direction] = assign["FOverLA"]
            elif assign["Type"] == "Moment":
                if assign["MOverLA"] != assign["MOverLB"]:
                    raise ValueError("MOverLA and MOverLB must be equal for distributed frame loads")

                raise NotImplementedError("Moment loads not implemented for frames")

            self._frame_loads[assign["Frame"]].append({
                "type": "Uniform",
                "basis": assign["CoordSys"].title(),
                "force": force,
                "moment": moment,
            })

        "FRAME LOADS - POINT"


    def apply(self, asm):
        """
        Apply the load pattern to the model.
        """
        model = asm.model
        dofs = ["U1", "U2", "U3", "R1", "R2", "R3"]

        ptag = asm.names.define("LoadPattern", "pattern", self.name)
        model.pattern("Plain", ptag, "Linear")
        for joint, sp in self._joint_sp.items():
            if not sp:
                continue
            for dof, value in sp.items():
                model.sp(
                    asm.names.identify("Joint", "node", joint),
                    dofs.index(dof)+1,
                    value,
                    pattern=ptag
                )

    def __str__(self):
        return f"LoadPattern(name={self.name})"


class LinearStaticAnalysis:
    def __init__(self, name, job):
        self.name = name
        self._csi = job._tree
        self._job = job


    def run(self, asm):
        """
        Run the linear static analysis case.
        """
        self._apply_loads(asm)

        # Run the analysis
        model = asm.model
        model.test("EnergyIncr", 1e-10, 10)
        model.system("Umfpack")
        model.constraints("Transformation")
        model.numberer("RCM")
        model.integrator("LoadControl", 1.0)
        model.algorithm("Newton")
        model.analysis("Static")
        model.analyze(1)
        
    def _apply_loads(self, asm):
        """
        Apply loads to the model for this linear static analysis case.
        """

        for assign in find_rows(self._csi.get("CASE - STATIC 1 - LOAD ASSIGNMENTS", []),
                       Case=self.name):
            pattern = self._job.pattern(assign["LoadName"])

            pattern.apply(asm)

    def __str__(self):
        return f"LinearStaticAnalysis(name={self.name})"
    
    def __repr__(self):
        return f"LinearStaticAnalysis(name={self.name})"

        
            
        


class NonlinearStaticAnalysis:
    def __init__(self, name, defs, csi, model):

        SolScheme = "Iterative Only"

        p04 = find_row(csi.get("CASE - STATIC 4 - NONLINEAR PARAMETERS", []),
                       Case=name)

        MaxIterNR = 10
        if p04 is not None:
            SolScheme = p04.get("SolScheme", SolScheme)

            if SolScheme != "Iterative Only":
                raise ValueError(f"Unsupported solution scheme: {SolScheme}")
            
            MaxIterNR = p04.get("MaxIterNR", MaxIterNR)
            ItConvTol = p04.get("ItConvTol", 1e-6)
            

        model.test()

    def apply_loads(self, model):
        """
        Apply loads to the model for this nonlinear static analysis case.
        """
        for assign in find_rows(self._csi.get("CASE - STATIC 2 - NONLINEAR LOAD APPLICATION", []),
                       Case=self.name):
            pattern = self._job.pattern(assign["LoadName"])
