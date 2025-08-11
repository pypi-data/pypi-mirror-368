#===----------------------------------------------------------------------===#
#
#         STAIRLab -- STructural Artificial Intelligence Laboratory
#
#===----------------------------------------------------------------------===#
#

class PeakDrift:
    def __init__(self, joints):
        self._joints = joints


    def record(self, asm):
        model = asm.model

        i = asm.names.identify("Joint", "node", self._joints[0])
        j = asm.names.identify("Joint", "node", self._joints[1])

        model.recorder("Node", "disp", node=(i,j), file=str(id(self)), dof=(1,2,3))


    def draw(self):
        pass


    def retrieve(self):
        return
