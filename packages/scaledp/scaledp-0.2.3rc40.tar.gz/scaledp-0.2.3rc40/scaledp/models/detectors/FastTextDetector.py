import logging
from types import MappingProxyType
from typing import Any

import numpy as np
import torch
from doctr.models import detection_predictor
from pyspark import keyword_only

from scaledp.enums import Device
from scaledp.models.detectors.BaseDetector import BaseDetector
from scaledp.params import HasBatchSize, HasDevice
from scaledp.schemas.Box import Box
from scaledp.schemas.DetectorOutput import DetectorOutput


class FastTextDetector(BaseDetector, HasDevice, HasBatchSize):
    _model = None
    defaultParams = MappingProxyType(
        {
            "inputCol": "image",
            "outputCol": "boxes",
            "keepInputData": False,
            "scaleFactor": 1.0,
            "scoreThreshold": 0.7,
            "batchSize": 2,
            "device": Device.CPU,
            "partitionMap": False,
            "numPartitions": 0,
            "pageCol": "page",
            "pathCol": "path",
            "propagateError": False,
        },
    )

    @keyword_only
    def __init__(self, **kwargs: Any) -> None:
        super(FastTextDetector, self).__init__()
        self._setDefault(**self.defaultParams)
        self._set(**kwargs)
        self.get_model({k.name: v for k, v in self.extractParamMap().items()})

    @classmethod
    def get_model(cls, params):
        if cls._model:
            return cls._model
        device = "cuda" if int(params["device"]) == Device.CUDA.value else "cpu"

        # Initialize the fast text detection model from doctr
        cls._model = detection_predictor(
            arch="fast_tiny",  # Use DBNet with ResNet50 backbone
            pretrained=True,     # Use pretrained weights
            assume_straight_pages=True,
        ).to(device)

        return cls._model
    @classmethod
    def call_detector(cls, images, params):
        model = cls.get_model(params)
        device = "cuda" if int(params["device"]) == Device.CUDA.value else "cpu"
        results = []

        for image, image_path in images:
            try:
                # Convert PIL image to numpy array if needed
                if not isinstance(image, np.ndarray):
                    image = np.array(image)

                # Normalize image
                if image.max() > 1:
                    image = image / 255.

                # Get predictions
                out = model([[image]])

                # Extract boxes from predictions
                # doctr returns relative coordinates (0-1)
                predictions = out[0]

                # Convert doctr boxes to Box objects
                # Scale relative coordinates to absolute coordinates
                height, width = image.shape[:2]
                box_objects = []
                for pred in predictions:
                    # Get coordinates
                    x_min, y_min = pred[0]  # Top-left
                    x_max, y_max = pred[2]  # Bottom-right

                    # Convert to absolute coordinates
                    abs_coords = [
                        int(x_min * width),   # x_min
                        int(y_min * height),  # y_min
                        int(x_max * width),   # x_max
                        int(y_max * height),   # y_max
                    ]

                    box_objects.append(Box.from_bbox(abs_coords))
                results.append(
                    DetectorOutput(
                        path=image_path,
                        type="fast",
                        bboxes=box_objects,
                        exception="",
                    ),
                )

            except Exception as e:
                logging.exception(e)
                results.append(
                    DetectorOutput(
                        path=image_path,
                        type="fast",
                        bboxes=[],
                        exception=f"FastTextDetector error: {e!s}",
                    ),
                )

        if device == "cuda":
            torch.cuda.empty_cache()

        return results


# from pyspark.ml.param.shared import HasInputCol, HasOutputCol
# from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable, JavaMLReadable, JavaMLWritable
# from pyspark.ml.wrapper import JavaTransformer
# from pyspark.ml.param import Param, Params, TypeConverters
# from pyspark.sql.types import *
# from pyspark import keyword_only
# from pathlib import Path
#
# import json
# import time
# import logging
# import traceback
#
# import pyspark.sql.functions as f
# import torch
# from pyspark.ml import Transformer
# from cleverdoc.schemas import Box, Image
# from cleverdoc.params import HasKeepInput
#
#
#
# class TextDetector(Transformer, HasInputCol, HasOutputCol,
#                           HasKeepInput, DefaultParamsReadable, DefaultParamsWritable, JavaMLReadable, JavaMLWritable):
#     name = "TextDetector"
#
#     scoreThreshold = Param(Params._dummy(), "scoreThreshold",
#                            "Score threshold above which detection is considered as reliable",
#                            typeConverter=TypeConverters.toFloat)
#     textThreshold = Param(Params._dummy(), "textThreshold",
#                           "Threshold for the region(text) score. The region score represents \
#                           the probability that the given pixel is the center of the character",
#                           typeConverter=TypeConverters.toFloat)
#     linkThreshold = Param(Params._dummy(), "linkThreshold",
#                           "Threshold for the the link(affinity) score. The link score represents \
#                           the center probability of the space between adjacent characters",
#                           typeConverter=TypeConverters.toFloat)
#     sizeThreshold = Param(Params._dummy(), "sizeThreshold",
#                           "Threshold for height of the detected regions",
#                           typeConverter=TypeConverters.toInt)
#     withRefiner = Param(Params._dummy(), "withRefiner",
#                         "Enable to run refiner net as postprocessing step.",
#                         typeConverter=TypeConverters.toBoolean)
#     width = Param(Params._dummy(), "width",
#                   "Width of the desired input image. Image will be resized to this width.",
#                   typeConverter=TypeConverters.toInt)
#
#     mergeIntersects = Param(Params._dummy(), "mergeIntersects",
#                             "Merge intersects boxes.",
#                             typeConverter=TypeConverters.toBoolean)
#
#     useGPU = Param(Params._dummy(), "useGPU",
#                    "Try to use the GPU if available.",
#                    typeConverter=TypeConverters.toBoolean)
#
#     usePandasUdf = Param(Params._dummy(), "usePandasUdf",
#                          "Use Pandas Udf.",
#                          typeConverter=TypeConverters.toBoolean)
#
#     @keyword_only
#     def __init__(self):
#         super(TextDetector, self).__init__()
#
#         self._setDefault(scoreThreshold=0.7)
#         self._setDefault(textThreshold=0.4)
#         self._setDefault(linkThreshold=0.4)
#         self._setDefault(width=1280)
#         self._setDefault(sizeThreshold=-1)
#         self._setDefault(mergeIntersects=True)
#         self._setDefault(forceProcessing=True)
#         self._setDefault(keepInput=True)
#         self._setDefault(useGPU=False)
#         self._setDefault(usePandasUdf=False)
#
#
#     def setInputCol(self, value):
#         """
#         Sets the value of :py:attr:`inputCol`.
#         """
#         return self._set(inputCol=value)
#
#     def setOutputCol(self, value):
#         """
#         Sets the value of :py:attr:`outputCol`.
#         """
#         return self._set(outputCol=value)
#
#     @staticmethod
#     def get_prediction(
#             image,
#             craft_net,
#             refine_net=None,
#             text_threshold: float = 0.7,
#             link_threshold: float = 0.4,
#             low_text: float = 0.4,
#             cuda: bool = False,
#             long_size: int = 1280,
#             poly: bool = True,
#     ):
#
#         import cv2
#
#         from craft_text_detector import craft_utils
#         from craft_text_detector import image_utils
#         from craft_text_detector import torch_utils
#         # pylint: disable=pointless-string-statement
#         """
#         Arguments:scoreThreshold
#             image: path to the image to be processed or numpy array or PIL image
#             output_dir: path to the results to be exported
#             craft_net: craft net model
#             refine_net: refine net model
#             text_threshold: text confidence threshold
#             link_threshold: link confidence threshold
#             low_text: text low-bound score
#             cuda: Use cuda for inference
#             canvas_size: image size for inference
#             long_size: desired longest image size for inference
#             poly: enable polygon type
#         Output:
#             {"masks": lists of predicted masks 2d as bool array,
#              "boxes": list of coords of points of predicted boxes,
#              "boxes_as_ratios": list of coords of points of predicted boxes as ratios of image size,
#              "polys_as_ratios": list of coords of points of predicted polys as ratios of image size,
#              "heatmaps": visualizations of the detected characters/links,
#              "times": elapsed times of the sub modules, in seconds}
#         """
#         t0 = time.time()
#
#         # read/convert image
#         image = image_utils.read_image(image)
#
#         # resize
#         img_resized, target_ratio, size_heatmap = image_utils.resize_aspect_ratio(
#             image, long_size, interpolation=cv2.INTER_LINEAR
#         )
#         ratio_h = ratio_w = 1 / target_ratio
#         resize_time = time.time() - t0
#         t0 = time.time()
#
#         # preprocessing
#         x = image_utils.normalizeMeanVariance(img_resized)
#         x = torch_utils.from_numpy(x).permute(2, 0, 1)  # [h, w, c] to [c, h, w]
#         x = torch_utils.Variable(x.unsqueeze(0))  # [c, h, w] to [b, c, h, w]
#         if cuda:
#             x = x.cuda()
#         preprocessing_time = time.time() - t0
#         t0 = time.time()
#
#         # forward pass
#         with torch_utils.no_grad():
#             y, feature = craft_net(x)
#         craftnet_time = time.time() - t0
#         t0 = time.time()
#
#         # make score and link map
#         score_text = y[0, :, :, 0].cpu().data.numpy()
#         score_link = y[0, :, :, 1].cpu().data.numpy()
#
#         # refine link
#         if refine_net is not None:
#             with torch_utils.no_grad():
#                 y_refiner = refine_net(y, feature)
#             score_link = y_refiner[0, :, :, 0].cpu().data.numpy()
#         refinenet_time = time.time() - t0
#         t0 = time.time()
#
#         # Post-processing
#         boxes, polys = craft_utils.getDetBoxes(
#             score_text, score_link, text_threshold, link_threshold, low_text, poly
#         )
#
#         # coordinate adjustment
#         boxes = craft_utils.adjustResultCoordinates(boxes, ratio_w, ratio_h)
#
#         postprocess_time = time.time() - t0
#
#         times = {
#             "resize_time": resize_time,
#             "preprocessing_time": preprocessing_time,
#             "craftnet_time": craftnet_time,
#             "refinenet_time": refinenet_time,
#             "postprocess_time": postprocess_time,
#         }
#
#         return {
#             "boxes": boxes,
#             "times": times,
#         }
#
#     @staticmethod
#     def udf(image, model_path, params, exception):
#         logging.info("Run ImageTextDetectorV2")
#
#         try:
#
#             params = json.loads(params)
#             use_cuda = torch.cuda.is_available() and params.get("useGPU")
#
#             from craft_text_detector import (
#                 load_craftnet_model,
#                 load_refinenet_model,
#                 # get_prediction,
#                 empty_cuda_cache
#             )
#             # read image
#             image = to_opencv_image(image)
#
#             # load models
#             refine_net = None
#             if params.get("withRefiner"):
#                 refine_net = load_refinenet_model(cuda=use_cuda,
#                                                   weight_path=str(Path(model_path, "craft_refiner_CTW1500.pth")))
#             craft_net = load_craftnet_model(cuda=use_cuda, weight_path=str(Path(model_path, "craft_mlt_25k.pth")))
#
#             long_size = int(params.get("width") if params.get("width") != 0 else 1280)
#             # perform prediction
#             prediction_result = ImageTextDetectorV2.get_prediction(
#                 image=image,
#                 craft_net=craft_net,
#                 refine_net=refine_net,
#                 text_threshold=params.get("scoreThreshold"),
#                 link_threshold=params.get("linkThreshold"),
#                 low_text=params.get("textThreshold"),
#                 cuda=use_cuda,
#                 long_size=long_size,
#                 poly=False
#             )
#
#             rects = [Rectangle.from_box(box) for box in prediction_result["boxes"]]
#             character_height = get_size(rects, lambda x: x.get_height())
#
#             size_threshold = params.get("sizeThreshold")
#             if params.get("sizeThreshold") == -1:
#                 size_threshold = int(character_height / 2)
#             line_tolerance = int(character_height / 2)
#
#             rects = list(filter(lambda x: x.get_height() > size_threshold, rects))
#
#             if params.get("mergeIntersects"):
#                 rects = Rectangle.merge_intersects(rects, line_tolerance)
#
#             regions = [rect.to_region() for rect in rects]
#         except Exception as error:
#             logging.exception(error)
#             regions = []
#             exception = "ImageTextDetectorV2: Error during text detection: " + str(traceback.format_exc()) + str(
#                 exception)
#         finally:
#             if use_cuda:
#                 empty_cuda_cache()
#
#         return (regions, exception)
#
#     @staticmethod
#     def pandas_udf(images, model_path, params, exception):
#         logging.info("Run ImageTextDetectorV2")
#
#         params = json.loads(params[0])
#         use_cuda = torch.cuda.is_available() and params.get("useGPU")
#
#         exception = exception[0]
#
#         import pandas as pd
#
#         from craft_text_detector import (
#             load_craftnet_model,
#             load_refinenet_model,
#             empty_cuda_cache
#         )
#
#         # load models
#         refine_net = None
#         if params.get("withRefiner"):
#             refine_net = load_refinenet_model(cuda=use_cuda,
#                                               weight_path=str(Path(model_path[0], "craft_refiner_CTW1500.pth")))
#         craft_net = load_craftnet_model(cuda=use_cuda, weight_path=str(Path(model_path[0], "craft_mlt_25k.pth")))
#
#         long_size = int(params.get("width") if params.get("width") != 0 else 1280)
#
#         res = []
#         for i, image in images.iterrows():
#             logging.info(f"ImageTextDetectorV2: process image {i}")
#             try:
#                 # read image
#                 image = to_opencv_image(Image(**image))
#                 prediction_result = ImageTextDetectorV2.get_prediction(
#                     image=image,
#                     craft_net=craft_net,
#                     refine_net=refine_net,
#                     text_threshold=params.get("scoreThreshold"),
#                     link_threshold=params.get("linkThreshold"),
#                     low_text=params.get("textThreshold"),
#                     cuda=use_cuda,
#                     long_size=long_size,
#                     poly=False
#                 )
#
#                 rects = [Rectangle.from_box(box) for box in prediction_result["boxes"]]
#                 character_height = get_size(rects, lambda x: x.get_height())
#
#                 size_threshold = params.get("sizeThreshold")
#                 if params.get("sizeThreshold") == -1:
#                     size_threshold = int(character_height / 2)
#                 line_tolerance = int(character_height / 2)
#
#                 rects = list(filter(lambda x: x.get_height() > size_threshold, rects))
#
#                 if params.get("mergeIntersects"):
#                     rects = Rectangle.merge_intersects(rects, line_tolerance)
#
#                 regions = [rect.to_region() for rect in rects]
#
#             except Exception as error:
#                 logging.exception(error)
#                 regions = []
#                 exception = "ImageToTextV2: Error during text detection: " + traceback.format_exc() + exception
#             res.append(json.dumps({params['outputCol']: regions, "exception": exception}))
#         if use_cuda:
#             empty_cuda_cache()
#
#         return pd.Series(res)
#
#     def _transform(self, dataset):
#
#         out_col = self.getOutputCol()
#
#         if self.getInputCol() not in dataset.columns:
#             uid_ = self.uid
#             inp_col = self.getInputCol()
#             raise ValueError(f"""Missing input column in {uid_}: Column '{inp_col}' is not present.
#         Make sure such transformer exist in your pipeline,
#         with the right output names.""")
#
#         image_col = self.getInputCol()
#
#         params = json.dumps({k.name: v for k, v in self.extractParamMap().items()})
#
#         output_schema = StructType([StructField(out_col, CoordinateSchema, True),
#                                     StructField('exception', StringType(), True)])
#
#         if "exception" not in dataset.columns:
#             dataset = dataset.withColumn("exception", f.lit(""))
#
#         if self.getOrDefault(self.usePandasUdf):
#             sel_cols_input = [f.from_json(f.pandas_udf(ImageTextDetectorV2.pandas_udf, StringType())(image_col,
#                                                                                                      f.lit(
#                                                                                                          self.getModelPath()),
#                                                                                                      f.lit(params),
#                                                                                                      "exception"),
#                                           output_schema).alias("tmp_result")] + \
#                              [f.col(x) for x in dataset.columns if
#                               x not in (image_col, "exception")]
#         else:
#             sel_cols_input = [self.exploding_wrap(f.udf(ImageTextDetectorV2.udf, output_schema))(image_col,
#                                                                                                  f.lit(
#                                                                                                      self.getModelPath()),
#                                                                                                  f.lit(params),
#                                                                                                  "exception").alias(
#                 "tmp_result")] + \
#                              [f.col(x) for x in dataset.columns if
#                               x not in (image_col, "exception")]
#
#         sel_cols = [f.col("tmp_result.*")] + \
#                    [f.col(x) for x in dataset.columns if x not in (image_col, "exception")]
#
#         if self.getOrDefault(self.keepInput):
#             sel_cols_input.append(f.col(image_col))
#             sel_cols.append(f.col(image_col))
#
#         result = dataset.select(*sel_cols_input) \
#             .select(*sel_cols)
#         if not self.getOrDefault(self.keepInput):
#             result = result.drop(image_col)
#         return result
#
#     def setTextThreshold(self, value):
#         """
#         Sets the value of :py:attr:`inputCol`.
#         """
#         return self._set(textThreshold=value)
#
#     def setLinkThreshold(self, value):
#         """
#         Sets the value of :py:attr:`inputCol`.
#         """
#         return self._set(linkThreshold=value)
#
#     def setScoreThreshold(self, value):
#         """
#         Sets the value of :py:attr:`inputCol`.
#         """
#         return self._set(scoreThreshold=value)
#
#     def setWithRefiner(self, value):
#         """
#         Sets the value of :py:attr:`inputCol`.
#         """
#         return self._set(withRefiner=value)
#
#     def setUseGPU(self, value):
#         """
#         Sets the value of :py:attr:`useGPU`.
#         """
#         return self._set(useGPU=value)
#
#     def setSizeThreshold(self, value):
#         """
#         Sets the value of :py:attr:`sizeThreshold`.
#         """
#         return self._set(sizeThreshold=value)
#
#     def setWidth(self, value):
#         """
#         Sets the value of :py:attr:`inputCol`.
#         """
#         return self._set(width=value)
#
#     def setMergeIntersects(self, value):
#         """
#         Sets the value of :py:attr:`mergeIntersects`.
#         """
#         return self._set(mergeIntersects=value)
#
#     def setUsePandasUdf(self, value):
#         """
#         Sets the value of :py:attr:`spaceWidth`.
#         """
#         return self._set(usePandasUdf=value)
