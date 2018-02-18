#!/usr/bin/env python
""" Create folders on already existing project for assets or shots.
Use with 3 arguments: project entityType folderWanted
e.g. got7 S /data/description
e.g. brt A /data/layout
"""
import os
import argparse
import errno

#PROJECT_LOCATION = '/rdo/shows'
PROJECT_LOCATION = '/home/jniquet'

def _getBasePath(project, entity):
    basePath = os.path.join(PROJECT_LOCATION, project)
    if entity == 'A':
        basePath = os.path.join(PROJECT_LOCATION, project, '_asset')
    return basePath

def _listSequence(basePath):
    projectBase = os.listdir(basePath)
    sequenceList = [x for x in projectBase if not x.startswith('_') and not x.startswith('.')]
    return sequenceList

def _listAllShots(basePath, sequenceName):
    shots = []
    for sequence in sequenceName:
        seqBase = os.listdir(os.path.join(basePath, sequence))
        for x in seqBase:
            if not x.startswith('_') and not x.startswith('.'):
                shot = os.path.join(basePath,sequence,x)
                shots.append(shot)
    for x in sequenceName:
        shots.append(os.path.join(basePath, x,'_shot'))
    shots.append(os.path.join(basePath, '_seq', '_shot'))
    return shots

def buildAssetPath(basePath, assetNames):
    assets = []
    for asset in assetNames:
        assetPath = os.path.join(basePath, asset)
        assets.append(assetPath)
    assets.append(os.path.join(basePath,'_asset_template'))
    return assets

def _listAsset(basePath):
    projectBase = os.listdir(basePath)
    assetList = [x for x in projectBase if not x.startswith('_') and not x.startswith('.')]
    return assetList

def finalPaths(allPaths, folderName):
    paths = []
    for x in allPaths:
        paths.append(x+folderName)
    return paths

def confirm(pathsList):
    for paths in pathsList:
        print 'Creating {0}'.format(paths)
    text = raw_input('This is what will be run. Continue? y/N ')
    if text.upper() in ['Y']:
        execute(pathsList)

def execute(pathsList):
    os.umask(0)
    for paths in pathsList:
        try:
            os.makedirs(paths, 0777)
            print 'Creating {0}'.format(paths)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(paths):
                print '{0} exists already! Skipping...'.format(paths)
                pass
            else:
                raise

def run(project, entity, folderName):
    basePath = _getBasePath(project, entity)
    if not folderName.startswith('/'):
        folderName = '/' + folderName
    if entity == 'S':
        sequenceName = _listSequence(basePath)
        shotPath = _listAllShots(basePath, sequenceName)
        pathsList =  finalPaths(shotPath, folderName)
        confirm(pathsList)
    elif entity == 'A':
        assetNames = _listAsset(basePath)
        assetPath = buildAssetPath(basePath, assetNames)
        pathsList = finalPaths(assetPath, folderName)
        confirm(pathsList)
    else:
        print 'Wrong entity type, A for asset or S for shot are accepted value. Not {0}...'.format(entity)

def _getArgs():
    description = 'Add folders to already existing shots or assets'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('project',
                        type=str,
                        help='Project name e.g. got7')
    parser.add_argument('type',
                        type=str,
                        help='[A]sset or [S]hot')
    parser.add_argument('folderName',
                        type=str,
                        help='Folder to add. From the base of the entity e.g. /data/description')
    return parser.parse_args()

if __name__ == '__main__':
    args = _getArgs()
    project = args.project
    entity = args.type
    folderName = args.folderName
    run(project, entity, folderName)