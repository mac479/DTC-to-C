from dtctc import Converter
from dtctc import TestMaker

#Creates model and tester code without compiling it in a seperate directory.
Converter.DTCTC_FromPKL("phases-model.pkl", "phases-scaler.pkl", ['cycles', 'instr', 'llc_accesses', 'llc_misses', 'bus_accesses'], "DTCTC_Demo_1", "Code")
TestMaker.MakeTest(['cycles', 'instr', 'llc_accesses', 'llc_misses', 'bus_accesses'], False, "DTCTC_Demo_1", "Code")

#Creates model and tester code in current directory and compiles it into a program that can be run from the command line.
#To run the program use: ./DTCTC_Demo_2_Tester master_test_reorg.csv
Converter.DTCTC_FromPKL("phases-model.pkl", "phases-scaler.pkl", ['cycles', 'instr', 'llc_accesses', 'llc_misses', 'bus_accesses'], "DTCTC_Demo_2")
TestMaker.MakeTest(['cycles', 'instr', 'llc_accesses', 'llc_misses', 'bus_accesses'], True, "DTCTC_Demo_2")