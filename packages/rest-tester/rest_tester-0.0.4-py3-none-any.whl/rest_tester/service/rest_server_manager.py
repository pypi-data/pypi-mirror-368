import threading
import logging
import time
from flask import Flask, request
from werkzeug.serving import make_server

class ServerThread(threading.Thread):
    def __init__(self, host, port, logger):
        super().__init__()
        self.host = host
        self.port = port
        self.logger = logger
        self.app = Flask(f"server_{host}_{port}")
        self.srv = None
        self._shutdown = threading.Event()
        self._endpoints = {}  # endpoint: (methods, handler)
        # Register generic route
        # self.app.add_url_rule("/<path:endpoint>", "dynamic", self._dispatch, methods=["GET", "POST"])
        # Add dummy shutdown endpoint
        self.app.add_url_rule("/__shutdown__", "__shutdown__", lambda: "shutting down", methods=["GET"])

    def _dispatch(self, **args):
        handler_info = self._endpoints.get(request.url_rule.rule)

        if handler_info and request.method in handler_info[0]:
            # Übergib das request-Objekt an den Handler
            return handler_info[1](request)
        
        return ("Not found", 404)

    def add_endpoint(self, endpoint, methods, initial_delay_sec, handler):
        time.sleep(initial_delay_sec)
        if endpoint not in self._endpoints:
            self.logger.info(f"Register endpoint {endpoint} on {self.host}:{self.port}")
            self.app.add_url_rule(endpoint, endpoint, view_func=self._dispatch, methods=["GET", "POST","PUT","DELETE"])
        else:
            self.logger.info(f"Update handler for endpoint {endpoint} on {self.host}:{self.port}")
        self._endpoints[endpoint] = (methods, handler)

    def remove_endpoint(self, endpoint):
        if endpoint in self._endpoints:
            self.logger.info(f"Unregister endpoint {endpoint} on {self.host}:{self.port}")
            self._endpoints.pop(endpoint)

    def run(self):
        self.srv = make_server(self.host, self.port, self.app)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.logger.info(f"Server started on {self.host}:{self.port}")
        while not self._shutdown.is_set():
            self.srv.handle_request()
        self.logger.info(f"Server stopped on {self.host}:{self.port}")

    def shutdown(self):
        self._shutdown.set()
        try:
            import requests
            requests.get(f"http://{self.host}:{self.port}/__shutdown__")
        except Exception:
            pass

class RestServerManager:
    def __init__(self):
        self.servers = {}  # (host, port): ServerThread
        self.logger = logging.getLogger("RestServerManager")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _get_server(self, host, port):
        return self.servers.get((host, port))

    def add_endpoint(self, host, port, endpoint, methods, initial_delay_sec, handler):
        key = (host, port)
        if key not in self.servers:
            logger = logging.getLogger(f"{host}:{port}")
            logger.setLevel(logging.INFO)
            for h in self.logger.handlers:
                logger.addHandler(h)
            server = ServerThread(host, port, logger)
            self.servers[key] = server
            server.start()
            time.sleep(0.1)  # Give server time to start
        self.servers[key].add_endpoint(endpoint, methods, initial_delay_sec, handler)

    def remove_endpoint(self, host, port, endpoint):
        key = (host, port)
        server = self.servers.get(key)
        if server:
            server.remove_endpoint(endpoint)
            if not server._endpoints:
                server.shutdown()
                server.join(timeout=1)
                del self.servers[key]

    def rename_endpoint_reference(self, old_host, old_port, old_endpoint, new_host, new_port, new_endpoint):
        """
        Umbenennung von Server-Referenzen: Falls sich Host/Port/Endpoint ändern,
        wird der entsprechende Endpoint gestoppt und muss neu gestartet werden.
        """
        old_key = (old_host, old_port)
        new_key = (new_host, new_port)
        
        # Wenn sich nur der Endpoint-Name ändert, aber Host/Port gleich bleiben
        if old_key == new_key:
            server = self.servers.get(old_key)
            if server and old_endpoint in server._endpoints:
                # Endpoint-Referenz umbenennen
                handler_info = server._endpoints[old_endpoint]
                server._endpoints[new_endpoint] = handler_info
                del server._endpoints[old_endpoint]
                self.logger.info(f"Renamed endpoint {old_endpoint} to {new_endpoint} on {old_host}:{old_port}")
        # Wenn sich Host/Port ändert, muss der Server neu gestartet werden
        # Das wird über remove_endpoint und add_endpoint gehandhabt

    def shutdown_all(self):
        for key, server in list(self.servers.items()):
            server.shutdown()
            server.join(timeout=1)
        self.servers.clear()
