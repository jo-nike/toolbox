#!/usr/bin/env python
"""Verify if there are floating houdini fx license available. Verify who uses them.
If there are no license available. Email current users.
"""
import subprocess
import re
import os
import rodeo.emailTools
import argparse

def queryHoudiniLicenseServer():
    """Returns the output of ssh a command ran on houdini license server.

    :return data: Information regarding licenses.
    """
    cmd = 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -q -t houdini "sudo /usr/lib/sesi/sesictrl -i"'
    data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    return data

def parseLicenseInfo(data,licenseType):
    """Parse the information queried from the houdini license server. Print information about the total
    and information about the users.

    :param data: result of queryHoudiniLicenseServer

    :return licenseFree: Int. Value equals to number of license free.
    :return users: List. List of users currently using licenses.
    """
    licenseFree = int()
    licenseTotal = int()
    users = []
    # Split the data into license "bundle"
    for entry in data.split('Lic'):
        # Only keep information for Houdini-Master licenses.
        if 'Houdini-Master' in entry and licenseType in 'FX':   
            licenseFree += _getTotalFree(entry)
            licenseTotal += _getTotalAvailable(entry,'Master')
            users += _getUsers(entry)
        # Only keep information for Houdini-Escape licenses.
        if 'Houdini-Escape' in entry and licenseType in 'Core':
            licenseFree += _getTotalFree(entry)
            licenseTotal += _getTotalAvailable(entry,'Escape')
            users += _getUsers(entry)
    
    print '{0}:There are {1} licenses. {2} are free'.format(licenseType, licenseTotal, licenseFree)
    print '{0}:The following users are currently using Floating {0} License: {1}'.format(licenseType, users)

    return licenseFree, users

def _getTotalFree(data):
    """Parse the entry to see how many license are free.

    :param data: Currated data including only houdini-master license.

    :return licenseFree: Int. Number of free license.
    """
    licenseFree = int()
    pattern = '([^\W]+) licenses free'
    results = re.findall(pattern, data)
    for result in results:
        licenseFree += int(result)
    return licenseFree


def _getTotalAvailable(data,licenseType):
    """Parse the entry to see how many license are available in total.

    :param data: Currated data including only houdini-master license.

    :return licenseFree: Int. Number of available licenses.
    """
    licenseTotal = int()
    pattern = '([^\W]+) "Houdini-{0}'.format(licenseType)
    results = re.findall(pattern, data)
    for result in results:
        licenseTotal += int(result)
    return licenseTotal

def _getUsers(data):
    """Parse the entry to see who is using licenses.

    :param data: Currated data including only houdini-master license.

    :return licenseFree: List. List of users currently using licenses.
    """
    users = []
    pattern = re.compile('([^\W]+)@')
    results = re.findall(pattern, data)
    for name in results:
        users.append(name)
    return users

def sendMail(recipients,licenseType):
    """Send an email to the current license users.

    :param recipients: List. List of user received from parseLicenseInfo.
    """
    server = rodeo.emailTools.EMailServer.default()
    message = server.newMessage()
    message.recipients = recipients
    message.recipients.append(os.environ['USER'])
    message.sender = os.environ['USER']
    message.subject = 'Houdini {0} Floating License needed!'.format(licenseType)
    message.text = '''Hi, this is an automated message sent to you because you're currently assigned
one of our rare Houdini-{0} floating license and someone else would like to use it! If possible at all,
could you please hook a bro by freeing up a license?! Thanks!'''.format(licenseType)
    server.send(message)
    print 'Mail sent!'

def run(licenseType):
    data = queryHoudiniLicenseServer()
    # If there is no license currently free, email the current licenses users
    if parseLicenseInfo(data, licenseType)[0] == 0:
        print '--------------------------------------------------------------------------------'
        text = raw_input('Look like all licenses are in used:( Do you want me to send a mail to request one to be freed up? Y/N\n')
        if text.upper() in ['Y']:
            sendMail(parseLicenseInfo(data)[1], licenseType) 

def _getArgs():
    description = 'Verify the current state of the houdini floating pool of licenses'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('version',
                        type=str,
                        help='Type of licenses. FX or Core.')
    return parser.parse_args()

if __name__ == '__main__':
    args = _getArgs()
    licenseType = args.version
    run(licenseType)
