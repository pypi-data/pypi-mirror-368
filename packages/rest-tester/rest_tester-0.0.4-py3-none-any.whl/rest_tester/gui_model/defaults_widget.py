import json
import re
import socket
import rfc3986
from PySide6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QCheckBox, QHBoxLayout, QTextEdit, QGroupBox, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal


class DefaultsWidget(QWidget):
    """Widget for editing default values for server or client instances."""
    
    defaults_changed = Signal()  # Signal when defaults are modified
    
    def __init__(self, config, is_server=True):
        super().__init__()
        self.config = config
        self.is_server = is_server
        self.defaults = config.raw['defaults']['server'] if is_server else config.raw['defaults']['client']
        
        # Create group box
        title = "Server Defaults" if is_server else "Client Defaults"
        self.group_box = QGroupBox(title)
        
        # Set minimum height for consistent layout
        self.setMinimumHeight(250)
        self.setMaximumHeight(300)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.group_box)
        
        # Form layout inside group box
        self.layout = QFormLayout(self.group_box)
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Create form widgets based on server or client type."""
        if self.is_server:
            self._create_server_widgets()
        else:
            self._create_client_widgets()
            
    def _create_server_widgets(self):
        """Create widgets for server defaults."""
        # Host
        self.host_edit = QLineEdit(self.defaults.get('host', ''))
        self.host_edit.textChanged.connect(lambda val: self._on_host_edit('host', val))
        self.host_edit.focusOutEvent = lambda event: self._host_focus_out_event(event)
        self.layout.addRow("Host", self.host_edit)
        
        # Autostart
        self.autostart_box = QCheckBox()
        self.autostart_box.setChecked(self.defaults.get('autostart', False))
        self.autostart_box.stateChanged.connect(lambda _: self._on_edit('autostart', self.autostart_box.isChecked()))
        self.layout.addRow("Autostart", self.autostart_box)
        
        # Initial Delay
        self.initial_delay_edit = QLineEdit(str(self.defaults.get('initial_delay_sec', 0.0)))
        self.initial_delay_edit.textChanged.connect(lambda val: self._on_numeric_edit('initial_delay_sec', val, self.initial_delay_edit))
        self.initial_delay_edit.focusOutEvent = lambda event: self._numeric_focus_out_event(event, 'initial_delay_sec', self.initial_delay_edit)
        self.layout.addRow("Initial Delay (s)", self.initial_delay_edit)
        
        # Response Delay
        self.response_delay_edit = QLineEdit(str(self.defaults.get('response_delay_sec', 0.0)))
        self.response_delay_edit.textChanged.connect(lambda val: self._on_numeric_edit('response_delay_sec', val, self.response_delay_edit))
        self.response_delay_edit.focusOutEvent = lambda event: self._numeric_focus_out_event(event, 'response_delay_sec', self.response_delay_edit)
        self.layout.addRow("Response Delay (s)", self.response_delay_edit)
        
        # Route
        self.route_edit = QLineEdit(self.defaults.get('route', ''))
        self.route_edit.textChanged.connect(lambda val: self._on_route_edit('route', val))
        self.route_edit.focusOutEvent = lambda event: self._route_focus_out_event(event)
        self.layout.addRow("Route", self.route_edit)
        
        # Methods (horizontal checkboxes)
        self.methods_checks = []
        self.methods_layout = QHBoxLayout()
        available_methods = ["GET", "POST"]
        current_methods = self.defaults.get('methodes', [])
        
        for method in available_methods:
            cb = QCheckBox(method)
            cb.setChecked(method in current_methods)
            cb.stateChanged.connect(self._on_methods_changed)
            self.methods_checks.append(cb)
            self.methods_layout.addWidget(cb)
        self.layout.addRow("Methods", self.methods_layout)
        
        # Response (4 lines high)
        self.response_edit = QTextEdit(self.defaults.get('response', ''))
        self.response_edit.setFixedHeight(70)  # Fixed height for exactly 4 lines + 20%
        self.response_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.response_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.response_edit.textChanged.connect(lambda: self._on_edit('response', self.response_edit.toPlainText()))
        self.response_edit.focusOutEvent = self._response_focus_out_event
        self.layout.addRow("Response", self.response_edit)
        
        # Initial validation
        self._validate_and_pretty_response()
        
        # Initial host validation
        self._validate_initial_host()
        
        # Initial numeric validation
        self._validate_initial_numeric()
        
        # Initial route validation
        self._validate_initial_route()
        
    def _create_client_widgets(self):
        """Create widgets for client defaults."""
        # Host
        self.host_edit = QLineEdit(self.defaults.get('host', ''))
        self.host_edit.textChanged.connect(lambda val: self._on_host_edit('host', val))
        self.host_edit.focusOutEvent = lambda event: self._host_focus_out_event(event)
        self.layout.addRow("Host", self.host_edit)
        
        # Autostart
        self.autostart_box = QCheckBox()
        self.autostart_box.setChecked(self.defaults.get('autostart', False))
        self.autostart_box.stateChanged.connect(lambda _: self._on_edit('autostart', self.autostart_box.isChecked()))
        self.layout.addRow("Autostart", self.autostart_box)
        
        # Initial Delay
        self.initial_delay_edit = QLineEdit(str(self.defaults.get('initial_delay_sec', 0.0)))
        self.initial_delay_edit.textChanged.connect(lambda val: self._on_numeric_edit('initial_delay_sec', val, self.initial_delay_edit))
        self.initial_delay_edit.focusOutEvent = lambda event: self._numeric_focus_out_event(event, 'initial_delay_sec', self.initial_delay_edit)
        self.layout.addRow("Initial Delay (s)", self.initial_delay_edit)
        
        # Loop
        self.loop_box = QCheckBox()
        self.loop_box.setChecked(self.defaults.get('loop', False))
        self.loop_box.stateChanged.connect(lambda _: self._on_edit('loop', self.loop_box.isChecked()))
        self.layout.addRow("Loop", self.loop_box)
        
        # Period
        self.period_edit = QLineEdit(str(self.defaults.get('period_sec', 1.0)))
        self.period_edit.textChanged.connect(lambda val: self._on_numeric_edit('period_sec', val, self.period_edit))
        self.period_edit.focusOutEvent = lambda event: self._numeric_focus_out_event(event, 'period_sec', self.period_edit)
        self.layout.addRow("Period (s)", self.period_edit)
        
        # Route
        self.route_edit = QLineEdit(self.defaults.get('route', ''))
        self.route_edit.textChanged.connect(lambda val: self._on_route_edit('route', val))
        self.route_edit.focusOutEvent = lambda event: self._route_focus_out_event(event)
        self.layout.addRow("Route", self.route_edit)
        
        # Method (exclusive checkboxes)
        self.method_checks = []
        self.method_layout = QHBoxLayout()
        server_methods = ["GET", "POST"]
        current_method = self.defaults.get('methode', server_methods[0] if server_methods else 'GET')
        
        for method in server_methods:
            cb = QCheckBox(method)
            cb.setChecked(method == current_method)
            cb.stateChanged.connect(self._on_method_changed)
            self.method_checks.append(cb)
            self.method_layout.addWidget(cb)
        self.layout.addRow("Method", self.method_layout)
        
        # Request (4 lines high)
        self.request_edit = QTextEdit(self.defaults.get('request', ''))
        self.request_edit.setFixedHeight(70)  # Fixed height for exactly 4 lines + 20%
        self.request_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.request_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.request_edit.textChanged.connect(lambda: self._on_edit('request', self.request_edit.toPlainText()))
        self.request_edit.focusOutEvent = self._request_focus_out_event
        self.layout.addRow("Request", self.request_edit)
        
        # Initial validation
        self._validate_and_pretty_request()
        
        # Initial host validation
        self._validate_initial_host()
        
        # Initial numeric validation
        self._validate_initial_numeric()
        
        # Initial route validation
        self._validate_initial_route()
        
    def _on_host_edit(self, key, val):
        """Handle host field changes."""
        self._on_edit(key, val)
    
    def _host_focus_out_event(self, event):
        """Validate host format and update styling."""
        from PySide6.QtWidgets import QLineEdit
        QLineEdit.focusOutEvent(self.host_edit, event)
        
        host = self.host_edit.text().strip()
        is_valid = self._validate_host(host)
        
        if is_valid:
            self.host_edit.setStyleSheet("")
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
            self.host_edit.setStyleSheet("")

    def _validate_initial_numeric(self):
        """Validate numeric fields on startup and set styling accordingly."""
        numeric_fields = []
        
        # Add fields based on server or client type
        if self.is_server:
            numeric_fields = [
                ('initial_delay_sec', self.initial_delay_edit),
                ('response_delay_sec', self.response_delay_edit)
            ]
        else:
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
                widget.setStyleSheet("")

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
            self.route_edit.setStyleSheet("")

    def _on_route_edit(self, key, val):
        """Handle route field changes."""
        is_valid = self._validate_route(val)
        
        if is_valid:
            self._on_edit(key, val)
            self.route_edit.setStyleSheet("")
        else:
            self.route_edit.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")

    def _route_focus_out_event(self, event):
        """Validate route format and update styling."""
        from PySide6.QtWidgets import QLineEdit
        QLineEdit.focusOutEvent(self.route_edit, event)
        
        route = self.route_edit.text().strip()
        is_valid = self._validate_route(route)
        
        if is_valid:
            self.route_edit.setStyleSheet("")
            self._on_edit('route', route)
        else:
            self.route_edit.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")

    def _on_numeric_edit(self, key, value, widget):
        """Handle numeric field changes with validation."""
        is_valid = self._validate_numeric(value)
        
        if is_valid:
            self._on_edit(key, value)
            widget.setStyleSheet("")
        else:
            widget.setStyleSheet("background-color: #ffcccc; border: 1px solid red;")

    def _on_edit(self, key, value):
        """Handle value changes."""
        # Convert numeric values
        if key in ['initial_delay_sec', 'response_delay_sec', 'period_sec']:
            try:
                value = float(value)
            except (ValueError, TypeError):
                # Bei ungültiger Eingabe nichts tun
                return
        
        # Update the defaults
        self.defaults[key] = value
        
        # Emit signal that defaults changed
        self.defaults_changed.emit()
        
    def _numeric_focus_out_event(self, event, key, widget):
        """Handle focus out for numeric fields to ensure proper float formatting."""
        from PySide6.QtWidgets import QLineEdit
        try:
            # Hole den aktuellen Wert und konvertiere zu Float
            current_text = widget.text().strip()
            if current_text == "":
                # Wenn leer, verwende Default - hol aus ursprünglichen config defaults
                if self.is_server:
                    default_value = self.config.raw['defaults']['server'].get(key, 0.0)
                else:
                    default_value = self.config.raw['defaults']['client'].get(key, 0.0)
                widget.setText(str(float(default_value)))
                self.defaults[key] = float(default_value)
                widget.setStyleSheet("")
            else:
                # Validiere den Wert
                is_valid = self._validate_numeric(current_text)
                if is_valid:
                    # Konvertiere zu Float und formatiere
                    float_value = float(current_text)
                    widget.setText(str(float_value))
                    self.defaults[key] = float_value
                    widget.setStyleSheet("")
                else:
                    # Bei ungültiger Eingabe, verwende Default
                    if self.is_server:
                        default_value = self.config.raw['defaults']['server'].get(key, 0.0)
                    else:
                        default_value = self.config.raw['defaults']['client'].get(key, 0.0)
                    widget.setText(str(float(default_value)))
                    self.defaults[key] = float(default_value)
                    widget.setStyleSheet("")
        except (ValueError, TypeError):
            # Bei ungültiger Eingabe, verwende Default
            if self.is_server:
                default_value = self.config.raw['defaults']['server'].get(key, 0.0)
            else:
                default_value = self.config.raw['defaults']['client'].get(key, 0.0)
            widget.setText(str(float(default_value)))
            self.defaults[key] = float(default_value)
            widget.setStyleSheet("")
        
        # Signal senden, dass sich defaults geändert haben
        self.defaults_changed.emit()
        
        # Original focus out event aufrufen
        super(QLineEdit, widget).focusOutEvent(event)
        
    def _on_methods_changed(self):
        """Handle server methods selection (multiple allowed)."""
        selected = [cb.text() for cb in self.methods_checks if cb.isChecked()]
        if not selected:
            # At least one method must be selected
            self.methods_checks[0].setChecked(True)
            selected = [self.methods_checks[0].text()]
        
        self.defaults['methodes'] = selected
        self.defaults_changed.emit()
        
    def _on_method_changed(self):
        """Handle client method selection (exclusive)."""
        sender = self.sender()
        if sender.isChecked():
            # Uncheck all others
            for cb in self.method_checks:
                if cb is not sender:
                    cb.setChecked(False)
            self.defaults['methode'] = sender.text()
        else:
            # Must have at least one selected
            if not any(cb.isChecked() for cb in self.method_checks):
                sender.setChecked(True)
                
        self.defaults_changed.emit()
        
    def _validate_and_pretty_response(self):
        """Validate and format response JSON."""
        if not hasattr(self, 'response_edit'):
            return
            
        text = self.response_edit.toPlainText()
        try:
            parsed = json.loads(text)
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            self.response_edit.setPlainText(pretty)
            self.response_edit.setStyleSheet("")
        #TODO: rework validation (of rendered template)
        except Exception:
            pass
            '''
            if text.strip():  # Only show error if there's content
                self.response_edit.setStyleSheet("background-color: #ffcccc;")
            else:
                self.response_edit.setStyleSheet("")
            '''
                
    def _validate_and_pretty_request(self):
        """Validate and format request JSON."""
        if not hasattr(self, 'request_edit'):
            return
            
        text = self.request_edit.toPlainText()
        try:
            parsed = json.loads(text)
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            self.request_edit.setPlainText(pretty)
            self.request_edit.setStyleSheet("")
        #TODO: rework validation (of rendered template)
        except Exception:
            pass
            '''
            if text.strip():  # Only show error if there's content
                self.request_edit.setStyleSheet("background-color: #ffcccc;")
            else:
                self.request_edit.setStyleSheet("")
            '''
                
    def _response_focus_out_event(self, event):
        """Handle response field focus out."""
        self._validate_and_pretty_response()
        super(QTextEdit, self.response_edit).focusOutEvent(event)
        
    def _request_focus_out_event(self, event):
        """Handle request field focus out."""
        self._validate_and_pretty_request()
        super(QTextEdit, self.request_edit).focusOutEvent(event)
