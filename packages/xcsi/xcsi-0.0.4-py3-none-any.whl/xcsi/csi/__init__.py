#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
# Certain operations are loosley adapted from:
#    https://github.com/XunXun-Zhou/Sap2OpenSees/blob/main/STO_ver1.0.py
#
#
import numpy as np
from ..names import Names
from .parse import load
from .utility import UnimplementedInstance, print_log
from .point import create_points
from .link import create_links
from ._section import add_shell_sections
from ._frame.section import add_frame_sections
from ._frame.outlines import collect_geometry as collect_outlines
from .utility import find_row, find_rows

CONFIG = {
    "Frame": {
        "Taper": "Subdivide", # Integrate
        "Element": "PrismFrame",
    }
}



def create_materials(csi, model, conv):
    "SD STRESS-STRAIN 01 - REBAR PARK"
    "SD STRESS-STRAIN 02 - REBAR SIMPLE"
    "SD STRESS-STRAIN 03 - STRUCTURAL STEEL"
    "SD STRESS-STRAIN 04 - CONCRETE SIMPLE"
    "SD STRESS-STRAIN 05 - CONCRETE MANDER UNCONFINED"
    "SD STRESS-STRAIN 06 - CONCRETE MANDER CONFINED CIRCLE"
    "SD STRESS-STRAIN 07 - CONCRETE MANDER CONFINED RECTANGLE"
    library = conv._library

    # 1) Material

    #
    # 2) Links
    #
    mat_total = 1

    for mat in csi.get("MATERIAL PROPERTIES 01 - GENERAL", []):
        if mat["SymType"] == "Isotropic":
            pass
        else:
            conv.log(UnimplementedInstance("Material", mat))
            continue
        
        p02 = find_row(csi.get("MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES", []), Material=mat["Material"])

        name = mat["Material"]
        model.nDMaterial(
            "ElasticIsotropic",
            conv.define("Material", "material", name),
            p02["E1"],  # Young
            p02["U12"], # Poisson
        )

    for link in csi.get("LINK PROPERTY DEFINITIONS 02 - LINEAR", []):
        if link["Fixed"]:
            conv.log(UnimplementedInstance("Link.Fixed", link))
            continue

        name = link["Link"]
        if "R" in link["DOF"]:
            stiff = link["RotKE"]
            damp  = link["RotCE"]
        else:
            stiff = link["TransKE"]
            damp  = link["TransCE"]

        # TODO: use damp
        model.eval(f"material ElasticIsotropic {mat_total} {stiff} 0.3\n")

        dof = link["DOF"]
        library["link_materials"][name][dof] = mat_total
        mat_total += 1

    for damper in csi.get("LINK PROPERTY DEFINITIONS 04 - DAMPER", []):
        # TODO: implement dampers
        conv.log(UnimplementedInstance("Link.Damper", damper))
        continue
        name = damper["Link"]
        stiff = damper["TransK"]
        dampcoeff = damper["TransC"]
        exp = damper["CExp"]
        model.eval(f"uniaxialMaterial ViscousDamper {mat_total} {stiff} {dampcoeff}' {exp}\n")

        dof = damper["DOF"]
        library["link_materials"][name][dof] = mat_total
        mat_total += 1


    for link in csi.get("LINK PROPERTY DEFINITIONS 10 - PLASTIC (WEN)", []):
        name = link["Link"]

        if not link.get("Nonlinear", False):
            stiff = link["TransKE"]
            model.eval(f"uniaxialMaterial Elastic {mat_total} {stiff}\n")
        else:
            stiff = link["TransK"]
            fy    = link["TransYield"]
            exp   = link["YieldExp"] # TODO
            ratio = link["Ratio"]
            model.eval(f"uniaxialMaterial Steel01 {mat_total} {fy} {stiff} {ratio}\n")

        dof = link["DOF"]
        library["link_materials"][name][dof] = mat_total
        mat_total += 1
    return library


def _create_sections(csi, model, conv):
    # 2) Frame
    if len(csi.get("CONNECTIVITY - FRAME", [])) > 0:
        add_frame_sections(csi, model, conv)


    # 3) Shell
    add_shell_sections(csi, model, conv)



def assemble(csi, model=None, verbose=False):
    from xcsi.job import Job
    return Job(csi).assemble(verbose=verbose)



def create_model(csi, types=None, model=None, verbose=False, names=None):
    """
    Parameters
    ==========
    csi: a dictionary formed by calling ``csi.parse.load("file.b2k")``

    Returns
    =======
    model: opensees.openseespy.Model object
    """

    import opensees.openseespy as ops

    config = CONFIG

    used = {
        "TABLES AUTOMATICALLY SAVED AFTER ANALYSIS"
    }


    #
    # Create model
    #
    dofs = {key:val for key,val in csi["ACTIVE DEGREES OF FREEDOM"][0].items() } # if val }
    dims = {key for key,val in csi["ACTIVE DEGREES OF FREEDOM"][0].items() } # if val }
    ndf = sum(1 for v in csi["ACTIVE DEGREES OF FREEDOM"][0].values())
    ndm = sum(1 for k,v in csi["ACTIVE DEGREES OF FREEDOM"][0].items()
              if k[0] == "U")

    if isinstance(verbose, int) and verbose > 3:
        import sys
        echo_file = sys.stdout
    else:
        echo_file = None

    if model is None:
        model = ops.Model(ndm=ndm, ndf=ndf, echo_file=echo_file)

    if names is None:
        names = Names()

    used.add("ACTIVE DEGREES OF FREEDOM")

#   dofs = [f"U{i}" for i in range(1, ndm+1)]
#   if ndm == 3:
#       dofs = dofs + ["R1", "R2", "R3"]
#   else:
#       dofs = dofs + ["R3"]

    config["ndm"]  = ndm
    config["ndf"]  = ndf
    config["dofs"] = dofs

    #
    # Create nodes
    #
    create_points(csi, model, None, config, names)

    #
    # Create materials and sections
    #
    library = create_materials(csi, model, names)

    _create_sections(csi, model, names)


    # Unimplemented objects
    for item in [
        "CONNECTIVITY - CABLE",
        "CONNECTIVITY - TENDON"]:
        for elem in csi.get(item, []):
            names.log(UnimplementedInstance(item, elem))

    #
    # Add elements
    #
    _add_elements(model, csi, library, config, names)


    if verbose and len(names._log) > 0:
        print_log(names._log)

    if verbose and False:
        for table in csi:
            if table not in used:
                print(f"\t{table}", file=sys.stderr)


    model.frame_tags = library.get("frame_tags", {})
    return model


def _add_elements(model, csi, library, config, names):
    """
    Add elements to the model.
    """
    from ._frame import add_frames
    from ._shell import add_shells
    from ._solid import add_solids

    create_links(csi, model, library, config, names)
    add_frames(csi, model, library, config, names)
    add_shells(csi, model, names)
    add_solids(csi, model, config, names)
