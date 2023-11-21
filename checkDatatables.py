from argparse import ArgumentParser
from enum import Enum
import json

from helpers import (
    doesPathExist,
    findAllObjects,
    findDoubloninList,
    findKeyInList,
    isChn,
    loadFile,
)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-l",
        "--language",
        default="englishUsText",
        help="This sets the language used for sorting the files. Possible values are : japaneseText, englishUsText, chineseTText, chineseSText and koreanText",
    )

    args = parser.parse_args()
    language = args.language

    if language not in [
        "japaneseText",
        "englishUsText",
        "chineseTText",
        "chineseSText",
        "koreanText",
    ]:
        print(
            "Invalid language, Possible values are : japaneseText, englishUsText, chineseTText, chineseSText and koreanText"
        )
        exit(1)

isChn = isChn()

# region Loading files
checkFile = {}

infos = loadFile(path="./Data/x64/datatable/musicinfo.bin")
usb = loadFile(path="./Data/x64/datatable/music_usbsetting.bin")
order = loadFile(path="./Data/x64/datatable/music_order.bin")
attributes = loadFile(path="./Data/x64/datatable/music_attribute.bin")
words = loadFile(path="./Data/x64/datatable/wordlist.bin")
# endregion


# region Classes And Methods
class Genres(Enum):
    Unknown = -1
    Pop = 0
    Anime = 1
    Kids = 2
    Vocaloid = 3
    GameMusic = 4
    NamcoOriginal = 5
    Variety = 6 if isChn else 7
    Classical = 7 if isChn else 8
    if not isChn:
        Custom = 9

    @classmethod
    def _missing_(cls, value):
        return cls.Unknown


class Song:
    id = ""
    uniqueId = -1
    genreNo = -1
    name = ""
    sub = ""
    detail = ""

    def __init__(self, id, uniqueId, genreNo, name, sub, detail):
        self.id = id
        self.uniqueId = uniqueId
        self.genreNo = genreNo
        self.name = name
        self.sub = sub
        self.detail = detail


def initCheckFile():
    global checkFile
    checkFile = {
        "musicinfo.bin": {
            "TotalEntries": len(infos),
            "MaxId": max(infos, key=lambda ev: ev["uniqueId"])["uniqueId"],
            "UniqueIdTooHigh": 0,
            "UniqueIdTooHighList": [],
            "UnusedUniqueIds": 0,
            "UnusedUniqueIdsList": [],
            "Doublons": 0,
            "DoublonsList": [],
            "GenreNoList": [],
        },
    }

    if attributes is not None:
        checkFile["music_attribute.bin"] = {
            "TotalEntries": len(attributes),
            "Missing": 0,
            "MissingList": [],
            "Mismatch": 0,
            "MismatchList": [],
            "Doublons": 0,
            "DoublonsList": [],
        }

    if order is not None:
        checkFile["music_order.bin"] = {
            "TotalEntries": len(order),
            "UniqueEntries": 0,
            "UniqueEntriesList": [],
            "GenreNoList": [],
            "Missing": 0,
            "MissingList": [],
            "Mismatch": 0,
            "MismatchList": [],
        }

    if usb is not None:
        checkFile["music_usbsetting.bin"] = {
            "TotalEntries": len(usb),
            "Missing": 0,
            "MissingList": [],
            "Mismatch": 0,
            "MismatchList": [],
            "Doublons": 0,
            "DoublonsList": [],
        }

    if words is not None:
        checkFile["wordlist.bin"] = {
            "TotalEntries": len(words),
            "MissingSongName": 0,
            "MissingSongNameList": [],
            "MissingSongSub": 0,
            "MissingSongSubList": [],
            "MissingSongDetail": 0,
            "MissingSongDetailList": [],
            "Doublons": 0,
            "DoublonsList": [],
        }

    checkFile.update(
        {
            "GameFiles": {
                "MissingSound": 0,
                "MissingSoundList": [],
                "MissingFumen": 0,
                "MissingFumenList": [],
            },
        }
    )


# endregion

# Loading all songs from musicinfo in an array
songs = []

for song in infos:
    name = findKeyInList(
        list=words,
        key="key",
        keyValue="song_" + song["id"],
        value=language,
    )
    sub = findKeyInList(
        list=words,
        key="key",
        keyValue="song_sub_" + song["id"],
        value=language,
    )
    detail = findKeyInList(
        list=words,
        key="key",
        keyValue="song_detail_" + song["id"],
        value=language,
    )

    songs.append(
        Song(
            id=song["id"],
            uniqueId=song["uniqueId"],
            genreNo=song["genreNo"],
            name=name,
            sub=sub,
            detail=detail,
        )
    )

# Preparing the json file containing the results of this checking script
initCheckFile()

# Checking...
for song in songs:
    # musicinfo.bin
    if infos is not None:
        # Checking for too high of an id
        if song.uniqueId > 1599:
            checkFile["musicinfo.bin"]["UniqueIdTooHigh"] += 1
            checkFile["musicinfo.bin"]["UniqueIdTooHighList"].append(
                {
                    "id": song.id,
                    "uniqueId": song.uniqueId,
                }
            )
        # Listing genres and counting entries for each genres
        genre = {
            "GenreNo": song.genreNo,
            "Name": Genres(song.genreNo).name,
            "NumberofSongs": 0,
        }
        if (
            findKeyInList(
                list=checkFile["musicinfo.bin"]["GenreNoList"],
                key="GenreNo",
                keyValue=song.genreNo,
            )
            is None
        ):
            genre["NumberofSongs"] = len(
                findAllObjects(list=infos, key="genreNo", keyValue=song.genreNo)
            )
            checkFile["musicinfo.bin"]["GenreNoList"].append(genre)
        # Search doublons
        if findDoubloninList(list=infos, key="id", keyValue=song.id):
            if song.id not in checkFile["musicinfo.bin"]["DoublonsList"]:
                checkFile["musicinfo.bin"]["Doublons"] += 1
                checkFile["musicinfo.bin"]["DoublonsList"].append(song.id)

        if findDoubloninList(list=infos, key="uniqueId", keyValue=song.uniqueId):
            if song.id not in checkFile["musicinfo.bin"]["DoublonsList"]:
                checkFile["musicinfo.bin"]["Doublons"] += 1
                checkFile["musicinfo.bin"]["DoublonsList"].append(song.uniqueId)

    # music_usbsetting.bin
    if usb is not None:
        # Check for missing uniqueIds or id and uniqueId mismatches
        orderOccurences = findAllObjects(list=usb, key="id", keyValue=song.id)
        if len(orderOccurences) == 0:
            checkFile["music_usbsetting.bin"]["Missing"] += 1
            checkFile["music_usbsetting.bin"]["MissingList"].append(song.id)
        else:
            for occurence in orderOccurences:
                if not all(
                    [song.id == occurence["id"], song.uniqueId == occurence["uniqueId"]]
                ):
                    if song.id not in checkFile["music_usbsetting.bin"]["MismatchList"]:
                        checkFile["music_usbsetting.bin"]["Mismatch"] += 1
                        checkFile["music_usbsetting.bin"]["MismatchList"].append(
                            {
                                "id": song.id,
                                "ExpectedUniqueId": song.uniqueId,
                                "CurrentUniqueId": occurence["uniqueId"],
                            }
                        )

        # Search doublons
        if findDoubloninList(list=usb, key="id", keyValue=song.id):
            if song.id not in checkFile["music_usbsetting.bin"]["DoublonsList"]:
                checkFile["music_usbsetting.bin"]["Doublons"] += 1
                checkFile["music_usbsetting.bin"]["DoublonsList"].append(song.id)
        if findDoubloninList(list=usb, key="uniqueId", keyValue=song.uniqueId):
            if song.id not in checkFile["musicinfo.bin"]["DoublonsList"]:
                checkFile["music_usbsetting.bin"]["Doublons"] += 1
                checkFile["music_usbsetting.bin"]["DoublonsList"].append(song.uniqueId)

    # music_attribute.bin
    if attributes is not None:
        # Check for missing uniqueIds or id and uniqueId mismatches
        orderOccurences = findAllObjects(list=attributes, key="id", keyValue=song.id)
        if len(orderOccurences) == 0:
            checkFile["music_attribute.bin"]["Missing"] += 1
            checkFile["music_attribute.bin"]["MissingList"].append(song.id)
        else:
            for occurence in orderOccurences:
                if not all(
                    [song.id == occurence["id"], song.uniqueId == occurence["uniqueId"]]
                ):
                    if song.id not in checkFile["music_attribute.bin"]["MismatchList"]:
                        checkFile["music_attribute.bin"]["Mismatch"] += 1
                        checkFile["music_attribute.bin"]["MismatchList"].append(
                            {
                                "id": song.id,
                                "ExpectedUniqueId": song.uniqueId,
                                "CurrentUniqueId": occurence["uniqueId"],
                            }
                        )
        if findDoubloninList(list=attributes, key="id", keyValue=song.id):
            if song.id not in checkFile["music_attribute.bin"]["DoublonsList"]:
                checkFile["music_attribute.bin"]["Doublons"] += 1
                checkFile["music_attribute.bin"]["DoublonsList"].append(song.id)
        if findDoubloninList(list=attributes, key="uniqueId", keyValue=song.uniqueId):
            if song.id not in checkFile["musicinfo.bin"]["DoublonsList"]:
                checkFile["music_attribute.bin"]["Doublons"] += 1
                checkFile["music_attribute.bin"]["DoublonsList"].append(song.uniqueId)

    # music_order.bin
    if order is not None:
        # Check for missing uniqueIds or id and uniqueId mismatches
        orderOccurences = findAllObjects(list=order, key="id", keyValue=song.id)
        if len(orderOccurences) == 0:
            checkFile["music_order.bin"]["Missing"] += 1
            checkFile["music_order.bin"]["MissingList"].append(song.id)
        else:
            songGenres = []
            for occurence in orderOccurences:
                songGenres.append(occurence["genreNo"])
                if not all(
                    [song.id == occurence["id"], song.uniqueId == occurence["uniqueId"]]
                ):
                    if song.id not in checkFile["music_order.bin"]["MismatchList"]:
                        checkFile["music_order.bin"]["Mismatch"] += 1
                        checkFile["music_order.bin"]["MismatchList"].append(
                            {
                                "id": song.id,
                                "ExpectedUniqueId": song.uniqueId,
                                "CurrentUniqueId": occurence["uniqueId"],
                            }
                        )

            # Counting unique entries
            checkFile["music_order.bin"]["UniqueEntries"] += 1
            checkFile["music_order.bin"]["UniqueEntriesList"].append(
                {
                    song.id: songGenres,
                }
            )

    # wordlist.bin
    if words is not None:
        if song.name == "":
            checkFile["wordlist.bin"]["MissingSongName"] += 1
            checkFile["wordlist.bin"]["MissingSongNameList"].append(song.id)
        if song.sub == "":
            checkFile["wordlist.bin"]["MissingSongSub"] += 1
            checkFile["wordlist.bin"]["MissingSongSubList"].append(song.id)
        if song.detail == "":
            checkFile["wordlist.bin"]["MissingSongDetail"] += 1
            checkFile["wordlist.bin"]["MissingSongDetailList"].append(song.id)

    # Gamefiles
    if not doesPathExist("./Data/x64/sound/" + "song_" + song.id + ".nus3bank"):
        checkFile["GameFiles"]["MissingSound"] += 1
        checkFile["GameFiles"]["MissingSoundList"].append(song.id)
    if not doesPathExist("./Data/x64/fumen/" + song.id):
        checkFile["GameFiles"]["MissingFumen"] += 1
        checkFile["GameFiles"]["MissingFumenList"].append(song.id)

# Checking for vacant uniqueIds
for i in range(max(checkFile["musicinfo.bin"]["MaxId"], 1600)):
    key = findKeyInList(list=infos, key="uniqueId", keyValue=i)

    if key is not None:
        # Updating GenreNoList of music_order.bin
        for song in findAllObjects(
            list=order, key="uniqueId", keyValue=key["uniqueId"]
        ):
            genre = {
                "GenreNo": song["genreNo"],
                "Name": Genres(song["genreNo"]).name,
                "NumberofSongs": 0,
            }
            if (
                findKeyInList(
                    list=checkFile["music_order.bin"]["GenreNoList"],
                    key="GenreNo",
                    keyValue=song["genreNo"],
                )
                is None
            ):
                genre["NumberofSongs"] = len(
                    findAllObjects(list=order, key="genreNo", keyValue=song["genreNo"])
                )
                checkFile["music_order.bin"]["GenreNoList"].append(genre)
    else:
        # Finding unused Ids bellow 1599
        if i < 1600:
            checkFile["musicinfo.bin"]["UnusedUniqueIds"] += 1
            checkFile["musicinfo.bin"]["UnusedUniqueIdsList"].append(i)

# Checking for doublons in wordlist
if words is not None:
    for word in words:
        if findDoubloninList(list=words, key="key", keyValue=word["key"]):
            if word["key"] not in checkFile["wordlist.bin"]["DoublonsList"]:
                checkFile["wordlist.bin"]["Doublons"] += 1
                checkFile["wordlist.bin"]["DoublonsList"].append(word["key"])

# Sorting some values for better readability
checkFile["musicinfo.bin"]["GenreNoList"].sort(
    key=lambda x: x["GenreNo"], reverse=False
)
checkFile["music_order.bin"]["GenreNoList"].sort(
    key=lambda x: x["GenreNo"], reverse=False
)

# Writing everything to checks.json
json_object = json.dumps(checkFile, ensure_ascii=False, indent="\t")
# json_object = json.dumps(jsonList, ensure_ascii=False, indent="\t")
with open("./checks.json", "w", encoding="utf8") as outfile:
    outfile.write(json_object)
print("Wrote checks.\n")
