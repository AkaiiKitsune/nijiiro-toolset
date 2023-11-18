import gzip
import json
import shutil

from helpers import doesPathExist, findAllObjects, findKeyInList

from encryption import decrypt_file

# "japaneseText"
# "englishUsText"
# "chineseTText"
# "koreanText"
# "chineseSText"
language = "japaneseText"
isChn = False

# Loading musicinfo.bin, music_order.bin and wordlist.bin
try:
    info = json.load(gzip.open("./Data/x64/datatable/musicinfo.bin", "rb"))["items"]
    order = json.load(gzip.open("./Data/x64/datatable/music_order.bin", "rb"))["items"]
    words = json.load(gzip.open("./Data/x64/datatable/wordlist.bin", "rb"))["items"]
except:
    try:
        info = json.loads(
            decrypt_file(input_file="./Data/x64/datatable/musicinfo.bin")
        )["items"]
        order = json.loads(
            decrypt_file(input_file="./Data/x64/datatable/music_order.bin")
        )["items"]
        words = json.load(gzip.open("./Data/x64/datatable/wordlist.bin", "rb"))["items"]
        isChn = True
    except:
        print("Couldn't load files, exiting.")
        exit(0)


class Entry:
    name = ""
    genreNo = -1
    id = ""
    uniqueId = -1
    closeDispType = -1

    def __init__(self, name, genreNo, id, uniqueId, closeDispType):
        self.name = name
        self.genreNo = genreNo
        self.id = id
        self.uniqueId = uniqueId
        self.closeDispType = closeDispType

    def toJson(self):
        return {
            # "name": self.name,
            "genreNo": self.genreNo,
            "id": self.id,
            "uniqueId": self.uniqueId,
            "closeDispType": self.closeDispType,
        }


# Adding all the existing songs in song_order in an array
entries = []
for entry in order:
    name = findKeyInList(
        list=words,
        key="key",
        keyValue="song_" + entry["id"],
        value=language,
    )

    if name == "":
        print(entry["id"] + " is missing a name")

    entries.append(
        Entry(
            name=name,
            genreNo=entry["genreNo"],
            id=entry["id"],
            uniqueId=entry["uniqueId"],
            closeDispType=entry["closeDispType"],
        )
    )

# # Adding all the missing songs in song_order in an array
# for entry in info:
#     alreadyIn = False
#     occurences = findAllObjects(list=order, key="id", keyValue=entry["id"])
#     if len(occurences) > 0:
#         for occurence in occurences:
#             if entry["genreNo"] == occurence["genreNo"]:
#                 alreadyIn = True
#                 break

#     if not alreadyIn:
#         name = findKeyInList(
#             list=words,
#             key="key",
#             keyValue="song_" + entry["id"],
#             value=language,
#         )

#         if name == "":
#             print(entry["id"] + " is missing a name")
#             continue

#         print("Adding " + entry["id"])
#         entries.append(
#             Entry(
#                 name=name,
#                 genreNo=entry["genreNo"],
#                 id=entry["id"],
#                 uniqueId=entry["uniqueId"],
#                 closeDispType=0,
#             )
#         )

# Sorting names alphabetically.
entries.sort(key=lambda x: x.name, reverse=False)

# Backing up the original order file
if not doesPathExist(path="./Data/x64/datatable/music_order.bin.bak"):
    print("Backed up music_order")
    dest = shutil.move(
        "./Data/x64/datatable/music_order.bin",
        "./Data/x64/datatable/music_order.bin.bak",
    )

file = []
for entry in entries:
    file.append(entry.toJson())
# Writing song_order.bin
json_object = json.dumps(file, ensure_ascii=False, indent="\t")
if not isChn:
    with open("./Data/x64/datatable/music_order.bin", "w", encoding="utf8") as outfile:
        outfile.write(gzip.compress(json_object))
