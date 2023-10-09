from decore.constant import ImageType
from de_bot_utility import BotUtility
from de_process import Process

import time
import psutil
import os
import queue

#  Derotate  Deskew  Grayscale contrast  removedBg blackWhite  noLines denoised  Joints/metadata Lines/metadata  Normalized
#  Raster    TRUE    TRUE      TRUE      TRUE      TRUE        TRUE    TRUE      TRUE
#  Vector    TRUE    TRUE
#  Variant   No      No        No        No        No          No      No        No              Yes             Yes
#  Type      NA      NA        NA        NA        NA          NA      NA        JSON            JSON            png
#  Capture all the flags

bot_start_time = time.time()
input_data = app.get_request_data()['input']
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

service_bundle = app.bean_registry.get_object("ServiceBundle")
sb_apis = app.bean_registry.get_object("ServiceBundle").apis
tesserocr_queue = queue.Queue()
debug_dir = "./debug_output/"

NUM_THREADS = thread


def normalize_variant(page_entities):
    results = BotUtility.perform_web_requests(page_entities, thread, lambda_url)


# ================================================================================
# Main Code
# ================================================================================
document = sb_apis['file_api'].get_file_meta(file_id)

# PAGE WISE PROCESSING OF A FILE
end_page = document['pageCount'] + 1 if end_page < 0 else min(end_page, document['pageCount']) + 1
page_entities = []
thread_input_count = 1
for page in range(start_page, end_page):
    page_entities.append({"config": {"bearer_token": app.configuration['bearer_token'],
                                     "gateway_url": app.configuration['gateway_url']},
                          "bot_file_id": "",
                          "debug": False,
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
                          "file_id": file_id, "page_id": page})
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

print(f"PROCESS MEMORY USAGE OF MAIN PROCESS: {psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2} MiB")

res = {"file": input_data["file"]}
res["bot_execution_time"] = " %s seconds" % (time.time() - bot_start_time)
response = app.ok_response(res)
