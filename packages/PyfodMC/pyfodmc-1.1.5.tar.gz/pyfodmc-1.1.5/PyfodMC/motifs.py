"""
Define motifs to be used for core and bond/lone FODs
"""

import numpy


class Motifs:
    def get_motif(self, 
                  no_points=1, 
                  r=1, 
                  core_or_bond="core"):
        if no_points == 0:
            pos = numpy.array([])
        elif no_points == 1:
            pos = self.point_alongz(r=r)
        elif no_points == 2:
            pos = self.line_alongz(r=r)
        elif no_points == 3:
            pos = self.triangle_alongz(r=r)
        elif no_points == 4:
            if core_or_bond == "core":
                pos = self.tetrahedron_alongz(r=r)
            elif core_or_bond == "bond" or core_or_bond == "lone":
                pos = self.fourgon_alongz(r=r)
                # pos = self.ngon_plane(n=no_points,r=r)
        # for bonds with N > 4
        elif core_or_bond == "bond":
            pos = self.ngon_plane(n=no_points, r=r)
        else:
            if no_points == 5:
                pos = self.fivegon_alongz(r=r)
            if no_points == 6:
                pos = self.sixgon_alongz(r=r)
            if no_points == 7:
                pos = self.sevengon_alongz(r=r)
            if no_points == 8:
                pos = self.eightgon_alongz(r=r)
            if no_points == 9:
                pos = self.ninegon_alongz(r=r)
            if no_points == 10:
                pos = self.tengon_alongz(r=r)
            if no_points == 11:
                pos = self.elevengon_alongz(r=r)
            if no_points == 12:
                pos = self.twelvegon_alongz(r=r)
            if no_points == 13:
                pos = self.thirteengon_alongz(r=r)
        return pos

    def ngon_plane(self, n=2, r=1.0):
        """
        Create ngon in a plane
        - can be used for any bond > 4
        """
        pos = numpy.zeros((n, 3))
        angle = 2 * numpy.pi / n
        for bla in range(n):
            z = r * numpy.cos(angle * bla)
            x = r * numpy.sin(angle * bla)
            pos[bla] = [x, 0, z]
        return pos

    def point_alongz(self, r=1.0):
        """
        Single point along z
        """
        pos = numpy.zeros((1, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos *= r
        return pos

    def line_alongz(self, r=1.0):
        """
        Line (2 points) along z
        """
        pos = numpy.zeros((2, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos[1] = [0.0, 0.0, -1.0]
        pos *= r
        return pos

    def triangle_alongz(self, r=1.0):
        """
        Triangle along z
        """
        pos = numpy.zeros((3, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos[1] = [numpy.sqrt(3.0 / 4.0), 0.0, -0.5]
        pos[2] = [-1.0 * numpy.sqrt(3.0 / 4.0), 0.0, -0.5]
        pos *= r
        return pos

    def tetrahedron_alongz(self, r=1.0):
        """
        Tetrahedron, aligned along z
        """
        pos = numpy.zeros((4, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos[1] = [numpy.sqrt(8.0 / 9.0), 0.0, -1.0 / 3.0]
        pos[2] = [-1.0 * numpy.sqrt(2.0 / 9.0), numpy.sqrt(2.0 / 3.0), -1.0 / 3.0]
        pos[3] = [
            -1.0 * numpy.sqrt(2.0 / 9.0),
            -1.0 * numpy.sqrt(2.0 / 3.0),
            -1.0 / 3.0,
        ]
        pos *= r
        return pos

    def fourgon_alongz(self, r=1.0):
        """
        Quadruple bond
        """
        pos = numpy.zeros((4, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos[1] = [numpy.sqrt(3.0 / 4.0), 0.0, -0.5]
        pos[2] = [-1.0 * numpy.sqrt(3.0 / 4.0), 0.0, -0.5]
        pos[3] = [0.0, 0.0, 0.0]
        pos *= r
        return pos

    def fivegon_alongz(self, r=1.0):
        """
        5-gon (triangle + line) along z
        """
        pos = numpy.zeros((5, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos[1] = [0.0, 0.0, -1.0]
        pos[2] = [1.0, 0.0, 0.0]
        pos[3] = [-0.5, numpy.sqrt(0.75), 0.0]
        pos[4] = [-0.5, -1.0 * numpy.sqrt(0.75), 0.0]
        pos *= r
        return pos

    def sixgon_alongz(self, r=1.0):
        """
        6-gon (octahedron) along z
        """
        pos = numpy.zeros((6, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos[1] = [0.0, 0.0, -1.0]
        pos[2] = [1.0, 0.0, 0.0]
        pos[3] = [-1.0, 0.0, 0.0]
        pos[4] = [0.0, 1.0, 0.0]
        pos[5] = [0.0, -1.0, 0.0]
        pos *= r
        return pos

    def sevengon_alongz(self, r=1.0):
        """
        7-gon (pentagon + line) along z
        """
        pos = numpy.zeros((7, 3))
        pos[0] = [0, 0, 1]
        pos[1] = [0, 0, -1]
        pos[2] = [1, 0, 0]
        pos[3] = [
            numpy.sin(18.0 / 360 * 2.0 * numpy.pi),
            numpy.sin(72.0 / 360 * 2.0 * numpy.pi),
            0.0,
        ]
        pos[4] = [
            numpy.sin(18.0 / 360 * 2.0 * numpy.pi),
            -1.0 * numpy.sin(72.0 / 360 * 2.0 * numpy.pi),
            0.0,
        ]
        pos[5] = [
            -1.0 * numpy.sin(54.0 / 360 * 2.0 * numpy.pi),
            numpy.sin(36.0 / 360 * 2.0 * numpy.pi),
            0.0,
        ]
        pos[6] = [
            -1.0 * numpy.sin(54.0 / 360 * 2.0 * numpy.pi),
            -1.0 * numpy.sin(36.0 / 360 * 2.0 * numpy.pi),
            0.0,
        ]
        pos *= r
        return pos

    def eightgon_alongz(self, r=1.0):
        """
        8-gon (twisted cube) along z; from fodMC
        """
        pos = numpy.zeros((8, 3))
        pos[0] = [0.523842100, 0.641286608, 0.5595346325]
        pos[1] = [-0.523842100, -0.641286608, 0.5595346325]
        pos[2] = [-0.824785975, -0.082731438, -0.5595346325]
        pos[3] = [0.824785975, 0.082731438, -0.5595346325]
        pos[4] = [-0.641286608, 0.523842100, 0.5595346325]
        pos[5] = [0.641286608, -0.523842100, 0.5595346325]
        pos[6] = [-0.082731438, 0.824785975, -0.5595346325]
        pos[7] = [0.082731438, -0.824785975, -0.5595346325]
        pos *= r
        return pos

    def ninegon_alongz(self, r=1.0):
        """
        9-gon (twisted cube + pole) along z; from fodMC
        """
        pos = numpy.zeros((9, 3))
        pos[0] = [0, 0, 1]
        pos[1] = [0.47353004441203156, 0.80594647912770400, 0.35527598454680115]
        pos[2] = [-0.47353004441203156, -0.80594647912770400, 0.35527598454680115]
        pos[3] = [-0.27326802860984000, 0.82178524771742300, -0.5]
        pos[4] = [0.27326802860984000, -0.82178524771742300, -0.5]
        pos[5] = [-0.66769965479981240, -0.22203384174912840, -0.71054777716017660]
        pos[6] = [0.66769965479981240, 0.22203384174912840, -0.71054777716017660]
        pos[7] = [0.86187128595732240, -0.36187760873760340, 0.35527598454680115]
        pos[8] = [-0.86187128595732240, 0.36187760873760340, 0.35527598454680115]
        pos *= r
        return pos

    def tengon_alongz(self, r=1.0):
        """
        10-gon (twisted cube + 2 poles) along z; from fodMC
        """
        pos = numpy.zeros((10, 3))
        pos[0] = [0, 0, 1]
        pos[1] = [0, 0, -1]
        pos[2] = [0.57697333050312170, -0.69888428215415700, 0.42268501450052165]
        pos[3] = [-0.57697333050312170, 0.69888428215415700, 0.42268501450052165]
        pos[4] = [-0.90216746645970310, 0.08620418087144224, -0.42268501450052165]
        pos[5] = [0.90216746645970310, -0.08620418087144224, -0.42268501450052165]
        pos[6] = [-0.08620418087144224, -0.90216746645970310, -0.42268501450052165]
        pos[7] = [0.08620418087144224, 0.90216746645970310, -0.42268501450052165]
        pos[8] = [0.69888428215415700, 0.57697333050312170, 0.42268501450052165]
        pos[9] = [-0.69888428215415700, -0.57697333050312170, 0.42268501450052165]
        pos *= r
        return pos

    def elevengon_alongz(self, r=1.0):
        """
        11-gon (optimized on sphere, symmetrized) along z
        """
        pos = numpy.zeros((11, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos[1] = [0.0, 0.0, -1.0]
        pos[2] = [-0.8811173318878970, 0.0, 0.50576613432521511]
        pos[3] = [0.8811173318878970, 0.0, 0.50576613432521511]
        pos[4] = [-0.8811173318878970, 0.0, -0.50576613432521511]
        pos[5] = [0.6907077686855492, 0.5919768905769777, -0.41531450653670410]
        pos[6] = [0.6907077686855492, -0.5919768905769777, -0.41531450653670410]
        pos[7] = [-0.3962306096476184, 0.8559263424032470, -0.33225197574049019]
        pos[8] = [-0.3962306096476184, -0.8559263424032470, -0.33225197574049019]
        pos[9] = [0.1076602931240165, 0.8559263424032470, 0.50576613432521511]
        pos[10] = [0.1076602931240165, -0.8559263424032470, 0.50576613432521511]
        pos *= r
        return pos

    def twelvegon_alongz(self, r=1.0):
        """
        12-gon (optimized on sphere, symmetrized) along z
        """
        pos = numpy.zeros((12, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos[1] = [0.0, 0.0, -1.0]
        pos[2] = [0.8944271964414205, 0.0, -0.4472136093200896]
        pos[3] = [-0.8944271964414205, 0.0, 0.4472136093200896]
        pos[4] = [-0.7236067608996548, 0.5257311002899420, -0.4472136093200896]
        pos[5] = [0.7236067608996548, -0.5257311002899420, 0.4472136093200896]
        pos[6] = [-0.7236067608996548, -0.5257311002899420, -0.4472136093200896]
        pos[7] = [0.7236067608996548, 0.5257311002899420, 0.4472136093200896]
        pos[8] = [-0.2763932535717489, 0.8506508093627088, 0.4472136093200896]
        pos[9] = [0.2763932535717489, -0.8506508093627088, -0.4472136093200896]
        pos[10] = [-0.2763932535717489, -0.8506508093627088, 0.4472136093200896]
        pos[11] = [0.2763932535717489, 0.8506508093627088, -0.4472136093200896]
        pos *= r
        return pos

    def thirteengon_alongz(self, r=1.0):
        """
        13-gon (optimized on sphere, symmetrized) along z
        """
        pos = numpy.zeros((13, 3))
        pos[0] = [0.0, 0.0, 1.0]
        pos[1] = [0.0, 0.7914041835107868, 0.6112932341140491]
        pos[2] = [0.0, -0.7914041835107868, 0.6112932341140491]
        pos[3] = [0.0, -0.5052436675057863, -0.8629767298624487]
        pos[4] = [0.0, 0.5052436675057863, -0.8629767298624487]
        pos[5] = [-0.8521756639771645, 0.0, 0.5006051956338737]
        pos[6] = [0.8521756639771645, 0.0, 0.5006051956338737]
        pos[7] = [0.8521756639771645, 0.0, -0.5446312612755209]
        pos[8] = [-0.8521756639771645, 0.0, -0.5446312612755209]
        pos[9] = [-0.5801427167040671, 0.8078028455389760, -0.1043503274002259]
        pos[10] = [0.5801427167040671, 0.8078028455389760, -0.1043503274002259]
        pos[11] = [-0.5801427167040671, -0.8078028455389760, -0.1043503274002259]
        pos[12] = [0.5801427167040671, -0.8078028455389760, -0.1043503274002259]
        pos *= r
        return pos


def test_motifs():
    """
    Test Motifs functionality.
    """
    mymotif = Motifs()
    pos = mymotif.get_motif(no_points=8, r=2, core_or_bond="bond")
    print(pos)


if __name__ == "__main__":
    test_motifs()
