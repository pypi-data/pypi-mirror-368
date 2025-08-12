import importlib
import sys
import threading
from PySide6.QtWidgets import (
    QApplication, QWidget, QSplitter, QTabWidget, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox, QLineEdit, QGroupBox, QMenu, QTabBar
)
from PySide6.QtCore import Qt, QEvent
from .gui_model import ConfigModel, ServerInstance, ClientInstance, ServerInstanceWidget, ClientInstanceWidget, DefaultsWidget

class InstanceTabWidget(QWidget):
    def __init__(self, config, is_server=True, manager=None):
        super().__init__()
        self.config = config
        self.is_server = is_server
        self.manager = manager
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._on_close_tab)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.tabs.tabBar().installEventFilter(self)
        self.tabs.tabBar().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabs.tabBar().customContextMenuRequested.connect(self._show_tab_context_menu)
        self.tabs.tabBarDoubleClicked = getattr(self.tabs, 'tabBarDoubleClicked', None)
        if hasattr(self.tabs, 'tabBarDoubleClicked'):
            self.tabs.tabBarDoubleClicked.connect(self._on_tab_rename)

        # Flag um zu tracken ob wir gerade den + Tab hinzufügen/entfernen
        self._updating_plus_tab = False

        # Buttons
        self.update_btn = QPushButton("Start/Update")
        self.stop_btn = QPushButton("Stop")
        if self.is_server:
            self.update_btn.clicked.connect(self._update_endpoint)
            self.stop_btn.clicked.connect(self._stop_endpoint)
        else:
            self.update_btn.clicked.connect(self._start_client_request)
            self.stop_btn.clicked.connect(self._stop_client_request)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.stop_btn)
        
        # Create defaults widget
        self.defaults_widget = DefaultsWidget(config, is_server)
        self.defaults_widget.defaults_changed.connect(self._on_defaults_changed)
        
        # Create instances group box
        self.instances_group = QGroupBox("Instances")
        instances_layout = QVBoxLayout(self.instances_group)
        instances_layout.addWidget(self.tabs)
        instances_layout.addLayout(btn_layout)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.defaults_widget)
        layout.addWidget(self.instances_group)
        self.setLayout(layout)
        self._init_tabs()
        # Autostart: Endpunkte/Clients beim Start registrieren
        if self.is_server and self.manager:
            for inst in self.config.servers:
                if inst.get_value('autostart'):
                    self._register_endpoint(inst)
        elif not self.is_server and self.manager:
            for inst in getattr(self.config, 'clients', []):
                if inst.get_value('autostart'):
                    self._start_client(inst)
    def eventFilter(self, obj, event):
        if obj == self.tabs.tabBar() and event.type() == QEvent.MouseButtonDblClick:
            # Verwende die neue API: event.position().toPoint() statt event.pos()
            index = self.tabs.tabBar().tabAt(event.position().toPoint())
            if index >= 0:
                self._on_tab_rename(index)
            return True
        return super().eventFilter(obj, event)

    def _show_tab_context_menu(self, position):
        """Zeigt Kontextmenü für Tab-Bar an"""
        index = self.tabs.tabBar().tabAt(position)
        if index < 0:
            return
            
        # Kontextmenü nicht für den + Tab anzeigen
        if self._is_plus_tab(index):
            return
            
        menu = QMenu(self)
        
        # Clone-Aktion
        clone_action = menu.addAction("Clone")
        clone_action.triggered.connect(lambda: self._clone_instance(index))
        
        # Reset-Aktion
        reset_action = menu.addAction("Reset")
        reset_action.triggered.connect(lambda: self._reset_instance_by_index(index))
        
        # Zeige Menü an der Mausposition
        menu.exec_(self.tabs.tabBar().mapToGlobal(position))

    def _on_tab_rename(self, index):
        tab_bar = self.tabs.tabBar()
        old_name = self.tabs.tabText(index)
        editor = QLineEdit(old_name, tab_bar)
        editor.setGeometry(tab_bar.tabRect(index))
        editor.setFocus()
        editor.selectAll()
        editor.editingFinished.connect(lambda: self._finish_tab_rename(index, editor))
        editor.show()

    def _finish_tab_rename(self, index, editor):
        new_name = editor.text().strip()
        if not new_name:
            editor.deleteLater()
            return
        # Eindeutigkeit prüfen
        all_names = [self.tabs.tabText(i) for i in range(self.tabs.count())]
        if new_name in all_names and new_name != self.tabs.tabText(index):
            QMessageBox.warning(self, "Name existiert", "Der Name muss eindeutig sein!")
            editor.deleteLater()
            return
        
        # Alten Namen für Thread-Referenz merken
        old_name = self.tabs.tabText(index)
        
        self.tabs.setTabText(index, new_name)
        # Instanzname im Model aktualisieren
        if self.is_server:
            server_inst = self.config.servers[index]
            old_server_name = server_inst.name
            server_inst.name = new_name
            
            # Bei Server-Threads: Prüfe ob ein Endpoint mit diesem Namen läuft
            if self.manager and hasattr(self.manager, 'rename_endpoint_reference'):
                # Hole die aktuellen Server-Parameter
                host, port, route, _, _, _, _ = self._get_endpoint_params(server_inst)
                # Da sich nur der Name ändert, nicht die Endpoint-Parameter,
                # müssen wir den Endpoint nicht umbenennen - der Name ist nur für die GUI
                # Der Server läuft weiter mit den gleichen Host/Port/Route Parametern
                pass
        else:
            self.config.clients[index].name = new_name
            # Bei Client-Threads: Referenz im Manager aktualisieren
            if self.manager and old_name in self.manager.clients:
                # Hole den laufenden Thread mit dem alten Namen
                thread = self.manager.clients[old_name]
                # Aktualisiere den Namen im Thread selbst
                thread.name = new_name
                # Verschiebe die Referenz im Manager Dictionary
                self.manager.clients[new_name] = thread
                del self.manager.clients[old_name]
        
        editor.deleteLater()
        # Config speichern, damit Änderung persistent ist
        if hasattr(self.config, 'save'):
            self.config.save()

    def _get_client_params(self, inst):
        host_port = inst.get_value('host')
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            host = host.strip()
            port = int(port)
            host = f"{host}:{port}"
        else:
            host = host_port
        route = inst.get_value('route')
        method = inst.get_value('methode')
        request_data = inst.get_value('request')
        period_sec = float(inst.get_value('period_sec') or 1.0)
        loop = bool(inst.get_value('loop'))
        initial_delay_sec = float(inst.get_value('initial_delay_sec') or 0.0)
        return inst.name, host, route, method, request_data, period_sec, loop, initial_delay_sec

    def _start_client(self, inst):
        if not self.manager:
            return
        name, host, route, method, request_data, period_sec, loop, initial_delay_sec = self._get_client_params(inst)
        self.manager.start_client(name, host, route, method, request_data, period_sec, loop, initial_delay_sec=initial_delay_sec)

    def _start_client_request(self):
        idx = self.tabs.currentIndex()
        if idx < 0 or self.is_server or not self.manager:
            return
        inst = getattr(self.config, 'clients', [])[idx]
        self._start_client(inst)

    def _stop_client_request(self):
        idx = self.tabs.currentIndex()
        if idx < 0 or self.is_server or not self.manager:
            return
        inst = getattr(self.config, 'clients', [])[idx]
        self.manager.stop_client(inst.name)

    def _stop_endpoint(self):
        idx = self.tabs.currentIndex()
        if idx < 0 or not self.is_server or not self.manager:
            return
        inst = self.config.servers[idx]
        self._remove_endpoint(inst)

    def _get_endpoint_params(self, inst):
        # Host: host:port
        host_port = inst.get_value('host')
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            host = host_port
            port = 5000
        route = inst.get_value('route')
        methods = inst.get_value('methodes')
        response = inst.get_value('response')
        response_delay_sec = float(inst.get_value('response_delay_sec') or 0.0)
        initial_delay_sec = float(inst.get_value('initial_delay_sec') or 0.0)
        return host, port, route, methods, response, response_delay_sec, initial_delay_sec

    def _register_endpoint(self, inst):
        from .service.endpoint_utils import make_generic_handler
        host, port, route, methods, response, response_delay_sec, initial_delay_sec = self._get_endpoint_params(inst)
        
        #TODO: fix to early validation
        '''
        try:
            import json
            response_json = json.loads(response) if response else {}
        except Exception:
            response_json = {"error": "invalid response json"}
        '''
        handler = make_generic_handler(response, response_delay_sec)

        # put call with potential initial delay in background thread
        thread = threading.Thread(target=self.manager.add_endpoint, args=(host, port, route, methods, initial_delay_sec, handler))
        thread.start()

    def _remove_endpoint(self, inst):
        host, port, route, _, _, _, _ = self._get_endpoint_params(inst)
        self.manager.remove_endpoint(host, port, route)

    def _update_endpoint(self):
        idx = self.tabs.currentIndex()
        if idx < 0 or not self.is_server or not self.manager:
            return
        inst = self.config.servers[idx]
        self._register_endpoint(inst)

    def _init_tabs(self):
        self.tabs.clear()
        # Korrigiere Zugriff auf Clients
        instances = self.config.servers if self.is_server else getattr(self.config, 'clients', [])
        for inst in instances:
            widget = ServerInstanceWidget(inst) if self.is_server else ClientInstanceWidget(inst)
            self.tabs.addTab(widget, inst.name)
        
        # Füge den + Tab hinzu
        self._add_plus_tab()

    def _add_plus_tab(self):
        """Fügt einen kleinen + Tab am Ende hinzu"""
        if not self._updating_plus_tab:
            self._updating_plus_tab = True
            # Erstelle einen leeren Widget für den + Tab
            plus_widget = QWidget()
            plus_index = self.tabs.addTab(plus_widget, "+")
            # Mache den + Tab nicht schließbar
            self.tabs.tabBar().setTabButton(plus_index, QTabBar.ButtonPosition.RightSide, None)
            self._updating_plus_tab = False

    def _is_plus_tab(self, index):
        """Prüft ob der gegebene Index der + Tab ist"""
        return index >= 0 and self.tabs.tabText(index) == "+"

    def _remove_plus_tab(self):
        """Entfernt den + Tab temporär"""
        if not self._updating_plus_tab:
            self._updating_plus_tab = True
            for i in range(self.tabs.count()):
                if self._is_plus_tab(i):
                    self.tabs.removeTab(i)
                    break
            self._updating_plus_tab = False

    def _add_instance(self):
        # Entferne + Tab temporär
        self._remove_plus_tab()
        
        base = "Server" if self.is_server else "Client"
        if self.is_server:
            existing = [inst.name for inst in self.config.servers]
            defaults = self.config.defaults
        else:
            existing = [inst.name for inst in getattr(self.config, 'clients', [])]
            defaults = self.config.raw['defaults']['client']
            server_methods = self.config.raw['defaults']['server']['methodes']
        idx = 1
        while f"{base}{idx}" in existing:
            idx += 1
        name = f"{base}{idx}"
        if self.is_server:
            inst = ServerInstance(name, defaults)
            self.config.servers.append(inst)
            widget = ServerInstanceWidget(inst)
        else:
            inst = ClientInstance(name, defaults, server_methods)
            self.config.clients.append(inst)
            widget = ClientInstanceWidget(inst)
        self.tabs.addTab(widget, name)
        
        # Füge + Tab wieder hinzu
        self._add_plus_tab()
        
        # Wechsle zum neuen Tab (nicht zum + Tab)
        self.tabs.setCurrentIndex(self.tabs.count()-2)

    def _clone_instance(self, source_index):
        """Klont eine Instanz basierend auf dem gegebenen Index"""
        if source_index < 0 or source_index >= self.tabs.count() or self._is_plus_tab(source_index):
            return
            
        # Entferne + Tab temporär
        self._remove_plus_tab()
            
        # Hole die Quell-Instanz
        if self.is_server:
            source_inst = self.config.servers[source_index]
            existing = [inst.name for inst in self.config.servers]
            base = source_inst.name
        else:
            source_inst = getattr(self.config, 'clients', [])[source_index]
            existing = [inst.name for inst in getattr(self.config, 'clients', [])]
            base = source_inst.name
            
        # Finde einen eindeutigen Namen für den Klon
        clone_name = f"{base}_copy"
        idx = 1
        while clone_name in existing:
            clone_name = f"{base}_copy{idx}"
            idx += 1
            
        # Erstelle neue Instanz mit kopierten Werten
        if self.is_server:
            # Kopiere alle Werte aus der Quell-Instanz
            clone_inst = ServerInstance(clone_name, source_inst.defaults)
            for key, value in source_inst.values.items():
                clone_inst.set_value(key, value)
            # Füge in die Liste an der richtigen Position ein (nach source_index)
            self.config.servers.insert(source_index + 1, clone_inst)
            widget = ServerInstanceWidget(clone_inst)
        else:
            # Kopiere alle Werte aus der Quell-Instanz
            clone_inst = ClientInstance(clone_name, source_inst.defaults, source_inst.server_methods)
            for key, value in source_inst.values.items():
                clone_inst.set_value(key, value)
            # Füge in die Liste an der richtigen Position ein (nach source_index)
            self.config.clients.insert(source_index + 1, clone_inst)
            widget = ClientInstanceWidget(clone_inst)
            
        # Füge Tab an der richtigen Position hinzu (nach source_index)
        self.tabs.insertTab(source_index + 1, widget, clone_name)
        
        # Füge + Tab wieder hinzu
        self._add_plus_tab()
        
        # Wechsle zum neuen Tab
        self.tabs.setCurrentIndex(source_index + 1)

    def _reset_instance(self):
        idx = self.tabs.currentIndex()
        if idx < 0:
            return
        self._reset_instance_by_index(idx)

    def _reset_instance_by_index(self, idx):
        """Reset eine Instanz basierend auf dem gegebenen Index"""
        if idx < 0 or idx >= self.tabs.count():
            return
            
        widget = self.tabs.widget(idx)
        # Unterscheide zwischen Server und Client
        if self.is_server:
            for key in widget.server.defaults:
                widget.server.set_value(key, widget.server.defaults[key])
            widget.host_edit.setText(widget.server.get_value('host'))
            widget.autostart_box.setChecked(widget.server.get_value('autostart'))
            widget.initial_delay_edit.setText(str(widget.server.get_value('initial_delay_sec')))
            widget.delay_edit.setText(str(widget.server.get_value('response_delay_sec')))
            widget.route_edit.setText(widget.server.get_value('route'))
            default_methods = widget.server.defaults.get('methodes', [])
            for i, cb in enumerate(widget.methods_checks):
                cb.setChecked(cb.text() in default_methods)
            widget.response_edit.setPlainText(widget.server.get_value('response') if widget.server.get_value('response') else "")
        else:
            for key in widget.client.defaults:
                widget.client.set_value(key, widget.client.defaults[key])
            widget.host_edit.setText(widget.client.get_value('host'))
            widget.autostart_box.setChecked(widget.client.get_value('autostart'))
            widget.initial_delay_edit.setText(str(widget.client.get_value('initial_delay_sec')))
            widget.loop_box.setChecked(widget.client.get_value('loop'))
            widget.period_edit.setText(str(widget.client.get_value('period_sec')))
            widget.route_edit.setText(widget.client.get_value('route'))
            for i, cb in enumerate(widget.methode_checks):
                cb.setChecked(cb.text() == widget.client.get_value('methode'))
            widget.request_edit.setPlainText(widget.client.get_value('request') if widget.client.get_value('request') else "")

    def _delete_instance(self):
        # Verhindere das Löschen des letzten Tabs (+ Plus-Tab)
        actual_tabs = self.tabs.count() - 1  # -1 für den + Tab
        if actual_tabs <= 1:
            return
            
        idx = self.tabs.currentIndex()
        if idx < 0 or self._is_plus_tab(idx):
            return
            
        # Entferne + Tab temporär
        self._remove_plus_tab()
        
        if self.is_server and self.manager:
            inst = self.config.servers[idx]
            self._remove_endpoint(inst)
        elif not self.is_server and self.manager:
            inst = getattr(self.config, 'clients', [])[idx]
            # Stoppe ggf. laufenden Client-Thread vor dem Löschen
            self.manager.stop_client(inst.name)
        # Zugriff auf Clients robust machen
        if self.is_server:
            instances = self.config.servers
        else:
            instances = getattr(self.config, 'clients', [])
        del instances[idx]
        self.tabs.removeTab(idx)
        
        # Füge + Tab wieder hinzu
        self._add_plus_tab()

    def _on_close_tab(self, idx):
        # Verhindere das Schließen des + Tabs
        if self._is_plus_tab(idx):
            return
        self.tabs.setCurrentIndex(idx)
        self._delete_instance()

    def _on_tab_changed(self, idx):
        # Wenn der + Tab ausgewählt wird, erstelle eine neue Instanz
        if idx >= 0 and self._is_plus_tab(idx):
            self._add_instance()

    def _on_defaults_changed(self):
        """Called when default values are changed."""
        # Update all instance widgets to reflect new defaults
        for i in range(self.tabs.count()):
            # Skip the + tab
            if self._is_plus_tab(i):
                continue
                
            widget = self.tabs.widget(i)
            if self.is_server:
                # Update server instance defaults reference
                widget.server.defaults = self.config.raw['defaults']['server']
                # Refresh widgets that display default values
                self._refresh_instance_widget(widget)
            else:
                # Update client instance defaults reference
                widget.client.defaults = self.config.raw['defaults']['client']
                # Update server_methods reference for client instances
                widget.client.server_methods = self.config.raw['defaults']['server']['methodes']
                # Refresh widgets that display default values
                self._refresh_instance_widget(widget)

    def _refresh_instance_widget(self, widget):
        """Refresh an instance widget to show updated default values."""
        if self.is_server:
            # Update the values dictionary with new defaults for unchanged fields
            for key, default_value in widget.server.defaults.items():
                if widget.server.is_default(key):
                    widget.server.values[key] = default_value
 
            # Update text for fields that are at default values
            if widget.server.is_default('host'):
                widget.host_edit.setText(widget.server.get_value('host'))
            if widget.server.is_default('autostart'):
                widget.autostart_box.setChecked(widget.server.get_value('autostart'))
            if widget.server.is_default('initial_delay_sec'):
                widget.initial_delay_edit.setText(str(widget.server.get_value('initial_delay_sec')))
            if widget.server.is_default('response_delay_sec'):
                widget.delay_edit.setText(str(widget.server.get_value('response_delay_sec')))
            if widget.server.is_default('route'):
                widget.route_edit.setText(widget.server.get_value('route'))
            if widget.server.is_default('response'):
                widget.response_edit.setPlainText(widget.server.get_value('response') or "")
                
            # Update methods checkboxes if at default
            if widget.server.is_default('methodes'):
                current_methods = widget.server.get_value('methodes') or []
                for cb in widget.methods_checks:
                    cb.setChecked(cb.text() in current_methods)
        else:
            # Update the values dictionary with new defaults for unchanged fields
            for key, default_value in widget.client.defaults.items():
                if widget.client.is_default(key):
                    widget.client.values[key] = default_value
            
            # Update text for fields that are at default values
            if widget.client.is_default('host'):
                widget.host_edit.setText(widget.client.get_value('host'))
            if widget.client.is_default('autostart'):
                widget.autostart_box.setChecked(widget.client.get_value('autostart'))
            if widget.client.is_default('initial_delay_sec'):
                widget.initial_delay_edit.setText(str(widget.client.get_value('initial_delay_sec')))
            if widget.client.is_default('loop'):
                widget.loop_box.setChecked(widget.client.get_value('loop'))
            if widget.client.is_default('period_sec'):
                widget.period_edit.setText(str(widget.client.get_value('period_sec')))
            if widget.client.is_default('route'):
                widget.route_edit.setText(widget.client.get_value('route'))
            if widget.client.is_default('request'):
                widget.request_edit.setPlainText(widget.client.get_value('request') or "")
                
            # Update method checkboxes if at default
            if widget.client.is_default('methode'):
                current_method = widget.client.get_value('methode')
                for cb in widget.methode_checks:
                    cb.setChecked(cb.text() == current_method)

class MainWindow(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        from .service.rest_server_manager import RestServerManager
        from .service.rest_client_manager import RestClientManager
        self.manager = RestServerManager() #TODO: renaming to avoid confusion
        self.client_manager = RestClientManager()
        self.setWindowTitle("Rest Client / Server Tester")
        splitter = QSplitter(Qt.Horizontal)
        self.server_tabs = InstanceTabWidget(config, is_server=True, manager=self.manager)
        self.client_tabs = InstanceTabWidget(config, is_server=False, manager=self.client_manager)
        splitter.addWidget(self.server_tabs)
        splitter.addWidget(self.client_tabs)
        layout = QVBoxLayout(self)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def closeEvent(self, event):
        self.config.save()
        if hasattr(self, 'manager') and self.manager:
            self.manager.shutdown_all()
        if hasattr(self, 'client_manager') and self.client_manager:
            self.client_manager.stop_all()
        event.accept()
