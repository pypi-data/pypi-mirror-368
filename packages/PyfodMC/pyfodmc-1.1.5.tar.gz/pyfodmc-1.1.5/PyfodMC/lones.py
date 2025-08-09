import numpy
from PyfodMC.helperfunctions import HelperFunctions


class Lones(HelperFunctions):
    def assign_lone(self):
        """
        Assign lone FODs to atoms

        Requires:
            - self.lone (user input)
            - self.atomic_sym
            - self.bond_partners
            - self.core_charge
            - self.con_mat
            - self.charge

        Provides:
            - self.lone (modified)

        Returns:
            None
        """
        # From HelperFunctions
        _, atomic_numbers, chemical_symbols = self.get_atomic_data()

        # First, check self.lone -> if input is an atomic type -> assign lones to all of these types
        # Order: lone_type:[atomic indices OR types]
        dummy = dict()
        for key, value in self.lone.items():
            for val in value:
                if isinstance(val, str):
                    # must be atomic type -> set all indices of all atoms of this type to the value
                    if val in chemical_symbols and val not in self.atomic_sym:
                        raise ValueError(
                            f"\nLones for element {val} specified; this element does not exist in your system: {self.atomic_sym}!"
                        )

                    for s, sym in enumerate(self.atomic_sym):
                        if sym == val:
                            dummy[s] = key
                # Indices are provided explicitely -> just overwrite
                elif isinstance(val, int):
                    if val >= len(self.atomic_sym):
                        raise ValueError(
                            f"\nLones for atomic index {val} specified; however, atomic indices only range from 0 to {len(self.atomic_pos)-1}"
                        )
                    dummy[val] = key
        self.lone = dummy.copy()

        # assign lone FODs based on connectivity matrix
        for s, sym in enumerate(self.atomic_sym):
            # Do not overwrite values that do already exist!!
            if s not in self.lone.keys():
                # if no bonds -> use number of outermost electrons
                if (
                    len(self.bond_partners[s]) == 0
                ):  # sum(self.con_mat[0,s,:]) + sum(self.con_mat[1,s,:]) == 0:
                    self.lone[s] = (
                        f"{len(self.fods[s][0][-1])}-{len(self.fods[s][1][-1])}"
                    )
                else:
                    # fodMC logic... get core charge .. defined in Database
                    core_charge = self.core_charge[s]
                    # for i in range(len(self.fods[s][0])): core_charge += len(self.fods[s][0][i])
                    # for i in range(len(self.fods[s][1])): core_charge += len(self.fods[s][1][i])
                    # Good old fodMC logic: Count electrons; and how many are already assigned; then add lone if any
                    # ruff format did this ..... doesn;t look good
                    if (
                        sum(self.con_mat[0, s, :]) + sum(self.con_mat[1, s, :])
                    ) / 2.0 + self.charge[s] + core_charge < atomic_numbers[sym]:
                        up_lone = int(
                            numpy.ceil(
                                (
                                    atomic_numbers[sym]
                                    - core_charge
                                    - self.charge[s]
                                    - (
                                        sum(self.con_mat[0, s, :])
                                        + sum(self.con_mat[1, s, :])
                                    )
                                    / 2.0
                                )
                                / 2.0
                            )
                        )
                        dn_lone = int(
                            numpy.floor(
                                (
                                    atomic_numbers[sym]
                                    - core_charge
                                    - self.charge[s]
                                    - (
                                        sum(self.con_mat[0, s, :])
                                        + sum(self.con_mat[1, s, :])
                                    )
                                    / 2.0
                                )
                                / 2.0
                            )
                        )
                        self.lone[s] = f"{up_lone}-{dn_lone}"

    # CLEAN THIS UP!! THIS IS TERRIBLE (but should work)
    def make_multiplelones(self, lone_no=1, idx_atom=0, lone_center=[]):
        """
        Make mutliple Lone FODs, based on lone center, bonds, and number of FODs


        Requires:
            - self.dist_vecs
            - self.bond_partners
            - self.atomic_pos
            - self.get_motif()
            - self.ngon_plane()
            - self.rotmat_vec1vec2()
            - self.rotmat_around_axis()
            - self.r_bond
            - self.scale_r
            - self.bond_orientation
            - self.is_linear_planar
            - lone_no which is the number of lone FODs
            - idx_atom which is the index of the atom
            - lone_center which is the position of the center of the lone FODs wrt this atom

        Provides:
            - None

        Returns:
            Lone-FOD positions
        """
        # HERE: if No bond partners -> we should still be doing something here!

        # Define it here again, cause it doesn't cost much
        bonds = [
            self.dist_vecs[idx_atom][partner]
            for partner in self.bond_partners[idx_atom]
        ]

        # Define Motif
        motif = self.get_motif(
            no_points=lone_no, r=self.r_bond * self.scale_r, core_or_bond="bond"
        )
        # If planar or linear -> orient parallel to plane/line; rotate ; rotate perpenmdicular to a bond vector
        # If neighbor planar -> rotate into plane
        # otherwise, try to rotate wrt bonds somehow...

        # NEW
        # if self.bond_orientations contains nearby bonds -> orient wrt that!
        # Copied from Bonds!
        # ADD EXPLANATION!!!
        for keys, values in self.bond_orientation.items():
            # Dont do this for linear/planar; actually do it for linear4both!!!
            if idx_atom in [
                int(keys.split("-")[0]),
                int(keys.split("-")[1]),
            ] and self.is_linear_planar[idx_atom] not in ["planar4both"]:
                org_vec = values

                # Rotate motif into org_vec; then make sure it is perpendicular to bond vector; then rotate by numpy.pi/bond_order degrees around bond -> always rotated wrt to each other
                # Rotate motif into org_vec
                rotmat = self.rotmat_vec1vec2(motif[0], org_vec)
                rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])
                # Rotate perpendicular vector into bond_vec; ONLY IF bond_order > 2
                if lone_no > 2:
                    perp_motif = numpy.cross(
                        rot_pos[0], rot_pos[1]
                    ) / numpy.linalg.norm(numpy.cross(rot_pos[0], rot_pos[1]))
                    # If angle is 180* -> do not do anything -> would flip motif!
                    if (
                        numpy.dot(perp_motif, lone_center)
                        / (
                            numpy.linalg.norm(perp_motif)
                            * numpy.linalg.norm(lone_center)
                        )
                        == -1.0
                    ):
                        rot_pos2 = rot_pos.copy()
                    else:
                        rotmat2 = self.rotmat_vec1vec2(perp_motif, lone_center)
                        rot_pos2 = numpy.array(
                            [numpy.matmul(rotmat2, po) for po in rot_pos]
                        )
                # For double bonds: Just copy original rot_pos
                else:
                    rot_pos2 = rot_pos.copy()

                # Now, rotate around bond_vec to counter-align the motif with the original bond orientation vector
                if lone_no == 4:
                    # 4-bond motif is a trinagle with a point in the middle!
                    linear_rot = self.rotmat_around_axis(
                        axis=lone_center, angle=numpy.pi / 3
                    )
                else:
                    linear_rot = self.rotmat_around_axis(
                        axis=lone_center, angle=numpy.pi / lone_no
                    )
                rot_pos3 = numpy.array(
                    [numpy.matmul(linear_rot, po) for po in rot_pos2]
                )

                if self.is_linear_planar[idx_atom] == "linear4both":
                    new_FOD = [self.atomic_pos[idx_atom] + rot_pos3]
                else:
                    new_FOD = [self.atomic_pos[idx_atom] + rot_pos3 + lone_center]
                return new_FOD

        # ACTUALLY: for linear -> distribute lones around the atom in question -> align with loine_center, and rotate perpendicular motif vector into bond vector!
        # Same for planar and lone == 2
        if self.is_linear_planar[idx_atom] in ["linear4both"] or (
            self.is_linear_planar[idx_atom] in ["planar4both"] and lone_no == 2
        ):
            # HERE -> careful; if there is 4 lone FODs, then we need the square motif, not the one with a triangle and a dot at the middle (because that one would be inside the atom)!
            if lone_no == 4:
                motif = self.ngon_plane(n=lone_no, r=self.r_bond * self.scale_r)

            # Double lenghts of rotated motif, because atom is at the center now!!
            factor = 2.0
            # rotate motif into lone center
            rotmat = self.rotmat_vec1vec2(motif[0], lone_center)
            rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])
            # now perpenduclar direction into lone_center to orient properly; only if lone_up > 2!
            if lone_no == 2:
                new_FOD = [self.atomic_pos[idx_atom] + rot_pos * factor]
            # For more than 2; rotate into bond
            else:
                # need perp vec for motif; properly align with bonds
                perp_vec = numpy.cross(rot_pos[0], rot_pos[1]) / numpy.linalg.norm(
                    numpy.cross(rot_pos[0], rot_pos[1])
                )
                rotmat = self.rotmat_vec1vec2(perp_vec, bonds[0])
                rot_pos2 = numpy.array([numpy.matmul(rotmat, po) for po in rot_pos])
                new_FOD = [self.atomic_pos[idx_atom] + rot_pos2 * factor]

        # planar, with more than 2
        # if lone_up == 2 -> do the same as for linear; otherwise, put lones at lone_center .... see above
        elif self.is_linear_planar[idx_atom] in ["planar4both"]:
            perp_vec = numpy.cross(bonds[0], bonds[1]) / numpy.linalg.norm(
                numpy.cross(bonds[0], bonds[1])
            )

            # rotate motif into this; then rotate into lone_center to orient properly
            rotmat = self.rotmat_vec1vec2(motif[0], perp_vec)
            rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])

            # need perp vec for motif; properly align with bonds
            perp_vec = numpy.cross(rot_pos[0], rot_pos[1]) / numpy.linalg.norm(
                numpy.cross(rot_pos[0], rot_pos[1])
            )
            rotmat = self.rotmat_vec1vec2(perp_vec, lone_center)
            rot_pos2 = numpy.array([numpy.matmul(rotmat, po) for po in rot_pos])
            new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2]

        # ADD planar4bonds!!!!!
        elif self.is_linear_planar[idx_atom] in ["planar4bonds"]:
            # SAME AS FINAL else; just copied for now
            # CAREFUL!! if only one bond -> any rotation
            if len(self.bond_partners[idx_atom]) == 1:
                # take any orientation
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
                rotmat = self.rotmat_vec1vec2(motif[0], outofaxis)
                rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])

                # for more than 2 lones->
                if lone_no != 2:
                    perp_vec = numpy.cross(rot_pos[0], rot_pos[1]) / numpy.linalg.norm(
                        numpy.cross(rot_pos[0], rot_pos[1])
                    )
                    rotmat = self.rotmat_vec1vec2(perp_vec, lone_center)
                    rot_pos2 = numpy.array([numpy.matmul(rotmat, po) for po in rot_pos])
                    new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2]
                else:
                    new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos]
            else:
                # NOTE: bonds[0] should not align with lone_center I think!!! But careful!!!
                perp_vec = numpy.cross(bonds[0], lone_center) / numpy.linalg.norm(
                    numpy.cross(bonds[0], lone_center)
                )

                # rotate motif into this; then rotate into lone_center to orient properly
                rotmat = self.rotmat_vec1vec2(motif[0], perp_vec)
                rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])
                if lone_no == 2:
                    new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos]
                else:
                    # need perp vec for motif; properly align with bonds
                    perp_vec = numpy.cross(rot_pos[0], rot_pos[1]) / numpy.linalg.norm(
                        numpy.cross(rot_pos[0], rot_pos[1])
                    )
                    rotmat = self.rotmat_vec1vec2(perp_vec, lone_center)
                    rot_pos2 = numpy.array([numpy.matmul(rotmat, po) for po in rot_pos])
                    new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2]

        # Do linear4bonds: Dimers! Invert motif in case it is alinged with bond vector!
        elif self.is_linear_planar[idx_atom] in ["linear4bonds"]:
            # Invert motif wrt bonds
            # For bonds, we only consider bond_vec from 0 to 1; so if indices are other way around -> invert here
            factor = 1
            if self.bond_partners[idx_atom][0] < idx_atom:
                factor = -1
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
            rotmat = self.rotmat_vec1vec2(motif[0], outofaxis)
            rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])

            # For two lones -> rotate 90 degrees if linear
            if lone_no == 2:
                linear_rot = self.rotmat_around_axis(
                    axis=bonds[0], angle=numpy.pi / 2.0
                )
                rot_pos2 = numpy.array([numpy.matmul(linear_rot, po) for po in rot_pos])
                new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2]
            # Else
            else:
                # need perp vec for motif; properly align with bonds
                perp_vec = numpy.cross(rot_pos[0], rot_pos[1]) / numpy.linalg.norm(
                    numpy.cross(rot_pos[0], rot_pos[1])
                )

                # Do not flip if angle is 180*
                if (
                    numpy.dot(perp_vec, lone_center)
                    / (numpy.linalg.norm(perp_vec) * numpy.linalg.norm(lone_center))
                    == -1.0
                ):
                    rot_pos2 = rot_pos.copy()
                else:
                    rotmat = self.rotmat_vec1vec2(perp_vec, lone_center)
                    rot_pos2 = numpy.array([numpy.matmul(rotmat, po) for po in rot_pos])
                new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2 * factor]

        # NEED TO CHECK WHETHER BOND PARTNERS ARE LINEAR/PLANAR
        elif numpy.any(
            [
                self.is_linear_planar[s2] in ["planar4bonds", "planar4both"]
                for s2 in self.bond_partners[idx_atom]
            ]
        ):
            # Check which atom is planar -> get in-plane direction
            # QUestion: If there is more than 1 -> does it matter??
            #   we just take the first one for now
            planar = [
                s2
                for s2 in self.bond_partners[idx_atom]
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
            # Go through bond vectors etc etc bla. Invert logic for bonds -> get in-plane direction
            inplane = numpy.cross(outofplane, lone_center) / numpy.linalg.norm(
                numpy.cross(outofplane, lone_center)
            )
            # Rotate first motif into this in-plane vector
            rotmat = self.rotmat_vec1vec2(motif[0], inplane)
            rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])
            # if 2 lones -> just put them there
            if lone_no == 2:
                new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos]
            # otherwise, rotate motif into lone center
            else:
                # need perp vec for motif; properly align with bonds
                perp_vec = numpy.cross(rot_pos[0], rot_pos[1]) / numpy.linalg.norm(
                    numpy.cross(rot_pos[0], rot_pos[1])
                )
                rotmat = self.rotmat_vec1vec2(perp_vec, lone_center)
                rot_pos2 = numpy.array([numpy.matmul(rotmat, po) for po in rot_pos])
                new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2]

        elif numpy.any(
            [
                self.is_linear_planar[s2] in ["linear4bonds", "linear4both"]
                for s2 in self.bond_partners[idx_atom]
            ]
        ):
            # There should be exactly one bond partner here, and this one has exactly 2 bond partners
            linear = [
                s2
                for s2 in self.bond_partners[idx_atom]
                if self.is_linear_planar[s2] in ["linear4bonds", "linear4both"]
            ][0]
            partners_linear = self.bond_partners[linear]
            # figure out the bonding; counter align lones ....
            # I guess first bond partner is rotated for double bond, second one different ... Think about it. If so, we can derive what to do here!
            # first one is rotated 90 degrees, second bond 180; Use same logic to figure out lones (double bonds).
            # otherwise, just use same logic as Bonds, and invert
            # So we can just use bond vectors here to do that!

            # THIS DOES NOT APPLY FOR DIMERS!!!

            rotate_linear = 0
            if self.is_linear_planar[linear] == "linear4both":
                if idx_atom == partners_linear[1] and lone_no == 2:
                    rotate_linear = numpy.pi / 2.0
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
            rotmat = self.rotmat_vec1vec2(motif[0], outofaxis)
            rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])

            # For two lones -> rotate 90 degrees if linear
            if lone_no == 2:
                linear_rot = self.rotmat_around_axis(axis=bonds[0], angle=rotate_linear)
                rot_pos2 = numpy.array([numpy.matmul(linear_rot, po) for po in rot_pos])
                new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2]
            # Else
            else:
                # need perp vec for motif; properly align with bonds
                perp_vec = numpy.cross(rot_pos[0], rot_pos[1]) / numpy.linalg.norm(
                    numpy.cross(rot_pos[0], rot_pos[1])
                )

                # Do not flip if angle is 180*
                if (
                    numpy.dot(perp_vec, lone_center)
                    / (numpy.linalg.norm(perp_vec) * numpy.linalg.norm(lone_center))
                    == -1.0
                ):
                    rot_pos2 = rot_pos.copy()
                else:
                    rotmat = self.rotmat_vec1vec2(perp_vec, lone_center)
                    rot_pos2 = numpy.array([numpy.matmul(rotmat, po) for po in rot_pos])
                new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2]

        # anything else
        else:
            # CAREFUL!! if only one bond -> any rotation
            if len(self.bond_partners[idx_atom]) == 1:
                # TODO: maybe check neighbors and their neighbors -> derive orientation from that?? If neighbore has mutliple bonds!
                # check self.bond_orientation ... of neighbors if bond is in it ...

                # take any orientation
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
                rotmat = self.rotmat_vec1vec2(motif[0], outofaxis)
                rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])

                # for more than 2 lones->
                if lone_no != 2:
                    perp_vec = numpy.cross(rot_pos[0], rot_pos[1]) / numpy.linalg.norm(
                        numpy.cross(rot_pos[0], rot_pos[1])
                    )
                    rotmat = self.rotmat_vec1vec2(perp_vec, lone_center)
                    rot_pos2 = numpy.array([numpy.matmul(rotmat, po) for po in rot_pos])
                    new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2]
                else:
                    new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos]

            else:
                # NOTE: bonds[0] should not align with lone_center I think!!! But careful!!!
                perp_vec = numpy.cross(bonds[0], lone_center) / numpy.linalg.norm(
                    numpy.cross(bonds[0], lone_center)
                )

                # rotate motif into this; then rotate into lone_center to orient properly
                rotmat = self.rotmat_vec1vec2(motif[0], perp_vec)
                rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])
                if lone_no == 2:
                    new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos]
                else:
                    # need perp vec for motif; properly align with bonds
                    perp_vec = numpy.cross(rot_pos[0], rot_pos[1]) / numpy.linalg.norm(
                        numpy.cross(rot_pos[0], rot_pos[1])
                    )
                    rotmat = self.rotmat_vec1vec2(perp_vec, lone_center)
                    rot_pos2 = numpy.array([numpy.matmul(rotmat, po) for po in rot_pos])
                    new_FOD = [self.atomic_pos[idx_atom] + lone_center + rot_pos2]

        return new_FOD

    def create_lone(self):
        """
        Create the actual lone fod positions; careful with planar/linear

         Requires:
            - self.atomic_sym
            - self.atomic_pos
            - self.bond_partners
            - self.lone
            - self.dist_vecs
            - self.is_linear_planar
            - self.make_multiplelones()

        Provides:
            - None

        Returns:
            All lone-FOD positions
        """
        lones = []
        for s, sym in enumerate(self.atomic_sym):
            # If NO bonds -> do atomic guess
            # else:
            # for all lone FODs
            if (
                s in self.lone.keys()
                and self.bond_partners[s] != []
                and self.lone[s] != "0-0"
            ):
                lone_up = int(self.lone[s].split("-")[0])
                lone_dn = int(self.lone[s].split("-")[1])
                no_lone = lone_up + lone_dn

                # Get all bonds to this atom
                bonds = [
                    self.dist_vecs[s][partner] for partner in self.bond_partners[s]
                ]
                # Define lone center
                if self.is_linear_planar[s] in ["planar4both"]:
                    # Get out-of-plane direction via cross product. rotate tmp to align with that
                    lone_center = numpy.cross(bonds[0], bonds[1]) / numpy.linalg.norm(
                        numpy.cross(bonds[0], bonds[1])
                    )
                    lone_center *= self.r_bond
                elif self.is_linear_planar[s] in ["linear4both"]:
                    lone_center = numpy.cross(
                        bonds[0], [0, 0, 1]
                    )  # /numpy.linalg.norm(numpy.cross(vec_bond,[0,0,1]))
                    if lone_center.tolist() == [0, 0, 0]:
                        lone_center = numpy.cross(
                            bonds[0], [1, 0, 0]
                        ) / numpy.linalg.norm(numpy.cross(bonds[0], [1, 0, 0]))
                        lone_center *= self.r_bond
                    else:
                        lone_center /= numpy.linalg.norm(lone_center)
                        lone_center *= self.r_bond
                else:
                    # Get vector formed by all bond vectors to atom s ; opposite direction is direction where we want the lone FODs
                    vecc = -1.0 * numpy.sum(bonds, axis=0)
                    vecc /= numpy.linalg.norm(vecc)
                    # will be added to the atom later on
                    lone_center = 1.0 / (no_lone / 2.0) * vecc * self.r_bond

                new_FOD_up = [[]]
                new_FOD_dn = [[]]
                # UP CHANNEL
                if lone_up == 1:
                    new_FOD_up = [[self.atomic_pos[s] + lone_center.copy()]]
                # for multiple lones -> use similar logic to BOnds; vector of other atoms -> perp vector to that
                # ALSO, check whether any neighbor is planar -> if so, have to rotate FODs accordinly in-plane!
                elif lone_up > 1:
                    new_FOD_up = self.make_multiplelones(
                        lone_no=lone_up, idx_atom=s, lone_center=lone_center
                    )

                # DN CHANNEL
                if lone_dn == lone_up:
                    new_FOD_dn = new_FOD_up.copy()
                else:
                    if lone_dn == 1:
                        new_FOD_dn = [[self.atomic_pos[s] + lone_center.copy()]]
                    # for multiple lones -> use similar logic to BOnds; vector of other atoms -> perp vector to that
                    # ALSO, check whether any neighbor is planar -> if so, have to rotate FODs accordingly in-plane!
                    # HERE
                    # define motif
                    elif lone_dn > 1:
                        new_FOD_dn = self.make_multiplelones(
                            lone_no=lone_dn, idx_atom=s, lone_center=lone_center
                        )
                lones.append([new_FOD_up, new_FOD_dn])

            # If NO bond partner, but lones are explicitely defined --> lone_center is the atom -> do something with that
            elif (
                s in self.lone.keys()
                and self.bond_partners[s] == []
                and self.lone[s] != "0-0" # TO BE REMOVED --> allow lones to be deleted!!
            ):
                # maybe still have an orientation wrt nearest atom -> orient somehow ... TODO
                # Define Motif
                lone_up = int(self.lone[s].split("-")[0])
                lone_dn = int(self.lone[s].split("-")[1])

                # For 0-0 -> could be really bad for transition metal atoms
                # Check whether up and dn have same amount of shellls -> then we can collectively remove them

                # HERE: Remove outpermost shell of the atom in question!!! self.fods
                del self.fods[s][0][-1]
                del self.fods[s][1][-1]
                
                # self.r_bond -> needs to be based on radii in database -> outermost shell!
                conf = self.config[s]
                radius_up = self.atomic_data[sym][conf]["r_up"][-1]
                radius_dn = self.atomic_data[sym][conf]["r_dn"][-1]

                motif_up = self.get_motif(
                    no_points=lone_up, 
                    r=radius_up * self.scale_r, 
                    core_or_bond="core")
                motif_up += self.atomic_pos[s] 
                motif_dn = self.get_motif(
                    no_points=lone_dn, 
                    r=radius_dn * self.scale_r, 
                    core_or_bond="core")
                motif_dn += self.atomic_pos[s] 

                lones.append([[motif_up],[motif_dn]])

        return lones
