import numpy as np
from scipy import signal

res = np.correlate([1, 2, 3], [0, 1, 0.5])
print(res)

res = np.correlate([1, 2, 3], [0, 1, 0.5], mode="same")
print(res)

res = np.correlate([1, 2, 3], [0, 1, 0.5], mode="full")
print(res)

res = np.correlate([1, 2, 3, 4, 5], [2, 3])
print("here", res)

res = np.correlate([1, 2, 3, 4], [1, 2, 3, 4])
print(res)
res = np.correlate([1, 2, 3, 4], [2, 3, 4, 5])
print(res)


data_length = 8192

a = np.random.randn(data_length)
b = np.zeros(data_length * 2)

b[int(data_length/2): int(data_length/2+data_length)] = a # This works for data_length being even

# Do an array flipped convolution, which is a correlation.
c = signal.fftconvolve(b, a[::-1], mode='valid')

# Use np.correlate for comparison
d = np.correlate(a, a, mode='same')

# c will be exactly the same as d, except for the last sample (which 
# completes the symmetry)
print(np.allclose(c[:-1], d)) # Should be True