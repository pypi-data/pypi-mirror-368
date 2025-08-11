#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
from xcsi.csi import create_model
from xcsi.names import Names
from dataclasses import dataclass
from xcsi.csi.utility import find_row



class Assembly:
    def __init__(self, tree, model=None):
        self._tree = tree
        self._names = Names()
        self._model = create_model(tree, model=model, names=self._names, verbose=False)

    def frame_shape(self, name=None, tag=None):
        pass

    @property
    def units(self):
    
        units = None 
        unit_str = None
        for row in self._tree["PROGRAM CONTROL"]:
            if "CurrUnits" in row:
                unit_str = row["CurrUnits"]
        
        if unit_str.lower() == "kip, ft, f":
            import xara.units.fks as units
        elif unit_str.lower() == "kip, in, f":
            import xara.units.iks as units
        elif unit_str.lower() == "lb, in, f":
            import xara.units.ips as units
        elif unit_str.lower() == "kn, m, c":
            import xara.units.mks as units

        return units

    @property 
    def names(self):
        return self._names

    @property 
    def model(self):
        return self._model


class Job:
    def __init__(self, tree):
        self._tree = tree

    def assemble(self, model=None):
        return Assembly(self._tree, model=model)
    
    def pattern(self, name):
        from xcsi.csi.analysis import LoadPattern
        return LoadPattern(name, self._tree)
    
    def patterns(self):
        for pattern in self._tree.get("LOAD PATTERN DEFINITIONS", []):
            yield self.pattern(pattern["LoadPat"])
    
    def steps(self):
        from xcsi.csi.analysis import LinearStaticAnalysis

        for case in self._tree.get("LOAD CASE DEFINITIONS", []):
            if case["Type"] == "LinStatic":
                yield LinearStaticAnalysis(case["Case"], self)
            else:
                raise ValueError(f"Unsupported case type: {case['Type']}")
