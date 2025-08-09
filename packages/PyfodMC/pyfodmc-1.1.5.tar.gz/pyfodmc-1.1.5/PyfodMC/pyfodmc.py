"""
fodMC@Python
K. Trepte
11. April 2024

current: June 27, 2024
"""

from PyfodMC.database import Database
from PyfodMC.helperfunctions import timeit
from PyfodMC.bonds import Bonds
from PyfodMC.lones import Lones
from PyfodMC.cores import Cores
import numpy


# Note: functionalities of HelperFunctions are imported through Bonds, Lones
class PyfodMC(Database, Bonds, Lones, Cores):
    def __init__(self):
        """
        ## Mandatory input ##
        geometry    ... User input: file containing the coordinates of all atoms of your system, of cif file in case of PBCs       default: test.xyz

        ## Important user inputs ##
        bonds       ... User input: Dictionary defining the bond patterns between atoms                                            default: single bond between all atoms that are close to each other
                                    Input is a follows:
                                      - The key of the dictionary is the bond type in terms of the number of up and dn FODs
                                         e.g. "2-2" for double bond
                                      - The value is a list of pairs of either
                                        (a) atomic indices or
                                        (b) atomic types
                                        E.g. bonds = {"2-2":["1-3","0-4","N-O"]}
                                        means that there will be a double bond between indices 1 and 3, 0 and 4, and
                                        all atomic pairs of N-O.
                                        Note that N-O that are far away from each other will not be initialized with this option
                                    NOTE: All bonds will be initialized as single bonds
                                          -> No need to intialize single bonds by hand!
        lone        ... User input: Dictionary defining the lone pattern for each atom, or atomic type                             default: up and dn lone FODs per atom are determined based on the number of bonds, and its charge
                                    Input is a follows:
                                      - The key of the dictionary is the lone type in terms of the number of up and dn FODs
                                         e.g. "2-2" for two lone pairs
                                      - The value is a list composed of either
                                        (a) atomic indices or
                                        (b) atomic types
                                        E.g. lone = {"2-1":["C",1]}
                                        means that there will be 2 up and 1 dn FOD in the lone region for
                                        all C atoms as well as atom with index 1
                                    NOTE: Lone FODs are automatically assigned based on the number of bonds and the charge of the species

        ## Other user inputs ##
        output      ... User input: output file to be written, containing atoms as well as FODs                                    default: new_test.xyz
        fix1s       ... User input: if True, place 1s FODs at the atomic coordinates                                               default: True
        guess_type  ... User input: if 'restricted', only one spin channel will be added                                           default: "unrestricted"

        ## Extra user inputs ##
        charge      ... User input: Dictionary defining the charge of all atoms                                                    default: all 0
                                    Input is a follows:
                                      - The key of the dictionary is the charge, e.g. 2 or -1
                                      - The value is a list composed of either
                                        (a) atomic indices or
                                        (b) atomic types
                                        E.g. charge = {2:["Ni",13]}
                                        means that there will be a positive charge of 2 for all Ni and atom index 13
        switch_updn ... User input: Dictionary defining for which atom to exchange the up and dn channel                            default: all False
                                    Can be useful for transition metal atoms with antiferromagnetic order
                                    Input is a follows:
                                      - The key of the dictionary is either True or False
                                      - The value is a list composed of either
                                        (a) atomic indices or
                                        (b) atomic types
                                        E.g. switch_updn = {True:["S",11]}
                                        means that there fodMC will switch up and dn for all S and atom index 11
        invert_updn ... User input: Dictionary defining for which atom to invert UP and DN FODs (core FODs for molecules)           default: all False
                                    Can be useful for LDQ guesses and maximized spin-polarization
                                    Input is a follows:
                                      - The key of the dictionary is either True or False
                                      - The value is a list composed of either
                                        (a) atomic indices or
                                        (b) atomic types
                                        E.g. invert_updn = {True:["S",11]}
                                        means that there fodMC will invert up and dn for all S and atom index 11
        ecp         ... User input: Dictionary defining what kind of core FODs to remove from any atom                              default: all None
                                    Input is a follows:
                                      - The key of the dictionary the size of the core to remove, either 'sc' or 'lc' (small core, large core)
                                      - The value is a list composed of either
                                        (a) atomic indices or
                                        (b) atomic types
                                        E.g. charge = {"lc":["Kr",14],"sc":[12]}
                                        means that there will be large core removal for all Kr and atom index 14,
                                        and a small core removal fr atom index 12
        config      ... user input: Dictionary defining which configuration to use for all atoms                                     default: all "default"
                                    "default" exists for all elements; for transition metals alternative options exists
                                    Input is a follows:
                                      - The key of the dictionary is the configuration, e.g. "4s2"
                                      - The value is a list composed of either
                                        (a) atomic indices or
                                        (b) atomic types
                                        E.g. charge = {"4s2":["Ni","Cr"]}
                                        means that there fodMC will use 4s2 configuration for all Ni and Cr atoms
        ## Not for user ##
        fods        ... Place holder to store the FODs throughout the generation process                                           default: []
        scale_r     ... Global variable: Scales the size of mutliple bonds/multiple lone FODs                                      default: 0.65
        ecp_charge  ... How much electrons are being removed when using ECPs -> for correct assignment of charge at the end        default: 0
        """
        Database.__init__(self)

        self.geometry = "test.xyz"
        # Define which bonds and lone pairs to explicitely form; if not specified, do default
        self.bonds = dict()
        self.lone = dict()
        # Other user inputs
        self.output = "new_test.xyz"
        self.fix1s = True
        self.guess_type = "unrestricted"
        # If mol file is read -> allow user to still define bonds themselves
        self.bonds_from_molfile = dict()
        # Extra options
        # either indices and values; or atomic type and values
        # e.g. self.charge = {"F":-1} or self.ecp = {1:'sc',4:'lc'}
        self.charge = dict()
        self.switch_updn = dict()
        self.invert_updn = dict()
        self.ecp = dict()
        self.config = dict()
        # Place holder, and global variable
        self.fods = []
        self.scale_r = 0.65
        self.ecp_charge = 0

    

    def create_atomic_guess(self):
        """
        Create atomic guess

        Requires:
            - self.atomic_sym
            - self.atomic_pos
            - self.charge
            - self.config
            - self.fix1s
            - self.invert_updn
            - self.ecp
            - self.switch_updn

        Provides:
            - self.fods

        Returns:
            None

        """
        # From Database
        fods = self.get_initial_FODs(
            species=self.atomic_sym[0],
            charge=self.charge[0],
            config=self.config[0],
            fix1s=self.fix1s,
            invert_updn=self.invert_updn[0],
            ecp=self.ecp[0],
            switch_updn=self.switch_updn[0],
        )
        # Need to add the atomic position to the FOD positions
        for f, fod in enumerate(fods):
            for shell in fod:
                for fodpos in shell:
                    fodpos += self.atomic_pos[0]
        self.fods = [fods]

        charge, spin, dip = self.get_charge_spin_dip()
        self.write()
        print(f"Generate atomic guess for {self.atomic_sym[0]}")
        print(
            f"Charge = {charge}  spin = {spin}   mu = {dip[0]:10.4f} {dip[1]:10.4f} {dip[2]:10.4f}"
        )

    def create_molecularORpbc_guess(self):
        """
        Create molecular or PBC guess

        Requires:
            - self.atomic_sym
            - self.atomic_pos
            - self.charge
            - self.config
            - self.fix1s
            - self.invert_updn
            - self.ecp
            - self.switch_updn
            - self.assign_bonds()
            - self.linear_planar()
            - self.create_bonds()
            - self.assign_lone()
            - self.create_lone()
            - self.create_core()

        Provides:
            - self.fods

        Returns:
            None
        """
        for s, sym in enumerate(self.atomic_sym):
            fods = self.get_initial_FODs(
                species=sym,
                charge=self.charge[s],
                config=self.config[s],
                fix1s=self.fix1s,
                invert_updn=self.invert_updn[s],
                ecp=self.ecp[s],
                switch_updn=self.switch_updn[s],
            )
            # Need to add the atomic position to the FOD positions
            for f, fod in enumerate(fods):
                for shell in fod:
                    for fodpos in shell:
                        fodpos += self.atomic_pos[s]
            self.fods.append(fods)

        # Create bond/connectivity matrix
        self.assign_bonds()
        # Check which atoms are in a planar/linear enviroment, if any (needed to place FODs accordingly)
        self.linear_planar()
        # create_bonds()
        bond_fods = self.create_bonds()

        # Create lone FOD assignment
        self.assign_lone()
        # Create lones
        lone_fods = self.create_lone()

        # Add bond FODs to self.fods
        self.fods.extend(bond_fods)
        self.fods.extend(lone_fods)

        # Rotate cores wrt bonds/lone
        # Work in progress
        core_fods = self.create_core()
        self.fods.extend(core_fods)

        charge, spin, dip = self.get_charge_spin_dip()
        self.write()
        # Define the chemical formula
        syms, cnts = numpy.unique(self.atomic_sym, return_counts=True)
        formula = ""
        for sym, cnt in zip(syms, cnts):
            if cnt == 1:
                formula += f"{sym}"
            else:
                formula += f"{sym}{cnt}"
        print(f"Generate guess for {formula}")
        print(
            f"Charge = {charge}  spin = {spin}   mu = {dip[0]:10.4f} {dip[1]:10.4f} {dip[2]:10.4f}"
        )

    @timeit
    def create_guess(self):
        """
        Create fodMC guess

        Requires:
            - self.read_atoms()
            - self.check()
            - self.create_atomic_guess()
            - self.create_molecular_guess()
            - self.create_periodic_guess()

        Provides:
            - None

        Returns:
            None
        """
        # Read atomic positions and symbols
        #self.read_atoms()
        self.read()
        # Check charge, switch_updn, ecp, config dicts -> if atomic type -> set to indices/values dicts
        # Set values for all atoms correctly
        self.check()

        if len(self.atomic_pos) == 1:
            # Atomic guess
            self.create_atomic_guess()
        else:
            # Molecular OR PBC guess
            self.create_molecularORpbc_guess()


def test_pyfodmc():
    """
    Test pyfodmc functionality.
    """
    myfodmc = PyfodMC()

    test = open("test2.xyz", "w")
    test.write("2\n\nN 0 0 -0.5\nN 0 0 +0.5")
    test.close()
    myfodmc.geometry = "test2.xyz"

    myfodmc.bonds = {"3-3": ["0-1"]}
    myfodmc.lone = {}

    myfodmc.fix1s = True
    myfodmc.create_guess()


if __name__ == "__main__":
    test_pyfodmc()
