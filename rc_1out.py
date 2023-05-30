import raw_read

from matplotlib import pyplot
import numpy as np
from sklearn.metrics import mean_squared_error
[arrs1,plots]=raw_read.rawread('output_tree/rawfile0.raw')
# time
stime = arrs1[0]
res_out = arrs1[1:-1]
x=res_out.T
temp = np.linalg.pinv(x)
vref=np.load("output_tree/ref.npy")
vref=vref.T
w_out = np.load("output_tree/w_out.npy")
outlayer=1

readout=np.zeros((res_out.shape[1],outlayer))
for t in range(0, res_out.shape[1]):
    readout[t] = np.dot(res_out[:, t], w_out)


error = abs(readout[1:] - vref[1:])
error1= mean_squared_error(readout[1:], vref[1:],squared=False)


print(error1)

pyplot.figure(figsize=(10,6))
pyplot.subplots_adjust(wspace =0, hspace =0.2)
pyplot.plot(stime[1:],vref[1:],'r')
pyplot.plot(stime[1:],readout[1:],'mediumspringgreen')

pyplot.xlabel("Time (s)",fontsize=15)
pyplot.show()