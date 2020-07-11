# customFunc.py
#
#
from typing import List

import pandas
import numpy as np
import requests
from os import mkdir, remove, listdir, getcwd
from os.path import exists, expanduser, abspath, join
from time import sleep
from ipaddress import ip_address as ipC
import datetime
import json
import pprint
import logging
import threading

#   Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s:')
file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

now = datetime.datetime.now()
userDesk = join(abspath(expanduser('~') + '\\desktop\\'))  # expanduser resolves C:.../users/User


def set_id_index(sel_indexes, _all):
    try:
        res = []
        for index, value in enumerate(sel_indexes):
            res.append(_all[value])
        return res
    except Exception as e:
        raise e


def get_id_index(sel_list, _all):
    #   receive treeview selected and all indexes, parse to match positions and return a list of indexes.
    try:
        res = []
        for val in sel_list:
            for subindex in range(0, len(_all)):
                if val == _all[subindex]:
                    res.append(subindex)
        logger.info('Got selected indexes')
        logger.info(res)
        return res
    except Exception as e:
        raise e


def indexes(arr):
    results = []
    for each in arr:
        if each not in results:
            results.append(each)
        else:
            continue

    return results


def dates(nDate):
    #   nDate == datetime.datetime.now()
    date = str(nDate.year) + '-'
    if len(str(nDate.month)) == 1:
        date += '0' + str(nDate.month) + '-'
    else:
        date += str(nDate.month) + '-'
    if len(str(nDate.day)) == 1:
        date += '0' + str(nDate.day) + '-'
    else:
        date += str(nDate.day) + '-'

    if len(str(nDate.hour)) == 1:
        date += '0' + str(nDate.hour) + '-'
    else:
        date += str(nDate.hour) + '-'

    if len(str(nDate.minute)) == 1:
        date += '0' + str(nDate.minute) + '-'
    else:
        date += str(nDate.minute) + '-'

    if len(str(nDate.second)) == 1:
        date += '0' + str(nDate.second)
    else:
        date += str(nDate.second)

    return date


def revDate(date):
    #   date in yyyy-mm... format
    #   reverse to datetime.datetime
    try:
        if date == '':
            pass
        else:
            y = int(date[:date.find('-')])
            date = date[date.find('-') + 1:]
            m = int(date[:date.find('-')])
            date = date[date.find('-') + 1:]
            d = int(date[:date.find('-')])
            date = date[date.find('-') + 1:]
            h = int(date[:date.find('-')])
            date = date[date.find('-') + 1:]
            mn = int(date[:date.find('-')])
            date = date[date.find('-') + 1:]
            se = int(date)
            dt = datetime.datetime(y, m, d, h, mn, se)
            return dt
    except Exception as e:
        logger.exception('Rev Date', e)


def autodate(date, option, custom_period=''):
    #   date == datetime.datetime.now()
    #   date is current date in yyyy-mm...
    #   will change according to option and return valide date
    #
    # -   Button: 1 dia, 1 semana, 10 dias, 2 semanas, 1 mes, custom period
    if option == custom_period:
        #   calculate for that period
        pass

    elif option == '+':
        nu_date = date + datetime.timedelta(hours=1)

    elif option == '-':
        nu_date = date - datetime.timedelta(hours=1)

    elif option == '1 Day':
        nu_date = date - datetime.timedelta(days=1)
        nu_date = datetime.datetime(nu_date.year, nu_date.month, nu_date.day)

    elif option == '5 Days':
        nu_date = date - datetime.timedelta(days=5)
        nu_date = datetime.datetime(nu_date.year, nu_date.month, nu_date.day)

    elif option == '10 Days':
        nu_date = date - datetime.timedelta(days=10)
        nu_date = datetime.datetime(nu_date.year, nu_date.month, nu_date.day)

    elif option == '1 Week':
        nu_date = date - datetime.timedelta(weeks=1)
        nu_date = datetime.datetime(nu_date.year, nu_date.month, nu_date.day)

    elif option == '2 Weeks':
        nu_date = date - datetime.timedelta(weeks=2)
        nu_date = datetime.datetime(nu_date.year, nu_date.month, nu_date.day)

    elif option == '3 Weeks':
        nu_date = date - datetime.timedelta(weeks=3)
        nu_date = datetime.datetime(nu_date.year, nu_date.month, nu_date.day)

    elif option == '4 Weeks':
        nu_date = date - datetime.timedelta(weeks=4)
        nu_date = datetime.datetime(nu_date.year, nu_date.month, nu_date.day)

    elif option == '30 Days':
        nu_date = date - datetime.timedelta(days=30)
        nu_date = datetime.datetime(nu_date.year, nu_date.month, nu_date.day)

    elif option == 'last s':
        nu_date = datetime.datetime(date.year, date.month - 1, 1)

    elif option == 'last f':
        nu_date = datetime.datetime(date.year, date.month + 1, 1)
        nu_date = nu_date - datetime.timedelta(days=1)

    elif option == 'last df':
        nu_date = datetime.datetime(date.year, date.month, date.day)
        #   today
        nu_date = nu_date - datetime.timedelta(days=1)
        #   yesterday 00:00 hours*
        nu_date = nu_date + datetime.timedelta(days=1)
        #   today 00:00 hours*
        nu_date = nu_date - datetime.timedelta(seconds=1)

    elif option == 'last ds':
        nu_date = datetime.datetime(date.year, date.month, date.day)
        nu_date = nu_date + datetime.timedelta(days=1)
        nu_date = nu_date - datetime.timedelta(days=1)

    dt = dates(nu_date)
    return dt


def testConn(usn, pw, ip, ht, port=''):
    # input validator

    try:
        if not port.isdigit():
            return False, 'Invalid Port'
        url = ''
        if ht == 1:
            # https
            url = 'https://'
        elif ht == 0:
            url = 'http://'

        if validIP(ip):
            print('valid IP', ip)
            url += str(ip) + ':' + port + '/api/getstatus.xml'
            par = {'id': 0, 'username': usn, 'password': pw}
            r = requests.get(url, params=par, verify=False)  # , verify=False
            if r.status_code == 200:
                logger.info('Test successful.')
                r.close()
                return True, r.status_code
            else:
                print('Test Unsuccessful.')
                r.close()
                return False, str(r.status_code) + ' ' + str(r.reason)
        else:
            return False, 'Invalid IP'
            #   return error code too pls

    except Exception as e:
        logger.exception('Credential test error', e)


def findNJoin(idlist):  # receives a list of ['text','0',...]
    st = ''
    for word in idlist:
        if word != '0':
            if idlist.index(word) == len(idlist) - 1:  # only works if its last of list
                st += word
            else:
                st += word + ','
        else:
            continue
        # given for columns=*
    return st.strip(',')  # should return string as "selected,selected,..."


def credSave(usn, pw, ip, ht, port=''):
    #   encrypt / decrypt
    try:
        f = open('qd.rst', "w")
        f.write(usn)
        f.write('\n')
        f.write(pw)
        f.write('\n')
        f.write(ip)
        f.write('\n')
        f.write(port)
        print(port, 'port')
        f.write('\n')
        ht = str(ht)
        print(ht, '1 of https')
        f.write(ht)
        f.close()
    except Exception as e:
        logger.exception('Saving credentials error', e)


def validIP(ip):
    try:
        ipC(ip)
        return True
    except Exception as e:
        logger.exception('ipvalidation error', e)
        return False


def txtlog(lista, path, custom_name=''):
    #   changing to match internal db
    #   creats a csv file to match db.csv of matching results
    #   lista:
    #       [id, id, id]
    try:
        if custom_name == '':
            name = namecheck('Request Catalog', 'csv', path)
        else:
            name = namecheck('Request Catalog - ' + custom_name, 'csv', path)
        dbPath = getcwd() + '/sensors.csv'
        db = pandas.read_csv(dbPath)
        tempList = []

        for thing in range(0, len(lista)):
            tempList.append(db[db['ID'] == lista[thing]])

        res = pandas.concat(tempList, ignore_index=True)
        del res['Unnamed: 0']
        #del res['Unnamed: 8']
        #   unnamed: 0 is row # in original db csv file.
        res.to_csv(name)

    except Exception as e:
        logger.exception('Catalog error', e)


def remove_files(file_list):
    try:
        #   check if exists before deleting although it should exist every time.
        for file in file_list:
            if exists(file):
                remove(file)
            else:
                print(file, 'Not found')
                continue
    except Exception as e:
        logger.exception('remove_files', e)


def merge(path, lista, remove, custom_name=''):
    #   add custom_file_name.
    global merge_list
    logger.info('Name:')
    logger.info(custom_name)
    try:
        if path == userDesk:
            if custom_name == '':

                name = namecheck('Merge', 'csv', path)
                combine = (pandas.read_csv(f, dtype={'ID': np.int32, 'Date Time(RAW)': np.float32, 'Coverage(RAW)': np.float16}, engine='c', sep=',') for f in merge_list)
                #   combine == generator
                #   accessible with next(combine)
                #   change this to not read and load files to memory twice.
                #
                concat = pandas.concat(combine, ignore_index=True, sort=False)
                concat.to_csv(name)
                txtlog(lista, path)

            else:
                name = namecheck(custom_name, 'csv', path)
                combine = (
                pandas.read_csv(f, dtype={'ID': np.int32, 'Date Time(RAW)': np.float32, 'Coverage(RAW)': np.float16},
                                engine='c', sep=',') for f in merge_list)
                #   combine == generator
                #   accessible with next(combine)
                #   change this to not read and load files to memory twice.
                #
                concat = pandas.concat(combine, ignore_index=True, sort=False)
                concat.to_csv(name)
                txtlog(lista, path, custom_name)
            #   after merging clear list.
        else:
            if custom_name == '':
                name = namecheck('Merge', 'csv', path)
                combine = (pandas.read_csv(f, dtype={'ID': np.int32, 'Date Time(RAW)': np.float32, 'Coverage(RAW)': np.float16},
                                engine='c', sep=',') for f in merge_list)
                concat = pandas.concat(combine, ignore_index=True, sort=False)
                concat.to_csv(name)
                txtlog(lista, path,)

            else:
                logger.info("Custom name and path")
                name = namecheck(custom_name, 'csv', path)
                combine = (pandas.read_csv(f, dtype={'ID': np.int32, 'Date Time(RAW)': np.float32, 'Coverage(RAW)': np.float16},
                                engine='c', sep=',') for f in merge_list)

                concat = pandas.concat(combine, ignore_index=True, sort=False)
                concat.to_csv(name)
                txtlog(lista, path, custom_name)

        #   After creating merged csv check if remove request files == True
        if remove == 1:
            remove_files(merge_list)
            merge_list = []
        else:
            #   move all request files to a single folder here, maybe.
            pass
        merge_list = []
    except Exception as e:
        logger.exception('Merge func,', e)


def csvmerger(path, lista, remove, name):
    #   receive all files names to merge from makeRequest()
    #   create folder for each merge "session"
    #       - check if it exists and if it does rename (#)
    #       - will also create the default folder
    #       - create txt file with full list of IDs
    m = 'CSV Merge'
    cont = 1
    if path == userDesk:
        try:
            #   no custom path so create folder on desktop is default
            if exists(userDesk + '\\PRTG API Requests'):
                path = userDesk + '\\PRTG API Requests'
                if exists(path + '\\CSV Merge'):
                    path = userDesk + '\\PRTG API Requests\\' + 'CSV Merge'
                    merge(path, lista, remove, name)
                else:
                    mkdir(path + '\\CSV Merge')
                    path = userDesk + '\\PRTG API Requests\\' + 'CSV Merge'
                    merge(path, lista, remove, name)

            else:
                try:
                    mkdir(userDesk + '\\PRTG API Requests')
                    mkdir(userDesk + '\\PRTG API Requests\\CSV Merge')
                    path = userDesk + '\\PRTG API Requests\\' + 'CSV Merge'
                    merge(path, lista, remove, name)

                except Exception as e:
                    logger.exception('csvmerger mkdir error', e)

        except Exception as e:
            logger.exception('csvmerger in desktop error,', e)

    else:
        #   custom path
        #   check and then create the merge "session" folder.
        try:
            if exists(path + '\\CSV Merge'):
                path = path + '\\CSV Merge'
                merge(path, lista, remove, name)
            else:
                mkdir(path + '\\CSV Merge')
                logger.info('Created custom path directory')
                logger.info(path)
                path = path + '\\CSV Merge'
                merge(path, lista, remove, name)

        except Exception as e:
            logger.exception('Custom path error,', e)


def fileCheck(filename, output):
    filename += '.' + output
    try:
        files = listdir(userDesk + '/prtg test')
        if filename in files:

            return True
        else:
            return False
    except Exception as e:
        logger.exception('file check error', e)


def requestsWithId(ids):
    #   IDS getter&Setter
    #   ADD
    #
    #       -   check from prebuilt csv dataframe if valid id's are in database.csv (in csv.ID)
    #       -   create a bypass for this setting as well.
    #
    #   func that will return a list of all id's to iter through
    #   ids == string.
    #   this func might be joined with open from disk to import csv
    #   as to keep csv management under one roof.
    #   which I guess could then become a class as to be accessed as a csv object always.
    #   hmms
    ids = ids.strip()
    #   remove whitespace from both ends.
    theList: List[int] = []
    reps: List[int] = []
    #   hold each id so we can use to iter and make independent requests and new files
    #   should also verify there are no repeated ids
    commas = ids.count(',')
    try:
        for each in range(0, commas + 1):
            #   for each comma in id's plus one (assuming 1,2,3,4...)
            if each == commas:
                #   its the last loop so last number should be after the last comma.
                temp = ids
                temp = temp.strip()
                if temp.isdigit() and int(temp) not in theList:
                    theList.append(int(temp))
                else:
                    reps.append(temp)
                    continue

            else:
                temp = ids[:ids.find(',')]
                temp = temp.strip()
                if temp.isdigit() and int(temp) not in theList:
                    theList.append(int(temp))
                    ids = ids[ids.find(',') + 1:]
                else:
                    reps.append(temp)
                    ids = ids[ids.find(',') + 1:]
                    continue
        #   returns list of valid ids and the repeated or invalid ids list.
        return theList, reps

    except Exception as e:
        logger.exception('requestsWithId error', e)


def namecheck(name, output, path):
    # checks path, if not checks whether default api folder exists
    if path == userDesk:
        try:
            #   no custom path so create folder on desktop is default
            if exists(userDesk + '\\PRTG API Requests'):
                files = listdir(userDesk + '\\PRTG API Requests')
                if name in str(files):
                    files = str(files)
                    x = files.count(name) + 1
                    return path + '/PRTG API Requests/' + name + ' (' + str(x) + ')' + '.' + output
                else:
                    return path + '/PRTG API Requests/' + name + '.' + output

            else:
                mkdir(userDesk + '\\PRTG API Requests')
                return path + '/PRTG API Requests/' + name + '.' + output
        except Exception as e:
            logger.exception('Namecheck, default path error')
    else:
        try:
            c = 1
            files = listdir(path)
            f = name + '.' + output
            while f in files:
                f = name + ' (' + str(c) + ')' + '.' + output
                c += 1

            return path + '\\' + f

        except Exception as e:
            logger.exception('Namecheck custom path error,', e)
            return False


global merge_list
merge_list = []
total_retries = 0
#   global var to manage amount of retries and break for loop


def fileFolder(filename, output, path, data, merge, ID=''):
    #   takes ^
    #   uses
    #       pandas to read csv, add objectID to csv's
    #       namecheck() to verify not to overwrite a file using "name (x)" format
    #
    try:
        if ID == '':
            file = namecheck(filename, output, path)
            if output == 'json':
                js = json.loads(data)
                formatted_data = json.dumps(js, indent=2)
                f = open(file, 'w')
                f.write(formatted_data)
                f.close()
                return

            f = open(file, 'wb')
            f.write(data)
            f.close()
        else:
            filename += ' ID ' + str(ID)
            file = namecheck(filename, output, path)
            if output == 'json':
                js = json.loads(data)
                formatted_data = json.dumps(js, indent=2)
                f = open(file, 'w')
                f.write(formatted_data)
                f.close()
                return

            f = open(file, 'wb')
            f.write(data)
            f.close()
            try:
                #   adding ID number to ID Column in CSV
                #   only add to Values request.
                if output == 'csv' and 'values' in filename:
                    print('adding ID column')
                    csvfile = pandas.read_csv(file, sep=',', error_bad_lines=False)
                    #   using error_bad_lines to skip last 2 lines of csv file
                    csvfile.ID = ID
                    csvfile.to_csv(file, index=False, sep=',')

                elif output == 'csv' and 'Historic' in filename:
                    print('Hist file:', filename)
                    csvfile = pandas.read_csv(file, sep=',', error_bad_lines=False)
                    csvfile.insert(0, 'ID', ID)
                    csvfile = csvfile[:-1]
                    #   will also remove the last line to remove the "ID,Averages (of X values)"
                    csvfile.to_csv(file, index=False, sep=',')

                if merge == 1:
                    #   if its to be merged add to merge list
                    merge_list.append(file)

            except Exception as e:
                logger.exception('Pandas error,', e)

    except Exception as e:
        logger.exception('Naming error', e)


#   vars to import

dateoptions = [
    'None', 'today', 'yesterday', '7days', '30days', '12months', '6months'
]

devReq = [  # devices
    'objid', 'name', 'type', 'tags', 'active',
    'access', 'comments', 'dependency',
    'device', 'deviceicon', 'downacksens',
    'downsens', 'favorite', 'group', 'grpdev',
    'icon', 'intervalx', 'location', 'message',
    'notifiesx', 'partialdownsens', 'pausedsens',
    'priority', 'probe', 'probegroupdevice', 'schedule',
    'status', 'totalsens', 'undefinedsens',
    'unusualsens', 'upsens', 'warnsens'
]

sensorsReq = [  # sensors
    'objid', 'name', 'type', 'tags',
    'access', 'active', 'comments', 'cumsince', 'dependency',
    'device', 'downacksens', 'downsens', 'downtime',
    'downtimesince', 'downtimetime', 'favorite', 'group',
    'grpdev', 'interval', 'intervalx', 'knowntime',
    'lastcheck', 'lastdown', 'lastup', 'lastvalue',
    'message', 'minigraph', 'notifiesx', 'parentid', 'partialdownsens',
    'pausedsens', 'priority', 'probe', 'probegroupdevice',
    'schedule', 'sensor', 'status', 'totalsens',
    'undefinedsens', 'unusualsens', 'upsens',
    'uptime', 'uptimesince', 'uptimetime', 'warnsens'
]

senstReq = [  # sensortree
    'objid', 'name', 'type', 'tags', 'active',
    'comments', 'basetype', 'baselink', 'parentid'
]

groupsReq = [  # groups
    'objid', 'name', 'type', 'tags', 'active',
    'comments', 'access', 'baselink', 'basetype',
    'condition', 'dependency', 'devicenum',
    'downacksens', 'downsens', 'favorite',
    'fold', 'group', 'groupnum', 'intervalx',
    'message', 'notifiesx', 'parentid',
    'partialdownsens', 'pausedsens', 'priority', 'probe',
    'probegroupdevice', 'schedule', 'status', 'totalsens',
    'undefinedsens', 'unusualsens', 'upsens', 'warnsens'
]

chanReq = [  # channels
    'objid', 'name', 'type', 'tags', 'active',
    'comments', 'lastvalue'
]

probeReq = [  # probes
    'objid', 'name', 'type', 'tags', 'active',
    'comments',
    'access', 'baselink', 'basetype', 'condition',
    'dependency', 'devicenum', 'downacksens', 'downsens',
    'favorite', 'fold', 'groupnum', 'intervalx',
    'message', 'notifiesx', 'parentid', 'partialdownsens',
    'pausedsens', 'priority', 'probe', 'probegroupdevice',
    'schedule', 'status', 'totalsens', 'undefinedsens',
    'unusualsens', 'upsens', 'warnsens'
]

presets = {
    '1': {'nick': 'Preset 1',
          'selected': [],
          'output': 'xml',
          'request': 'request'
          },
    '2': {'nick': 'Preset 2',
          'selected': [],
          'output': 'xml',
          'request': 'request'
          },
    '3': {'nick': 'Preset 3',
          'selected': [],
          'output': 'xml',
          'request': 'request'
          },
    '4': {'nick': 'Preset 4',
          'selected': [],
          'output': 'xml',
          'request': 'request'
          },
    '5': {'nick': 'Preset 5',
          'selected': [],
          'output': 'xml',
          'request': 'request'
          },
}

valReq = [
    'objid', 'type', 'name', 'tags', 'active',
    'comments', 'coverage', 'dateonly', 'datetime',
    'timeonly', 'value_',

]

ticReq = [
    'objid', 'type', 'name', 'tags', 'active',
    'comments', 'dateonly', 'datetime', 'fold', 'message',
    'modifiedby', 'priority', 'status', 'timeonly', 'tickettype',
    'user'

]

repReq = [
    'objid', 'type', 'name', 'tags', 'active',
    'comments', 'email', 'period', 'lastrun', 'nextrun',
    'schedule', 'template',

]

mesReq = [
    'objid', 'type', 'name', 'tags', 'active',
    'status', 'message', 'priority', 'parent', 'datetime',
    'dateonly', 'timeonly', 'comments',
]

tdataReq = [
    'message', 'user', 'datetime', 'modifiedby'
]

storedReq = [
    'size',
]

dictOfChecks = {'Sensors': sensorsReq, 'Groups': groupsReq,
                'Channels': chanReq, 'Sensortree': senstReq,
                'Devices': devReq, 'Values': valReq,
                'Tickets': ticReq, 'Messages': mesReq,
                'Reports': repReq, 'Ticketdata': tdataReq,
                'StoredReports': storedReq
                # 'Channels', 'Devices', 'Groups', 'Messages',
                # 'Reports', 'Sensors', 'Sensortree', 'StoredReports',
                # 'Ticketdata', 'Tickets', 'Toplists', 'Values'

                }
#   end of vars to import
