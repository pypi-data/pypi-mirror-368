import numpy
from PyfodMC.helperfunctions import HelperFunctions

class Bonds(HelperFunctions):
    def assign_bonds(self):
        """
        Assign bond matrix according to user inputs; also, set all bonds to 1 if unassigned

        Requires:
            - self.bonds (user input)
            - self.atomic_sym
            - self.atomic_pos

        Provides:
            - self.bonds     (modified)
            - self.con_mat   (connectivity matrix)
            - self.dist_vecs (all bond vectors between atoms)
            - self.dist_mat  (distance matrix between all atoms)
            - self.r_bond    (scaling factor based on largest bond distance)
            - self.bond_partners (bond partners for each atom)

        Returns:
            None
        """
        # From HelperFunctions
        covalent_radii, atomic_numbers, chemical_symbols = self.get_atomic_data()

        # First, check self.bonds -> if inputs are in the wrong order (e.g. self.bonds = {"2-1":"2-2"}) -> correct this so that the smaller index always comes first
        # Exclude entries that are atomic types -> see at end of this function
        dummy = dict()
        for key, value in self.bonds.items():
            for val in value:
                # Error check for atomic types; deal with them later
                check1 = val.split("-")[0]
                check2 = val.split("-")[1]
                if (check1 in chemical_symbols and check1 not in self.atomic_sym) or (check2 in chemical_symbols and check2 not in self.atomic_sym):
                    raise ValueError(
                        f"\nBonds for elements {val} specified; Your system only has these elements: {self.atomic_sym}!"
                    )
                # If we have indices
                elif val.split("-")[0] not in self.atomic_sym:
                    val1 = int(val.split("-")[0])
                    val2 = int(val.split("-")[1])
                    # Make sure the indices make sense
                    if (val1 >= len(self.atomic_pos)) or (val2 >= len(self.atomic_pos)):
                        raise ValueError(
                            f"\nBonds for atomic indices {val} specified; however, atomic indices only range from 0 to {len(self.atomic_pos)-1}"
                        )
                    #
                    if val1 > val2:
                        if f"{val2}-{val1}" in dummy:
                            raise ValueError(
                                f"\nBonds between {val2} and {val1} were assigned multiple times; please check your input"
                            )
                        else:
                            dummy[f"{val2}-{val1}"] = key
                    # sanity check: if keys are identical -> not a valid input
                    elif val1 == val2:
                        raise ValueError(
                            f"\nBonds cannot be formed between an atom with itself; check inputs of bonds; entry found: {val,key}"
                        )
                    else:
                        dummy[val] = key
                # Store atomic types, if any
                else:
                    dummy[val] = key
        self.bonds = dummy.copy()

        # Store all paired indices for atomic types that form some bonds; later, only assign the ones that actually form a bond
        additional_indices = {}
        # check self.bonds -> if there are atomic types -> assign all indices accordingly
        # Only allow only atomictypes, or numbers!
        # Check the type of the keys; could be strings in which case they must be atomic types
        tmp = self.bonds.copy()
        for key, value in self.bonds.items():
            if key.split("-")[0] in self.atomic_sym:
                # make sure second entry is also atomic symbol
                if key.split("-")[1] not in self.atomic_sym:
                    raise ValueError(f"Invalid entry for bonds: {key}")
                else:
                    idx1 = numpy.where(
                        numpy.array(self.atomic_sym) == key.split("-")[0]
                    )[0]
                    idx2 = numpy.where(
                        numpy.array(self.atomic_sym) == key.split("-")[1]
                    )[0]
                    for id1 in idx1:
                        for id2 in idx2:
                            if id1 > id2:
                                additional_indices[f"{id2}-{id1}"] = value
                            elif id1 < id2:
                                additional_indices[f"{id1}-{id2}"] = value
                del tmp[key]
        self.bonds = tmp.copy()

        # Check bonds_from_molfile -> add them if we do not have them already -> add it to additonal_indices ..
        if self.bonds_from_molfile != {}:
            for key,value in self.bonds_from_molfile.items():
                for val in value:
                    if val not in additional_indices:
                        additional_indices[val] = key

        ### initialize bonds: All atoms which are close to each other will automatically have a single bond
        # Compute distance matrix
        #   Store this distance matrix -> could be used later on for bond vectors etc!!! get vectors!
        #  get_distances comes from HelperFunctions
        self.dist_vecs, self.dist_mat = self.get_distances(
            self.atomic_pos, cell=self.cell, pbc=self.pbc
        )
        # also need matrix of combined covalent radii
        cov_mat = numpy.zeros((len(self.atomic_sym), len(self.atomic_sym)))
        for s1, sym1 in enumerate(self.atomic_sym):
            for s2, sym2 in enumerate(self.atomic_sym):
                # add value of 0.2, in line with original fodMC
                cov_mat[s1, s2] = (
                    covalent_radii[atomic_numbers[sym1]]
                    + covalent_radii[atomic_numbers[sym2]]
                    + 0.2
                )
        # Whatever is negative -> bond!
        diff = self.dist_mat - cov_mat
        # We only need to worry about the upper triangle
        diff_ut = numpy.triu(diff)
        # See what is negative -> two sets of indices, rows and columns
        mask = numpy.where(diff_ut < 0.0)
        # Exclude main diagonal
        for idx1, idx2 in zip(mask[0], mask[1]):
            if idx1 != idx2:
                # Careful: we also need to assign the bonds that are explicitely specified! -> do not overwrite them!
                if f"{idx1}-{idx2}" not in self.bonds.keys():
                    # Form bonds specified via atomic types or mol file data!
                    if f"{idx1}-{idx2}" in additional_indices:
                        self.bonds[f"{idx1}-{idx2}"] = additional_indices[
                            f"{idx1}-{idx2}"
                        ]
                    else:
                        self.bonds[f"{idx1}-{idx2}"] = "1-1"

        # Remove all entries that are "0-0" (removing bonds)
        tmp = self.bonds.copy()
        for key, value in self.bonds.items():
            if value == "0-0":
                del tmp[key]
        self.bonds = tmp.copy()

        # Create actual bond order matrix!
        self.con_mat = numpy.zeros(
            (2, len(self.atomic_sym), len(self.atomic_sym)), dtype=int
        )
        for key, value in self.bonds.items():
            key1 = int(key.split("-")[0])
            key2 = int(key.split("-")[1])
            val1 = int(value.split("-")[0])
            val2 = int(value.split("-")[1])
            self.con_mat[0, key1, key2] += val1
            self.con_mat[0, key2, key1] += val1
            self.con_mat[1, key1, key2] += val2
            self.con_mat[1, key2, key1] += val2

        #'''
        #   Determine the largest bond distance -> use that as scaling factor for all initialized bonds/lone FODs
        #   Needed for mutliple bonds, and making sure they are all of the same size!!
        #    original fodMC: d_bond
        #'''
        # Check what bonds we have, aND their corresponding distances -> masks ontop of dist_mat
        mask_up = numpy.where(self.con_mat[0] != 0)
        mask_dn = numpy.where(self.con_mat[1] != 0)
        # use maximum of all bonds
        self.r_bond = (
            max([max(self.dist_mat[mask_up]), max(self.dist_mat[mask_dn])]) / 2.0
        )
        # in case we have NO bonds
        if self.r_bond == 0.0:
            self.r_bond = 1.0

        # Define all bond partners per atom -> useful in creating bonds and lones!
        self.bond_partners = []
        for s, sym in enumerate(self.atomic_sym):
            tmp = numpy.where(self.con_mat[0][s] != 0)[0].tolist()
            # Add DN bonds, if not already in up channel
            also = [
                new
                for new in numpy.where(self.con_mat[1][s] != 0)[0].tolist()
                if new not in tmp
            ]
            tmp.extend(also)
            self.bond_partners.append(tmp)

    def make_singlebonds(self, idx_atom1, idx_atom2):
        """
        Create single bonds between two atoms

        Requires:
            - self.dist_vecs 
            - self.atomic_sym
            - self.atomic_pos
            - idx_atom1 which is the index of the first atom
            - idx_atom2 which is the index of the second atom

        Provides:
            None

        Returns:
            Single-bond FOD position
        """
        vec_bond = self.dist_vecs[idx_atom1, idx_atom2]
        # put FOD closer to H if any H involved
        if self.atomic_sym[idx_atom1] == "H" and self.atomic_sym[idx_atom2] != "H":
            new_FOD = [numpy.array([self.atomic_pos[idx_atom1] + 0.15 * vec_bond])]
        elif self.atomic_sym[idx_atom1] != "H" and self.atomic_sym[idx_atom2] == "H":
            new_FOD = [numpy.array([self.atomic_pos[idx_atom1] + 0.85 * vec_bond])]
        # for anything else
        else:
            new_FOD = [numpy.array([self.atomic_pos[idx_atom1] + 0.5 * vec_bond])]
        return new_FOD

    def make_multiplebonds(self, idx_atom1, idx_atom2, bond_order):
        """
        Create multiple bonds bonds, take bond patterns and planarity/linearity into account
          Bond between idx_atom1 and idx_atom2
          bond_order defines which bond to form; bond order

        Requires:
            - self.dist_vecs
            - self.get_motif()
            - self.r_bond
            - self.scale_r
            - self.atomic_sym
            - self.atomic_pos
            - self.bond_orientation
            - self.bond_partners
            - self.is_linear_planar
            - self.rotmat_vec1vec2()
            - idx_atom1 which is the index of the first atom
            - idx_atom2 which is the index of the second atom
            - bond_order which is the bond order between the two atoms

        Provides:
            None

        Returns:
            Multiple-bond FODs positions

        """
        # general: use first position to rotate into per direction; use that positions to the bond center as axis, and cross product of motif to rotate into vec_bond??

        # bond vector
        vec_bond = self.dist_vecs[idx_atom1, idx_atom2]
        #
        motif = self.get_motif(
            no_points=bond_order, r=self.r_bond * self.scale_r, core_or_bond="bond"
        )
        # also, rotate first position of motif into perpendicular vector -> better/easier; works only for double bonds!
        vec2rot = motif[0]

        # if self.bond_orientations contains nearby bonds -> orient wrt that!
        # True for any bond, not just double!
        # ADD EXPLANATION!!!
        for keys, values in self.bond_orientation.items():
            # DO NOT DO THIS IN CASE OF PLANAR
            if (
                idx_atom1 in [int(keys.split("-")[0]), int(keys.split("-")[1])]
                and self.is_linear_planar[idx_atom1]
                not in ["planar4bonds", "planar4both"]
                and self.is_linear_planar[idx_atom2]
                not in ["planar4bonds", "planar4both"]
            ):
                org_vec = values

                # Rotate motif into org_vec; then make sure it is perpendicular to bond vector; then rotate by numpy.pi/bond_order degrees around bond -> always rotated wrt to each other
                # Rotate motif into org_vec
                rotmat = self.rotmat_vec1vec2(vec2rot, org_vec)
                rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])
                # Rotate perpendicular vector into bond_vec; ONLY IF bond_order > 2
                if bond_order > 2:
                    perp_motif = numpy.cross(
                        rot_pos[0], rot_pos[1]
                    ) / numpy.linalg.norm(numpy.cross(rot_pos[0], rot_pos[1]))
                    # If angle is 180* -> do not do anything -> would flip motif!
                    if (
                        numpy.dot(perp_motif, vec_bond)
                        / (numpy.linalg.norm(perp_motif) * numpy.linalg.norm(vec_bond))
                        == -1.0
                    ):
                        rot_pos2 = rot_pos.copy()
                    else:
                        rotmat2 = self.rotmat_vec1vec2(perp_motif, vec_bond)
                        rot_pos2 = numpy.array(
                            [numpy.matmul(rotmat2, po) for po in rot_pos]
                        )
                # For double bonds: Just copy original rot_pos
                else:
                    rot_pos2 = rot_pos.copy()

                # Now, rotate around bond_vec to counter-align the motif with the original bond orientation vector
                if bond_order == 4:
                    # 4-bond motif is a trinagle with a point in the middle!
                    linear_rot = self.rotmat_around_axis(
                        axis=vec_bond, angle=numpy.pi / 3
                    )
                else:
                    linear_rot = self.rotmat_around_axis(
                        axis=vec_bond, angle=numpy.pi / bond_order
                    )
                rot_pos3 = numpy.array(
                    [numpy.matmul(linear_rot, po) for po in rot_pos2]
                )
                # Add this orientation to self.bond_orientations
                self.bond_orientation[f"{idx_atom1}-{idx_atom2}"] = rot_pos3[
                    0
                ] / numpy.linalg.norm(rot_pos3[0])

                new_FOD = [self.atomic_pos[idx_atom1] + rot_pos3 + 0.5 * vec_bond]
                return new_FOD

        # Otherwise: Setup orientation according to bonds and planarity/linearity

        # CLEAN THIS UP!!!

        # If any of the atoms are in a planar environment -> get out-of-plane direction via cross product. Same for linear
        # priority to first atom; if both in palanr environemtn, we pick the first atom;
        # if one is planar, the other lienar -> we pick planar

        # Befine 1st rotation matrix
        if self.is_linear_planar[idx_atom1] in ["planar4bonds", "planar4both"]:
            # Get out-of-plane direction via cross product. rotate tmp to align with that
            bonds = [
                self.dist_vecs[idx_atom1][partner]
                / numpy.linalg.norm(self.dist_vecs[idx_atom1][partner])
                for partner in self.bond_partners[idx_atom1]
            ]
            outofplane = numpy.cross(bonds[0], bonds[1]) / numpy.linalg.norm(
                numpy.cross(bonds[0], bonds[1])
            )
            # Rotate tmp into outofplane
            rotmat = self.rotmat_vec1vec2(vec2rot, outofplane)
        elif self.is_linear_planar[idx_atom2] in ["planar4bonds", "planar4both"]:
            # Get out-of-plane direction via cross product. rotate tmp to align with that
            bonds = [
                self.dist_vecs[idx_atom2][partner]
                / numpy.linalg.norm(self.dist_vecs[idx_atom2][partner])
                for partner in self.bond_partners[idx_atom2]
            ]
            outofplane = numpy.cross(bonds[0], bonds[1]) / numpy.linalg.norm(
                numpy.cross(bonds[0], bonds[1])
            )
            # Rotate tmp into outofplane
            rotmat = self.rotmat_vec1vec2(vec2rot, outofplane)
        # any linear -> check whether this is the first or the second bond -> invert 2nd one!
        elif self.is_linear_planar[idx_atom1] in ["linear4bonds", "linear4both"]:
            # need orientation perpendicular. Try with z and x axis to see which orientations work with cross product
            outofaxis = numpy.cross(
                vec_bond, [0, 0, 1]
            )  # /numpy.linalg.norm(numpy.cross(vec_bond,[0,0,1]))
            if outofaxis.tolist() == [0, 0, 0]:
                outofaxis = numpy.cross(vec_bond, [1, 0, 0]) / numpy.linalg.norm(
                    numpy.cross(vec_bond, [1, 0, 0])
                )
            else:
                outofaxis /= numpy.linalg.norm(outofaxis)
            # Rotate tmp into outofaxis
            rotmat = self.rotmat_vec1vec2(vec2rot, outofaxis)
        elif self.is_linear_planar[idx_atom2] in ["linear4bonds", "linear4both"]:
            # need orientation perpendicular. Try with z and x axis to see which orientations work with cross product
            outofaxis = numpy.cross(
                vec_bond, [0, 0, 1]
            )  # /numpy.linalg.norm(numpy.cross(vec_bond,[0,0,1]))
            if outofaxis.tolist() == [0, 0, 0]:
                outofaxis = numpy.cross(vec_bond, [1, 0, 0]) / numpy.linalg.norm(
                    numpy.cross(vec_bond, [1, 0, 0])
                )
            else:
                outofaxis /= numpy.linalg.norm(outofaxis)
            # Rotate tmp into outofaxis
            rotmat = self.rotmat_vec1vec2(vec2rot, outofaxis)
        else:
            # TRY: use any two atoms that are bonded to the original one: use their bond vectors in corss product with vec_bond -> might work
            if len(self.bond_partners[idx_atom1]) >= len(self.bond_partners[idx_atom2]):
                tpartn = [
                    partner
                    for partner in self.bond_partners[idx_atom1]
                    if partner != idx_atom2
                ]
            else:
                tpartn = [
                    partner
                    for partner in self.bond_partners[idx_atom2]
                    if partner != idx_atom1
                ]
            bond = self.atomic_pos[tpartn[0]] - self.atomic_pos[tpartn[1]]
            orientation = numpy.cross(vec_bond, bond) / numpy.linalg.norm(
                numpy.cross(vec_bond, bond)
            )
            # Rotate tmp into orientation
            rotmat = self.rotmat_vec1vec2(vec2rot, orientation)

        # Rotate positions according to first rotation matrix
        rot_pos = numpy.array([numpy.matmul(rotmat, po) for po in motif])
        # Now: rotate the motif so that its perpendicular vector aligns with the bond vector
        # this works because we are at the origin; otherwise we would need to take the differences between the positions -> motif vectors
        perp_motif = numpy.cross(
            rot_pos[0], rot_pos[1]
        )  # /numpy.linalg.norm(numpy.cross(rot_pos[0],rot_pos[1]))
        # for bond_order = 2
        if perp_motif.tolist() == [0, 0, 0]:
            self.bond_orientation[f"{idx_atom1}-{idx_atom2}"] = rot_pos[
                0
            ] / numpy.linalg.norm(rot_pos[0])
            new_FOD = [self.atomic_pos[idx_atom1] + rot_pos + 0.5 * vec_bond]
            return new_FOD

        perp_motif /= numpy.linalg.norm(numpy.cross(rot_pos[0], rot_pos[1]))
        # not double bond!
        # If angle is 180* -> do not do anything -> would flip motif!
        if (
            numpy.dot(perp_motif, vec_bond)
            / (numpy.linalg.norm(perp_motif) * numpy.linalg.norm(vec_bond))
            == -1.0
        ):
            rot_pos2 = rot_pos.copy()
        else:
            rotmat2 = self.rotmat_vec1vec2(perp_motif, vec_bond)
            rot_pos2 = numpy.array([numpy.matmul(rotmat2, po) for po in rot_pos])

        # use for other bonds/lones
        self.bond_orientation[f"{idx_atom1}-{idx_atom2}"] = rot_pos2[
            0
        ] / numpy.linalg.norm(rot_pos2[0])

        new_FOD = [self.atomic_pos[idx_atom1] + rot_pos2 + 0.5 * vec_bond]
        return new_FOD

    def create_bonds(self):
        """
        Create bond FOD positions.

        Remove outermost shells of atoms that form bond; then form bonds and add to self.fods


        Requires:
            - self.bond_partners
            - self.fods
            - self.con_mat
            - self.make_singlebonds()
            - self.make_multiplebonds()

        Provides:
            - self.bond_orientation

        Returns:
            All bond FODs positions
        """
        # Store orientation of bond motifs, for usage for orientations of other bonds and lone FODs
        self.bond_orientation = dict()

        #
        bonds = []
        # Take ALL bond partners into account -> or make sure that all bonds of the bond partners are taken into account;
        # Take atoms with most bonds first, create bonds; then exclude that we form the same bond twice!
        no_bonds_sort = numpy.argsort(
            [len(partners) for partners in self.bond_partners]
        )
        bonds_sort = numpy.flip(no_bonds_sort)
        # do bonds for one atoms with most bonds -> then exclude atoms that have already been dealt with
        # we essentially have to monitor the bonds we formed
        # Store all bond FODs in bonds list. Then we can use the positions to adjust lone, core ...
        for idx_sort, s in enumerate(bonds_sort):
            # Remove outermost shell of atoms that form any bond; careful, cause we transfer this info to lone FODs as well..
            #   re-use bond_partners from is_linear_planar
            if len(self.bond_partners[s]) != 0:
                # remove outermost UP and DN shell of this atom
                self.fods[s][0] = self.fods[s][0][:-1]
                self.fods[s][1] = self.fods[s][1][:-1]

            # Create up/dn bonds in between the atoms; use bond vectors and stuff
            # treat single, double, triple, quadruple independently ?
            # add bonds as entries to self.fods -> then we can rotate them wrt each other -> all entries with index > N_atoms are bonds (same for lone later on?)
            # HERE: careful with logix!!!!!!!!
            # combine spin up and dn ...

            # Exclude all bonds that have already been dealt with
            bonds_to_consider = [
                partner
                for partner in self.bond_partners[s]
                if partner not in bonds_sort[: idx_sort + 1]
            ]

            for s2, (con_up, con_dn) in enumerate(
                zip(self.con_mat[0][s], self.con_mat[1][s])
            ):
                if s2 in bonds_to_consider:
                    # only check upper triangle matrix
                    if con_up != 0 or con_dn != 0:
                        new_FOD_up = [[]]
                        new_FOD_dn = [[]]

                        if con_up == 1:
                            new_FOD_up = self.make_singlebonds(s, s2)
                        # any other bonds: Check if atoms are in planar/linear environment -> set bonds accordingly. Carefully! (SO2)
                        elif con_up >= 2:
                            # logic; planar > linear > neither
                            new_FOD_up = self.make_multiplebonds(s, s2, con_up)

                        # DN channel
                        if con_dn == con_up:
                            new_FOD_dn = new_FOD_up.copy()
                        else:
                            if con_dn == 1:
                                new_FOD_dn = self.make_singlebonds(s, s2)
                            elif con_dn >= 2:
                                new_FOD_dn = self.make_multiplebonds(s, s2, con_dn)

                        bonds.append([new_FOD_up, new_FOD_dn])

        return bonds
