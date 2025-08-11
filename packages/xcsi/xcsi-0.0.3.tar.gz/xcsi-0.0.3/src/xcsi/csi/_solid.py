#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
# April 29, 2025
#
from .utility import UnimplementedInstance, find_row
from ..names import RE, Names

def add_solids(csi, model, config, names: Names):
    ndm = config.get("ndm", 3)
    log = []


    for elem in csi.get("CONNECTIVITY - SOLID",[]):
        nodes = tuple(
                names.identify("Joint", "node", v) or print(v)
                for k,v in elem.items() if RE["joint_key"].match(k)
        )

        nodes = (
            nodes[0],
            nodes[1],
            nodes[3],
            nodes[2],
            nodes[4],
            nodes[5],
            nodes[7],
            nodes[6]
        )

        props = find_row(csi.get("SOLID PROPERTY ASSIGNMENTS", []), Solid=elem["Solid"])
        if props is None:
            log.append(UnimplementedInstance("Solid", elem))
            continue
        props = find_row(csi.get("SOLID PROPERTY DEFINITIONS", []), SolidProp=props["SolidProp"])
        if props is None:
            log.append(UnimplementedInstance("Solid", elem))
            continue

        material = names.identify("Material", "material", props["Material"])
        if material is None:
            raise ValueError(f"Material {props['Material']} not found")

        if len(nodes) == 8:
            model.element("stdBrick", 
                          names.define("Solid", "element", elem["Solid"]),
                          nodes,
                          material
            )
        else:
            log.append(UnimplementedInstance("Solid", elem))
            continue