from deplatform.bot.bot_test import BotTestCase
from deplatform.bot.template.file_processor import FileProcessor
from deplatform.bot.template.file_processor import FileProcInOut
from devision.ocr.tesseract.tesseract_ocr import TesseractOCR
import pandas as pd

from decore.constant import ImageType
import sys
import json
import cv2
sys.path.insert(0, '/home/chethan/PyProject/deb-bots/deb-imgpreprocess')
sys.path.insert(0, '/home/chethan/PyProject/deb-bots/deb-imgpreprocess/lib')
from lib.preprocessor import Preprocessor

path_to_input = "/home/chethan/PyProject/deb-bots/deb-imgpreprocess/tests/resources/input_jsons/"
input_json_path = path_to_input + "partner.prod_derotation_validation.json"
with open(input_json_path,"r") as fp:
    input_json = json.load(fp)

columns = ["File Name", "Page Number", "Expected Rotation Angle", "Predicted Rotation Angle", "Status"]
rows = []
empty_row = ["", "", "", "", ""]
status_list = []


class InheritedPreprocessor(Preprocessor):
    def __init__(self,
                 transform_types,
                 operation_inputs,
                 operation_output,
                 OCRObject,
                 contrast_factor=2,
                 denoise_filter_size1=5,
                 denoise_filter_size2=3,
                 lowres_size=2400,
                 threshold=0.9,
                 resizewidth=1024,
                 resizeheight=0,
                 degree=90,
                 logger=None,
                 create_other_variants=False):
        Preprocessor.__init__(self,
                 transform_types,
                 operation_inputs,
                 operation_output,
                 OCRObject,
                 contrast_factor=contrast_factor,
                 denoise_filter_size1=denoise_filter_size1,
                 denoise_filter_size2=denoise_filter_size2,
                 lowres_size=lowres_size,
                 threshold=threshold,
                 resizewidth=resizewidth,
                 resizeheight=resizeheight,
                 degree=degree,
                 logger=logger,
                 create_other_variants=create_other_variants)

    def parse_func(self, input_data):
        result_dict = {"formats": {}, "annotations": {}}
        page_id = int(input_data[FileProcInOut.PAGE_ID])
        file_id = input_data[FileProcInOut.FILE_ID]
        file_name = input_data[FileProcInOut.NAME]

        image_bundle = input_data['formats']
        result = self.process(image_bundle)

        if len(result) > 1:
            result_dict["formats"] = result
        else:
            result_dict["formats"] = {self.operation_output: result[next(iter(result))]}

        for key, value in result_dict["formats"].items():
            output_path = "/home/chethan/PyProject/deb-bots/deb-imgpreprocess/tests/resources/output_images/derotated_images/"
            if isinstance(value, dict):
                if str(page_id) in input_json['files'][file_id]['pages']:
                    expected_rotation = input_json['files'][file_id]['pages'][str(page_id)]['expected_rotation']
                    predicted_rotation = value['rotation_angle']
                    status = 'Passed' if expected_rotation == predicted_rotation else 'Failed'
                    status_list.append(status)
                    rows.append([file_name, page_id, expected_rotation, predicted_rotation, status])
                cv2.imwrite(output_path + file_name + "_" + key + "_" + str(page_id) + ".png", value["image"])
            else:
                cv2.imwrite(output_path + file_name + "_" + key + "_" + str(page_id) + ".png", value)

        return {}

class TestImageToDoc(BotTestCase):

    def __init__(self, *args, **kwargs):
        self.input_json = input_json
        if "host" not in kwargs:
            kwargs["host"] = self.input_json["env"]
        if "bearer_token" not in kwargs:
            kwargs["bearer_token"] = self.input_json["token"]
        # self.api_cache = JsonFileCache(use_cache=True, reset_cache=False, cache_file="./cache/api_cache.json")
        # kwargs["cache"] = self.api_cache
        BotTestCase.__init__(self, *args, **kwargs)

    def test_normalizer(self):
        inputs_json = self.input_json['files']
        for file_id, input in inputs_json.items():
            input_data = {
              "file": {
                "type": "application/pdf",
                "id": file_id,
                "name": input['name']
              },
              "end_page": -1,
              "start_page": 1
            }

            file_id = input_data["file"]["id"]
            input_format = input_data.get("inputVariant", ImageType.ORIGINAL)
            start_page = int(input_data.get("start_page", 1))
            end_page = int(input_data.get("end_page", -1))

            output_format = ImageType.NORMALIZED

            read_as_grayscale = False
            operation_inputs = {"img": input_format}
            OCRObject = TesseractOCR(oem=3)

            parser = InheritedPreprocessor(transform_types=[output_format],
                                  operation_inputs=operation_inputs,
                                  operation_output=output_format,
                                  OCRObject=OCRObject)

            file_fromat_generator = FileProcessor(app=self.app,
                                                  file_id=file_id,
                                                  page_func=parser.parse_func,
                                                  input_formats=[[input_format, read_as_grayscale]],
                                                  start_page=start_page,
                                                  end_page=end_page)
            result = file_fromat_generator.process()
        rows.append(empty_row)
        rows.append(["", "", "", "", "Accuracy"])
        accuracy_percentage = str((status_list.count('Passed')/len(status_list))*100) + "%"
        rows.append(["", "", "", "", accuracy_percentage])
        df = pd.DataFrame(rows, columns=columns)
        test_suite_report = df.to_csv(index=False)
        with open("DerotationTestReport.csv", 'w+') as fp:
            fp.write(test_suite_report)


if __name__ == "__main__":
    BotTestCase.run_test(TestImageToDoc)
