import os


def find_onnx_lib_path():
    curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
    horizon_onnx_path = os.path.join(curr_path, "../ir/horizon_onnx/")
    cmake_build_path = os.path.join(curr_path, "../../../build/")

    lib_path = [horizon_onnx_path, cmake_build_path]
    lib_path = [os.path.join(p, "onnx_cpp2py_export.so") for p in lib_path]
    lib_path = [p for p in lib_path if os.path.exists(p) and os.path.isfile(p)]

    if len(lib_path) == 0:
        raise RuntimeError("Cannot find the onnx_cpp2py_export.so library.")

    return lib_path[0]


def find_onnxruntime_lib_path():
    curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
    horizon_onnxruntime_path = os.path.join(curr_path, "../horizon_onnxruntime/")
    cmake_build_path = os.path.join(curr_path, "../../../build/onnxruntime/")

    lib_path = [horizon_onnxruntime_path, cmake_build_path]
    lib_path = [os.path.join(p, "onnxruntime_pybind11_state.so") for p in lib_path]
    lib_path = [p for p in lib_path if os.path.exists(p) and os.path.isfile(p)]

    if len(lib_path) == 0:
        raise RuntimeError("Cannot find the onnxruntime_pybind11_state.so library.")

    return lib_path[0]


if __name__ == "__main__":
    lib_onnx_path = find_onnx_lib_path()
    lib_onnxruntime_path = find_onnxruntime_lib_path()
    print(lib_onnx_path)
    print(lib_onnxruntime_path)
