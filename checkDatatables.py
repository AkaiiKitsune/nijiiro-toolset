from enum import Enum
import gzip
from encryption import decrypt_file
import json
import os

from helpers import doesPathExist, findAllObjects, findDoubloninList, findKeyInList

# "japaneseText"
# "englishUsText"
# "chineseTText"
# "koreanText"
# "chineseSText"
language = "japaneseText"

isCHN = False

# region Loading files
checkFile = {}

# Loading musicinfo.bin
try:
    infos = json.load(gzip.open("./Data/x64/datatable/musicinfo.bin", "rb"))["items"]
except:
    try:
        infos = json.loads(
            decrypt_file(input_file="./Data/x64/datatable/musicinfo.bin")
        )["items"]
        isCHN = True
    except:
        print("Couldn't load musicinfo.bin, exiting.")
        exit(0)

# Loading music_usbsetting.bin
try:
    usb = (
        json.loads(
            decrypt_file(input_file="./Data/x64/datatable/music_usbsetting.bin")
        )["items"]
        if isCHN
        else None
    )
except:
    usb = None

# Loading music_order.bin
try:
    order = (
        json.loads(decrypt_file(input_file="./Data/x64/datatable/music_order.bin"))[
            "items"
        ]
        if isCHN
        else json.load(gzip.open("./Data/x64/datatable/music_order.bin", "rb"))["items"]
    )
except:
    order = None

# Loading music_attribute.bin
try:
    attributes = (
        json.loads(decrypt_file(input_file="./Data/x64/datatable/music_attribute.bin"))[
            "items"
        ]
        if isCHN
        else json.load(gzip.open("./Data/x64/datatable/music_attribute.bin", "rb"))[
            "items"
        ]
    )
except:
    attributes = None

# Loading wordlist.bin
try:
    words = (
        json.loads(decrypt_file(input_file="./Data/x64/datatable/wordlist.bin"))[
            "items"
        ]
        if isCHN
        else json.load(gzip.open("./Data/x64/datatable/wordlist.bin", "rb"))["items"]
    )
except:
    words = None
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
    Variety = 6 if not isCHN else 7
    Classical = 7 if not isCHN else 8
    if not isCHN:
        Custom = 9

    @classmethod
    def _missing_(cls, value):
        return cls.Unknown


def initCheckFile():
    global checkFile
    checkFile = {
        "musicinfo.json": {
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
        checkFile["music_attribute.json"] = {
            "TotalEntries": len(attributes),
            "Missing": 0,
            "MissingList": [],
            "Mismatch": 0,
            "MismatchList": [],
            "Doublons": 0,
            "DoublonsList": [],
        }

    if order is not None:
        checkFile["music_order.json"] = {
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
        checkFile["music_usbsetting.json"] = {
            "TotalEntries": len(usb),
            "Missing": 0,
            "MissingList": [],
            "Mismatch": 0,
            "MismatchList": [],
            "Doublons": 0,
            "DoublonsList": [],
        }

    if words is not None:
        checkFile["wordlist.json"] = {
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
    # musicinfo.json
    if infos is not None:
        # Checking for too high of an id
        if song.uniqueId > 1599:
            checkFile["musicinfo.json"]["UniqueIdTooHigh"] += 1
            checkFile["musicinfo.json"]["UniqueIdTooHighList"].append(
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
                list=checkFile["musicinfo.json"]["GenreNoList"],
                key="GenreNo",
                keyValue=song.genreNo,
            )
            is None
        ):
            genre["NumberofSongs"] = len(
                findAllObjects(list=infos, key="genreNo", keyValue=song.genreNo)
            )
            checkFile["musicinfo.json"]["GenreNoList"].append(genre)
        # Search doublons
        if findDoubloninList(list=infos, key="id", keyValue=song.id):
            if song.id not in checkFile["musicinfo.json"]["DoublonsList"]:
                checkFile["musicinfo.json"]["Doublons"] += 1
                checkFile["musicinfo.json"]["DoublonsList"].append(song.id)

    # music_usbsetting.json
    if usb is not None:
        # Check for missing uniqueIds or id and uniqueId mismatches
        orderOccurences = findAllObjects(list=usb, key="id", keyValue=song.id)
        if len(orderOccurences) == 0:
            checkFile["music_usbsetting.json"]["Missing"] += 1
            checkFile["music_usbsetting.json"]["MissingList"].append(song.id)
        else:
            for occurence in orderOccurences:
                if not all(
                    [song.id == occurence["id"], song.uniqueId == occurence["uniqueId"]]
                ):
                    if (
                        song.id
                        not in checkFile["music_usbsetting.json"]["MismatchList"]
                    ):
                        checkFile["music_usbsetting.json"]["Mismatch"] += 1
                        checkFile["music_usbsetting.json"]["MismatchList"].append(
                            {
                                "id": song.id,
                                "ExpectedUniqueId": song.uniqueId,
                                "CurrentUniqueId": occurence["uniqueId"],
                            }
                        )

        # Search doublons
        if findDoubloninList(list=usb, key="id", keyValue=song.id):
            if song.id not in checkFile["music_usbsetting.json"]["DoublonsList"]:
                checkFile["music_usbsetting.json"]["Doublons"] += 1
                checkFile["music_usbsetting.json"]["DoublonsList"].append(song.id)

    # music_attribute.json
    if attributes is not None:
        # Check for missing uniqueIds or id and uniqueId mismatches
        orderOccurences = findAllObjects(list=attributes, key="id", keyValue=song.id)
        if len(orderOccurences) == 0:
            checkFile["music_attribute.json"]["Missing"] += 1
            checkFile["music_attribute.json"]["MissingList"].append(song.id)
        else:
            for occurence in orderOccurences:
                if not all(
                    [song.id == occurence["id"], song.uniqueId == occurence["uniqueId"]]
                ):
                    if song.id not in checkFile["music_attribute.json"]["MismatchList"]:
                        checkFile["music_attribute.json"]["Mismatch"] += 1
                        checkFile["music_attribute.json"]["MismatchList"].append(
                            {
                                "id": song.id,
                                "ExpectedUniqueId": song.uniqueId,
                                "CurrentUniqueId": occurence["uniqueId"],
                            }
                        )
        if findDoubloninList(list=attributes, key="id", keyValue=song.id):
            if song.id not in checkFile["music_attribute.json"]["DoublonsList"]:
                checkFile["music_attribute.json"]["Doublons"] += 1
                checkFile["music_attribute.json"]["DoublonsList"].append(song.id)

    # music_order.json
    if order is not None:
        # Check for missing uniqueIds or id and uniqueId mismatches
        orderOccurences = findAllObjects(list=order, key="id", keyValue=song.id)
        if len(orderOccurences) == 0:
            checkFile["music_order.json"]["Missing"] += 1
            checkFile["music_order.json"]["MissingList"].append(song.id)
        else:
            songGenres = []
            for occurence in orderOccurences:
                songGenres.append(occurence["genreNo"])
                if not all(
                    [song.id == occurence["id"], song.uniqueId == occurence["uniqueId"]]
                ):
                    if song.id not in checkFile["music_order.json"]["MismatchList"]:
                        checkFile["music_order.json"]["Mismatch"] += 1
                        checkFile["music_order.json"]["MismatchList"].append(
                            {
                                "id": song.id,
                                "ExpectedUniqueId": song.uniqueId,
                                "CurrentUniqueId": occurence["uniqueId"],
                            }
                        )

            # Counting unique entries
            checkFile["music_order.json"]["UniqueEntries"] += 1
            checkFile["music_order.json"]["UniqueEntriesList"].append(
                {
                    song.id: songGenres,
                }
            )

    # wordlist.json
    if words is not None:
        if song.name == "":
            checkFile["wordlist.json"]["MissingSongName"] += 1
            checkFile["wordlist.json"]["MissingSongNameList"].append(song.id)
        if song.sub == "":
            checkFile["wordlist.json"]["MissingSongSub"] += 1
            checkFile["wordlist.json"]["MissingSongSubList"].append(song.id)
        if song.detail == "":
            checkFile["wordlist.json"]["MissingSongDetail"] += 1
            checkFile["wordlist.json"]["MissingSongDetailList"].append(song.id)

    # Gamefiles
    if not doesPathExist("./Data/x64/sound/" + "song_" + song.id + ".nus3bank"):
        checkFile["GameFiles"]["MissingSound"] += 1
        checkFile["GameFiles"]["MissingSoundList"].append(song.id)
    if not doesPathExist("./Data/x64/fumen/" + song.id):
        checkFile["GameFiles"]["MissingFumen"] += 1
        checkFile["GameFiles"]["MissingFumenList"].append(song.id)

# Checking for vacant uniqueIds
for i in range(max(checkFile["musicinfo.json"]["MaxId"], 1600)):
    key = findKeyInList(list=infos, key="uniqueId", keyValue=i)

    if key is not None:
        # Updating GenreNoList of music_order.json
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
                    list=checkFile["music_order.json"]["GenreNoList"],
                    key="GenreNo",
                    keyValue=song["genreNo"],
                )
                is None
            ):
                genre["NumberofSongs"] = len(
                    findAllObjects(list=order, key="genreNo", keyValue=song["genreNo"])
                )
                checkFile["music_order.json"]["GenreNoList"].append(genre)
    else:
        # Finding unused Ids bellow 1599
        if i < 1600:
            checkFile["musicinfo.json"]["UnusedUniqueIds"] += 1
            checkFile["musicinfo.json"]["UnusedUniqueIdsList"].append(i)

# Checking for doublons in wordlist
if words is not None:
    for word in words:
        if findDoubloninList(list=words, key="key", keyValue=word["key"]):
            if word["key"] not in checkFile["wordlist.json"]["DoublonsList"]:
                checkFile["wordlist.json"]["Doublons"] += 1
                checkFile["wordlist.json"]["DoublonsList"].append(word["key"])

# Sorting some values for better readability
checkFile["musicinfo.json"]["GenreNoList"].sort(
    key=lambda x: x["GenreNo"], reverse=False
)
checkFile["music_order.json"]["GenreNoList"].sort(
    key=lambda x: x["GenreNo"], reverse=False
)

# Writing everything to checks.json
json_object = json.dumps(checkFile, ensure_ascii=False, indent="\t")
# json_object = json.dumps(jsonList, ensure_ascii=False, indent="\t")
with open("./checks.json", "w", encoding="utf8") as outfile:
    outfile.write(json_object)
print("Wrote checks.\n")
