from preprocessor import Preprocessor
from deplatform.bot.bot_test import BotTestCase
from deplatform.bot.template.file_processor import FileProcessor

from decore.constant import ImageType
import cv2
import time


class TestImagePreProcess(BotTestCase):

    def __init__(self, *args, **kwargs):
        if "host" not in kwargs:
            kwargs["host"] = "https://cso.dev.decisionengines.ai"
        if "bearer_token" not in kwargs:
            kwargs["bearer_token"] = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJzaGVnZGUiLCJhdWQiOiJhbnkiLCJ1c2VyRGV0YWlsIjoie1xuICBcInVzZXJuYW1lXCIgOiBcInNoZWdkZVwiLFxuICBcImZpcnN0TmFtZVwiIDogXCJTdWRhcnNoYW5cIixcbiAgXCJsYXN0TmFtZVwiIDogXCJIZWdkZVwiLFxuICBcImVtYWlsXCIgOiBcInNoZWdkZUBkZWNpc2lvbmVuZ2luZXMuYWlcIixcbiAgXCJleGlzdGluZ1VzZXJcIiA6IGZhbHNlLFxuICBcImF1dGhvcml0aWVzXCIgOiBbIHtcbiAgICBcInJvbGVcIiA6IFwiUk9MRV9BZG1pbmlzdHJhdG9yXCIsXG4gICAgXCJhdXRob3JpdHlcIiA6IFwiUk9MRV9BZG1pbmlzdHJhdG9yXCJcbiAgfSwge1xuICAgIFwicm9sZVwiIDogXCJST0xFX0dST1VQX1Jldmlld1JvbGVcIixcbiAgICBcImF1dGhvcml0eVwiIDogXCJST0xFX0dST1VQX1Jldmlld1JvbGVcIlxuICB9IF0sXG4gIFwidGVuYW50SWRcIiA6IFwiREVcIixcbiAgXCJjcmVhdGVkVFNcIiA6IDAsXG4gIFwidXBkYXRlZFRTXCIgOiAwLFxuICBcInVzclJvbGVzXCIgOiBbIHtcbiAgICBcImRiX2lkXCIgOiBcInJvbGU6Uk9MRV9BZG1pbmlzdHJhdG9yXCIsXG4gICAgXCJuYW1lXCIgOiBcIlJPTEVfQWRtaW5pc3RyYXRvclwiLFxuICAgIFwiZGVzY3JpcHRpb25cIiA6IFwiXCIsXG4gICAgXCJzeXN0ZW1Sb2xlXCIgOiB0cnVlLFxuICAgIFwicGVybWlzc2lvbnNcIiA6IFsgXVxuICB9LCB7XG4gICAgXCJkYl9pZFwiIDogXCJyb2xlOlJPTEVfR1JPVVBfUmV2aWV3Um9sZVwiLFxuICAgIFwibmFtZVwiIDogXCJST0xFX0dST1VQX1Jldmlld1JvbGVcIixcbiAgICBcImRlc2NyaXB0aW9uXCIgOiBcIlRoaXMgcm9sZSBpcyB1c2VkIHRvIGFzc2lnbiByZXZpZXdcIixcbiAgICBcInN5c3RlbVJvbGVcIiA6IGZhbHNlLFxuICAgIFwicGVybWlzc2lvbnNcIiA6IFsgXVxuICB9IF0sXG4gIFwiZW52VHlwZVwiIDogXCJkZXZcIixcbiAgXCJlbnZJZFwiIDogXCJjc29kZXZcIixcbiAgXCJ0b2tlbkV4cGlyYXRpb25NaW5zXCIgOiAxNDQwLFxuICBcInJvbGVzXCIgOiBbIFwiUk9MRV9BZG1pbmlzdHJhdG9yXCIsIFwiUk9MRV9HUk9VUF9SZXZpZXdSb2xlXCIgXSxcbiAgXCJncm91cHNcIiA6IFsgXCJST0xFX0dST1VQX1Jldmlld1JvbGVcIiBdLFxuICBcImFkbWluXCIgOiB0cnVlXG59IiwidGVuYW50SWQiOiJERSIsImVudklkIjoiY3NvZGV2IiwiZXhwIjoxNjQ3NjkxNzM4LCJpYXQiOjE2NDc2MDUzMzh9.77Ryc1av_ENFZSk70i5j7Jz-SI2SKdtiSqi8I80Z2ZG2WqBYGYPlOXiryQHqAvCQsfBIHaWn46d7MQbUPDgMZw"
        BotTestCase.__init__(self, *args, **kwargs)

    def test_preprocessor(self):
        input_data = {
          "file": {
            "name": "Contract 2column.pdf",
            "type": "application/pdf",
            "id": "defile:62346ccdb5c78900077f84f7"
          },
          "end_page": -1,
          "start_page": 1,
          "inputVariant": "img"
        }
        bot_start_time = time.time()
        file_id = input_data["file"]["id"]
        input_format = input_data.get("inputVariant", ImageType.ORIGINAL)
        start_page = int(input_data.get("start_page", 1))
        end_page = int(input_data.get("end_page", -1))

        output_format = ImageType.NORMALIZED

        read_as_grayscale = False
        operation_inputs = {"img": input_format}

        parser = Preprocessor(transform_types=[output_format],
                              operation_inputs=operation_inputs,
                              operation_output=output_format)

        file_fromat_generator = FileProcessor(app=self.app,
                                              file_id=file_id,
                                              page_func=parser.parse_func,
                                              input_formats=[[input_format, read_as_grayscale]],
                                              output_formats=[output_format],
                                              start_page=start_page,
                                              end_page=end_page)
        result = file_fromat_generator.process()
        print("--- %s seconds ---" % (time.time() - bot_start_time))


if __name__ == "__main__":
    BotTestCase.run_test(TestImagePreProcess)
