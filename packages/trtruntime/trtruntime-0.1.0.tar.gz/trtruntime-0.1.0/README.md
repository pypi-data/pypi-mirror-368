# trtruntime

`trtruntime` is a lightweight Python package that provides a TensorRT inference runtime similar in API style to [onnxruntime](https://onnxruntime.ai/). It allows easy loading and running of TensorRT engines with a clean and simple interface.

## Features

- Load serialized TensorRT engine files (`*.engine`) or plan files (`*.plan`)
- Automatically handle CUDA memory bindings and streams
- Simple API modeled after onnxruntime's `InferenceSession`
- Supports querying input and output tensor metadata
- Compatible with TensorRT, PyCUDA, and NumPy

## Installation

```bash
pip install trtruntime
````

> **Note:** You need to have TensorRT and PyCUDA installed on your system.

## Usage

```python
import numpy as np
from trtruntime import InferenceSession

# Create inference session with your TensorRT engine file
sess = InferenceSession("model.engine")

# Prepare input feed as dictionary {input_name: numpy_array}
input_feed = {
    "input_1": np.random.rand(1, 3, 224, 224).astype(np.float32),
}

# Run inference
outputs = sess.run(output_names=None, input_feed=input_feed)

# outputs is a list of numpy arrays corresponding to requested outputs
print(outputs)
```