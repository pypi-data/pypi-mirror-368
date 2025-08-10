"""
Salesforce Authentication Widget
===============================

Widget for authenticating with Salesforce and establishing a connection.
"""

import os
from typing import Optional

from Orange.data import Table
from Orange.widgets import gui, settings
from Orange.widgets.utils.signals import Output
from Orange.widgets.widget import OWWidget, Msg
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

try:
    from simple_salesforce import Salesforce
except ImportError:
    Salesforce = None


class OWSalesforceAuth(OWWidget):
    """Widget for authenticating with Salesforce."""
    
    name = "Salesforce Authentication"
    description = "Authenticate with Salesforce using username/password or access token"
    icon = "icons/sfdc.svg"
    category = "Salesforce"
    keywords = ["salesforce", "authentication", "login"]
    
    class Outputs:
        connection = Output("Connection", object, doc="Salesforce connection object")
    
    class Error(OWWidget.Error):
        auth_error = Msg("Authentication failed: {}")
        import_error = Msg("simple-salesforce package not available")
    
    # Settings
    username = settings.Setting("")
    password = settings.Setting("")
    security_token = settings.Setting("")
    domain = settings.Setting("login")  # login or test
    instance_url = settings.Setting("")
    access_token = settings.Setting("")
    
    def __init__(self):
        super().__init__()
        
        if Salesforce is None:
            self.Error.import_error()
            return
        
        self.connection = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Username/Password section
        self.auth_method = 0  # Default to username/password
        auth_group = gui.radioButtonsInBox(
            self.controlArea, self, "auth_method", 
            ["Username/Password", "Access Token"], 
            "Authentication Method", 
            callback=self._on_auth_method_changed
        )
        
        # Username/Password fields
        self.username_edit = QLineEdit(self.username)
        self.username_edit.setPlaceholderText("Enter Salesforce username")
        self.username_edit.textChanged.connect(self._on_username_changed)
        
        self.password_edit = QLineEdit(self.password)
        self.password_edit.setPlaceholderText("Enter Salesforce password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.textChanged.connect(self._on_password_changed)
        
        self.token_edit = QLineEdit(self.security_token)
        self.token_edit.setPlaceholderText("Enter security token (if required)")
        self.token_edit.textChanged.connect(self._on_token_changed)
        
        # Domain selection
        self.domain_combo = gui.comboBox(
            self.controlArea, self, "domain", 
            items=["login", "test"], 
            label="Domain:"
        )
        
        # Access token field
        self.access_token_edit = QLineEdit(self.access_token)
        self.access_token_edit.setPlaceholderText("Enter access token")
        self.access_token_edit.textChanged.connect(self._on_access_token_changed)
        
        # Instance URL field
        self.instance_url_edit = QLineEdit(self.instance_url)
        self.instance_url_edit.setPlaceholderText("Enter instance URL (e.g., https://na1.salesforce.com)")
        self.instance_url_edit.textChanged.connect(self._on_instance_url_changed)
        
        # Add fields to layout
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        username_layout.addWidget(self.username_edit)
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        password_layout.addWidget(self.password_edit)
        
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("Security Token:"))
        token_layout.addWidget(self.token_edit)
        
        instance_layout = QHBoxLayout()
        instance_layout.addWidget(QLabel("Instance URL:"))
        instance_layout.addWidget(self.instance_url_edit)
        
        # Add to main layout
        layout.addLayout(username_layout)
        layout.addLayout(password_layout)
        layout.addLayout(token_layout)
        layout.addLayout(instance_layout)
        
        # Access token layout
        access_token_layout = QHBoxLayout()
        access_token_layout.addWidget(QLabel("Access Token:"))
        access_token_layout.addWidget(self.access_token_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self._connect)
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self._disconnect)
        self.disconnect_btn.setEnabled(False)
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        
        layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
        
        self.controlArea.layout().addLayout(layout)
        
        # Set initial state
        self._on_auth_method_changed()
    
    def _on_auth_method_changed(self):
        """Handle authentication method change."""
        if self.auth_method == 0:  # Username/Password
            self.username_edit.setEnabled(True)
            self.password_edit.setEnabled(True)
            self.token_edit.setEnabled(True)
            self.domain_combo.setEnabled(True)
            self.access_token_edit.setEnabled(False)
            self.instance_url_edit.setEnabled(False)
        else:  # Access Token
            self.username_edit.setEnabled(False)
            self.password_edit.setEnabled(False)
            self.token_edit.setEnabled(False)
            self.domain_combo.setEnabled(False)
            self.access_token_edit.setEnabled(True)
            self.instance_url_edit.setEnabled(True)
    
    def _on_username_changed(self, text):
        """Handle username change."""
        self.username = text
    
    def _on_password_changed(self, text):
        """Handle password change."""
        self.password = text
    
    def _on_token_changed(self, text):
        """Handle security token change."""
        self.security_token = text
    
    def _on_access_token_changed(self, text):
        """Handle access token change."""
        self.access_token = text
    
    def _on_instance_url_changed(self, text):
        """Handle instance URL change."""
        self.instance_url = text
    
    def _connect(self):
        """Establish connection to Salesforce."""
        try:
            if self.auth_method == 0:  # Username/Password
                if not self.username or not self.password:
                    QMessageBox.warning(self, "Missing Information", "Please enter username and password.")
                    return
                
                # Combine password and security token
                full_password = self.password
                if self.security_token:
                    full_password += self.security_token
                
                self.connection = Salesforce(
                    username=self.username,
                    password=full_password,
                    domain=self.domain
                )
            else:  # Access Token
                if not self.access_token or not self.instance_url:
                    QMessageBox.warning(self, "Missing Information", "Please enter access token and instance URL.")
                    return
                
                self.connection = Salesforce(
                    instance_url=self.instance_url,
                    session_id=self.access_token
                )
            
            # Test connection
            self.connection.query("SELECT Id FROM User LIMIT 1")
            
            # Update UI
            self.status_label.setText("Connected successfully")
            self.status_label.setStyleSheet("color: green;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            
            # Send connection output
            self.Outputs.connection.send(self.connection)
            
        except Exception as e:
            self.Error.auth_error(str(e))
            self.connection = None
    
    def _disconnect(self):
        """Disconnect from Salesforce."""
        self.connection = None
        self.status_label.setText("Not connected")
        self.status_label.setStyleSheet("color: red;")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        
        # Clear output
        self.Outputs.connection.send(None)
    
    def onDeleteWidget(self):
        """Clean up when widget is deleted."""
        if self.connection:
            self._disconnect()
        super().onDeleteWidget()
