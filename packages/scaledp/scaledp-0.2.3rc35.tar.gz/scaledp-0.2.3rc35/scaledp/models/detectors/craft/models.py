import multiprocessing

import onnxruntime
from crafter.resources import res


class Craftnet:
    def __init__(self, onnx_path=None):
        onnx_path = "/home/mykola/PycharmProjects/scaledp/tests/model.quant.onnx"

        num_cores = multiprocessing.cpu_count()

        session_options = onnxruntime.SessionOptions()
        #session_options.intra_op_num_threads = num_cores  # For parallelism inside ops
        #session_options.inter_op_num_threads = num_cores  # For parallelism across ops
        #session_options.execution_mode = onnxruntime.ExecutionMode.ORT_PARALLEL
        #session_options.graph_optimization_level =
        # onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
        if onnx_path is None:
            onnx_path = res("craftnet.onnx")
        self._onnx_session = onnxruntime.InferenceSession(onnx_path, sess_options=session_options)

    def __call__(self, image):
        return self._onnx_session.run(None, {"image": image})


class Refinenet:
    def __init__(self, onnx_path=None):
        if onnx_path is None:
            onnx_path = res("refinenet.onnx")
        self._onnx_session = onnxruntime.InferenceSession(onnx_path)

    def __call__(self, y, feature):
        return self._onnx_session.run(None, {"y": y, "feature": feature})[0]
