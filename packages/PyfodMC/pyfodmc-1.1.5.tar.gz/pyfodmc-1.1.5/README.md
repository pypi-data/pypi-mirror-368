# PyfodMC - Python Fermi-orbital descriptor Monte-Carlo 
[![license](https://img.shields.io/badge/license-APACHE2-green)](https://www.apache.org/licenses/LICENSE-2.0)
[![language](https://img.shields.io/badge/language-Python3-blue)](https://www.python.org/)
[![version](https://img.shields.io/badge/version-1.1.3-lightgrey)](https://gitlab.com/opensic/PyfodMC/-/blob/main/README.md)

The Python Fermi-orbital descriptor Monte-Carlo (PyfodMC) is a Python code for      
the determination of Fermi-orbital descriptors (FODs) for atomic, molecular,     
and periodic systems. It follows a simple input structure, where users primarily    
define the bond patterns between the atoms in the structure. Everything else     
is handled internally through PyfodMC. Additional options for greater flexibility     
have also been added, like the explicit definition of lone FODs. Further options     
include the definiton of charge, whether to exchange the up and the dn channel,    
the definition of alternate electronic configurations, and the removal of core FODs    
for each atom.    


PyfodMC is the successor of the Fermi-orbital descriptor Monte-Carlo (fodMC) code.      
PyfodMC is based on fodMC, version 1.2.2, but has been written exclusively in Python.      
Furthermore, several improvements over the original fodMC code have been added for       
increased robustness and reproducibility.     
As such, the support for the original fodMC code will stop, and support for the PyfodMC    
code will start.    



## Installation
Using pip
```bash 
$ pip3 install PyfodMC
```
or install locally
```bash 
$ git clone https://gitlab.com/opensic/PyfodMC.git
$ cd PyfodMC
$ pip3 install -e .
```

Examples can be found in the examples folder.


## Citation
For publications, please consider citing the following articles        

- **Interpretation and automatic generation of Fermi-orbital descriptors**         
    [S. Schwalbe et al., J. Comput. Chem. 40, 2843-2857, 2019](https://onlinelibrary.wiley.com/doi/full/10.1002/jcc.26062)


# ATTENTION
While the PyfodMC can create FODs for      
any system, we do not recommend using       
guesses for systems containing transition metals.
