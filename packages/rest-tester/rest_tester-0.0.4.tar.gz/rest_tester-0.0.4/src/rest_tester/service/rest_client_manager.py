import threading
import time, random, json, math, os, sys, datetime
import requests
from jinja2 import Environment

class ClientThread(threading.Thread):
    def __init__(self, name, host, route, method, request_data, period_sec=1.0, loop=False, initial_delay_sec=0.0, on_response=None, counter=0):
        super().__init__()
        self.name = name
        self.host = host
        self.route = route
        self.method = method.upper()
        self.request_data = request_data
        self.period_sec = period_sec
        self.loop = loop
        self._stop_event = threading.Event()
        self.initial_delay_sec = initial_delay_sec
        self.on_response = on_response
        self.counter = counter

        self.env = Environment(
         autoescape=False
        )

    def run(self):

        if not self.host or not self.route:
            print(f"[Client {self.name}] Error: Host and route must be set before starting.")
            return
        
        url = f"http://{self.host}{self.route}"
        

        time.sleep(self.initial_delay_sec)
        while not self._stop_event.is_set():
            try:
                data = None
                json_data = None
                headers = {"Content-Type": "application/json"}
                if self.request_data:
                    try:

                        # render paylooad
                        json_template_request = self.env.from_string(self.request_data)
                        rendered_json_request = json_template_request.render( time=time, random=random, json=json, math=math, os=os, sys=sys, datetime=datetime, counter=self.counter)
                        json_data = json.loads(rendered_json_request)

                    except Exception:
                        data = self.request_data

                #render url
                json_template_url = self.env.from_string(url)
                rendered_url = json_template_url.render( time=time, random=random, json=json, math=math, os=os, sys=sys, datetime=datetime, counter=self.counter)

                resp = requests.request(self.method, rendered_url, json=json_data, data=data, headers=headers)
                self.counter += 1

                print("----- Request JSON -----")
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
                print("------------------------")

                if self.on_response:
                    self.on_response(self.name, resp)
                else:
                    print(f"[Client {self.name}] Response: {resp.status_code} {resp.text}")

            except Exception as e:
                print(f"[Client {self.name}] Error: {e}")
            if not self.loop:
                break
            time.sleep(self.period_sec)

    def stop(self):
        self._stop_event.set()

class RestClientManager:
    def __init__(self):
        self.clients = {}  # name: ClientThread
        self.counter = 0  # Global counter for all clients

    def start_client(self, name, host, route, method, request_data, period_sec=1.0, loop=False, initial_delay_sec=0.0, on_response=None):
        self.stop_client(name)
        thread = ClientThread(name, host, route, method, request_data, period_sec, loop, initial_delay_sec, on_response, self.counter)
        self.counter += 1 
        self.clients[name] = thread
        thread.start()

    def stop_client(self, name):
        thread = self.clients.get(name)
        if thread:
            thread.stop()
            thread.join(timeout=1)
            del self.clients[name]
            
    def stop_all(self):
        for name in list(self.clients.keys()):
            self.stop_client(name)
        
