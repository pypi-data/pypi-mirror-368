import numpy
from PyfodMC.helperfunctions import HelperFunctions

class Cores(HelperFunctions):
    def create_core(self):
        """
        Create the core FOD positions via rotations
        For tetrahedra: use atomic positions to rotate tetrahedron accordingly (default)
        Otherwise: Rotate to minimize 1/r to all other bond/lone FODs

        Requires:
            - self.atomic_pos
            - self.fods
            - self.bond_partners
            - self.is_linear_planar
            - self.dist_vecs
            - self.rotmat_vec1vec2()
            - self.rotmat_around_axis()

        Provides:
            - self.fods (modified)

        Returns:
            All core FODs positions
        """
        cores = []

        for s, sym in enumerate(self.atomic_sym):
            # If there is a core, and it is more than 1 (up or dn channel)

            if (
                len(self.fods[s][0]) > 1 or len(self.fods[s][1]) > 1
            ) and self.bond_partners[s] != []:
                # monitor how many up and dn, so we can put them into self.fods later on
                fods_to_rot = []
                core_up = 0
                core_dn = 0
                for f, shell in enumerate(self.fods[s][0]):
                    for fodpos in shell:
                        fods_to_rot.append(fodpos.tolist())
                        core_up += 1
                for f, shell in enumerate(self.fods[s][1]):
                    for fodpos in shell:
                        fods_to_rot.append(fodpos.tolist())
                        core_dn += 1
                fods_to_rot = numpy.array(fods_to_rot)
                # Shift all core FODs to origin
                fods_to_rot -= self.atomic_pos[s]

                # Identify the tetrahedron shell -> use that for all rotations
                # Teteahedron shell has 4 fods
                # Prefer UP vs DN
                # Take the last tetrahedron shell
                # Store positions, to assign rotations correctly
                tetra_up = [f for f in self.fods[s][0] if len(f) == 4]
                tetra_dn = [f for f in self.fods[s][1] if len(f) == 4]
                #
                if tetra_up == [] and tetra_dn != []:
                    tetra = tetra_dn[-1] - self.atomic_pos[s]
                elif tetra_up != []:
                    tetra = tetra_up[-1] - self.atomic_pos[s]
                else:
                    tetra = []

                # Actually: Take any tetrahedron in the core -> rotate accordingly; if nothing is available, do the 1/r thing
                # If tetrahedron AND planar -> rotate out-of-plane
                # If tetrahedron and linear -> rotate into bond axis
                # Anyhting else: Rotate wrt bond vectors;
                # for No tetrahedron: Do 1/r
                if len(tetra) != 0:
                    if self.is_linear_planar[s] in ["planar4both", "planar4bonds"]:
                        # Get out-of-plane direction; move two FODs in there
                        bonds = [
                            self.dist_vecs[s][partner]
                            / numpy.linalg.norm(self.dist_vecs[s][partner])
                            for partner in self.bond_partners[s]
                        ]
                        outofplane = numpy.cross(
                            bonds[0], bonds[1]
                        ) / numpy.linalg.norm(numpy.cross(bonds[0], bonds[1]))
                        # Rotate into outofplane
                        vec2rot = tetra[0] - tetra[1]
                        rotmat = self.rotmat_vec1vec2(vec2rot, outofplane)
                        # Rotate
                        rotpos = numpy.array(
                            [numpy.matmul(rotmat, po) for po in fods_to_rot]
                        )
                        # Also rotate tetra, to have correct positions for additonal rotations
                        tetra = numpy.array([numpy.matmul(rotmat, po) for po in tetra])

                        # need rotated positions
                        vec2rot = tetra[2] - tetra[3]
                        # Define rotation axis and angle
                        # Angle can be defined by rotating the other two tetrahedra poitions to align with a vector vconnecting any two bonding partners
                        tmp_vec = bonds[0] - bonds[1]
                        angle = numpy.arccos(
                            numpy.dot(vec2rot, tmp_vec)
                            / (numpy.linalg.norm(vec2rot) * numpy.linalg.norm(tmp_vec))
                        )

                        # Current hack: No better ideas right now. This might work though
                        if angle > numpy.pi / 2.0:
                            vec2rot = tetra[3] - tetra[2]
                            angle = numpy.arccos(
                                numpy.dot(vec2rot, tmp_vec)
                                / (
                                    numpy.linalg.norm(vec2rot)
                                    * numpy.linalg.norm(tmp_vec)
                                )
                            )
                        rotmat = self.rotmat_around_axis(axis=outofplane, angle=angle)

                        # For planar: The first tetrahedron positions should be closer to the adjactend bonds than the in-plane ones
                        # Also rotate tetra, to have correct positions for additonal rotations
                        tetra = numpy.array([numpy.matmul(rotmat, po) for po in tetra])
                        # Check distances to neighbors; if first two further away -> invert
                        _, dist_mat = self.get_distances(
                            tetra + self.atomic_pos[s],
                            self.atomic_pos[self.bond_partners[s][0]],
                            cell=self.cell,
                            pbc=self.pbc,
                        )
                        if min(dist_mat[0], dist_mat[1]) > min(
                            dist_mat[2], dist_mat[3]
                        ):
                            factor = -1
                        else:
                            factor = 1

                        # Final cores; maybe invert due to rotations above
                        fods_to_rot = (
                            numpy.array(
                                [numpy.matmul(rotmat, po) * factor for po in rotpos]
                            )
                            + self.atomic_pos[s]
                        )

                        cores.append([[fods_to_rot[:core_up]], [fods_to_rot[core_up:]]])
                        # overwrite original pos -> won;t be written
                        self.fods[s][0] = [[], []]
                        self.fods[s][1] = [[], []]

                    elif self.is_linear_planar[s] in ["linear4both", "linear4bonds"]:
                        # Align two FODs with the bond direction; rotate the others to propely align out-of-axis
                        bonds = [
                            self.dist_vecs[s][partner]
                            / numpy.linalg.norm(self.dist_vecs[s][partner])
                            for partner in self.bond_partners[s]
                        ]
                        # Rotate into into bond axis
                        vec2rot = tetra[0] - tetra[1]
                        rotmat = self.rotmat_vec1vec2(vec2rot, bonds[0])

                        # Rotate
                        # Final cores
                        fods_to_rot = (
                            numpy.array(
                                [numpy.matmul(rotmat, po) for po in fods_to_rot]
                            )
                            + self.atomic_pos[s]
                        )
                        cores.append([[fods_to_rot[:core_up]], [fods_to_rot[core_up:]]])
                        # overwrite original pos -> won;t be written
                        self.fods[s][0] = [[], []]
                        self.fods[s][1] = [[], []]



                    else:
                        # We should always have more than 2 bond partners here!  NOT TRUE !!!! mol07 .. THINK
                        #  we should rotate teta[0]-tetra[1] into outofaxis
                        # SINGLE bond partner!!
                        if len(self.bond_partners[s]) == 1:
                            bonds = [
                                self.dist_vecs[s][partner]
                                / numpy.linalg.norm(self.dist_vecs[s][partner])
                                for partner in self.bond_partners[s]
                            ]


                            # Check neighbors; if planar -> orient out of plane
                            if numpy.any(
                                [
                                    self.is_linear_planar[s2] in ["planar4bonds", "planar4both"]
                                    for s2 in self.bond_partners[s]
                                ]
                            ):
                                # Check which atom is planar -> get in-plane direction
                                # QUestion: If there is more than 1 -> does it matter??
                                #   we just take the first one for now
                                planar = [
                                    s2
                                    for s2 in self.bond_partners[s]
                                    if self.is_linear_planar[s2] in ["planar4bonds", "planar4both"]
                                ][0]
                                bonds_planar = [
                                    self.dist_vecs[planar][partner]
                                    / numpy.linalg.norm(self.dist_vecs[planar][partner])
                                    for partner in self.bond_partners[planar]
                                ]
                                outofplane = numpy.cross(
                                    bonds_planar[0], bonds_planar[1]
                                ) / numpy.linalg.norm(numpy.cross(bonds_planar[0], bonds_planar[1]))

                                rotmat = self.rotmat_vec1vec2(tetra[0]-tetra[1], outofplane)
                                # rotate
                                fods_to_rot = (
                                    numpy.array(
                                        [numpy.matmul(rotmat, po) for po in fods_to_rot]
                                    )
                                )
                                # rotate tetra for further rotations
                                tetra = numpy.array([numpy.matmul(rotmat, po) for po in tetra])
                            else:
                                # Find 1st rotation matrix, analogous to Bonds
                                outofaxis = numpy.cross(
                                    bonds[0], [0, 0, 1]
                                )  # /numpy.linalg.norm(numpy.cross(vec_bond,[0,0,1]))
                                if outofaxis.tolist() == [0, 0, 0]:
                                    outofaxis = numpy.cross(bonds[0], [1, 0, 0]) / numpy.linalg.norm(
                                        numpy.cross(bonds[0], [1, 0, 0])
                                    )
                                else:
                                    outofaxis /= numpy.linalg.norm(outofaxis)
                                # Rotate tmp into outofaxis
                                rotmat = self.rotmat_vec1vec2(tetra[0]-tetra[1], outofaxis)
                                fods_to_rot = (
                                    numpy.array(
                                        [numpy.matmul(rotmat, po) for po in fods_to_rot]
                                    )
                                )
                                # rotate tetra for further rotations
                                tetra = numpy.array([numpy.matmul(rotmat, po) for po in tetra])


                            # rotate tetra, to have correct positions for additonal rotations
                            # also make sure that tetra[0]-tetra[1] is closer to the bond center; just convention; TODO
                            # Check distances to neighbors; if first two further away -> invert
                            _, dist_mat = self.get_distances(
                                tetra + self.atomic_pos[s],
                                self.atomic_pos[self.bond_partners[s][0]],
                                cell=self.cell,
                                pbc=self.pbc,
                            )

                            # Get first two tetrahedra closer to the atoms, via inversion
                            # This is convention
                            if min(dist_mat[0], dist_mat[1]) > min(dist_mat[2], dist_mat[3]):
                                factor = -1
                            else:
                                factor = 1

                            # perpendicular to this and to bond need to be tetra[2]-tetra[3]; rotate them!
                            orientation = numpy.cross(bonds[0],tetra[0]-tetra[1])/numpy.linalg.norm(numpy.cross(bonds[0],tetra[0]-tetra[1]))
                            angle = numpy.arccos(numpy.dot(tetra[2]-tetra[3],orientation)
                            / (numpy.linalg.norm(tetra[2]-tetra[3]) * numpy.linalg.norm(orientation)) )
                            # Current hack: No better ideas right now. This might work though
                            if angle > numpy.pi / 2.0:
                                angle = numpy.arccos(numpy.dot(tetra[3]-tetra[2],orientation)
                                / (numpy.linalg.norm(tetra[3]-tetra[2]) * numpy.linalg.norm(orientation)))

                            #rotmat = self.rotmat_around_axis(axis=outofplane, angle=angle)
                            rotmat = self.rotmat_around_axis(axis=orientation, angle=angle)

                            # rotate tetra -> if the angle between tetra[2]-tetra[3] and orientation is not correct -> do something else!
                            # Check angle
                            tetra = numpy.array([numpy.matmul(rotmat, po) for po in tetra])
                            # This is numerical check only
                            dottmp = numpy.dot(tetra[2]-tetra[3],orientation) / (numpy.linalg.norm(tetra[2]-tetra[3]) * numpy.linalg.norm(orientation)) 
                            if dottmp > +1: dottmp = +1
                            if dottmp < -1: dottmp = -1
                            # if not 1, -1 -> wrong rotation
                            if abs(dottmp) < 0.99:
                                # rotate backwards
                                angle *= -1
                                #rotmat = self.rotmat_around_axis(axis=outofplane, angle=angle)
                                rotmat = self.rotmat_around_axis(axis=orientation, angle=angle)

                            # Final cores; maybe invert due to rotations above
                            fods_to_rot = (
                                numpy.array(
                                    [numpy.matmul(rotmat, po) * factor for po in fods_to_rot]
                                )
                                + self.atomic_pos[s]
                            )

                            cores.append([[fods_to_rot[:core_up]], [fods_to_rot[core_up:]]])
                            # overwrite original pos -> won;t be written
                            self.fods[s][0] = [[], []]
                            self.fods[s][1] = [[], []]

                        # more than 1 bond partner!!
                        else:
                            # THINK ABOUT THIS!!!!  counter align with vectors between adjacent bonds
                            # Rotate first point into bonds[0]; then use that to rotate the next point into bonds[1]; then invert!
                            bonds = [
                                self.dist_vecs[s][partner]
                                / numpy.linalg.norm(self.dist_vecs[s][partner])
                                for partner in self.bond_partners[s]
                            ]
                            # Rotate into first bond
                            vec2rot = tetra[0]
                            rotmat = self.rotmat_vec1vec2(vec2rot, bonds[0])
                            # Rotate
                            rotpos = numpy.array(
                                [numpy.matmul(rotmat, po) for po in fods_to_rot]
                            )
                            # Also rotate tetra, to have correct positions for additonal rotations
                            tetra = numpy.array([numpy.matmul(rotmat, po) for po in tetra])

                            # need correct rotation angle around bonds[0]!!
                            # We need to find the angle in the plane of the other tetrahedron positions!!!
                            # some dot product of the bonds[1] with that plane ? or just with tetra[1]? and then get angle???
                            # need to project bonds[1] into tetrehedron plane ...

                            # https://math.stackexchange.com/questions/633181/formula-to-project-a-vector-onto-a-plane
                            # 1. plane normal
                            plane_normal = numpy.cross(
                                tetra[1], tetra[2]
                            ) / numpy.linalg.norm(numpy.cross(tetra[1], tetra[2]))
                            # 2. project bonds[1] into that plane
                            proj_bond = bonds[1] - numpy.dot(
                                numpy.dot(bonds[1], plane_normal), plane_normal
                            )
                            # actual angle between this and tetra[1]
                            angle = numpy.arccos(
                                numpy.dot(tetra[1], proj_bond)
                                / (
                                    numpy.linalg.norm(tetra[1])
                                    * numpy.linalg.norm(proj_bond)
                                )
                            )
                            # angle = numpy.arccos(numpy.dot(tetra[1],bonds[1])/(numpy.linalg.norm(tetra[1])*numpy.linalg.norm(bonds[1])))
                            rotmat = self.rotmat_around_axis(axis=bonds[0], angle=angle)

                            rotpos2 = numpy.array(
                                [numpy.matmul(rotmat, po) for po in rotpos]
                            )
                            # Final cores; INVERT THE POSITIONS HERE!!!
                            fods_to_rot = (
                                numpy.array([-1.0 * po for po in rotpos2])
                                + self.atomic_pos[s]
                            )
                            # fods_to_rot = numpy.array([numpy.matmul(rotmat,po) for po in fods_to_rot]) + self.atomic_pos[s]
                            cores.append([[fods_to_rot[:core_up]], [fods_to_rot[core_up:]]])
                            # overwrite original pos -> won;t be written
                            self.fods[s][0] = [[], []]
                            self.fods[s][1] = [[], []]

                # No tetrahedron -> optimize 1/r
                # Note: hould barely trigger
                else:
                    # flatten bonds and lones -> get list of all bond and lone positions in a single, flat list
                    # anything with index > N_atoms == bond,lone
                    flatten_bond_lone = []
                    for a, atm in enumerate(self.fods):
                        if a >= len(self.atomic_pos):
                            for f, shell in enumerate(atm[0]):
                                for fodpos in shell:
                                    flatten_bond_lone.append(fodpos.tolist())
                            for f, shell in enumerate(atm[1]):
                                for fodpos in shell:
                                    flatten_bond_lone.append(fodpos.tolist())
                    flatten_bond_lone = numpy.array(flatten_bond_lone)

                    # TRY: find most symmetric so;lution among all core FODs;
                    # This is terrible code -> to be improved!!!!

                    step = 10  # number of steps in each direction for rotations
                    factor = 1  # factor to subdivide the steps; we will make this larger for smaller divisions

                    # Do stepwise rotation; start with N steps around x,y,z -> then finer grid with N, then finer grid with another N
                    # DO THIS IN A numpy way? Do it differently, very bad this way!
                    minimum = 1e100
                    # Three cycles
                    for rot in range(3):
                        for angle_x in numpy.linspace(
                            -numpy.pi / factor, numpy.pi / factor, step + 1
                        ):  # +1 to take pi into account
                            for angle_y in numpy.linspace(
                                -numpy.pi / factor, numpy.pi / factor, step + 1
                            ):  # +1 to take pi into account
                                for angle_z in numpy.linspace(
                                    -numpy.pi / factor, numpy.pi / factor, step + 1
                                ):  # +1 to take pi into account
                                    # Create rot mat for all! matmul
                                    rotmat_x = self.rotmat_around_axis(
                                        axis=[1, 0, 0], angle=angle_x
                                    )
                                    rotmat_y = self.rotmat_around_axis(
                                        axis=[0, 1, 0], angle=angle_y
                                    )
                                    rotmat_z = self.rotmat_around_axis(
                                        axis=[0, 0, 1], angle=angle_z
                                    )

                                    tmp = numpy.matmul(rotmat_z, rotmat_y)
                                    rotmat = numpy.matmul(tmp, rotmat_x)

                                    # rotate ALL up and dn core FODs of the given atom
                                    rot_pos = numpy.array(
                                        [numpy.matmul(rotmat, po) for po in fods_to_rot]
                                    )
                                    # Get distances to bond/lone
                                    _, distmat = self.get_distances(
                                        rot_pos + self.atomic_pos[s],
                                        flatten_bond_lone,
                                        cell=self.cell,
                                        pbc=self.pbc,
                                    )
                                    # get 1/r as sum of 1/distmat
                                    overR = sum(sum(1.0 / distmat))
                                    if overR < minimum:
                                        minimum = overR
                                        best_rotmat = rotmat

                        # For each step, reset the core FODs; then rotate further
                        fods_to_rot = numpy.array(
                            [numpy.matmul(best_rotmat, po) for po in fods_to_rot]
                        )
                        factor *= step

                    # Final cores
                    fods_to_rot = (
                        numpy.array(
                            [numpy.matmul(best_rotmat, po) for po in fods_to_rot]
                        )
                        + self.atomic_pos[s]
                    )
                    cores.append([[fods_to_rot[:core_up]], [fods_to_rot[core_up:]]])

                    # overwrite original pos -> won;t be written
                    self.fods[s][0] = [[], []]
                    self.fods[s][1] = [[], []]

        return cores
