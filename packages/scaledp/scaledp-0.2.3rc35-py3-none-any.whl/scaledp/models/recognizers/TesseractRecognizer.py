from types import MappingProxyType
from typing import Any

import numpy as np
from pyspark import keyword_only
from pyspark.ml.param import Param, Params, TypeConverters

from scaledp.params import CODE_TO_LANGUAGE, LANGUAGE_TO_TESSERACT_CODE
from scaledp.schemas.Box import Box
from scaledp.schemas.Document import Document

from ...enums import OEM, PSM, TessLib
from .BaseRecognizer import BaseRecognizer


class TesseractRecognizer(BaseRecognizer):
    """
    Run Tesseract text recognition on images.
    """

    oem = Param(
        Params._dummy(),
        "oem",
        "OCR engine mode. Defaults to :attr:`OEM.DEFAULT`.",
        typeConverter=TypeConverters.toInt,
    )

    tessDataPath = Param(
        Params._dummy(),
        "tessDataPath",
        "Path to tesseract data folder.",
        typeConverter=TypeConverters.toString,
    )

    tessLib = Param(
        Params._dummy(),
        "tessLib",
        "The desired Tesseract library to use. Defaults to :attr:`TESSEROCR`",
        typeConverter=TypeConverters.toInt,
    )

    defaultParams = MappingProxyType(
        {
            "inputCols": ["image", "boxes"],
            "outputCol": "text",
            "keepInputData": False,
            "scaleFactor": 1.0,
            "scoreThreshold": 0.5,
            "oem": OEM.DEFAULT,
            "lang": ["eng"],
            "lineTolerance": 0,
            "keepFormatting": False,
            "tessDataPath": "/usr/share/tesseract-ocr/5/tessdata/",
            "tessLib": TessLib.PYTESSERACT,
            "partitionMap": False,
            "numPartitions": 0,
            "pageCol": "page",
            "pathCol": "path",
        },
    )

    @keyword_only
    def __init__(self, **kwargs: Any) -> None:
        super(TesseractRecognizer, self).__init__()
        self._setDefault(**self.defaultParams)
        self._set(**kwargs)

    @classmethod
    def call_pytesseract(cls, images, boxes, params):
        raise NotImplementedError("Pytesseract version not implemented yet.")

    @staticmethod
    def getLangTess(params):
        return "+".join(
            [
                LANGUAGE_TO_TESSERACT_CODE[CODE_TO_LANGUAGE[lang]]
                for lang in params["lang"]
            ],
        )

    @classmethod
    def call_pytesseract(cls, images, detected_boxes, params):  # pragma: no cover
        import cv2
        from tesserocr import PyTessBaseAPI

        results = []
        box_id = 0

        for (image, image_path), detected_box in zip(images, detected_boxes):
            # api.SetImage(image)

            boxes = []
            texts = []

            image_np = np.array(image)

            lang = cls.getLangTess(params)
            with PyTessBaseAPI(
                path=params["tessDataPath"],
                psm=PSM.SINGLE_WORD,
                oem=params["oem"],
                lang=lang,
            ) as api:
                api.SetVariable("debug_file", "ocr.log")

                for b in detected_box.bboxes:
                    box = b
                    if isinstance(box, dict):
                        box = Box(**box)
                    if not isinstance(box, Box):
                        box = Box(**box.asDict())

                    # Scale the bounding box first (if params["scaleFactor"] is used)
                    # Note: 'padding' in box.scale might add border, consider its effect on angle if it's applied after rotation
                    # For simplicity, assuming scaled_box gives the final desired dimensions and position.
                    scaled_box = box.scale(params["scaleFactor"], padding=10)

                    center_x = scaled_box.x + scaled_box.width / 2
                    center_y = scaled_box.y + scaled_box.height / 2
                    center_tuple = (float(center_x), float(center_y))

                    size_tuple = (float(scaled_box.width), float(scaled_box.height))

                    if scaled_box.angle == 90:
                        scaled_box.angle = -90

                    rect = (center_tuple, size_tuple, scaled_box.angle)

                    src_pts = cv2.boxPoints(rect).astype("float32")

                    # Define the destination points for the output cropped image
                    # This will be an upright rectangle with dimensions (width x height)
                    output_width = int(scaled_box.width)
                    output_height = int(scaled_box.height)

                    # # dst_pts order: Bottom-Left, Top-Left, Top-Right, Bottom-Right to match cv2.boxPoints
                    dst_pts = np.array(
                        [
                            [0, output_height - 1],
                            [0, 0],
                            [output_width - 1, 0],
                            [output_width - 1, output_height - 1],
                        ],
                        dtype="float32",
                    )
                    try:
                        M_transform = cv2.getPerspectiveTransform(src_pts, dst_pts)
                    except cv2.error as e:
                        print(
                            f"Error calculating perspective transform for box {box}: {e}. Skipping.",
                        )
                        continue

                    try:
                        cropped_rotated_as_is_np = cv2.warpPerspective(
                            image_np,
                            M_transform,
                            (output_width, output_height),
                            flags=cv2.INTER_CUBIC,
                            borderMode=cv2.BORDER_REPLICATE,
                        )
                    except cv2.error as e:
                        print(
                            f"Error during perspective warp for box {box}: {e}. Skipping.",
                        )
                        continue

                    if (
                        cropped_rotated_as_is_np.shape[0] == 0
                        or cropped_rotated_as_is_np.shape[1] == 0
                    ):
                        print(
                            f"Warning: Cropped image 'as is' for box {box} is empty. Skipping.",
                        )
                        continue

                    final_image_for_ocr_np = None
                    if cropped_rotated_as_is_np.ndim == 3:
                        if cropped_rotated_as_is_np.shape[2] == 4:
                            final_image_for_ocr_np = cv2.cvtColor(
                                cropped_rotated_as_is_np,
                                cv2.COLOR_RGBA2RGB,
                            )
                        elif cropped_rotated_as_is_np.shape[2] == 3:
                            final_image_for_ocr_np = cropped_rotated_as_is_np
                        else:
                            print(
                                f"Warning: Unexpected channels {cropped_rotated_as_is_np.shape[2]}. Converted to grayscale.",
                            )
                            final_image_for_ocr_np = cv2.cvtColor(
                                cropped_rotated_as_is_np,
                                cv2.COLOR_BGR2GRAY,
                            )
                    elif cropped_rotated_as_is_np.ndim == 2:
                        final_image_for_ocr_np = cropped_rotated_as_is_np
                    else:
                        print(
                            f"Error: Cropped image has unexpected dimensions: {cropped_rotated_as_is_np.shape}. Cannot process.",
                        )
                        continue
                    # --- Prepare the "as is" cropped image for OCR API ---
                    # Tesseract/Leptonica often prefers 8-bit grayscale or 24-bit RGB.
                    # Still need to handle potential format issues like 32-bit RGBA.

                    # Now, send this cropped_rotated_image to your OCR API
                    # The specific method will depend on your 'api' object.
                    # Assuming your 'api' has a method to set an image directly (like a PIL Image or NumPy array)
                    # You might need to convert `cropped_rotated_image` to a compatible format.
                    from PIL import Image

                    pil_image = Image.fromarray(final_image_for_ocr_np)
                    api.SetImage(pil_image)
                    api.Recognize(0)
                    box.text = api.GetUTF8Text()
                    # print(box.text)
                    box.conf = api.MeanTextConf()

                    # Example for Tesseract (pytesseract):
                    # If your `api` is a pytesseract-like wrapper, it might have an `image_to_string` method
                    # import pytesseract
                    # from PIL import Image
                    #
                    # pil_image = Image.fromarray(final_image_for_ocr_np)
                    #
                    #
                    # data = pytesseract.image_to_data(
                    #     pil_image,
                    #     lang=cls.getLangTess(params),
                    #     config="--psm 8",
                    #     output_type=pytesseract.Output.DICT,
                    # )
                    # # Get text and confidence from the first text element (if exists)
                    #
                    # if len(data["text"]) > 0:
                    #     text_entries = []
                    #     scores = []
                    #     for i in range(len(data["text"])):
                    #         if data["level"][i] == 5 and data["text"][i].strip():
                    #             text_entries.append(data["text"][i].replace("\n", ""))
                    #             scores.append(
                    #                 (
                    #                     float(data["conf"][i]) / 100
                    #                     if data["conf"][i] != "-1"
                    #                     else 0
                    #                 ),
                    #             )
                    #
                    #     if text_entries:
                    #         box.text = " ".join(text_entries)
                    #         box.score = sum(scores) / len(
                    #             scores,
                    #         )  # Average confidence score
                    # else:
                    #     box.text = ""
                    #     box.score = 0

                    if box.score > params["scoreThreshold"]:
                        boxes.append(box)
                        texts.append(box.text)

                if params["keepFormatting"]:
                    text = TesseractRecognizer.box_to_formatted_text(
                        boxes,
                        params["lineTolerance"],
                    )
                else:
                    text = " ".join(texts)

                results.append(
                    Document(
                        path=image_path,
                        text=text,
                        bboxes=boxes,
                        type="text",
                        exception="",
                    ),
                )
        return results

    @classmethod
    def call_tesserocr(cls, images, detected_boxes, params):  # pragma: no cover
        from tesserocr import PyTessBaseAPI

        results = []
        lang = cls.getLangTess(params)
        with PyTessBaseAPI(
            path=params["tessDataPath"],
            psm=PSM.SINGLE_WORD,
            oem=params["oem"],
            lang=lang,
        ) as api:
            api.SetVariable("debug_file", "ocr.log")

            for (image, image_path), detected_box in zip(images, detected_boxes):
                api.SetImage(image)

                boxes = []
                texts = []

                for b in detected_box.bboxes:
                    box = b
                    if isinstance(box, dict):
                        box = Box(**box)
                    if not isinstance(box, Box):
                        box = Box(**box.asDict())
                    scaled_box = box.scale(params["scaleFactor"], padding=0)
                    api.SetRectangle(
                        scaled_box.x,
                        scaled_box.y,
                        scaled_box.width,
                        scaled_box.height,
                    )
                    box.text = api.GetUTF8Text().replace("\n", "")
                    box.score = api.MeanTextConf() / 100
                    if box.score > params["scoreThreshold"]:
                        boxes.append(box)
                        texts.append(box.text)
                if params["keepFormatting"]:
                    text = TesseractRecognizer.box_to_formatted_text(
                        boxes,
                        params["lineTolerance"],
                    )
                else:
                    text = " ".join(texts)

                results.append(
                    Document(
                        path=image_path,
                        text=text,
                        bboxes=boxes,
                        type="text",
                        exception="",
                    ),
                )
        return results

    @classmethod
    def call_recognizer(cls, images, boxes, params):
        if params["tessLib"] == TessLib.TESSEROCR.value:
            return cls.call_tesserocr(images, boxes, params)
        if params["tessLib"] == TessLib.PYTESSERACT.value:
            return cls.call_pytesseract(images, boxes, params)
        raise ValueError(f"Unknown Tesseract library: {params['tessLib']}")

    def setOem(self, value):
        """
        Sets the value of :py:attr:`oem`.
        """
        return self._set(oem=value)

    def getOem(self):
        """
        Sets the value of :py:attr:`oem`.
        """
        return self.getOrDefault(self.oem)

    def setTessDataPath(self, value):
        """
        Sets the value of :py:attr:`tessDataPath`.
        """
        return self._set(tessDataPath=value)

    def getTessDataPath(self):
        """
        Sets the value of :py:attr:`tessDataPath`.
        """
        return self.getOrDefault(self.tessDataPath)

    def setTessLib(self, value):
        """
        Sets the value of :py:attr:`tessLib`.
        """
        return self._set(tessLib=value)

    def getTessLib(self):
        """
        Gets the value of :py:attr:`tessLib`.
        """
        return self.getOrDefault(self.tessLib)
