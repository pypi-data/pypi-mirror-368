import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit

class TRTBinding:
    def __init__(self, idx,  name, shape, dtype, is_input=True):
        self.idx = idx
        self.name = name
        self.shape = shape
        self.dtype = dtype
        self.is_input = is_input

class TensorRTInferenceSession:
    def __init__(self, engine_path):
        self.engine_path = engine_path
        self.logger = trt.Logger(trt.Logger.WARNING)
        self.engine = self._load_engine()
        self.context = self.engine.create_execution_context()
        self.inputs = self._get_inputs()
        self.outputs = self._get_outputs()
        self.bindings = [None] * (len(self.inputs) + len(self.outputs))

    def _load_engine(self):
        with open(self.engine_path, "rb") as f:
            engine_data = f.read()
        self.runtime = trt.Runtime(self.logger)
        return self.runtime.deserialize_cuda_engine(engine_data)

    def _get_bindings(self, mode: trt.TensorIOMode):
        bindings = []
        for i in range(self.engine.num_io_tensors):
            name = self.engine.get_tensor_name(i)
            if self.engine.get_tensor_mode(name) == mode:
                shape = self.engine.get_tensor_shape(name)
                dtype = self.engine.get_tensor_dtype(name)
                bindings.append(TRTBinding(i, name, shape, dtype, is_input=(mode == trt.TensorIOMode.INPUT)))
        return bindings

    def _get_inputs(self):
        return self._get_bindings(trt.TensorIOMode.INPUT)

    def _get_outputs(self):
        return self._get_bindings(trt.TensorIOMode.OUTPUT)
    
    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs
    
    def run(self, output_names=None, input_feed=None):
        if output_names is None:
            output_names = [b.name for b in self.outputs]

        # Fast path: no slicing
        return self._infer(output_names=output_names, input_feed=input_feed)

    def _infer(self, output_names, input_feed):
        stream = cuda.Stream()
        device_mem = {}
        host_mem = {}
        bindings = [None] * self.engine.num_io_tensors

        # === Prepare inputs ===
        for binding in self.inputs:
            name = binding.name
            data = input_feed[name]
            shape = data.shape
            dtype = trt.nptype(binding.dtype)

            size = trt.volume(shape)
            h_mem = cuda.pagelocked_empty(size, dtype)
            d_mem = cuda.mem_alloc(h_mem.nbytes)

            np.copyto(h_mem, data.ravel())
            cuda.memcpy_htod_async(d_mem, h_mem, stream)

            idx = binding.idx
            bindings[idx] = int(d_mem)

            self.context.set_tensor_address(name, int(d_mem))

            device_mem[name] = d_mem
            host_mem[name] = h_mem

        # === Prepare outputs ===
        for binding in self.outputs:
            name = binding.name
            shape = binding.shape
            dtype = trt.nptype(binding.dtype)

            size = trt.volume(shape)
            h_mem = cuda.pagelocked_empty(size, dtype)
            d_mem = cuda.mem_alloc(h_mem.nbytes)

            idx = binding.idx
            bindings[idx] = int(d_mem)

            self.context.set_tensor_address(name, int(d_mem))

            device_mem[name] = d_mem
            host_mem[name] = h_mem

        # === Run inference ===
        self.context.execute_async_v3(stream_handle=stream.handle)

        # === Copy output ===
        outputs = []
        for name in output_names:
            cuda.memcpy_dtoh_async(host_mem[name], device_mem[name], stream)

        stream.synchronize()

        for name in output_names:
            shape = self.context.get_tensor_shape(name)
            data = np.array(host_mem[name]).reshape(shape)
            outputs.append(data)

        return outputs
