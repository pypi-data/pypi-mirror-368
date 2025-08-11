#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#
# August 2025
#
import os
import contextlib
import numpy as np
import tqdm

import veux
import xara
from xcsi.csi import collect_outlines, load as load_csi
from xcsi.job import Job
from xcsi.metrics import PeakDrift


from dataclasses import dataclass

@dataclass
class Datum:
    angle_x: float = 0.0
    angle_y: float = 0.0


    def to_cardinal(self):
        """
        Create rotation matrix from datum basis to cardinal basis.
        The cardinal basis is defined as:
        cx = North, 
        cy = East, 
        cz = Up

        The datum basis is defined as:
        ex = Exp(orient_x cz) cx
        ey = Exp(orient_y cz) cy
        ez = Exp(orient_z cz) cz
        where orient_x, orient_y, and orient_z are the angles in radians and
        Exp is the exponential map which encodes the Rodrigues' rotation formula.

        We want to return the rotation Rec  such that:
            Rec @ [ex, ey, ez] = [cx, cy, cz]
        """
        import numpy as np
        from shps.rotor import exp

        orient_x = self.angle_x
        orient_y = self.angle_y

        ex, ey, ez = np.eye(3)
        cz = ez
        cx = exp(-orient_x*cz) @ ex
        cy = exp(-orient_y*cz) @ ey

        rotation = np.column_stack((cx, cy, cz))

        return rotation
    
    def to_other(self, other: "Datum"):
        """
        Create rotation matrix from datum basis to other datum basis.
        """
        R_cs = self.to_cardinal()
        R_cm = other.to_cardinal()
        return R_cm.T @ R_cs



def _analyze_and_render(model, artist, nt, dt):
    import veux, veux.motion

    motion = veux.motion.Motion(artist)
    for i in tqdm.tqdm(range(nt)):
        if model.analyze(1, dt) != 0:
            return -1
        motion.advance(i*dt)
        motion.draw_sections(position=lambda x: [1000*u for u in model.nodeDisp(x)],
                             rotation=model.nodeRotation)
        
    motion.add_to(artist.canvas)
    return 0


@contextlib.contextmanager
def new_cd(x):
    d = os.getcwd()
    # This could raise an exception, but it's probably
    # best to let it propagate and let the caller
    # deal with it, since they requested x
    os.chdir(x)

    try:
        yield

    finally:
        # This could also raise an exception, but you *really*
        # aren't equipped to figure out what went wrong if the
        # old working directory can't be restored.
        os.chdir(d)


def _create_excitation(asm, inputs, dt):
    import numpy as np
    model = asm.model
    units = asm.units

    if units is None:
        raise ValueError("Units not defined in assembly")

    rotation = np.eye(3)
    i = 1
    for sensor in inputs.values():
        if sensor["role"] == "input":
            for dof in range(3):
                series = sum(ai*dx*units.cm
                            for ai, dx in zip(np.array(sensor["series"]), rotation[dof]))

                model.timeSeries("Path", i, dt=dt, values=series.tolist())
                model.pattern("UniformExcitation", i, dof+1, accel=i)
                i += 1



def _create_inputs(event, config):

    nt = 0
    dt = 0.02

    inputs = {}
    R_ms = Datum(**config["sensor_group"]["datum"]).to_other(Datum(**config["predictor"]["datum"]))

    for sensor_assign in config["sensor_assign"]:
        sensor = next((s for s in config["sensor_group"]["sensors"]
                       if s["id"] == sensor_assign["id"]), None)
        if sensor is None:
            raise ValueError(f"Sensor {sensor_assign['id']} not found in sensor group")

        sensor_series = event.match("l", station_channel=str(sensor["id"])).accel.data
        # Series in the Sensor coordinate system
        series_s = [
            dx*sensor_series for dx in sensor["orient"]
        ]
        # Series in the Model coordinate system
        series_m = [
            sum(mij*si for mij in mi).tolist() for mi, si in zip(R_ms.T, series_s)
        ]

        inputs[sensor["id"]] = {
            "role":  "input",
            "series": series_m
        }
        nt = len(series_m[0])


    return inputs, nt, dt



def runPrediction(csi, event, config):

    # 1) Event
    nt = 500
    dt = 0.02
    inputs, nt, dt = _create_inputs(event, config)


    # Create model

    with new_cd(config["directory"]), open("model.tcl", "w") as echo_file:

        model = xara.Model(ndm=3, ndf=6, echo_file=echo_file)
        asm = Job(csi).assemble(model=model)

        sections = collect_outlines(csi, model.frame_tags)

        #
        # DAMPING
        #

        #
        # DYNAMIC RECORDERS
        #

        ## COLUMN SECTION DEFORMATIONS AT TOP AND BOTTOM FOR STRAIN-BASED DAMAGE STATES
        if False:
            column_strains = tuple(k["key"] for k in self.runs[run_id]["columns"] if k["strain"])
            if len(column_strains) > 0:
                model.recorder("Element",  "section", 1, "deformation", xml="eleDef1.txt", ele=column_strains) # section 1 deformation]
                model.recorder("Element",  "section", 4, "deformation", xml="eleDef4.txt", ele=column_strains) # section 4 deformation]

        # RESPONSE HISTORY RECORDERS
        metrics = [
            PeakDrift((31, 81))
        ]

        for metric in metrics:
            metric.record(asm)


        #
        # Run dynamic analysis
        #
        _create_excitation(asm, inputs, dt)
        
        model.eval(f"print -json -file model.json")

        model.eval(f"""
        wipeAnalysis
        set NewmarkGamma    0.50;
        set NewmarkBeta     0.25;
        constraints Transformation;
        numberer    RCM;
        test        EnergyIncr 1.0e-8 50 0;
        system      Umfpack;
        integrator  Newmark $NewmarkGamma $NewmarkBeta;
        algorithm   Newton;
        analysis    Transient;
        """)

        artist = veux.create_artist(model, vertical=3, model_config={
                "frame_outlines": sections
        })
        _analyze_and_render(model, artist, nt, dt)

        artist.save("motion.glb")

        model.wipe()


if __name__ == "__main__":
    import quakeio 
    import sys 

    config = {
        "directory": "./0/",

        "sensor_group": {
            "datum":  {"angle_x": 0, "angle_y": 0},
            "sensors": [
                {"id": 1, "orient": [1.0, 0.0, 0.0]},
                {"id": 3, "orient": [0.0, 1.0, 0.0]}
            ]
        },

        # Predictor
        "sensor_assign": [
            {"id": 1, "role": "input"},
            {"id": 3, "role": "input"},
        ],

        "metrics": [
            {"type": "PeakDrift", "joints": [31, 81]},
            {"type": "VeuxMotion"}
        ],

        "predictor": {
            "datum": {"angle_x": 0, "angle_y": 0},
        }
    }


    with open(sys.argv[1], "r") as f:
        csi = load_csi(f)

    event = quakeio.read(sys.argv[2])

    runPrediction(csi, event, config)
