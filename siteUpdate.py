# pip install --upgrade google-api-python-client oauth2client
# Column: ID	Name	Type	Available	New	leafly

from __future__ import print_function
from googleapiclient.discovery import build 
from httplib2 import Http
from oauth2client import file, client, tools
import sys
import os
from string import Template
import subprocess

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SPREADSHEET_ID = '$SPREADSHEET_ID'
RANGE_NAME = 'Sheet1!A2:F'

SATIVA = []
HYBRID = []
INDICA = []

def _auth():
    store = file.Storage(os.path.join(sys.path[0],'token.json'))
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(os.path.join(sys.path[0], 'credentials.json'), SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    return service

def _getData(service):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    data = result.get('values', [])
    return data

def _addSativaList(divHTML):
    SATIVA.append(divHTML)

def _addHybridList(divHTML):
    HYBRID.append(divHTML)

def _addIndicaList(divHTML):
    INDICA.append(divHTML)

def _getID(data):
    return data[0]

def _getName(data):
    return data[1]

def _getType(data):
    return data[2]

def _getAvailableStatus(data):
    if data[3] == 'TRUE':
        return True
    else:
        return False

def _getNewStatus(data):
    if data[4] == 'TRUE':
        return 'new'
    else:
        return 'strains'

def _getLeafly(data):
    try:
        leaflyLink = data[5]
        return leaflyLink
    except IndexError:
        return 'noleafly.html'

def _buildHTMLStrainButton(leafly, newStatus, name):
    template = "<a href='{0}' target='iframe'><div class='label {1}'>{2}</div></a>"
    div = template.format(leafly, newStatus, name)
    return div

def _buildTemplate():
    templatePath = os.path.join(sys.path[0], 'template.html')
    template = open(templatePath)
    source = Template(template.read())
    dictionary = {'sativa': '\n    '.join(str(x) for x in SATIVA), 'hybrid': '\n    '.join(str(x) for x in HYBRID), 'indica': '\n    '.join(str(x) for x in INDICA)}
    result = source.substitute(dictionary)
    template.close()
    indexHTML = os.path.join(sys.path[0], 'index.html')
    newIndexFile = open(indexHTML, 'w+')
    newIndexFile.write(result)
    newIndexFile.close()

def _scp():
    cmd = "scp -P $PORT {0} $USER@$SERVER:/home/$USER/public_html".format(os.path.join(sys.path[0], 'index.html'))
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()

def main():
    data = _getData(_auth())
    if not data:
        print('No data found.')
    else:
        for row in data:
            id =_getID(row)
            name = _getName(row)
            strainType = _getType(row)
            availableStatus = _getAvailableStatus(row)
            newStatus = _getNewStatus(row)
            leafly = _getLeafly(row)
            if availableStatus:
                divHTML = _buildHTMLStrainButton(leafly, newStatus, name)
                if strainType == 'Sativa':
                    _addSativaList(divHTML)
                if strainType in ['Hybrid', 'Unknown', 'CBD']:
                    _addHybridList(divHTML)
                if strainType == 'Indica':
                    _addIndicaList(divHTML)           
    _buildTemplate()
    _scp()
if __name__ == '__main__':
    main()
