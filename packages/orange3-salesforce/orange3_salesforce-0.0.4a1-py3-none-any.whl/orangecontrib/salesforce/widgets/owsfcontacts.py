"""
Salesforce Contacts Widget
==========================

Widget for fetching contacts data from Salesforce and converting it to Orange data table.
"""

from typing import Optional, List, Dict, Any
import pandas as pd

from Orange.data import Table, Domain, StringVariable, ContinuousVariable
from Orange.widgets import gui, settings
from Orange.widgets.utils.signals import Input, Output
from Orange.widgets.widget import OWWidget, Msg
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpinBox, QMessageBox
from PyQt5.QtCore import Qt

try:
    from simple_salesforce import Salesforce
except ImportError:
    Salesforce = None


class OWSalesforceContacts(OWWidget):
    """Widget for fetching contacts from Salesforce."""
    
    name = "Salesforce Contacts"
    description = "Fetch contacts data from Salesforce and convert to Orange data table"
    icon = "icons/sfdc.svg"
    category = "Salesforce"
    keywords = ["salesforce", "contacts", "data", "fetch"]
    
    class Inputs:
        connection = Input("Connection", object, doc="Salesforce connection object")
    
    class Outputs:
        data = Output("Data", Table, doc="Contacts data as Orange table")
    
    class Error(OWWidget.Error):
        connection_error = Msg("No Salesforce connection provided")
        fetch_error = Msg("Error fetching contacts: {}")
        import_error = Msg("simple-salesforce package not available")
    
    # Settings
    limit = settings.Setting(5)  # Default to 5 rows as requested
    
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
        
        # Connection status
        self.status_label = QLabel("No connection")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
        
        # Row limit
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Number of rows:"))
        self.limit_spin = QSpinBox()
        self.limit_spin.setMinimum(1)
        self.limit_spin.setMaximum(1000)
        self.limit_spin.setValue(self.limit)
        self.limit_spin.valueChanged.connect(self._on_limit_changed)
        limit_layout.addWidget(self.limit_spin)
        layout.addLayout(limit_layout)
        
        # Fetch button
        self.fetch_btn = QPushButton("Fetch Contacts")
        self.fetch_btn.clicked.connect(self._fetch_contacts)
        self.fetch_btn.setEnabled(False)
        layout.addWidget(self.fetch_btn)
        
        # Info label
        info_label = QLabel("This widget will fetch the first 5 contacts from Salesforce by default.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)
        
        self.controlArea.layout().addLayout(layout)
    
    def _on_limit_changed(self, value):
        """Handle limit change."""
        self.limit = value
    
    @Inputs.connection
    def set_connection(self, connection):
        """Set the Salesforce connection."""
        self.connection = connection
        if connection is not None:
            self.status_label.setText("Connected to Salesforce")
            self.status_label.setStyleSheet("color: green;")
            self.fetch_btn.setEnabled(True)
        else:
            self.status_label.setText("No connection")
            self.status_label.setStyleSheet("color: red;")
            self.fetch_btn.setEnabled(False)
            # Clear output
            self.Outputs.data.send(None)
    
    def _fetch_contacts(self):
        """Fetch contacts from Salesforce."""
        if not self.connection:
            self.Error.connection_error()
            return
        
        try:
            # Build SOQL query
            query = f"""
                SELECT Id, FirstName, LastName, Email, Phone, Title, Department, 
                       CreatedDate, LastModifiedDate
                FROM Contact 
                ORDER BY LastModifiedDate DESC 
                LIMIT {self.limit}
            """
            
            # Execute query
            result = self.connection.query(query)
            
            if not result['records']:
                QMessageBox.information(self, "No Data", "No contacts found in Salesforce.")
                return
            
            # Convert to Orange table
            table = self._convert_to_orange_table(result['records'])
            
            # Send output
            self.Outputs.data.send(table)
            
            # Update status
            self.status_label.setText(f"Fetched {len(result['records'])} contacts")
            
        except Exception as e:
            self.Error.fetch_error(str(e))
    
    def _convert_to_orange_table(self, records: List[Dict[str, Any]]) -> Table:
        """Convert Salesforce records to Orange data table."""
        # Define the domain (columns)
        variables = [
            StringVariable("Id"),
            StringVariable("FirstName"),
            StringVariable("LastName"),
            StringVariable("Email"),
            StringVariable("Phone"),
            StringVariable("Title"),
            StringVariable("Department"),
            StringVariable("CreatedDate"),
            StringVariable("LastModifiedDate")
        ]
        
        domain = Domain(variables)
        
        # Prepare data
        data = []
        for record in records:
            row = [
                record.get('Id', ''),
                record.get('FirstName', ''),
                record.get('LastName', ''),
                record.get('Email', ''),
                record.get('Phone', ''),
                record.get('Title', ''),
                record.get('Department', ''),
                record.get('CreatedDate', ''),
                record.get('LastModifiedDate', '')
            ]
            data.append(row)
        
        # Create Orange table
        table = Table.from_list(domain, data)
        return table
