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

here's some examples :

```py
# Display the help message
py .\encryption.py --help

# Decrypting a datatable :
py .\encryption.py --input "data.bin" --output "data.json"

# Encrypting a datatable :
py .\encryption.py --enc --input "data.json" --output "data.bin" 

# Encrypting a fumen for use in CHN :
py .\encryption.py --enc --fumen --input "data_e.bin" --output "data_e.bin" 
```

## checkDatatables.py

This script generates a comprehensive list of various informations regarding your database files. It is meant to be used for basic checks such as:

* Listing the amount of songs in your tables
* Listing all vacant entries bellow 1599 to facilitate adding songs in
* Checking their uniqueIds to make sure they don't exceed 1599
* Listing all missing word entries for your songlist
* Checking for doublons in various files
* Checking for id and uniqueId mismatches in various files
* Checking for missing sound and fumen files

To run this one you simply need to call it like so:

> py .\checkDatatables.py

The output will be written in a file named `checks.json`