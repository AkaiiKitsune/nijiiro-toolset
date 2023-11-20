import gzip
import json
import os

from encryption import decrypt_file


def isChn():
    return os.path.exists("./Data/x64/datatable/music_usbsetting.bin")


def loadFile(path: str):
    if doesPathExist(path):
        try:
            if not isChn():
                # Loading files for 08.18
                return json.load(gzip.open(path, "rb"))["items"]
            else:
                # Loading files for 32.09 CHN
                return json.loads(decrypt_file(input_file=path))["items"]
        except Exception as error:
            print(error)
            print("Couldn't load", path)
            return None
    else:
        print(path, "doesn't exist")


def findKeyInList(list: list, key: str, keyValue, value=None):
    for object in list:
        try:
            if object[key] == keyValue:
                if value is not None:
                    return object[value]
                else:
                    return object
        except:
            if value is not None:
                print(
                    value
                    + " doesn't exist in "
                    + str(object)
                    + ", are you using the right language ?"
                )
            exit(0)

    if value is not None:
        return ""
    else:
        return None


def findAllObjects(list: list, key: str, keyValue):
    templist = []
    templist.append(list)
    objects = []

    for element in templist[0]:
        if element[key] == keyValue:
            objects.append(element)

    return objects


def findDoubloninList(list: list, key: str, keyValue):
    if len(findAllObjects(list=list, key=key, keyValue=keyValue)) > 1:
        return True
    return False


def doesPathExist(path: str):
    if os.path.exists(path):
        return True
    return False
