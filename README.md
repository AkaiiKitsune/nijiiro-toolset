# Nijiiro Toolset

 A collection of various python scripts to help you edit and validate taiko nijiiro game files.

**This is meant to be placed straight in the game's folder**

 ```files
 .\Data\
 .\Executable\ 

 extract here <----
 ```

Please note that this works both on 08.18 and CHN.

## encryption.py

This script allows you to encrypt or decrypt both Datatables and Fumens

**You will need to provide your own aes keys for this script to work.**

```py
class Keys(Enum):
    Datatable = ""  # Add datatable key here
    Fumen = ""  # Add Fumen key here
```

you also need to install the pip module `cryptography`:
> pip install cryptography

here's some usage examples :

```py
# Display the help message
py encryption.py --help

# Decrypting a datatable :
py encryption.py --input "data.bin" --output "data.json"

# Decrypting all datatables :
py encryption.py --input "./Data/x64/datatable" --output "./decrypted_datatables" 

# Encrypting a datatable :
py encryption.py --enc --input "data.json" --output "data.bin" 

# Encrypting all datatables :
py encryption.py --enc --input "./Data/x64/datatable" --output "./decrypted_datatables" 

# Encrypting a folder of fumens for use in CHN :
py encryption.py --enc --fumen --input "./08.18/fumen/" --output "./CHN/fumen/" 
```

## sortAlphabetically.py

This script generates an alphabetically sorted music_order.bin file for a given language.
Possible languages are : japaneseText, englishUsText, chineseTText, chineseSText and koreanText

Here's some usage examples :

```py
# Display the help message
py sortAlphabetically.py --help

# Sort file by english name
py sortAlphabetically.py --language "englishUsText"

# Restore a backup of the original music_order file
py sortAlphabetically.py --restore
```

## checkDatatables.py

This script generates a comprehensive list of various informations regarding your database files for a given language.
It is meant to be used for basic checks such as:

* Listing the amount of songs in your tables
* Listing all vacant entries bellow 1599 to facilitate adding songs in
* Checking their uniqueIds to make sure they don't exceed 1599
* Listing all missing word entries for your songlist
* Checking for doublons in various files
* Checking for id and uniqueId mismatches in various files
* Checking for missing sound and fumen files

Possible languages are : japaneseText, englishUsText, chineseTText, chineseSText and koreanText.

To run this one you simply need to call it like so:

```py
# Check datatables 
py checkDatatables.py --language "englishUsText"
```

The output will be written in a file named `checks.json`
