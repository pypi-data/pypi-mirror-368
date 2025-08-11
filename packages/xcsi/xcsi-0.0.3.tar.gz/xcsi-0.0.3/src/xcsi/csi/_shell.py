#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
from .utility import UnimplementedInstance, find_row
from ..names import RE, TYPES


def add_shells(csi, model, conv):
    for shell in csi.get("CONNECTIVITY - AREA", []):
        if "AREA ADDED MASS ASSIGNMENTS" in csi:
            row = find_row(csi["AREA ADDED MASS ASSIGNMENTS"],
                           Area=shell["Area"])
            if row:
                mass = row["MassPerArea"]
            else:
                mass = 0.0
        else:
            mass = 0.0

        # Find section
        assign  = find_row(csi["AREA SECTION ASSIGNMENTS"],
                           Area=shell["Area"])

        section = conv.identify("ShellSection", "section", assign["Section"])

        nodes = tuple(
            conv.identify("Joint", "node", v)
            for k,v in shell.items() if RE["joint_key"].match(k)
        )

        if len(nodes) == 4:
            type = TYPES["Shell"]["Elastic"]

        elif len(nodes) == 3:
            type = "ShellNLDKGT"

        model.element(type,
                      conv.define("Shell", "element", shell["Area"]),
                      nodes, section
        )
