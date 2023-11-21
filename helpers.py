import gzip
import json
import os

from encryption import decrypt_file


def isChn():
    try:
        try:
            # Trying to load file for 08.18
            json.load(gzip.open("./Data/x64/datatable/musicinfo.bin", "rb"))["items"]
            return False
        except Exception as error:
            # Trying to load file for 32.09 CHN
            json.loads(decrypt_file(input_file="./Data/x64/datatable/musicinfo.bin"))[
                "items"
            ]
            return True
    except Exception as error:
        print(error)
        print("Couldn't find musicinfo.bin, assuming 08.18")


def loadFile(path: str):
    if doesPathExist(path):
        try:
            if not isChn():
                # Loading files for 08.18
                file = json.load(gzip.open(path, "rb"))["items"]
                print("Successfully loaded", path)
                return file
            else:
                # Loading files for 32.09 CHN
                file = json.loads(decrypt_file(input_file=path))["items"]
                print("Successfully loaded", path)
                return file
        except Exception as error:
            print(error)
            print("Couldn't load", path)
            return None
    else:
        print(path, "doesn't exist")


def findKeyInList(list: list, key: str, keyValue, value=None):
    try:
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
    except Exception as error:
        return None

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
