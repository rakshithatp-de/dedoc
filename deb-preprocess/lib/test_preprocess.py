from deplatform.bot.bot_test import BotTestCase
from deplatform.bot.template.file_processor import FileProcessor

from decore.constant import ImageType

from preprocessor import Preprocessor

class TestImageToDoc(BotTestCase):

    def __init__(self, *args, **kwargs):
        if "host" not in kwargs:
            kwargs["host"] = "https://partner.prod.decisionengines.ai"
        if "bearer_token" not in kwargs:
            kwargs["bearer_token"] = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ1YmVydXNlciIsImF1ZCI6ImFueSIsInVzZXJEZXRhaWwiOiJ7XG4gIFwidXNlcm5hbWVcIiA6IFwidWJlcnVzZXJcIixcbiAgXCJmaXJzdE5hbWVcIiA6IFwidWJlcnVzZXJcIixcbiAgXCJsYXN0TmFtZVwiIDogXCJ1YmVyVXNlck5hbWVcIixcbiAgXCJlbWFpbFwiIDogXCJhZG1pbkBkZWNpc2lvbmVuZ2luZXMuYWlcIixcbiAgXCJleGlzdGluZ1VzZXJcIiA6IGZhbHNlLFxuICBcImF1dGhvcml0aWVzXCIgOiBbIHtcbiAgICBcInJvbGVcIiA6IFwiUk9MRV9BZG1pbmlzdHJhdG9yXCIsXG4gICAgXCJhdXRob3JpdHlcIiA6IFwiUk9MRV9BZG1pbmlzdHJhdG9yXCJcbiAgfSwge1xuICAgIFwicm9sZVwiIDogXCJST0xFX1VTRVJfdWJlcnVzZXJcIixcbiAgICBcImF1dGhvcml0eVwiIDogXCJST0xFX1VTRVJfdWJlcnVzZXJcIlxuICB9IF0sXG4gIFwidGVuYW50SWRcIiA6IFwiREVcIixcbiAgXCJjcmVhdGVkVFNcIiA6IDAsXG4gIFwidXBkYXRlZFRTXCIgOiAwLFxuICBcInVzclJvbGVzXCIgOiBbIHtcbiAgICBcImRiX2lkXCIgOiBcInJvbGU6Uk9MRV9VU0VSX3ViZXJ1c2VyXCIsXG4gICAgXCJuYW1lXCIgOiBcIlJPTEVfVVNFUl91YmVydXNlclwiLFxuICAgIFwiZGVzY3JpcHRpb25cIiA6IFwiRGVmYXVsdCB1c2VyIHJvbGVcIixcbiAgICBcInN5c3RlbVJvbGVcIiA6IGZhbHNlLFxuICAgIFwicGVybWlzc2lvbnNcIiA6IFsgXVxuICB9LCB7XG4gICAgXCJkYl9pZFwiIDogXCJyb2xlOlJPTEVfQWRtaW5pc3RyYXRvclwiLFxuICAgIFwibmFtZVwiIDogXCJST0xFX0FkbWluaXN0cmF0b3JcIixcbiAgICBcImRlc2NyaXB0aW9uXCIgOiBcIlwiLFxuICAgIFwic3lzdGVtUm9sZVwiIDogdHJ1ZSxcbiAgICBcInBlcm1pc3Npb25zXCIgOiBbIF1cbiAgfSBdLFxuICBcImVudlR5cGVcIiA6IFwidGVzdFwiLFxuICBcImVudklkXCIgOiBcInBhcnRuZXJwcm9kXCIsXG4gIFwidG9rZW5FeHBpcmF0aW9uTWluc1wiIDogMTQ0MCxcbiAgXCJyb2xlc1wiIDogWyBcIlJPTEVfQWRtaW5pc3RyYXRvclwiLCBcIlJPTEVfVVNFUl91YmVydXNlclwiIF0sXG4gIFwiZ3JvdXBzXCIgOiBbIF0sXG4gIFwiYWRtaW5cIiA6IHRydWVcbn0iLCJ0ZW5hbnRJZCI6IkRFIiwiZW52SWQiOiJwYXJ0bmVycHJvZCIsImV4cCI6MTY0OTUwNzExNiwiaWF0IjoxNjQ5NDIwNzIxfQ.sK63_N1NOQWHi-rjxvUYLUMA56cjtOYXYj13vF6khSi78iXMUIRzq781fwt5S-jL-awfj3eEq_d5Kz-vUy0B8g"
        # self.api_cache = JsonFileCache(use_cache=True, reset_cache=False, cache_file="./cache/api_cache.json")
        # kwargs["cache"] = self.api_cache
        BotTestCase.__init__(self, *args, **kwargs)

    # def test_preprocessor(self):
    #     file_id = "defile:global:5fad9181834dc80006829be7"
    #     input_format = ImageType.NORMALIZED
    #     output_format = ImageType.PREPROCESSED
    #
    #     read_as_grayscale = False
    #     operation_inputs = {"img": input_format}
    #
    #     parser = Preprocessor(transform_types=[output_format],
    #                           operation_inputs=operation_inputs,
    #                           operation_output=output_format)
    #
    #     img_preprocessor = FileProcessor(app=self.app,
    #                                      file_id=file_id,
    #                                      page_func=parser.parse_func,
    #                                      input_formats=[[input_format, read_as_grayscale]],
    #                                      output_formats=[output_format],
    #                                      start_page=4,
    #                                      end_page=-1)
    #     result = img_preprocessor.process()
    #     print("Cache hit rate", self.api_cache.hit_rate)

    def test_normalizer(self):
        input_data = {
          "file": {
            "type": "application/pdf",
            "id": "defile:624f0c77c5f80c000849031e",
            "name": "344245.pdf"
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

        parser = Preprocessor(transform_types=[output_format],
                              operation_inputs=operation_inputs,
                              operation_output=output_format)

        file_fromat_generator = FileProcessor(app=self.app,
                                              file_id=file_id,
                                              page_func=parser.parse_func,
                                              input_formats=[[input_format, read_as_grayscale]],
                                              start_page=start_page,
                                              end_page=end_page)
        result = file_fromat_generator.process()

if __name__ == "__main__":
    BotTestCase.run_test(TestImageToDoc)
