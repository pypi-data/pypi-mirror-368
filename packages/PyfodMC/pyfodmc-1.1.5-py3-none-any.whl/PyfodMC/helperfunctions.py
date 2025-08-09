import numpy
from time import time
import itertools

def timeit(f):
    """
    timeit
    Decorator write to stdout

    Input
        - f : function
    """
    def f0(*args, **kwargs):
        before = time()
        res = f(*args, **kwargs)
        after = time()
        print("elapsed time ({}) = {:12.4f} [s]".format(f.__qualname__, after - before))
        return res

    return f0


class HelperFunctions:
    def read(self):
        """
        Read the nuclear geometry, and maybe the cell information.
        Supported file formats are .xyz and .mol (for molecules) and .cif and POSCAR (for extended systems)

        Requires:
            - self.geometry

        Provides:
            - self.atomic_pos
            - self.atomic_sym
            - self.atomic_num
            - self.cell

        Returns:
            None
        """
        # Get atomic information
        _, atomic_numbers, chemical_symbols = self.get_atomic_data()

        def read_xyz(name):
            """
            Read info from .xyz file
            """
            ffile = open(name,"r")
            lines = ffile.readlines()
            ffile.close()
            no_atoms = int(lines[0].split()[0])
            self.atomic_pos = numpy.zeros((no_atoms,3))
            self.atomic_sym = [] #numpy.zeros(natoms,dtype=str) -> this seems to allow only strings of size 1
            self.atomic_num = numpy.zeros(no_atoms,dtype=numpy.int8)
            for l in range(no_atoms):
                sym, pos_x, pos_y, pos_z = lines[l+2].split()
                self.atomic_pos[l] = numpy.array([float(pos_x), float(pos_y), float(pos_z)])
                self.atomic_sym.append(sym)
                self.atomic_num[l] = atomic_numbers[sym]
            self.atomic_sym = numpy.array(self.atomic_sym)
            self.cell = None
            self.pbc  = False

        def read_mol(name):
            """
            Read info from .mol file
            This includes reading the bonding information
            Adopted from ase
            """
            ffile = open(name, 'r')
            lines = ffile.readlines()
            ffile.close()
            # Description line to tells us how many atoms, and how many bonds
            L1 = lines[3]
            # The V2000 dialect uses a fixed field length of 3, which means there
            # won't be space between the numbers if there are 100+ atoms, and
            # the format doesn't support 1000+ atoms at all.
            if L1.rstrip().endswith('V2000'):
                natoms = int(L1[:3].strip())
                nbonds = int(L1[3:6].strip())
            else:
                natoms = int(L1.split()[0])
                nbonds = int(L1.split()[1])
            self.atomic_pos = numpy.zeros((natoms,3))
            self.atomic_sym = [] #numpy.zeros(natoms,dtype=str)
            self.atomic_num = numpy.zeros(natoms,dtype=numpy.int8)
            for l,line in enumerate(lines[4:4+natoms]):
                x, y, z, symbol = line.split()[:4]
                self.atomic_pos[l] = numpy.array([float(x), float(y), float(z)])
                self.atomic_sym.append(symbol)
                self.atomic_num[l] = atomic_numbers[symbol]
            self.atomic_sym = numpy.array(self.atomic_sym)

            # self.bonds_from_molfile. Will be used in conjunction with user inputs
            self.bonds_from_molfile = dict()
            for l in range(4 + natoms, 4 + natoms + nbonds):
                line = lines[l]
                A, B, BO = line.split()[:3]
                # subtract 1 from the indices, cause we start counting from 0
                if f"{BO}-{BO}" in self.bonds_from_molfile.keys():
                    self.bonds_from_molfile[f"{BO}-{BO}"].append(f"{int(A)-1}-{int(B)-1}")
                else:
                    self.bonds_from_molfile[f"{BO}-{BO}"] = [f"{int(A)-1}-{int(B)-1}"]
            #print("We extract bonding information from .mol file.")
            #print(f"self.bonds = {self.bonds}")
            self.cell = None
            self.pbc  = False

        def read_cif(name):
            """
            Read info from .cif file
            """
            ffile = open(name, 'r')
            lines = ffile.readlines()
            ffile.close()
            # get lengths and angles of cell vector
            a,b,c = 0,0,0
            alpha,beta,gamma = 0,0,0
            for line in lines:
                if line.find("_cell_length_a") != -1:
                    a = float(line.split()[1])
                if line.find("_cell_length_b") != -1:
                    b = float(line.split()[1])
                if line.find("_cell_length_c") != -1:
                    c = float(line.split()[1])
                if line.find("_cell_angle_alpha") != -1:
                    alpha = float(line.split()[1])
                if line.find("_cell_angle_beta") != -1:
                    beta = float(line.split()[1])
                if line.find("_cell_angle_gamma") != -1:
                    gamma = float(line.split()[1])
            # taken from ase
            # rounding check; if angles exactly 90 degrees -> set cos/sin to their exact values
            eps = 1e-10
            if abs(abs(alpha) - 90) < eps:
                cos_alpha = 0.0
            else:
                cos_alpha = numpy.cos(alpha * numpy.pi / 180.0)
            # beta
            if abs(abs(beta) - 90) < eps:
                cos_beta = 0.0
            else:
                cos_beta = numpy.cos(beta * numpy.pi / 180.0)
            # gamma
            if abs(gamma - 90) < eps:
                cos_gamma = 0.0
                sin_gamma = 1.0
            elif abs(gamma + 90) < eps:
                cos_gamma = 0.0
                sin_gamma = -1.0
            else:
                cos_gamma = numpy.cos(gamma * numpy.pi / 180.0)
                sin_gamma = numpy.sin(gamma * numpy.pi / 180.0)
            # Build the cell vectors
            cell = numpy.zeros((3,3))
            cell[0] = a * numpy.array([1, 0, 0])
            cell[1] = b * numpy.array([cos_gamma, sin_gamma, 0])
            cx = cos_beta
            cy = (cos_alpha - cos_beta * cos_gamma) / sin_gamma
            cz_sqr = 1. - cx * cx - cy * cy
            assert cz_sqr >= 0
            cz = numpy.sqrt(cz_sqr)
            cell[2] = c * numpy.array([cx, cy, cz])

            ## Now check the block which looks like
            #loop_
            #_atom_site_label         <--- could be used for symbols
            #_atom_site_occupancy
            #_atom_site_fract_x       <--- coordinates
            #_atom_site_fract_y
            #_atom_site_fract_z
            #_atom_site_adp_type
            #_atom_site_B_iso_or_equiv
            #_atom_site_type_symbol   <--- is the symbol (if it exists!)
            #   From there, check how many entries we have, and which ones are the symbols, which ones are the fractional coordinates
            atoms_identifiers = []
            for l,line in enumerate(lines):
                if line.find("loop_") != -1:
                    i = 1
                    while lines[l+i].find("_atom") != -1:
                        atoms_identifiers.append(lines[l+i].split()[0])
                        i += 1
                    start_read = l+i
                if "_atom_site_fract_x" in atoms_identifiers:
                    # we are in the right spot. Anything below this block should be the atoms and their position
                    if "_atom_site_type_symbol" in atoms_identifiers:
                        symbol_idx = atoms_identifiers.index("_atom_site_type_symbol")
                    elif "_atom_site_label" in atoms_identifiers:
                        symbol_idx = atoms_identifiers.index("_atom_site_label")
                    else:
                        raise ValueError("Cannot find any element symbol identifiers in the provided .cif file. Cannot find _atom_site_type_symbol or _atom_site_label")

            # starting point for reading is l+i ; stop either if we run out of lines, or there are no more entries
            #self.atomic_pos = numpy.zeros((natoms,3))
            #self.atomic_sym = [] #numpy.zeros(natoms,dtype=str)
            #self.atomic_num = numpy.zeros(natoms,dtype=numpy.int8)
            x_idx = atoms_identifiers.index("_atom_site_fract_x")
            y_idx = atoms_identifiers.index("_atom_site_fract_y")
            z_idx = atoms_identifiers.index("_atom_site_fract_z")
            pos_tmp = []
            sym_tmp = []
            for l,line in enumerate(lines):
                if l >= start_read:
                    if len(line.split()) != len(atoms_identifiers):
                        break
                    else:
                        splitt = line.split()
                        pos_tmp.append(float(splitt[x_idx])*cell[0] + float(splitt[y_idx])*cell[1] + float(splitt[z_idx])*cell[2]) # cartesian!
                        sym_tmp.append(splitt[symbol_idx].replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9",""))
            # Define the stuff for PyfodMC
            self.atomic_pos = numpy.zeros((len(pos_tmp),3))
            self.atomic_sym = [] #numpy.zeros(natoms,dtype=str)
            self.atomic_num = numpy.zeros(len(pos_tmp),dtype=numpy.int8)
            for i,(p,s) in enumerate(zip(pos_tmp,sym_tmp)):
                self.atomic_pos[i] = p
                self.atomic_sym.append(s)
                self.atomic_num[i] = atomic_numbers[s]
            self.atomic_sym = numpy.array(self.atomic_sym)
            self.cell = cell
            self.pbc = True

        def read_POSCAR(name):
            """
            Read info from POSCAR file
            """
            ffile = open(name, 'r')
            lines = ffile.readlines()
            ffile.close()
            self.cell = numpy.zeros((3,3))
            self.pbc = True
            scaling_factor = float(lines[1].split()[0])
            self.cell[0] = numpy.array([float(lines[2].split()[0]),float(lines[2].split()[1]),float(lines[2].split()[2])])*scaling_factor
            self.cell[1] = numpy.array([float(lines[3].split()[0]),float(lines[3].split()[1]),float(lines[3].split()[2])])*scaling_factor
            self.cell[2] = numpy.array([float(lines[4].split()[0]),float(lines[4].split()[1]),float(lines[4].split()[2])])*scaling_factor

            tmp_syms = lines[5].split()
            cnt_syms = lines[6].split()
            self.atomic_sym = []
            self.atomic_num = []
            for s,c in zip(tmp_syms,cnt_syms):
                for i in range(int(c)):
                    self.atomic_sym.append(s)
                    self.atomic_num.append(atomic_numbers[s])
            self.atomic_sym = numpy.array(self.atomic_sym)
            self.atomic_num = numpy.array(self.atomic_num)
            self.atomic_pos = numpy.zeros((len(self.atomic_sym),3))

            if lines[7].find("Selective dynamics") != -1:
                skip = 1
            else:
                skip = 0
            for l,line in enumerate(lines):
                if l+skip == 7:
                    if lines[l+skip].find("Cartesian") != -1 or lines[l+skip].find("cartesian") != -1:
                        # Cartesian coordinates: just read them out
                        for i in range(len(self.atomic_sym)):
                            splitt = lines[l+skip+i+1].split()
                            self.atomic_pos[i] = numpy.array([float(splitt[0]),float(splitt[1]),float(splitt[2])])
                    if lines[l+skip].find("Direct") != -1 or lines[l+skip].find("direct") != -1:
                        # Direct coordinates: transform them here
                        for i in range(len(self.atomic_sym)):
                            splitt = lines[l+skip+i+1].split()
                            self.atomic_pos[i] = float(splitt[0])*self.cell[0] + float(splitt[1])*self.cell[1] + float(splitt[2])*self.cell[2]


        ######################
        # Check what we have #
        ######################
        if self.geometry.find(".xyz") != -1:
            read_xyz(self.geometry)
        elif self.geometry.find(".mol") != -1:
            read_mol(self.geometry)
        elif self.geometry.find(".cif") != -1:
            read_cif(self.geometry)
        elif self.geometry.find("POSCAR") != -1:
            read_POSCAR(self.geometry)
        else:
            # For single atoms
            _, _, symbols = self.get_atomic_data()
            if self.geometry in symbols:
                no_atoms = 1
                self.atomic_pos = numpy.zeros((no_atoms,3))
                self.atomic_pos[0] = numpy.array([0.,0.,0.])
                self.atomic_sym = [] #numpy.zeros(natoms,dtype=str) -> this seems to allow only strings of size 1
                self.atomic_sym.append(self.geometry)
                self.atomic_sym = numpy.array(self.atomic_sym)
                self.atomic_num = numpy.zeros(no_atoms,dtype=numpy.int8)
                self.atomic_num[0] = atomic_numbers[self.geometry] 
                self.cell = None
                self.pbc  = False
            else:
                raise ValueError(f"Unknown file format; {self.geometry}. Only .xyz, .mol, .cif, and POSCAR are currently supported.")


    def write(self):
        """
        Write the final xyz/cif/POSCAR file, including the FODs

        Requires:
            - self.atomic_sym
            - self.atomic_pos
            - self.fods

        Provides:
            - None

        Returns:
            - None
        """
        # Get atomic information
        _, _, chemical_symbols = self.get_atomic_data()

        def write_xyz(name,
                      tmp_pos,
                      tmp_sym):
            """
            Write .xyz file, including FODs
            """
            ffile = open(name,"w")
            if self.guess_type == "restricted":
                ffile.write(f"{len(tmp_pos)}\nsym_fod1='X'\n")
            else:
                ffile.write(f"{len(tmp_pos)}\nsym_fod1='X' sym_fod2='{tmp_sym[-1]}'\n")
            for pos,sym in zip(tmp_pos,tmp_sym):
                ffile.write(f"{sym:<5s} {pos[0]:15.8f} {pos[1]:15.8f} {pos[2]:15.8f}\n")
            ffile.close()

        def write_cif(name,
                      tmp_pos,
                      tmp_sym):
            """
            Write .cif file, including FODs
            """
            def cart2frac(pos,lengths,angles):
                """
                Transform cartesian coordinates into fractional ones.
                """
                #! transformation matrix to get fractional coordinates. It is the inverse of the matrix containing the cell vectors
                #https://gist.github.com/Bismarrck/a68da01f19b39320f78a
                alpha = numpy.deg2rad(angles[0])
                beta  = numpy.deg2rad(angles[1])
                gamma = numpy.deg2rad(angles[2])
                cosa = numpy.cos(alpha)
                sina = numpy.sin(alpha)
                cosb = numpy.cos(beta)
                sinb = numpy.sin(beta)
                cosg = numpy.cos(gamma)
                sing = numpy.sin(gamma)
                volume = 1.0 - cosa**2.0 - cosb**2.0 - cosg**2.0 + 2.0 * cosa * cosb * cosg
                volume = numpy.sqrt(volume)
                r = numpy.zeros((3, 3))
                
                r[0, 0] = 1.0 / lengths[0]
                r[0, 1] = -cosg / (lengths[0] * sing)
                r[0, 2] = (cosa * cosg - cosb) / (lengths[0] * volume * sing)
                r[1, 1] = 1.0 / (lengths[1] * sing)
                r[1, 2] = (cosb * cosg - cosa) / (lengths[1] * volume * sing)
                r[2, 2] = sing / (lengths[2] * volume)

                pos_frac = numpy.zeros_like(pos) 
                for i,p in enumerate(pos):
                    pos_frac[i] = numpy.dot(r, p)
                    # MAKE SURE THAN ALL ENTRIES ARE WITHIN 0 and 1 !!
                    for xyz in range(3):
                        while pos_frac[i][xyz] < 0: 
                            pos_frac[i][xyz] += 1
                        while pos_frac[i][xyz] > 1: 
                            pos_frac[i][xyz] -= 1
                return pos_frac

            # For molecular systems: define cell so that there is at least 10 A of vaccum!
            if self.cell is None:
                # get largest distances within the molecule; add 10 angstrom to that
                max_dist = max([max(dists) for dists in self.dist_mat])
                max_dist += 10
                self.cell = numpy.zeros((3,3))
                for i in range(3):
                    self.cell[i][i] = max_dist
                # Shift all positions to the center of the cell
                tmp_pos += numpy.array([0.5,0.5,0.5])*max_dist

            # Transform cell into lengths, angles
            # Taken from ase
            lengths = [numpy.linalg.norm(v) for v in self.cell]
            angles = []
            for i in range(3):
                j = i - 1
                k = i - 2
                ll = lengths[j] * lengths[k]
                if ll > 1e-16:
                    x = numpy.dot(self.cell[j], self.cell[k]) / ll
                    angle = 180.0 / numpy.pi * numpy.arccos(x)
                else:
                    angle = 90.0
                angles.append(angle)

            # get fractional positions; make sure they are inside the unit cell!
            pos_frac = cart2frac(tmp_pos,lengths,angles) 
            
            # Write stuff
            ffile = open(name,"w")
            ffile.write(f"data_PyfodMC_guess_for_{self.geometry}\n")
            ffile.write(f"_cell_length_a       {lengths[0]:10.4f}\n")
            ffile.write(f"_cell_length_b       {lengths[1]:10.4f}\n")
            ffile.write(f"_cell_length_c       {lengths[2]:10.4f}\n")
            ffile.write(f"_cell_angle_alpha    {angles[0]:10.4f}\n")
            ffile.write(f"_cell_angle_beta     {angles[1]:10.4f}\n")
            ffile.write(f"_cell_angle_gamma    {angles[2]:10.4f}\n")
            ffile.write('_space_group_name_H-M_alt    "P 1"\n')
            ffile.write("_space_group_IT_number       1\n")
            ffile.write("\n")
            ffile.write("loop_\n")
            ffile.write("  _space_group_symop_operation_xyz\n")
            ffile.write("  'x, y, z'\n")
            ffile.write("\n")
            ffile.write("loop_\n")
            ffile.write("  _atom_site_type_symbol\n")
            ffile.write("  _atom_site_label\n")
            ffile.write("  _atom_site_fract_x\n")
            ffile.write("  _atom_site_fract_y\n")
            ffile.write("  _atom_site_fract_z\n")
            ffile.write("  _atom_site_occupancy\n")
            # Add a counter for all atomic types -> increase for 'label'
            counter = dict()
            unique_syms = numpy.unique(tmp_sym)
            for uni in unique_syms:
                counter[uni] = 0
            for p,s in zip(pos_frac,tmp_sym):
                counter[s] += 1
                tmp = f"{s}{counter[s]}"
                ffile.write(f"{s:5s} {tmp:10s} {p[0]:15.8f} {p[1]:15.8f} {p[2]:15.8f} {1.0:10.4f}\n")
            ffile.close()

        def write_POSCAR(name,
                         tmp_pos,
                         tmp_sym):
            """
            Write POSCAR file, including FODs
            """
            # For molecular systems: define cell so that there is at least 10 A of vaccum!
            if self.cell is None:
                # get largest distances within the molecule; add 10 angstrom to that
                max_dist = max([max(dists) for dists in self.dist_mat])
                max_dist += 10
                self.cell = numpy.zeros((3,3))
                for i in range(3):
                    self.cell[i][i] = max_dist
                # Shift all positions to the center of this cell
                tmp_pos += numpy.array([0.5,0.5,0.5])*max_dist

            ffile = open(name,"w")
            ffile.write(f"PyfodMC_guess_for_{self.geometry}\n")
            ffile.write("1.0000000\n") # scaling factor
            for i in range(3):
                ffile.write(f"{self.cell[i][0]:20.15f} {self.cell[i][1]:20.15f} {self.cell[i][2]:20.15f}\n")
            tmp_syms = []
            tmp_cnts = []
            counter = 0
            current = tmp_sym[0]
            for s,sym in enumerate(tmp_sym):
                if sym == current:
                    counter += 1
                else:
                    tmp_syms.append(current)
                    tmp_cnts.append(counter)
                    counter = 1 # reset to one so it takes the current position into account!
                    current = tmp_sym[s+1]
            # Add any leftover from the previous loop
            if counter != 0:
                tmp_syms.append(sym)
                tmp_cnts.append(counter)
            sym_str = ""
            cnt_str = ""
            for s,c in zip(tmp_syms,tmp_cnts):
                sym_str += f"{s:5s}"
                cnt_str += f"{c:<5d}"
            ffile.write(f"{sym_str}\n")
            ffile.write(f"{cnt_str}\n")
            ffile.write("Cartesian\n")
            for pos in tmp_pos:
                ffile.write(f"{pos[0]:15.8f} {pos[1]:15.8f} {pos[2]:15.8f}\n")
            ffile.close()



        ######################
        # Check what we have #
        ######################
        tmp_pos = self.atomic_pos.tolist()
        tmp_sym = self.atomic_sym.tolist()
        # Note: make sure that our system does not contain any He
        # If it does -> do not use "He" for the DN channel, but another species
        if "He" in tmp_sym:
            # Go through all chemical symbols: Whichever one is not used -> take it
            for s in chemical_symbols:
                if s not in tmp_sym:
                    dn_fod_sym = s
                    break
        else:
            dn_fod_sym = "He"
        up_fod_sym = "X"

        # Add fod positions
        fods_up = []
        fods_dn = []
        for a, atm in enumerate(self.fods):
            for f, shell in enumerate(atm[0]):
                for fodpos in shell:
                    fods_up.append(fodpos)
        for a, atm in enumerate(self.fods):
            for f, shell in enumerate(atm[1]):
                for fodpos in shell:
                    fods_dn.append(fodpos)

        # Erro checks for restricted
        if self.guess_type == "restricted":
            if len(fods_up) != len(fods_dn):
                raise ValueError("Cannot create restricted guess for N_up != N_dn")
            else:
                if numpy.allclose(fods_up,fods_dn):
                    for fods in fods_up:
                        tmp_pos.append(fods)
                        tmp_sym.append(up_fod_sym)
                else:
                    raise ValueError("Cannot construct a restricted guess, because the UP and DN positions differ too much. Please try guess_type='unrestricted'")
        else:
            for fods in fods_up:
                tmp_pos.append(fods)
                tmp_sym.append(up_fod_sym)
            for fods in fods_dn:
                tmp_pos.append(fods)
                tmp_sym.append(dn_fod_sym)


        if self.output.find(".xyz") != -1:
            write_xyz(self.output,
                      tmp_pos,
                      tmp_sym)
        if self.output.find(".cif") != -1:
            write_cif(self.output,
                      tmp_pos,
                      tmp_sym)
        if self.output.find("POSCAR") != -1:
            write_POSCAR(self.output,
                         tmp_pos,
                         tmp_sym)


    def check(self):
        """
        Check dicts charge, switch_updn, ecp, and config
         - if atomic type is given -> use inddices instead
         - populate with default values

        Requires:
            - self.atomic_sym
            - self.charge
            - self.switch_updn
            - self.invert_updn
            - self.ecp
            - self.config

        Provides:
            - self.charge      (modified)
            - self.switch_updn (modified)
            - self.invert_updn (modified)
            - self.ecp         (modified)
            - self.config      (modified)

        Returns:
            None
        """
        dummy = [dict(), dict(), dict(), dict(), dict()]
        for s, sym in enumerate(self.atomic_sym):
            dummy[0][s] = 0
            dummy[1][s] = False
            dummy[2][s] = False
            dummy[3][s] = None
            dummy[4][s] = "default"

        for t, to_check in enumerate(
            [self.charge, self.switch_updn, self.invert_updn, self.ecp, self.config]
        ):
            for key, value in to_check.items():
                for val in value:
                    if isinstance(val, str):
                        # must be atomic type -> set all indices of all atoms of this type to the value
                        for s, sym in enumerate(self.atomic_sym):
                            if sym == val:
                                dummy[t][s] = key
                    # Indices are provided explicitely -> just overwrite
                    elif isinstance(val, int):
                        dummy[t][val] = key

        # Overwrite all dicts()
        self.charge      = dummy[0].copy()
        self.switch_updn = dummy[1].copy()
        self.invert_updn = dummy[2].copy()
        self.ecp         = dummy[3].copy()
        self.config      = dummy[4].copy()

    def linear_planar(self):
        """
        Check which atoms are in a planar or linear environment

          - differentiate bonds and lone linearity/planarity
            - e/g/ SO2: for bonds, need planarity on S; for lone, we do not

         for lone it really only matters if it is planar (CH3)
         for bonds, it matters whether we are in a linear or planar environment
         (CO2,SO2,..)

        Requires:
            - self.atomic_sym
            - self.atomic_pos
            - sef.bond_partners

        Provides:
            - self.is_linear_planar

        Returns:
            None
        """
        self.is_linear_planar = {}

        for s, sym in enumerate(self.atomic_sym):
            self.is_linear_planar[s] = "neither"
            if len(self.bond_partners[s]) == 0:
                self.is_linear_planar[s] = "neither"

            elif len(self.bond_partners[s]) == 1:
                if len(self.atomic_pos) == 2:
                    # Do this only for diatomics?
                    self.is_linear_planar[s] = (
                        "linear4bonds"  # only linear for bonds; lones should be outside, not out of axis
                    )
            else:
                # take cross products of the vectors; check whether they align
                # self.is_linear_planar[s] = "TODO"
                bonds = []
                for partner in self.bond_partners[s]:
                    # use distance matrix from assign_bonds(): no need to recompute distances here!
                    # normalize it here -> no need to do it later
                    bonds.append(
                        self.dist_vecs[s][partner]
                        / numpy.linalg.norm(self.dist_vecs[s][partner])
                    )
                ## For 2 partners: could be linear -> check whether bonds are aligned
                # could also be planar; SO2 -> check this!!!
                if len(self.bond_partners[s]) == 2:
                    # check angle of bonds; if 0 or 180 -> linear
                    cos_alpha = numpy.dot(bonds[0], bonds[1])  # already normalized
                    if abs(cos_alpha) > 0.98:
                        self.is_linear_planar[s] = "linear4both"
                    # for two bonds, and not linear -> always planar
                    else:
                        self.is_linear_planar[s] = "planar4bonds"
                # For any more bonds: Check planarity
                else:
                    # use itertools to get all cross products between all bonds
                    tmp_cross_prods = [
                        numpy.cross(combo[0], combo[1])
                        #/ numpy.linalg.norm(numpy.cross(combo[0], combo[1]))
                        for combo in list(itertools.combinations(bonds, 2))
                    ]
                    # Here: cross_prods can be zero vector -> lengths of zero --> do not normalize!
                    cross_prods = []
                    for cross_prod in tmp_cross_prods:
                        if numpy.linalg.norm(cross_prod) == 0:
                            cross_prods.append(cross_prod)
                        else:
                            cross_prods.append(cross_prod/numpy.linalg.norm(cross_prod))

                    # Now check all angles of all cross products
                    cos_angles = [
                        numpy.dot(combo[0], combo[1])
                        for combo in list(itertools.combinations(cross_prods, 2))
                    ]
                    # if all cosines of all angles are 1 or -1 (or close to it -> planar
                    check = [abs(cos) > 0.98 for cos in cos_angles]
                    if numpy.all(check):
                        self.is_linear_planar[s] = "planar4both"
                    else:
                        self.is_linear_planar[s] = "neither"

    def get_charge_spin_dip(self):
        """
        Compute charge, spin and point charge dipole based on FODs and atoms

        Requires:
            - self.atomic_num
            - self.atomic_pos
            - self.fods

        Provides:
            - None

        Returns:
            charge, spin, dipole
        """
        charge = sum(self.atomic_num)
        spin = 0
        for a, atm in enumerate(self.fods):
            for f, fod in enumerate(atm):
                for shell in fod:
                    charge -= len(shell)
                    if f == 0:
                        spin += len(shell)
                    else:
                        spin -= len(shell)
        # Take ECP charge into account: Electrons that were removed by removing inner shells of atoms
        charge -= self.ecp_charge
        # point charge dipole
        center_atoms = numpy.sum(self.atomic_pos, axis=0) / len(self.atomic_pos)
        dip = numpy.zeros(3)
        for a, atm in enumerate(self.fods):
            for f, fod in enumerate(atm):
                for shell in fod:
                    for fodpos in shell:
                        dip -= fodpos - center_atoms
        return charge, spin, dip

    def rotmat(self, axis=[1, 1, 1], angle=0.0):
        """
        Define rotation matrix based on angle and axis,
          can be used by rotmat_around_axis and rotmat_vec1vec2

          axis needs to be normalized, angle in radians

        Requires:
            - axis
            - angle

        Provides:
            - None

        Returns:
            Rotation matrix
        """
        cos_a = numpy.cos(angle)
        sin_a = numpy.sin(angle)

        rotmat = numpy.zeros((3, 3))
        rotmat[0, 0] = cos_a + axis[0] ** 2 * (1.0 - cos_a)
        rotmat[0, 1] = axis[0] * axis[1] * (1.0 - cos_a) - axis[2] * sin_a
        rotmat[0, 2] = axis[0] * axis[2] * (1.0 - cos_a) + axis[1] * sin_a
        rotmat[1, 0] = axis[1] * axis[0] * (1.0 - cos_a) + axis[2] * sin_a
        rotmat[1, 1] = cos_a + axis[1] ** 2 * (1.0 - cos_a)
        rotmat[1, 2] = axis[1] * axis[2] * (1.0 - cos_a) - axis[0] * sin_a
        rotmat[2, 0] = axis[2] * axis[0] * (1.0 - cos_a) - axis[1] * sin_a
        rotmat[2, 1] = axis[2] * axis[1] * (1.0 - cos_a) + axis[0] * sin_a
        rotmat[2, 2] = cos_a + axis[2] ** 2 * (1.0 - cos_a)
        return rotmat

    def rotmat_around_axis(self, axis=[1, 1, 1], angle=0):
        """
        Rotation matrix for axis and angle
          angle in radians

        Requires:
            - axis
            - angle

        Provides:
            - None

        Returns:
            Rotation matrix
        """
        # normalized axis
        axis = numpy.array(axis) / numpy.linalg.norm(axis)

        rotmat = self.rotmat(axis, angle)
        return rotmat

    def rotmat_vec1vec2(self, vec1, vec2):
        """
        Rotmat for rotating vec1 into vec2

        Requires:
            - vec1 which is the first vector
            - vec2 which is the second vector

        Provides:
            - None

        Returns:
            Rotation matrix
        """
        tmp1 = vec1 / numpy.linalg.norm(vec1)
        tmp2 = vec2 / numpy.linalg.norm(vec2)

        cos_alpha = numpy.dot(tmp1, tmp2)
        if cos_alpha > 1.0:
            cos_alpha = 1.0
        if cos_alpha < -1.0:
            cos_alpha = -1.0
        angle = numpy.arccos(cos_alpha)

        rot_axis = numpy.cross(tmp1, tmp2)
        # no rotation necessary
        # CAREFUL: If cos_alpha = -1 -> invert
        if rot_axis.tolist() == [0.0, 0.0, 0.0]:
            rotmat = numpy.zeros((3, 3))
            rotmat[0][0] = cos_alpha
            rotmat[1][1] = cos_alpha
            rotmat[2][2] = cos_alpha
            return rotmat

        axis = rot_axis / numpy.linalg.norm(rot_axis)
        rotmat = self.rotmat(axis, angle)
        return rotmat


    def get_atomic_data(self):
        """
        Return covalent radii, chemical symbols and atomic number, 
        taken from ase.data

        Requires:
            - None

        Provides:
            - None

        Returns:
            - covalent_radii, chemical_symbols, atomic_numbers
        """
        # DATA FROM ASE
        covalent_radii = numpy.array([0.2 , 0.31, 0.28, 1.28, 0.96, 0.84, 0.76, 0.71, 0.66, 0.57, 0.58,
                                      1.66, 1.41, 1.21, 1.11, 1.07, 1.05, 1.02, 1.06, 2.03, 1.76, 1.7 ,
                                      1.6 , 1.53, 1.39, 1.39, 1.32, 1.26, 1.24, 1.32, 1.22, 1.22, 1.2 ,
                                      1.19, 1.2 , 1.2 , 1.16, 2.2 , 1.95, 1.9 , 1.75, 1.64, 1.54, 1.47,
                                      1.46, 1.42, 1.39, 1.45, 1.44, 1.42, 1.39, 1.39, 1.38, 1.39, 1.4 ,
                                      2.44, 2.15, 2.07, 2.04, 2.03, 2.01, 1.99, 1.98, 1.98, 1.96, 1.94,
                                      1.92, 1.92, 1.89, 1.9 , 1.87, 1.87, 1.75, 1.7 , 1.62, 1.51, 1.44,
                                      1.41, 1.36, 1.36, 1.32, 1.45, 1.46, 1.48, 1.4 , 1.5 , 1.5 , 2.6 ,
                                      2.21, 2.15, 2.06, 2.  , 1.96, 1.9 , 1.87, 1.8 , 1.69, 0.2 , 0.2 ,
                                      0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 ,
                                      0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 ])
        atomic_numbers = {'X': 0, 'H': 1, 'He': 2, 'Li': 3, 'Be': 4, 'B': 5, 'C': 6, 'N': 7, 'O': 8, 'F': 9, 'Ne': 10, 'Na': 11, 'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Ar': 18, 'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22, 'V': 23, 'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28, 'Cu': 29, 'Zn': 30, 'Ga': 31, 'Ge': 32, 'As': 33, 'Se': 34, 'Br': 35, 'Kr': 36, 'Rb': 37, 'Sr': 38, 'Y': 39, 'Zr': 40, 'Nb': 41, 'Mo': 42, 'Tc': 43, 'Ru': 44, 'Rh': 45, 'Pd': 46, 'Ag': 47, 'Cd': 48, 'In': 49, 'Sn': 50, 'Sb': 51, 'Te': 52, 'I': 53, 'Xe': 54, 'Cs': 55, 'Ba': 56, 'La': 57, 'Ce': 58, 'Pr': 59, 'Nd': 60, 'Pm': 61, 'Sm': 62, 'Eu': 63, 'Gd': 64, 'Tb': 65, 'Dy': 66, 'Ho': 67, 'Er': 68, 'Tm': 69, 'Yb': 70, 'Lu': 71, 'Hf': 72, 'Ta': 73, 'W': 74, 'Re': 75, 'Os': 76, 'Ir': 77, 'Pt': 78, 'Au': 79, 'Hg': 80, 'Tl': 81, 'Pb': 82, 'Bi': 83, 'Po': 84, 'At': 85, 'Rn': 86, 'Fr': 87, 'Ra': 88, 'Ac': 89, 'Th': 90, 'Pa': 91, 'U': 92, 'Np': 93, 'Pu': 94, 'Am': 95, 'Cm': 96, 'Bk': 97, 'Cf': 98, 'Es': 99, 'Fm': 100, 'Md': 101, 'No': 102, 'Lr': 103, 'Rf': 104, 'Db': 105, 'Sg': 106, 'Bh': 107, 'Hs': 108, 'Mt': 109, 'Ds': 110, 'Rg': 111, 'Cn': 112, 'Nh': 113, 'Fl': 114, 'Mc': 115, 'Lv': 116, 'Ts': 117, 'Og': 118}
        chemical_symbols = ['X', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']
        return covalent_radii, atomic_numbers, chemical_symbols


    def get_distances(self,
                      pos1,
                      pos2=None,
                      cell=None,
                      pbc=False):
        """
        Compute the distance matrix and all associated distance vectors for a given input structure.
        Take PBCs into account if necessary
           - Use brute-force way to compute minimum distance.
             We only have to do this ONCE. So it should be fine

        Requires:
           - pos1 .. all positions of the structure
           - pos2 .. Optional; if you want to compare specific distances with each other; otherwise, compare pos1 to itself
           - cell .. if pbc==True, then we also have to provide the cell information
           - pbc  .. Defines whether we need to check PBCs or not

        Provides:
           - None

        Returns:
           - dist_mat (Distance matrix), dist_vecs (Distance vectors)
        """
        if pos2 is None:
            pos2 = pos1.copy()
        if pbc:
            combos = []
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    for k in [-1,0,1]:
                        combos.append([i,j,k])
        # If we are checking a single position -> wrap it into a list so we can use the below logic
        if pos1.shape == (3,):
            pos1 = numpy.array([pos1])
        if pos2.shape == (3,):
            pos2 = numpy.array([pos2])


        dist_mat  = numpy.zeros((len(pos1),len(pos2)))
        dist_vecs = numpy.zeros((len(pos1),len(pos2),3))
        for p1,posi1 in enumerate(pos1):
            # If there are no PBCs: Just calculate all distances and vectors wrt all positions
            if not pbc:
                dist_vecs[p1] = [numpy.array(posi2-posi1) for posi2 in pos2]
                dist_mat[p1]  = [numpy.linalg.norm(vec) for vec in dist_vecs[p1]]
            else:
                # Check distances to ALL adjacent unit cells. Then take minimum.
                # Not efficient, but whatever. We only do this once!
                for p2,posi2 in enumerate(pos2):
                    tmp_vecs = [(posi2+i*cell[0]+j*cell[1]+k*cell[2])-posi1 for [i,j,k] in combos]
                    lengths  = [numpy.linalg.norm(vec) for vec in tmp_vecs]
                    idx_min  = numpy.argsort(lengths)[0]
                    dist_mat[p1][p2]  = lengths[idx_min]
                    dist_vecs[p1][p2] = tmp_vecs[idx_min]
        return dist_vecs, dist_mat

