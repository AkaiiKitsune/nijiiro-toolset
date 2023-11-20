from argparse import ArgumentParser
import gzip
from io import StringIO
import json
import os
import shutil

from helpers import doesPathExist, isChn, findKeyInList, loadFile

from encryption import encrypt_file

language = ""

order = None
words = None


def loadFiles():
    global order, words
    # Loading music_order.bin and wordlist.bin
    order = loadFile(path="./Data/x64/datatable/music_order.bin")
    words = loadFile(path="./Data/x64/datatable/wordlist.bin")

    if any([order == None, words == None]):
        print(
            "Couldn't load files. Consider restoring your music_order file using the --restore flag."
        )
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


def sort(reverse: bool):
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

    print("Sorting", str(len(entries)), "entries")

    # Sorting names alphabetically.
    if reverse:
        print("Reversed sorting order!")
    entries.sort(key=lambda x: x.name, reverse=reverse)

    # Backing up the original order file
    if not doesPathExist(path="./Data/x64/datatable/music_order.bin.bak"):
        print("Backed up music_order")
        shutil.move(
            "./Data/x64/datatable/music_order.bin",
            "./Data/x64/datatable/music_order.bin.bak",
        )

    file = {"items": []}
    for entry in entries:
        file["items"].append(entry.toJson())
    # Writing song_order.bin
    json_object = json.dumps(file, ensure_ascii=False, indent="\t")
    if not isChn():
        # Saving compressed bin file for 08.18
        with open("./Data/x64/datatable/music_order.bin", "wb") as outfile:
            outfile.write(gzip.compress(bytes(json_object, encoding="utf-8")))
    else:
        # Saving encrypted compressed bin file for 32.09 CHN
        # This is terrible but it works fine :))
        with open(
            "./Data/x64/datatable/music_order.json", "w", encoding="utf-8"
        ) as outfile:
            outfile.write(json_object)
        encrypted_object = encrypt_file(
            input_file="./Data/x64/datatable/music_order.json"
        )
        os.remove("./Data/x64/datatable/music_order.json")
        with open("./Data/x64/datatable/music_order.bin", "wb") as outfile:
            outfile.write(encrypted_object)


def restore():
    # Checking if we have a backup
    if doesPathExist(path="./Data/x64/datatable/music_order.bin.bak"):
        print("Restoring music_order")
        # Removing current music_order file
        if os.path.isfile("./Data/x64/datatable/music_order.bin"):
            os.remove("./Data/x64/datatable/music_order.bin")
        # Restoring backup
        shutil.move(
            "./Data/x64/datatable/music_order.bin.bak",
            "./Data/x64/datatable/music_order.bin",
        )
    else:
        print("There is no backup to restore.")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--restore",
        action="store_true",
        default=False,
        help="Use this flag to restore a backup of the original file",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        default=False,
        help="Revert sorting order",
    )
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

    if not args.restore:
        loadFiles()
        sort(args.reverse)
    else:
        restore()
