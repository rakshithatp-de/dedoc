from deplatform.bot.bot_test import BotTestCase

from decore.constant import ImageType
from de_bot_utility import BotUtility
from de_process import Process

import time
import psutil
import os
import queue
import uuid


class PreprocessTest(BotTestCase):
    def __init__(self, *args, **kwargs):
        if "host" not in kwargs:
            kwargs["host"] = "https://ebay.stg.decisionengines.ai"
        if "bearer_token" not in kwargs:
            kwargs[
                "bearer_token"] = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJjaGV0aGFuX3Rva2VuIiwiYXVkIjoiYW55IiwidXNlckRldGFpbCI6IntcbiAgXCJ1c2VybmFtZVwiIDogXCJjaGV0aGFuX3Rva2VuXCIsXG4gIFwiZmlyc3ROYW1lXCIgOiBcIkNoZXRoYW5cIixcbiAgXCJsYXN0TmFtZVwiIDogXCJUb2tlblwiLFxuICBcImV4aXN0aW5nVXNlclwiIDogZmFsc2UsXG4gIFwiYXV0aG9yaXRpZXNcIiA6IFsge1xuICAgIFwicm9sZVwiIDogXCJST0xFX0FkbWluaXN0cmF0b3JcIixcbiAgICBcImF1dGhvcml0eVwiIDogXCJST0xFX0FkbWluaXN0cmF0b3JcIlxuICB9LCB7XG4gICAgXCJyb2xlXCIgOiBcIio6KjoqXCIsXG4gICAgXCJhdXRob3JpdHlcIiA6IFwiKjoqOipcIlxuICB9IF0sXG4gIFwiY3JlYXRlZFRTXCIgOiAwLFxuICBcInVwZGF0ZWRUU1wiIDogMCxcbiAgXCJ0b2tlbkV4cGlyYXRpb25NaW5zXCIgOiAxMjk2MDAsXG4gIFwicm9sZXNcIiA6IFsgXCJST0xFX0FkbWluaXN0cmF0b3JcIiwgXCIqOio6KlwiIF0sXG4gIFwiZ3JvdXBzXCIgOiBbIF0sXG4gIFwiYWRtaW5cIiA6IHRydWVcbn0iLCJlbnZUeXBlIjoiZGV2IiwidGVuYW50SWQiOiJERSIsImVudklkIjoiREUiLCJleHAiOjE2OTAxOTU5MDksImlhdCI6MTY4MjQxOTkwOX0.v_BRq6F02zPwqVfuSP_kMz-XAFVoXghIlAKqBaylw3njEl8dGntokVp4bIKYMc_4Ksu3q7QymrJieWtooOAyXA"
        BotTestCase.__init__(self, *args, **kwargs)

    def test_lv(self):
        input_data = {
            "udtFileId": "defile:645de08017108b00084a094d",
            "deSkew": True,
            "userDefinedTemplate": True,
            "file": {
                "name": "IMG_0755 (1).jpg",
                "id": "defile:649020f7bc613b000899fe2e",
                "type": "image/jpeg"
            },
            "end_page": 1,
            "color": "Preserve",
            "start_page": 1,
            "deRotate": True,
            "removeBg": False,
            "noLines": True,
            "lambdaUrl": "https://aplhhqvhlb7k5edyro43gvlgq40grihs.lambda-url.us-east-1.on.aws/",
            "thread": 100
        }

        file_id = input_data["file"]["id"]
        input_format = input_data.get("inputVariant", ImageType.ORIGINAL)
        start_page = int(input_data.get("start_page", 1))
        end_page = int(input_data.get("end_page", -1))
        thread = int(input_data.get("thread", 1))
        lambda_url = input_data.get("lambdaUrl")
        color = input_data.get("color", "Preserve")
        de_rotate = input_data.get("deRotate", True)
        de_skew = input_data.get("deSkew", True)
        remove_bg = input_data.get("removeBg", True)
        user_defined_template = input_data.get("userDefinedTemplate", False)
        udt_file_id = input_data.get("udtFileId")
        no_lines = input_data.get("noLines", True)
        img2page_threshold = float(input_data.get("img2page_threshold", 0.5))

        service_bundle = self.app.bean_registry.get_object("ServiceBundle")
        sb_apis = self.app.bean_registry.get_object("ServiceBundle").apis
        tesserocr_queue = queue.Queue()
        debug_dir = "./debug_output/"

        NUM_THREADS = thread

        def normalize_variant(page_entities):
            results = BotUtility.perform_web_requests(page_entities, 10, lambda_url, self.app)

        # ================================================================================
        # Main Code
        # ================================================================================
        document = sb_apis['file_api'].get_file_meta(file_id)

        # PAGE WISE PROCESSING OF A FILE
        end_page = document['pageCount'] + 1 if end_page < 0 else min(end_page, document['pageCount']) + 1
        page_entities = []
        thread_input_count = 1
        for page in range(start_page, end_page):
            page_entities.append({"config": {"bearer_token": self.app.configuration['bearer_token'],
                                             "gateway_url": self.app.configuration['gateway_url']},
                                  "bot_file_id": "",
                                  "debug": True,
                                  "operation_params": {"de_rotate": de_rotate,
                                                       "de_skew": de_skew,
                                                       "remove_bg": remove_bg,
                                                       "no_lines": no_lines,
                                                       "udt": user_defined_template,
                                                       "udt_file_id": udt_file_id,
                                                       "img2page_threshold": img2page_threshold,
                                                       "input_format": input_format,
                                                       "color": color,
                                                       "start_page": start_page},
                                  "file_id": file_id,
                                  "page_id": page,
                                  "de_request_id": str(uuid.uuid4())})
            if thread_input_count == NUM_THREADS or page == end_page - 1 or page == start_page:
                p = Process(target=normalize_variant, args=(page_entities,))
                p.start()
                p.join()

                if p.exception:
                    error, traceback_log = p.exception
                    print(traceback_log)
                    raise error

                page_entities = []
                thread_input_count = 0
            print(f"PROCESS MEMORY USAGE : {psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2} MiB")
            thread_input_count += 1


if __name__ == '__main__':
    BotTestCase.run_test(PreprocessTest)
