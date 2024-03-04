import cupy as cp
import time

N = 900000000

a1 = cp.random.rand(N).astype(cp.float32)
b1 = cp.random.rand(N).astype(cp.float32)

start_time = time.time()
c=a1+b1
cp.cuda.Stream.null.synchronize()
end_time = time.time()
gpu_time = end_time - start_time

print("GPU execution time ",gpu_time)
