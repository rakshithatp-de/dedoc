import time
from threading import Thread
import requests
import json
import queue


class BotUtility:

    @staticmethod
    def get_resp_string(response):
        # Dump the full response object as a dictionary
        response_dict = response.__dict__

        # Convert the dictionary to JSON for better readability
        return json.dumps(response_dict, indent=4)


    @staticmethod
    def perform_web_requests(addresses, no_workers, lambda_url, app):
        class MonitorThread(Thread):
            def __init__(self, request_queue, total_size, results, inprogress):
                Thread.__init__(self)
                self.queue = request_queue
                self.results = results
                self.total_size = total_size
                self.stop_requested = False
                self.inprogress = inprogress

            def run(self):
                while not self.stop_requested:
                    app.logger.info(f"QUEUE SIZE {self.queue.qsize()}, PENDING: {self.total_size-len(self.results)} RESULTS SIZE: {len(self.results)} \n IN PROGRESS: {json.dumps(self.inprogress)}\n\n\n\n\n")
                    time.sleep(5)

        class Worker(Thread):
            def __init__(self, request_queue, results, inprogress):
                Thread.__init__(self)
                self.queue = request_queue
                self.results = results
                self.inprogress = inprogress

            def run(self):
                while not self.queue.empty():
                    content = self.queue.get(block=False)
                    if not content:
                        break
                    self.inprogress[content['de_request_id']] = content
                    url = lambda_url
                    payload = json.dumps(content)
                    headers = {
                        'Content-Type': 'application/json'
                    }

                    max_retry = 3
                    retry_count = 0
                    success = False

                    while not success:
                        app.logger.info(f"REQUEST retry count: {retry_count}, payload:{payload}")
                        try:
                            response = requests.request("GET", url, headers=headers, data=payload, timeout=300)
                            response_text = response.text
                            if response.status_code == 200:
                                response_json = json.loads(response.text)
                                result = {'page': content['page_id'], 'status_code':response.status_code, 'status': 'PASS', 'response': response_json}
                                self.results.append(result)
                                app.logger.info(f"SUCCESS payload:{payload} response:{response.headers}")
                                success = True
                        except Exception as e:
                            success = False
                            response = requests.Response()
                            response.status_code = 500  # Set the desired status code
                            app.logger.info(f"ERROR payload:{payload} response:{str(e)}")
                            response_text = str(e)

                        if not success:
                            retry_count += 1
                            if retry_count == max_retry:
                                result = {'page': content['page_id'], 'status_code':response.status_code, 'status': 'FAIL', 'response': response_text}
                                self.results.append(result)
                                app.logger.info(f"FAILED payload:{payload} response:{response}")
                                break
                    self.queue.task_done()
                    del self.inprogress[content['de_request_id']]


        inprogress = {}
        # Create queue and add addresses
        q = queue.Queue()
        for content in addresses:
            q.put(content)

        # Create workers and add tot the queue
        workers = []
        r = []
        monitor_thread = MonitorThread(q, len(addresses), r, inprogress)
        monitor_thread.start()
        for _ in range(no_workers):
            worker = Worker(q, r, inprogress)
            worker.start()
            workers.append(worker)

        # Join workers to wait till they finished
        for worker in workers:
            worker.join()
        monitor_thread.stop_requested = True
        return r
