from collections import namedtuple

Math = namedtuple("Math", ("ADD", "SUB"))
Phys = namedtuple("Phys", ("NEWTON", "EINSTEIN"))
Intel = namedtuple("Intel", ("MATH", "PHYS"))
Cap = namedtuple("Cap", ("INTEL",))
CAP = Cap(Intel(Math("addition", "subtraction"), Phys("Newton", "Einstein")))
# CAP
# Out[8]:
#   Cap(INTEL=Intel(MATH=Math(ADD='addition', SUB='subtraction'), PHYS=Phys(NEWTON='Newton', EINSTEIN='Einstein')))
# CAP.INTEL
# Out[9]: Intel(MATH=Math(ADD='addition', SUB='subtraction'), PHYS=Phys(NEWTON='Newton', EINSTEIN='Einstein'))
# type(CAP.INTEL)
# Out[10]: __main__.Intel
# CAP.INTEL.MATH
# Out[11]: Math(ADD='addition', SUB='subtraction')
# CAP.INTEL.MATH.ADD
# Out[12]: 'addition'
# CAP.INTEL.MATH.ADD == "addition"
# Out[13]: True
# CAP.INTEL.PHYS.EINSTEIN == "addition"
# Out[14]: False
# CAP.INTEL.PHYS.EINSTEIN == "Einstein"
# Out[15]: True
