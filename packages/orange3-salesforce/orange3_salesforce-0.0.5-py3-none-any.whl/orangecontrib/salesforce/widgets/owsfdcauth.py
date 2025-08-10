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
from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox
)
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
        # Main layout with proper margins and spacing
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title and description
        title_label = QLabel("Salesforce Connection")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 15px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        desc_label = QLabel("Choose your authentication method and enter your credentials")
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 13px; margin-bottom: 20px;")
        desc_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # Authentication method selection
        auth_group = gui.radioButtonsInBox(
            self.controlArea, self, "auth_method", 
            ["Username & Password", "Access Token"], 
            "Authentication Method", 
            callback=self._on_auth_method_changed
        )
        main_layout.addWidget(auth_group)
        
        # Username/Password section
        self.username_password_group = gui.groupBox(
            self.controlArea, "Login Credentials"
        )
        up_layout = QVBoxLayout()
        up_layout.setSpacing(15)
        up_layout.setContentsMargins(15, 15, 15, 15)
        
        # Username field
        username_layout = QHBoxLayout()
        username_layout.setSpacing(15)
        username_label = QLabel("Username:")
        username_label.setMinimumWidth(120)
        username_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.username_edit = QLineEdit(self.username)
        self.username_edit.setPlaceholderText("your.email@company.com")
        self.username_edit.setMinimumHeight(35)
        self.username_edit.textChanged.connect(self._on_username_changed)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit, 1)  # Stretch to fill space
        up_layout.addLayout(username_layout)
        
        # Password field
        password_layout = QHBoxLayout()
        password_layout.setSpacing(15)
        password_label = QLabel("Password:")
        password_label.setMinimumWidth(120)
        password_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.password_edit = QLineEdit(self.password)
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(35)
        self.password_edit.textChanged.connect(self._on_password_changed)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit, 1)  # Stretch to fill space
        up_layout.addLayout(password_layout)
        
        # Security token field
        token_layout = QHBoxLayout()
        token_layout.setSpacing(15)
        token_label = QLabel("Security Token:")
        token_label.setMinimumWidth(120)
        token_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.token_edit = QLineEdit(self.security_token)
        self.token_edit.setPlaceholderText("Optional - append to password if required")
        self.token_edit.setMinimumHeight(35)
        self.token_edit.textChanged.connect(self._on_token_changed)
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_edit, 1)  # Stretch to fill space
        up_layout.addLayout(token_layout)
        
        # Domain selection
        domain_layout = QHBoxLayout()
        domain_layout.setSpacing(15)
        domain_label = QLabel("Environment:")
        domain_label.setMinimumWidth(120)
        domain_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.domain_combo = gui.comboBox(
            self.username_password_group, self, "domain", 
            items=["Production (login.salesforce.com)", "Sandbox (test.salesforce.com)"], 
            label=""
        )
        self.domain_combo.setMinimumHeight(35)
        domain_layout.addWidget(domain_label)
        domain_layout.addWidget(self.domain_combo, 1)  # Stretch to fill space
        up_layout.addLayout(domain_layout)
        
        self.username_password_group.setLayout(up_layout)
        main_layout.addWidget(self.username_password_group)
        
        # Access Token section
        self.access_token_group = gui.groupBox(
            self.controlArea, "API Access"
        )
        at_layout = QVBoxLayout()
        at_layout.setSpacing(15)
        at_layout.setContentsMargins(15, 15, 15, 15)
        
        # Access token field
        at_layout_layout = QHBoxLayout()
        at_layout_layout.setSpacing(15)
        at_label = QLabel("Access Token:")
        at_label.setMinimumWidth(120)
        at_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.access_token_edit = QLineEdit(self.access_token)
        self.access_token_edit.setPlaceholderText("pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        self.access_token_edit.setMinimumHeight(35)
        self.access_token_edit.textChanged.connect(self._on_access_token_changed)
        at_layout_layout.addWidget(at_label)
        at_layout_layout.addWidget(self.access_token_edit, 1)  # Stretch to fill space
        at_layout.addLayout(at_layout_layout)
        
        # Instance URL field
        url_layout = QHBoxLayout()
        url_layout.setSpacing(15)
        url_label = QLabel("Instance URL:")
        url_label.setMinimumWidth(120)
        url_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.instance_url_edit = QLineEdit(self.instance_url)
        self.instance_url_edit.setPlaceholderText("https://na1.salesforce.com")
        self.instance_url_edit.setMinimumHeight(35)
        self.instance_url_edit.textChanged.connect(self._on_instance_url_changed)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.instance_url_edit, 1)  # Stretch to fill space
        at_layout.addLayout(url_layout)
        
        self.access_token_group.setLayout(at_layout)
        main_layout.addWidget(self.access_token_group)
        
        # Connection status
        status_group = gui.groupBox(
            self.controlArea, "Connection Status"
        )
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(15, 15, 15, 15)
        
        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 15px; background-color: #fdf2f2; border: 1px solid #f5c6cb; border-radius: 6px; font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setMinimumHeight(50)
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        self.connect_btn = QPushButton("Connect to Salesforce")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 180px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.connect_btn.clicked.connect(self._connect)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 140px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.disconnect_btn.clicked.connect(self._disconnect)
        self.disconnect_btn.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Add main layout to control area with proper margins
        control_layout = self.controlArea.layout()
        control_layout.setContentsMargins(20, 20, 20, 20)
        control_layout.addLayout(main_layout)
        
        # Set initial state
        self._on_auth_method_changed()
    
    def _on_auth_method_changed(self):
        """Handle authentication method change."""
        if self.auth_method == 0:  # Username & Password
            self.username_password_group.setVisible(True)
            self.access_token_group.setVisible(False)
        else:  # Access Token
            self.username_password_group.setVisible(False)
            self.access_token_group.setVisible(True)
    
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
                
                # Map domain selection to actual Salesforce URLs
                domain_url = "login.salesforce.com" if self.domain == 0 else "test.salesforce.com"
                
                self.connection = Salesforce(
                    username=self.username,
                    password=full_password,
                    domain=domain_url
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
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; padding: 15px; background-color: #d5f4e6; border: 1px solid #a9dfbf; border-radius: 6px; font-size: 14px;")
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
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 15px; background-color: #fdf2f2; border: 1px solid #f5c6cb; border-radius: 6px; font-size: 14px;")
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        
        # Clear output
        self.Outputs.connection.send(None)
    
    def onDeleteWidget(self):
        """Clean up when widget is deleted."""
        if self.connection:
            self._disconnect()
        super().onDeleteWidget()
