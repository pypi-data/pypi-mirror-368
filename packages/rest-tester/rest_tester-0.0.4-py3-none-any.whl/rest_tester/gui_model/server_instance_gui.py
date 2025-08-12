import sys
import json
import re
import socket
import rfc3986
from PySide6.QtWidgets import (
    QApplication, QWidget, QFormLayout, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt
from .model import ConfigModel

class ServerInstanceWidget(QWidget):
    def __init__(self, server_instance):
        super().__init__()
        self.server = server_instance
        self.layout = QFormLayout(self)
        # Host
        self.host_edit = QLineEdit(self.server.get_value('host'))
        self._set_default_style('host', self.host_edit)
        self.host_edit.textChanged.connect(lambda val: self._on_host_edit(val))
        self.host_edit.focusOutEvent = lambda event: self._host_focus_out_event(event)
        self.layout.addRow("Host", self.host_edit)
        # Autostart
        self.autostart_box = QCheckBox()
        self.autostart_box.setChecked(self.server.get_value('autostart'))
        self._set_default_style('autostart', self.autostart_box)
        self.autostart_box.stateChanged.connect(lambda _: self._on_edit('autostart', self.autostart_box.isChecked(), self.autostart_box))
        self.layout.addRow("Autostart", self.autostart_box)
        # Initial Delay
        self.initial_delay_edit = QLineEdit(str(self.server.get_value('initial_delay_sec')))
        self._set_default_style('initial_delay_sec', self.initial_delay_edit)
        self.initial_delay_edit.textChanged.connect(lambda val: self._on_numeric_edit('initial_delay_sec', val, self.initial_delay_edit))
        self.initial_delay_edit.focusOutEvent = lambda event: self._numeric_focus_out_event(event, 'initial_delay_sec', self.initial_delay_edit)
        self.layout.addRow("Initial Delay (s)", self.initial_delay_edit)
        # Response Delay
        self.delay_edit = QLineEdit(str(self.server.get_value('response_delay_sec')))
        self._set_default_style('response_delay_sec', self.delay_edit)
        self.delay_edit.textChanged.connect(lambda val: self._on_numeric_edit('response_delay_sec', val, self.delay_edit))
        self.delay_edit.focusOutEvent = lambda event: self._numeric_focus_out_event(event, 'response_delay_sec', self.delay_edit)
        self.layout.addRow("Response Delay (s)", self.delay_edit)
        # Route
        self.route_edit = QLineEdit(self.server.get_value('route'))
        self._set_default_style('route', self.route_edit)
        self.route_edit.textChanged.connect(lambda val: self._on_route_edit(val))
        self.route_edit.focusOutEvent = lambda event: self._route_focus_out_event(event)
        self.layout.addRow("Route", self.route_edit)
        # Methoden (Checkboxen horizontal)
        self.methods_checks = []
        self.methods_layout = QHBoxLayout()
        default_methods = self.server.defaults.get('methodes', [])
        current_methods = self.server.get_value('methodes') or []
        for m in default_methods:
            cb = QCheckBox(m)
            cb.setChecked(m in current_methods)
            cb.stateChanged.connect(self._on_methods_changed)
            self.methods_checks.append(cb)
            self.methods_layout.addWidget(cb)
        self.layout.addRow("Methoden", self.methods_layout)
        # Response (großes Textfeld)
        self.response_edit = QTextEdit(self.server.get_value('response') if self.server.get_value('response') else "")
        self.response_edit.setMinimumHeight(120)
        self._set_default_style('response', self.response_edit)
        self.response_edit.textChanged.connect(lambda: self._on_edit('response', self.response_edit.toPlainText(), self.response_edit))
        self.response_edit.focusOutEvent = self._response_focus_out_event
        self.layout.addRow("Response", self.response_edit)
        # Initiale Validierung und Pretty-Print
        self._validate_and_pretty_response()
        
        # Initial host validation
        self._validate_initial_host()
        
        # Initial numeric validation
        self._validate_initial_numeric()
        
        # Initial route validation
        self._validate_initial_route()

    def _set_default_style(self, key, widget):
        if self.server.is_default(key):
            widget.setStyleSheet("color: gray;")
        else:
            widget.setStyleSheet("")

    def _on_host_edit(self, val):
        """Handle host field changes."""
        self._on_edit('host', val, self.host_edit)
    
    def _host_focus_out_event(self, event):
        """Validate host format and update styling."""
        QLineEdit.focusOutEvent(self.host_edit, event)
        
        host = self.host_edit.text().strip()
        is_valid = self._validate_host(host)
        
        if is_valid:
            self._set_default_style('host', self.host_edit)
        else:
            self.host_edit.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")
    
    def _validate_host(self, host):
        """Validate host format (IP address or hostname with optional port)."""
        if not host:
            return False
        
        # Check if host includes port
        if ':' in host:
            host_part, port_part = host.rsplit(':', 1)
            
            # Validate port range
            try:
                port = int(port_part)
                if not (0 <= port <= 65535):
                    return False
            except ValueError:
                return False
        else:
            host_part = host
        
        # Validate IP address format
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if re.match(ip_pattern, host_part):
            return True
        
        # Validate hostname format
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if re.match(hostname_pattern, host_part):
            return True
        
        # Check if it's localhost or valid hostname using socket
        try:
            socket.gethostbyname(host_part)
            return True
        except socket.gaierror:
            return False

    def _validate_initial_host(self):
        """Validate host field on startup and set styling accordingly."""
        host = self.host_edit.text().strip()
        is_valid = self._validate_host(host)
        
        if not is_valid:
            self.host_edit.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")
        else:
            self._set_default_style('host', self.host_edit)

    def _validate_initial_numeric(self):
        """Validate numeric fields on startup and set styling accordingly."""
        numeric_fields = [
            ('initial_delay_sec', self.initial_delay_edit),
            ('response_delay_sec', self.delay_edit)
        ]
        
        for key, widget in numeric_fields:
            value = widget.text().strip()
            is_valid = self._validate_numeric(value)
            
            if not is_valid:
                widget.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")
            else:
                self._set_default_style(key, widget)

    def _validate_numeric(self, value):
        """Validate that value is a positive number (int or float)."""
        if not value:
            return False
        
        try:
            num_value = float(value)
            return num_value >= 0
        except (ValueError, TypeError):
            return False

    def _validate_route(self, route):
        """Validate route format according to RFC 3986."""
        if not route:
            return False
        
        try:
            # Parse the route as a URI path
            # Routes should start with / for HTTP endpoints
            if not route.startswith('/'):
                return False
            
            # Use rfc3986 to validate the URI structure
            # Create a minimal URI with the route as path
            test_uri = f"http://example.com{route}"
            uri = rfc3986.uri_reference(test_uri)
            
            # Validate the URI
            validator = rfc3986.validators.Validator().require_presence_of('scheme', 'host')
            validator.validate(uri)
            
            # Additional checks for path component
            if uri.path is None:
                return False
                
            # Check for valid path characters (allowing query parameters)
            # Path should not contain spaces or other invalid characters
            path_part = route.split('?')[0]  # Get path without query
            if ' ' in path_part or any(ord(c) < 32 or ord(c) > 126 for c in path_part):
                return False
                
            return True
            
        except Exception:
            return False

    def _validate_initial_route(self):
        """Validate route field on startup and set styling accordingly."""
        route = self.route_edit.text().strip()
        is_valid = self._validate_route(route)
        
        if not is_valid:
            self.route_edit.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")
        else:
            self._set_default_style('route', self.route_edit)

    def _on_route_edit(self, val):
        """Handle route field changes."""
        is_valid = self._validate_route(val)
        
        if is_valid:
            self._on_edit('route', val, self.route_edit)
        else:
            self.route_edit.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")

    def _route_focus_out_event(self, event):
        """Validate route format and update styling."""
        QLineEdit.focusOutEvent(self.route_edit, event)
        
        route = self.route_edit.text().strip()
        is_valid = self._validate_route(route)
        
        if is_valid:
            self._set_default_style('route', self.route_edit)
            self._on_edit('route', route, self.route_edit)
        else:
            self.route_edit.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")

    def _on_numeric_edit(self, key, value, widget):
        """Handle numeric field changes with validation."""
        is_valid = self._validate_numeric(value)
        
        if is_valid:
            self._on_edit(key, value, widget)
        else:
            widget.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")

    def _on_edit(self, key, value, widget=None):
        if isinstance(widget, QLineEdit) and value.strip() == "":
            value = self.server.defaults.get(key, "")
            widget.setText(str(value))
        
        # Float-Konvertierung für numerische Felder
        if key in ['initial_delay_sec', 'response_delay_sec']:
            try:
                value = float(value)
            except (ValueError, TypeError):
                # Bei ungültiger Eingabe nichts tun oder Default verwenden
                return
                
        self.server.set_value(key, value)
        self._set_default_style(key, widget)

    def _numeric_focus_out_event(self, event, key, widget):
        """Handle focus out for numeric fields to ensure proper float formatting."""
        try:
            # Hole den aktuellen Wert und konvertiere zu Float
            current_text = widget.text().strip()
            if current_text == "":
                # Wenn leer, verwende Default
                default_value = self.server.defaults.get(key, 0.0)
                widget.setText(str(float(default_value)))
                self.server.set_value(key, float(default_value))
            else:
                # Validiere den Wert
                is_valid = self._validate_numeric(current_text)
                if is_valid:
                    # Konvertiere zu Float und formatiere
                    float_value = float(current_text)
                    widget.setText(str(float_value))
                    self.server.set_value(key, float_value)
                    self._set_default_style(key, widget)
                else:
                    # Bei ungültiger Eingabe, verwende Default
                    default_value = self.server.defaults.get(key, 0.0)
                    widget.setText(str(float(default_value)))
                    self.server.set_value(key, float(default_value))
                    self._set_default_style(key, widget)
        except (ValueError, TypeError):
            # Bei ungültiger Eingabe, verwende Default
            default_value = self.server.defaults.get(key, 0.0)
            widget.setText(str(float(default_value)))
            self.server.set_value(key, float(default_value))
            self._set_default_style(key, widget)
        
        # Original focus out event aufrufen
        super(QLineEdit, widget).focusOutEvent(event)

    def _on_methods_changed(self):
        selected = [cb.text() for cb in self.methods_checks if cb.isChecked()]
        if not selected:
            # Mindestens eine Checkbox muss ausgewählt sein
            self.methods_checks[0].setChecked(True)
            selected = [self.methods_checks[0].text()]
        self.server.set_value('methodes', selected)
        # Info-Label entfernt

    # _reset_defaults entfernt

    def _validate_and_pretty_response(self):
        text = self.response_edit.toPlainText()
        try:
            parsed = json.loads(text)
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            self.response_edit.setPlainText(pretty)
            self.response_edit.setStyleSheet("")
        #TODO: Rework validation (of rendered template) 
        except Exception:
            pass
        #    self.response_edit.setStyleSheet("background-color: #ffcccc;")

    def _response_focus_out_event(self, event):
        # Wenn Response-Feld geleert wird, auf Default zurücksetzen
        text = self.response_edit.toPlainText()
        if text.strip() == "":
            default = self.server.defaults.get('response', "")
            self.response_edit.setPlainText(default)
        self._validate_and_pretty_response()
        super(QTextEdit, self.response_edit).focusOutEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    config = ConfigModel("config.yaml")
    if config.servers:
        w = ServerInstanceWidget(config.servers[0])
        w.setWindowTitle("Server-Instanz (Demo)")
        w.show()
        sys.exit(app.exec())
    else:
        print("Keine Server-Instanz in config.yaml gefunden.")
