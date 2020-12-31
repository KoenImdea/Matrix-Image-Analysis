#access2thematrix is to load directly omicron matrix data
import access2thematrix_test_printall_b as access2thematrix_test
import spiepy, spiepy.demo
import os, re
"""
///To use the object im with the SPIEPy library,
im must change from access2theMatrix Image Structure object to
SPIEPy Image Structure object.
"""


matrix_data = access2thematrix_test.MtrxData()
data_file = r'Y:\Raw_Data\2020-\2020\2020.07.30_LHe_Autip_TetraPPyr_Dy_Au111(CIII)_160C_2\20200731-STM_Spectroscopy-Ag111_C60_Autip_LN2--122_10.Z_mtrx'

traces, message = matrix_data.open(data_file)
print(message)
print(traces)
#print(matrix_data.x_points)
im, message = matrix_data.select_image(traces[0])
print(message)
print(len(im.data[1]))
#print(cu.x_points)
print(cu.data[0][:])
