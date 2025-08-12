import yaml
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

class ServerInstance:
    def __init__(self, name, defaults, config=None):
        self.name = name
        self.defaults = defaults
        self.config = config or {}
        self.values = dict(defaults)
        self.values.update(config or {})

    def set_value(self, key, value):
        if value == self.defaults.get(key):
            self.config.pop(key, None)
        else:
            self.config[key] = value
        self.values[key] = value

    def get_value(self, key):
        return self.values.get(key, self.defaults.get(key))

    def is_default(self, key):
        #return self.values.get(key, self.defaults.get(key)) == self.defaults.get(key)
        return key not in self.config or not self.config[key]

    def to_yaml(self):
        data = {k: v for k, v in self.config.items() if v != self.defaults.get(k)}
        if 'response' in data:
            data['response'] = LiteralScalarString(data['response'])
        data['name'] = self.name
        return data

class ClientInstance:
    def __init__(self, name, defaults, server_methods, config=None):
        self.name = name
        self.defaults = defaults
        self.server_methods = server_methods  # Liste der erlaubten Methoden
        self.config = config or {}
        self.values = dict(defaults)
        self.values.update(config or {})
        # Setze methode auf ersten Wert aus server_methods, falls nicht gesetzt oder ungültig
        if self.values.get('methode') not in self.server_methods:
            self.values['methode'] = self.server_methods[0] if self.server_methods else None

    def set_value(self, key, value):
        if key == 'methode' and value not in self.server_methods:
            value = self.server_methods[0] if self.server_methods else None
        if value == self.defaults.get(key):
            self.config.pop(key, None)
        else:
            self.config[key] = value
        self.values[key] = value

    def get_value(self, key):
        return self.values.get(key, self.defaults.get(key))

    def is_default(self, key):
        #return self.values.get(key, self.defaults.get(key)) == self.defaults.get(key)
        return key not in self.config or not self.config[key]

    def to_yaml(self):
        data = {k: v for k, v in self.config.items() if v != self.defaults.get(k)}
        if 'request' in data:
            data['request'] = LiteralScalarString(data['request'])
        data['name'] = self.name
        return data

class ConfigModel:
    def __init__(self, path):
        self.path = Path(path)
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.load()

    def load(self):
        with open(self.path, 'r') as f:
            self.raw = self.yaml.load(f)
        self.defaults = self.raw['defaults']['server']
        self.servers = []
        for s in self.raw.get('servers', []):
            name = s['name']
            config = dict(s)
            config.pop('name')
            self.servers.append(ServerInstance(name, self.defaults, config))
        # Clients analog laden (siehe vorherige Anpassung)
        self.clients = []
        defaults = self.raw['defaults']['client']
        server_methods = self.raw['defaults']['server']['methodes']
        for c in self.raw.get('clients', []):
            name = c['name']
            config = dict(c)
            config.pop('name')
            self.clients.append(ClientInstance(name, defaults, server_methods, config))

    def save(self):
        # Blockstil für response/request
        for s in self.servers:
            if 'response' in s.values:
                val = s.values['response']
                if not isinstance(val, str):
                    val = str(val)
                s.values['response'] = LiteralScalarString(val)

        for c in self.clients:
            if 'request' in c.values:
                val = c.values['request']
                if not isinstance(val, str):
                    val = str(val)
                c.values['request'] = LiteralScalarString(val)

        servers = [s.to_yaml() for s in self.servers]
        clients = [c.to_yaml() for c in self.clients]
        self.raw['servers'] = servers
        self.raw['clients'] = clients

        with open(self.path, 'w') as f:
            #print(self.raw)
            self.yaml.dump(self.raw, f)
