# Orange3-Salesforce

This allows users to interact and manage data in Salesforce directly within Orange3. This is only possible because of the fantastic library [simple-salesforce](https://github.com/simple-salesforce/simple-salesforce).

## Installation

### Option 1: Install via Orange3 Add-ons Manager (Recommended)
1. Open Orange3
2. Go to Options → Add-ons
3. Click "Add more..." 
4. Search for "orange3-salesforce"
5. Click Install

### Option 2: Install from Source
```bash
git clone https://github.com/yourusername/orange3-salesforce.git
cd orange3-salesforce
pip install -e .
```

**Note**: This extension uses the `orangeaddons` namespace to avoid conflicts with existing Orange3 packages.

## Features

### Current (MVP)
- **Salesforce Authentication Widget**: Connect to Salesforce orgs using username/password + security token
- **Salesforce Query Widget**: Execute SOQL queries and retrieve data as Orange3 tables
- Support for Contacts and Opportunities objects
- Simple dropdown selection for common objects

### Planned
- Bulk create, update, and delete operations
- Data validation and error handling
- Support for custom objects
- Advanced SOQL query builder

## Usage

### Basic Workflow
1. **Connect**: Use the Salesforce Authentication widget to connect to your org
2. **Query**: Use the Salesforce Query widget to retrieve data
3. **Analyze**: Use Orange3's built-in data analysis tools on your Salesforce data

### Example Workflow
1. Drag "Salesforce Authentication" widget to canvas
2. Enter your Salesforce credentials and click "Connect"
3. Drag "Salesforce Query" widget to canvas
4. Connect the authentication output to the query input
5. Select an object (Contact/Opportunity) and execute query
6. View results in Orange3's data table

## Requirements

- Orange3
- Python 3.7+
- simple-salesforce
- requests
- pandas


## License

MIT License - see LICENSE file for details




## TO BE DELETED

Local testing

```
/Applications/Orange.app/Contents/MacOS/PythonApp -m pip install docopt
```




