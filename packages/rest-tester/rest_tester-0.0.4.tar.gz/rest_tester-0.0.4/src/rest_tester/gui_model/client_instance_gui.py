import json
import re
import socket
import rfc3986
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QCheckBox, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt
from .model import ClientInstance

class ClientInstanceWidget(QWidget):
    def __init__(self, client_instance):
        super().__init__()
        self.client = client_instance
        self.layout = QFormLayout(self)
        # Host
        self.host_edit = QLineEdit(self.client.get_value('host'))
        self._set_default_style('host', self.host_edit)
        self.host_edit.textChanged.connect(lambda val: self._on_host_edit(val))
        self.host_edit.focusOutEvent = lambda event: self._host_focus_out_event(event)
        self.layout.addRow("Host", self.host_edit)
        # Autostart
        self.autostart_box = QCheckBox()
        self.autostart_box.setChecked(self.client.get_value('autostart'))
        self._set_default_style('autostart', self.autostart_box)
        self.autostart_box.stateChanged.connect(lambda _: self._on_edit('autostart', self.autostart_box.isChecked(), self.autostart_box))
        self.layout.addRow("Autostart", self.autostart_box)
        # Initial Delay
        self.initial_delay_edit = QLineEdit(str(self.client.get_value('initial_delay_sec')))
        self._set_default_style('initial_delay_sec', self.initial_delay_edit)
        self.initial_delay_edit.textChanged.connect(lambda val: self._on_numeric_edit('initial_delay_sec', val, self.initial_delay_edit))
        self.initial_delay_edit.focusOutEvent = lambda event: self._numeric_focus_out_event(event, 'initial_delay_sec', self.initial_delay_edit)
        self.layout.addRow("Initial Delay (s)", self.initial_delay_edit)
        # Loop
        self.loop_box = QCheckBox()
        self.loop_box.setChecked(self.client.get_value('loop'))
        self._set_default_style('loop', self.loop_box)
        self.loop_box.stateChanged.connect(lambda _: self._on_edit('loop', self.loop_box.isChecked(), self.loop_box))
        self.layout.addRow("Loop", self.loop_box)
        # Period_sec
        self.period_edit = QLineEdit(str(self.client.get_value('period_sec')))
        self._set_default_style('period_sec', self.period_edit)
        self.period_edit.textChanged.connect(lambda val: self._on_numeric_edit('period_sec', val, self.period_edit))
        self.period_edit.focusOutEvent = lambda event: self._numeric_focus_out_event(event, 'period_sec', self.period_edit)
        self.layout.addRow("Period (s)", self.period_edit)
        # Route
        self.route_edit = QLineEdit(self.client.get_value('route'))
        self._set_default_style('route', self.route_edit)
        self.route_edit.textChanged.connect(lambda val: self._on_route_edit(val))
        self.route_edit.focusOutEvent = lambda event: self._route_focus_out_event(event)
        self.layout.addRow("Route", self.route_edit)
        # Methode (Checkboxen horizontal, exklusiv)
        self.methode_checks = []
        self.methode_layout = QHBoxLayout()
        for m in self.client.server_methods:
            cb = QCheckBox(m)
            cb.setChecked(m == self.client.get_value('methode'))
            cb.stateChanged.connect(self._on_methode_changed)
            self.methode_checks.append(cb)
            self.methode_layout.addWidget(cb)
        self.layout.addRow("Methode", self.methode_layout)
        # Request (großes Textfeld)
        self.request_edit = QTextEdit(self.client.get_value('request') if self.client.get_value('request') else "")
        self.request_edit.setMinimumHeight(120)
        self._set_default_style('request', self.request_edit)
        self.request_edit.textChanged.connect(lambda: self._on_edit('request', self.request_edit.toPlainText(), self.request_edit))
        self.request_edit.focusOutEvent = self._request_focus_out_event
        self.layout.addRow("Request", self.request_edit)
        self._validate_and_pretty_request()
        
        # Initial host validation
        self._validate_initial_host()
        
        # Initial numeric validation
        self._validate_initial_numeric()
        
        # Initial route validation
        self._validate_initial_route()

    def _set_default_style(self, key, widget):
        if self.client.is_default(key):
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
            ('period_sec', self.period_edit)
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
                
            # Check for valid path characters (allowing query parameters and templates)
            # Path should not contain spaces or other invalid characters
            # Allow Jinja2 template syntax like {{counter}}
            path_part = route.split('?')[0]  # Get path without query
            if ' ' in path_part:
                return False
            
            # Check for invalid control characters but allow template syntax
            for c in path_part:
                if ord(c) < 32 or ord(c) > 126:
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
            value = self.client.defaults.get(key, "")
            widget.setText(str(value))
            
        # Float-Konvertierung für numerische Felder
        if key in ['initial_delay_sec', 'period_sec']:
            try:
                value = float(value)
            except (ValueError, TypeError):
                # Bei ungültiger Eingabe nichts tun oder Default verwenden
                return
                
        self.client.set_value(key, value)
        self._set_default_style(key, widget)

    def _numeric_focus_out_event(self, event, key, widget):
        """Handle focus out for numeric fields to ensure proper float formatting."""
        try:
            # Hole den aktuellen Wert und konvertiere zu Float
            current_text = widget.text().strip()
            if current_text == "":
                # Wenn leer, verwende Default
                default_value = self.client.defaults.get(key, 0.0)
                widget.setText(str(float(default_value)))
                self.client.set_value(key, float(default_value))
            else:
                # Validiere den Wert
                is_valid = self._validate_numeric(current_text)
                if is_valid:
                    # Konvertiere zu Float und formatiere
                    float_value = float(current_text)
                    widget.setText(str(float_value))
                    self.client.set_value(key, float_value)
                    self._set_default_style(key, widget)
                else:
                    # Bei ungültiger Eingabe, verwende Default
                    default_value = self.client.defaults.get(key, 0.0)
                    widget.setText(str(float(default_value)))
                    self.client.set_value(key, float(default_value))
                    self._set_default_style(key, widget)
        except (ValueError, TypeError):
            # Bei ungültiger Eingabe, verwende Default
            default_value = self.client.defaults.get(key, 0.0)
            widget.setText(str(float(default_value)))
            self.client.set_value(key, float(default_value))
            self._set_default_style(key, widget)
        
        # Original focus out event aufrufen
        super(QLineEdit, widget).focusOutEvent(event)

    def _on_methode_changed(self):
        # Exklusive Auswahl: Nur eine Checkbox darf aktiv sein
        sender = self.sender()
        if sender.isChecked():
            for cb in self.methode_checks:
                if cb is not sender:
                    cb.setChecked(False)
            self.client.set_value('methode', sender.text())
        else:
            # Mindestens eine Checkbox muss aktiv bleiben
            if not any(cb.isChecked() for cb in self.methode_checks):
                sender.setChecked(True)

    def _validate_and_pretty_request(self):
        text = self.request_edit.toPlainText()
        try:
            parsed = json.loads(text)
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            self.request_edit.setPlainText(pretty)
            self.request_edit.setStyleSheet("")
        
        #TODO: rework validation (of rendered template)
        except Exception:
            pass
        #    self.request_edit.setStyleSheet("background-color: #ffcccc;")

    def _request_focus_out_event(self, event):
        text = self.request_edit.toPlainText()
        if text.strip() == "":
            default = self.client.defaults.get('request', "")
            self.request_edit.setPlainText(default)
        self._validate_and_pretty_request()
        super(QTextEdit, self.request_edit).focusOutEvent(event)
