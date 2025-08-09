"""
Database for FODs per element
"""

from PyfodMC.motifs import Motifs
from PyfodMC.helperfunctions import HelperFunctions

class Database(Motifs,HelperFunctions):
    def __init__(self):
        """
        Logic: "default" or others: configuration (different ones available for transition metals),
               "up": number of up shells, and number of points per shell, same for "dn",
               r_up/r_dn are the respective radii
        Note: Radii come from the original implementation of fodMC
        Transition metals: 4s2 -> both 4s orbitals are filled;
                           4s1 -> only spin up is filled;
                           3d4s -> 4s and 3d are treated within the same shell (average shell radii TODO)
          - We introduce defaults, as well as all possible assignments (there is redunancy, but it'll be easier to assign them later on)

          ecp_charge is used to correctly assign charge in the outputs (printed statements about charge of the system)
        """
        self.core_charge = []
        self.atomic_data = {
            "H": {
                "default": {"up": [1], "dn": [0], "r_up": [0.15875], "r_dn": [0.15875]}
            },
            "He": {
                "default": {"up": [1], "dn": [1], "r_up": [0.15875], "r_dn": [0.15875]}
            },
            "Li": {
                "default": {
                    "up": [1, 1],
                    "dn": [1],
                    "r_up": [0.07303, 1.52773],
                    "r_dn": [0.05345],
                }
            },
            "Be": {
                "default": {
                    "up": [1, 1],
                    "dn": [1, 1],
                    "r_up": [0.04128, 1.10228],
                    "r_dn": [0.04128, 1.10228],
                }
            },
            "B": {
                "default": {
                    "up": [1, 2],
                    "dn": [1, 1],
                    "r_up": [0.01852, 1.06523],
                    "r_dn": [0.01217, 1.06523],
                }
            },
            "C": {
                "default": {
                    "up": [1, 3],
                    "dn": [1, 1],
                    "r_up": [0.04392, 1.05941],
                    "r_dn": [0.03651, 1.05941],
                }
            },
            "N": {
                "default": {
                    "up": [1, 4],
                    "dn": [1, 1],
                    "r_up": [0.00053, 0.82499],
                    "r_dn": [0.02805, 0.79324],
                }
            },
            "O": {
                "default": {
                    "up": [1, 4],
                    "dn": [1, 2],
                    "r_up": [0.00053, 0.71862],
                    "r_dn": [0.02434, 0.79959],
                }
            },
            "F": {
                "default": {
                    "up": [1, 4],
                    "dn": [1, 3],
                    "r_up": [0.00053, 0.63713],
                    "r_dn": [0.00053, 0.74402],
                }
            },
            "Ne": {
                "default": {
                    "up": [1, 4],
                    "dn": [1, 4],
                    "r_up": [0.00053, 0.57098],
                    "r_dn": [0.00053, 0.57098],
                }
            },
            "Na": {
                "default": {
                    "up": [1, 4, 1],
                    "dn": [1, 4],
                    "r_up": [0.00053, 0.47097, 2.55540],
                    "r_dn": [0.00053, 0.47097],
                }
            },
            "Mg": {
                "default": {
                    "up": [1, 4, 1],
                    "dn": [1, 4, 1],
                    "r_up": [0.00053, 0.37624, 2.07437],
                    "r_dn": [0.00053, 0.37624, 2.07437],
                }
            },
            "Al": {
                "default": {
                    "up": [1, 4, 2],
                    "dn": [1, 4, 1],
                    "r_up": [0.00053, 0.33603, 1.20599],
                    "r_dn": [0.00053, 0.33603, 1.56107],
                }
            },
            "Si": {
                "default": {
                    "up": [1, 4, 3],
                    "dn": [1, 4, 1],
                    "r_up": [0.00053, 0.29581, 1.08534],
                    "r_dn": [0.00053, 0.29581, 1.35205],
                }
            },
            "P": {
                "default": {
                    "up": [1, 4, 4],
                    "dn": [1, 4, 1],
                    "r_up": [0.00053, 0.26406, 0.96257],
                    "r_dn": [0.00053, 0.26406, 1.28325],
                }
            },
            "S": {
                "default": {
                    "up": [1, 4, 4],
                    "dn": [1, 4, 2],
                    "r_up": [0.00053, 0.24607, 0.85303],
                    "r_dn": [0.00053, 0.24607, 0.85145],
                }
            },
            "Cl": {
                "default": {
                    "up": [1, 4, 4],
                    "dn": [1, 4, 3],
                    "r_up": [0.00053, 0.22067, 0.76995],
                    "r_dn": [0.00053, 0.22067, 0.78318],
                }
            },
            "Ar": {
                "default": {
                    "up": [1, 4, 4],
                    "dn": [1, 4, 4],
                    "r_up": [0.00053, 0.20479, 0.70381],
                    "r_dn": [0.00053, 0.20479, 0.70381],
                }
            },
            "K": {
                "default": {
                    "up": [1, 4, 4, 1],
                    "dn": [1, 4, 4],
                    "r_up": [0.00053, 0.18786, 0.64824, 3.27719],
                    "r_dn": [0.00053, 0.18786, 0.63660],
                }
            },
            "Ca": {
                "default": {
                    "up": [1, 4, 4, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.17092, 0.67999, 2.09395],
                    "r_dn": [0.00053, 0.17092, 0.67999, 2.09395],
                }
            },
            "Sc": {
                "default": {
                    "up": [1, 4, 5, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.15822, 0.59744, 2.40987],
                    "r_dn": [0.00053, 0.15822, 0.59744, 2.40987],
                },
                "4s2": {
                    "up": [1, 4, 5, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.15822, 0.59744, 2.40987],
                    "r_dn": [0.00053, 0.15822, 0.59744, 2.40987],
                },
                "4s1": {
                    "up": [1, 4, 5, 1],
                    "dn": [1, 4, 5],
                    "r_up": [0.00053, 0.15822, 0.59744, 2.40987],
                    "r_dn": [0.00053, 0.15822, 0.59744],
                },
                "3d4s": {
                    "up": [1, 4, 6],
                    "dn": [1, 4, 5],
                    "r_up": [0.00053, 0.15822, 1.50366],
                    "r_dn": [0.00053, 0.15822, 1.50366],
                },
            },
            "Ti": {
                "default": {
                    "up": [1, 4, 6, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.15082, 0.53182, 2.30457],
                    "r_dn": [0.00053, 0.15082, 0.53182, 2.30457],
                },
                "4s2": {
                    "up": [1, 4, 6, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.15082, 0.53182, 2.30457],
                    "r_dn": [0.00053, 0.15082, 0.53182, 2.30457],
                },
                "4s1": {
                    "up": [1, 4, 6, 1],
                    "dn": [1, 4, 5],
                    "r_up": [0.00053, 0.15082, 0.53182, 2.30457],
                    "r_dn": [0.00053, 0.15082, 0.53182],
                },
                "3d4s": {
                    "up": [1, 4, 7],
                    "dn": [1, 4, 5],
                    "r_up": [0.00053, 0.15082, 1.41819],
                    "r_dn": [0.00053, 0.15082, 1.41819],
                },
            },
            "V": {
                "default": {
                    "up": [1, 4, 7, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.14023, 0.54294, 2.27546],
                    "r_dn": [0.00053, 0.14023, 0.54294, 2.27546],
                },
                "4s2": {
                    "up": [1, 4, 7, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.14023, 0.54294, 2.27546],
                    "r_dn": [0.00053, 0.14023, 0.54294, 2.27546],
                },
                "4s1": {
                    "up": [1, 4, 7, 1],
                    "dn": [1, 4, 5],
                    "r_up": [0.00053, 0.14023, 0.54294, 2.27546],
                    "r_dn": [0.00053, 0.14023, 0.54294],
                },
                "3d4s": {
                    "up": [1, 4, 8],
                    "dn": [1, 4, 5],
                    "r_up": [0.00053, 0.14023, 1.40920],
                    "r_dn": [0.00053, 0.14023, 1.40920],
                },
            },
            "Cr": {
                "default": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 4],
                    "r_up": [0.00053, 0.13759, 0.54241, 2.11671],
                    "r_dn": [0.00053, 0.13759, 0.54241],
                },
                "4s2": {
                    "up": [1, 4, 8, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.13759, 0.54241, 2.11671],
                    "r_dn": [0.00053, 0.13759, 0.54241, 2.11671],
                },
                "4s1": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 4],
                    "r_up": [0.00053, 0.13759, 0.54241, 2.11671],
                    "r_dn": [0.00053, 0.13759, 0.54241],
                },
                "3d4s": {
                    "up": [1, 4, 9],
                    "dn": [1, 4, 5],
                    "r_up": [0.00053, 0.13759, 1.32956],
                    "r_dn": [0.00053, 0.13759, 1.32956],
                },
            },
            "Mn": {
                "default": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.12700, 0.50272, 2.38130],
                    "r_dn": [0.00053, 0.12700, 0.47891, 2.38130],
                },
                "4s2": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 4, 1],
                    "r_up": [0.00053, 0.12700, 0.50272, 2.38130],
                    "r_dn": [0.00053, 0.12700, 0.47891, 2.38130],
                },
                "4s1": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 5],
                    "r_up": [0.00053, 0.12700, 0.50272, 2.38130],
                    "r_dn": [0.00053, 0.12700, 0.47891],
                },
                "3d4s": {
                    "up": [1, 4, 10],
                    "dn": [1, 4, 5],
                    "r_up": [0.00053, 0.12700, 1.44201],
                    "r_dn": [0.00053, 0.12700, 1.44201],
                },
            },
            "Fe": {
                "default": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 5, 1],
                    "r_up": [0.00053, 0.12171, 0.45509, 2.38130],
                    "r_dn": [0.00053, 0.12171, 0.45509, 2.38130],
                },
                "4s2": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 5, 1],
                    "r_up": [0.00053, 0.12171, 0.45509, 2.38130],
                    "r_dn": [0.00053, 0.12171, 0.45509, 2.38130],
                },
                "4s1": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 6],
                    "r_up": [0.00053, 0.12171, 0.45509, 2.38130],
                    "r_dn": [0.00053, 0.12171, 0.45509],
                },
                "3d4s": {
                    "up": [1, 4, 10],
                    "dn": [1, 4, 6],
                    "r_up": [0.00053, 0.12171, 1.41819],
                    "r_dn": [0.00053, 0.12171, 1.41819],
                },
            },
            "Co": {
                "default": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 6, 1],
                    "r_up": [0.00053, 0.11906, 0.43657, 2.24900],
                    "r_dn": [0.00053, 0.11906, 0.43657, 2.24900],
                },
                "4s2": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 6, 1],
                    "r_up": [0.00053, 0.11906, 0.43657, 2.24900],
                    "r_dn": [0.00053, 0.11906, 0.43657, 2.24900],
                },
                "4s1": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 7],
                    "r_up": [0.00053, 0.11906, 0.43657, 2.24900],
                    "r_dn": [0.00053, 0.11906, 0.43657],
                },
                "3d4s": {
                    "up": [1, 4, 10],
                    "dn": [1, 4, 7],
                    "r_up": [0.00053, 0.11906, 1.34279],
                    "r_dn": [0.00053, 0.11906, 1.34279],
                },
            },
            "Ni": {
                "default": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 7, 1],
                    "r_up": [0.00053, 0.11113, 0.43393, 2.22254],
                    "r_dn": [0.00053, 0.11113, 0.43393, 2.22254],
                },
                "4s2": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 7, 1],
                    "r_up": [0.00053, 0.11113, 0.43393, 2.22254],
                    "r_dn": [0.00053, 0.11113, 0.43393, 2.22254],
                },
                "4s1": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 8],
                    "r_up": [0.00053, 0.11113, 0.43393, 2.22254],
                    "r_dn": [0.00053, 0.11113, 0.43393],
                },
                "3d4s": {
                    "up": [1, 4, 10],
                    "dn": [1, 4, 8],
                    "r_up": [0.00053, 0.11113, 1.32824],
                    "r_dn": [0.00053, 0.11113, 1.32824],
                },
            },
            "Cu": {
                "default": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 9],
                    "r_up": [0.00053, 0.10319, 0.59797, 2.48713],
                    "r_dn": [0.00053, 0.10319, 0.59797],
                },
                "4s2": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 8, 1],
                    "r_up": [0.00053, 0.10319, 0.59797, 2.48713],
                    "r_dn": [0.00053, 0.10319, 0.59797, 2.22254],
                },
                "4s1": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 9],
                    "r_up": [0.00053, 0.10319, 0.59797, 2.48713],
                    "r_dn": [0.00053, 0.10319, 0.59797],
                },
                "3d4s": {
                    "up": [1, 4, 10],
                    "dn": [1, 4, 9],
                    "r_up": [0.00053, 0.10319, 1.54255],
                    "r_dn": [0.00053, 0.10319, 1.54255],
                },
            },
            "Zn": {
                "default": {
                    "up": [1, 4, 9, 1],
                    "dn": [1, 4, 9, 1],
                    "r_up": [0.00053, 0.09631, 0.39953, 2.51094],
                    "r_dn": [0.00053, 0.09631, 0.39953, 2.51094],
                },
                "3d4s": {
                    "up": [1, 4, 10],
                    "dn": [1, 4, 10],
                    "r_up": [0.00053, 0.09631, 1.45524],
                    "r_dn": [0.00053, 0.09631, 1.45524],
                },
            },
            "Ga": {
                "default": {
                    "up": [1, 4, 9, 2],
                    "dn": [1, 4, 9, 1],
                    "r_up": [0.00053, 0.09525, 0.37572, 2.20402],
                    "r_dn": [0.00053, 0.09525, 0.37572, 2.28869],
                }
            },
            "Ge": {
                "default": {
                    "up": [1, 4, 9, 3],
                    "dn": [1, 4, 9, 1],
                    "r_up": [0.00053, 0.09155, 0.35614, 1.76428],
                    "r_dn": [0.00053, 0.09155, 0.35614, 1.74417],
                }
            },
            "As": {
                "default": {
                    "up": [1, 4, 9, 4],
                    "dn": [1, 4, 9, 1],
                    "r_up": [0.00053, 0.08784, 0.33074, 1.69442],
                    "r_dn": [0.00053, 0.08784, 0.33074, 1.56266],
                }
            },
            "Se": {
                "default": {
                    "up": [1, 4, 9, 4],
                    "dn": [1, 4, 9, 2],
                    "r_up": [0.00053, 0.08414, 0.30957, 1.68913],
                    "r_dn": [0.00053, 0.08414, 0.30957, 1.53991],
                }
            },
            "Br": {
                "default": {
                    "up": [1, 4, 9, 4],
                    "dn": [1, 4, 9, 3],
                    "r_up": [0.00053, 0.08149, 0.29634, 1.40073],
                    "r_dn": [0.00053, 0.08149, 0.29634, 1.39385],
                }
            },
            "Kr": {
                "default": {
                    "up": [1, 4, 9, 4],
                    "dn": [1, 4, 9, 4],
                    "r_up": [0.00053, 0.07779, 0.27676, 1.30971],
                    "r_dn": [0.00053, 0.07779, 0.27676, 1.30971],
                }
            },
            "Rb": {
                "default": {
                    "up": [1, 4, 9, 4, 1],
                    "dn": [1, 4, 9, 4],
                    "r_up": [0.00053, 0.07779, 0.25566, 1.25971, 1.99543],
                    "r_dn": [0.00053, 0.07779, 0.25566, 1.25971],
                }
            },
            "Sr": {
                "default": {
                    "up": [1, 4, 9, 4, 1],
                    "dn": [1, 4, 9, 4, 1],
                    "r_up": [0.00053, 0.07779, 0.25566, 1.25971, 1.99543],
                    "r_dn": [0.00053, 0.07779, 0.25566, 1.25971, 1.99543],
                }
            },
            "Y": {
                "default": {
                    "up": [1, 4, 9, 5, 1],
                    "dn": [1, 4, 9, 4, 1],
                    "r_up": [0.00053, 0.07479, 0.24476, 0.79054, 1.89212],
                    "r_dn": [0.00053, 0.07479, 0.24476, 0.79054, 1.89212],
                }
            },
            "Zr": {
                "default": {
                    "up": [1, 4, 9, 6, 1],
                    "dn": [1, 4, 9, 4, 1],
                    "r_up": [0.00053, 0.07379, 0.23376, 0.78054, 1.85212],
                    "r_dn": [0.00053, 0.07379, 0.23376, 0.78054, 1.85212],
                }
            },
            "Nb": {
                "default": {
                    "up": [1, 4, 9, 7, 1],
                    "dn": [1, 4, 9, 4, 1],
                    "r_up": [0.00053, 0.07179, 0.22276, 0.75054, 1.80212],
                    "r_dn": [0.00053, 0.07179, 0.22276, 0.75054, 1.80212],
                }
            },
            "Mo": {
                "default": {
                    "up": [1, 4, 9, 8, 1],
                    "dn": [1, 4, 9, 4, 1],
                    "r_up": [0.00053, 0.06879, 0.21176, 0.71054, 1.75212],
                    "r_dn": [0.00053, 0.06879, 0.21176, 0.71054, 1.75212],
                }
            },
            "Tc": {
                "default": {
                    "up": [1, 4, 9, 9, 1],
                    "dn": [1, 4, 9, 4, 1],
                    "r_up": [0.00053, 0.06579, 0.20076, 0.67054, 1.70212],
                    "r_dn": [0.00053, 0.06579, 0.20076, 0.67054, 1.70212],
                }
            },
            "Ru": {
                "default": {
                    "up": [1, 4, 9, 9, 1],
                    "dn": [1, 4, 9, 5, 1],
                    "r_up": [0.00053, 0.06179, 0.18876, 0.62054, 1.64212],
                    "r_dn": [0.00053, 0.06179, 0.18876, 0.62054, 1.64212],
                }
            },
            "Rh": {
                "default": {
                    "up": [1, 4, 9, 9, 1],
                    "dn": [1, 4, 9, 6, 1],
                    "r_up": [0.00053, 0.05979, 0.17876, 0.60054, 1.61212],
                    "r_dn": [0.00053, 0.05979, 0.17876, 0.60054, 1.61212],
                }
            },
            "Pd": {
                "default": {
                    "up": [1, 4, 9, 9, 1],
                    "dn": [1, 4, 9, 7, 1],
                    "r_up": [0.00053, 0.05679, 0.16976, 0.58054, 1.58212],
                    "r_dn": [0.00053, 0.05679, 0.16976, 0.58054, 1.58212],
                }
            },
            "Ag": {
                "default": {
                    "up": [1, 4, 9, 9, 1],
                    "dn": [1, 4, 9, 8, 1],
                    "r_up": [0.00053, 0.05579, 0.16576, 0.55054, 1.55212],
                    "r_dn": [0.00053, 0.05579, 0.16576, 0.55054, 1.55212],
                }
            },
            "Cd": {
                "default": {
                    "up": [1, 4, 9, 9, 1],
                    "dn": [1, 4, 9, 9, 1],
                    "r_up": [0.00053, 0.05379, 0.16276, 0.54054, 1.52212],
                    "r_dn": [0.00053, 0.05379, 0.16276, 0.54054, 1.52212],
                }
            },
            "In": {
                "default": {
                    "up": [1, 4, 9, 9, 2],
                    "dn": [1, 4, 9, 9, 1],
                    "r_up": [0.00053, 0.05309, 0.16076, 0.52054, 1.50212],
                    "r_dn": [0.00053, 0.05309, 0.16076, 0.52054, 1.50212],
                }
            },
            "Sn": {
                "default": {
                    "up": [1, 4, 9, 9, 3],
                    "dn": [1, 4, 9, 9, 1],
                    "r_up": [0.00053, 0.05259, 0.15676, 0.50054, 1.48212],
                    "r_dn": [0.00053, 0.05259, 0.15676, 0.50054, 1.48212],
                }
            },
            "Sb": {
                "default": {
                    "up": [1, 4, 9, 9, 4],
                    "dn": [1, 4, 9, 9, 1],
                    "r_up": [0.00053, 0.05209, 0.15076, 0.49554, 1.46212],
                    "r_dn": [0.00053, 0.05209, 0.15076, 0.49554, 1.46212],
                }
            },
            "Te": {
                "default": {
                    "up": [1, 4, 9, 9, 4],
                    "dn": [1, 4, 9, 9, 2],
                    "r_up": [0.00053, 0.05159, 0.14876, 0.47554, 1.44212],
                    "r_dn": [0.00053, 0.05159, 0.14876, 0.47554, 1.44212],
                }
            },
            "I": {
                "default": {
                    "up": [1, 4, 9, 9, 4],
                    "dn": [1, 4, 9, 9, 3],
                    "r_up": [0.00053, 0.05109, 0.14676, 0.45554, 1.42212],
                    "r_dn": [0.00053, 0.05109, 0.14676, 0.45554, 1.42212],
                }
            },
            "Xe": {
                "default": {
                    "up": [1, 4, 9, 9, 4],
                    "dn": [1, 4, 9, 9, 4],
                    "r_up": [0.00053, 0.05027, 0.14447, 0.44874, 1.41714],
                    "r_dn": [0.00053, 0.05027, 0.14447, 0.44874, 1.41714],
                }
            },
        }

    def get_initial_FODs(
        self,
        species="H",
        charge=0,
        config="default",
        fix1s=True,
        invert_updn=False,
        ecp=None,
        switch_updn=False,
    ):
        """
        get_initial_FODs
           Construct the initial guess for FODs

           species      .. element identifier
           charge       .. charge assigned to this species,                            default: 0
           config       .. electronic configuration; 'default' exists for all species, default: 'default'
                           but transition metals have other options (4s1,4s2,3d4s)
           fix1s        .. Place the 1s FODs at the origin                             default: True
           invert_updn  .. Invert the up and the dn channel for all FODs               default: False
                           If False, up and dn will be paired (for all inner shells)
           ecp          .. to remove lower shell FODs;                                 default: None
                           can be 'sc' (small core) or 'lc' (large core)
           switch_updn  .. exchange up and dn globally                                 default: False
                           (useful for magnetic systems where one species' majority spin is DN


        Requires:
            - self.atomic_data
            - species
            - charge
            - config
            - fix1s
            - invert_updn
            - ecp
            - switch_updn

        Provides:
            - self.core_charge

        Returns:
            All FODs positions for the given species

        """
        # From HelperFunctions
        _, atomic_numbers, chemical_symbols = self.get_atomic_data()

        fods_up = []
        fods_dn = []
        # need .copy(), as otherwise atomic_data could be modified by charge adjustments of transition metals
        up_rad, up_pts = (
            self.atomic_data[species][config]["r_up"].copy(),
            self.atomic_data[species][config]["up"].copy(),
        )
        dn_rad, dn_pts = (
            self.atomic_data[species][config]["r_dn"].copy(),
            self.atomic_data[species][config]["dn"].copy(),
        )


        # Charge
        if charge != 0:
            # if not transition metal: just take the elemental composition of elem - charge; also for transition metals if negative charge
            if (
                species
                not in ["Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Zr"] # Add 4d metals, TODO
                or charge < 0
            ):
                tmp = atomic_numbers[species] - charge
                species = chemical_symbols[tmp]
                config = "default"
                up_rad, up_pts = (
                    self.atomic_data[species][config]["r_up"].copy(),
                    self.atomic_data[species][config]["up"].copy(),
                )
                dn_rad, dn_pts = (
                    self.atomic_data[species][config]["r_dn"].copy(),
                    self.atomic_data[species][config]["dn"].copy(),
                )
            else:
                # remove highest electrons according to charge
                # ugly, but good enough for now
                while charge > 0:
                    # if up has more electronic shells then down -> remove there
                    if len(up_rad) > len(dn_rad):
                        up_pts[-1] -= 1
                        # if no more electrons in this shell -> remove shell
                        if up_pts[-1] == 0:
                            up_pts = up_pts[:-1]
                            up_rad = up_rad[:-1]
                    # Dn has more shells than up
                    elif len(dn_rad) > len(up_rad):
                        dn_pts[-1] -= 1
                        # if no more electrons in this shell -> remove shell
                        if dn_pts[-1] == 0:
                            dn_pts = dn_pts[:-1]
                            dn_rad = dn_rad[:-1]
                    # Same shells -> remove electrons from shell with larger number
                    elif len(up_rad) == len(dn_rad):
                        if up_pts[-1] > dn_pts[-1]:
                            up_pts[-1] -= 1
                            # if no more electrons in this shell -> remove shell
                            if up_pts[-1] == 0:
                                up_pts = up_pts[:-1]
                                up_rad = up_rad[:-1]
                        else:
                            dn_pts[-1] -= 1
                            # if no more electrons in this shell -> remove shell
                            if dn_pts[-1] == 0:
                                dn_pts = dn_pts[:-1]
                                dn_rad = dn_rad[:-1]
                    charge -= 1
            
        # add core charge here, before removing stuff for ECPs
        self.core_charge.append(sum(up_pts[:-1]) + sum(dn_pts[:-1]))

        # ECP -> remove lower shells; small core and large core
        if ecp is not None:
            remove = 0  # for H, He -> nothing to remove
            # check how many electrons we have
            no_elec = sum(up_pts) + sum(dn_pts)
            # Define how many shells we remove
            if ecp == "lc":
                if no_elec > 2 and no_elec <= 10:
                    remove = 1
                elif no_elec > 10 and no_elec <= 18:
                    remove = 2
                elif no_elec > 18:
                    remove = 3
                elif no_elec > 36:
                    remove = 4
            elif ecp == "sc":
                if no_elec > 2 and no_elec <= 18:
                    remove = 1
                elif no_elec > 18:
                    remove = 2
                elif no_elec > 36:
                    remove = 3

            self.ecp_charge += sum(up_pts[:remove])
            self.ecp_charge += sum(dn_pts[:remove])

            up_rad = up_rad[remove:]
            up_pts = up_pts[remove:]
            dn_rad = dn_rad[remove:]
            dn_pts = dn_pts[remove:]


        # switch up and dn?
        if switch_updn:
            tmp_rad = dn_rad
            tmp_pts = dn_pts
            dn_rad = up_rad
            dn_pts = up_pts
            up_rad = tmp_rad
            up_pts = tmp_pts


        # Inversion of shells as well as up-dn
        #  - Invert shells globally wrt each other; and if invert_updn, take that into account too
        # Further, include fix1s
        if invert_updn:
            factor_dn = -1
        else:
            factor_dn = +1

        for i, rad in enumerate(up_rad):
            if fix1s and i == 0 and ecp is None:
                rad = 0
            # Inversion of shell of the same spin
            if i % 2 != 0:
                factor = -1
            else:
                factor = +1
            fods_up.append(self.get_motif(no_points=up_pts[i], r=rad) * factor)
        for i, rad in enumerate(dn_rad):
            if fix1s and i == 0 and ecp is None:
                rad = 0
            # Inversion of shell of the same spin
            if i % 2 != 0:
                factor = -1
            else:
                factor = +1
            fods_dn.append(
                self.get_motif(no_points=dn_pts[i], r=rad) * factor * factor_dn
            )
        fods = [fods_up, fods_dn]
        return fods


def test_database():
    """
    Test database functionality.
    """
    data = Database()
    la = data.get_initial_FODs(species="Cl")
    for b, bubu in enumerate(la):
        for pos in bubu:
            for p in pos:
                if b == 0:
                    print("X", p[0], p[1], p[2])
                else:
                    print("He", p[0], p[1], p[2])


if __name__ == "__main__":
    test_database()
