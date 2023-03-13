# Pantastic

Scan a computer for the existance of Credit Card PANs. This script contains configurations
to ignore IINs, major identifiers, specific card numbers, file types and deprecated issuers.

The script will analyse and identify card numbers from 12 to 19 digits in length across
many different types of industries. Cards will be identified by their IIN and Luhn check
compliance. Cards will be detected as single numbers or even as multiple groups of digits. Various
options are included to assist in the identification of false positives.

All options listed below can be used within configuration files. For example:

`python ./pantastic.py --config_file=ignore_uatp.ini`

Or to override a value in a configuration file, specify the value on the
command line.

`python ./pantastic.py --config_file=ignore_uatp.ini --dir=/`

# Installation

This version has been updated to support Python 3. Due to the conversion, some of the old 2.x standard
libraries have been replaced. This project now uses [PDM](https://pdm.fming.dev/latest/) as its dependency manager.

You will also need Python 3.9+ to run this.

Once PDM is installed, to install dependencies you can issue the command:

`pdm install`

This will attempt to install the required dependencies for this project.

PLEASE NOTE THAT THE PYTHON 3.x CONVERSION GETS THE PROJECT INTO A WORKING
STATE AND IS NOT A COMPLETE RE-WRITE OF THE APPLICATION.

## Quickstart

Download or clone this into a folder somewhere. Include it in your path if you like. Then:

`python ./pantastic.py --dir=/ --ignore_paths=ignore_paths.txt --ignore_file_extensions=ignore_extensions.txt --verbose=True`

This will scan the root of a PC, ignoring common file extensions and common
Linux paths which don't really store data and then send the results to the
screen.

## Usage

python ./pantastic.py [--config_file=*file*] [--log_file=*file*] [--log_level=*level*] [--ignore_cards=*list file*] [--ignore_iins=*list file*] [--ignore_industries=*list file*] [--include_deprecated] [--minimum_digits=*integer*] [--maximum_digits=*integer*] [--cards_per_file=*integer*] [--ignore_file_extensions=*list file*] [--unmask_card_number] [--max_group_count=*integer*] [--max_group_distance=*integer*] [--output=*file*] [--verbose] --dir=*location* *or* --file=*file*

**--config_file**
[*filename*] A config file to use during operation. Files are in INI file format and the
options are identical to the command line option names. Default is `./pantastic.ini`

**--log_file**
[*filename*] Write all operations to this file. Default is `./app.log`

**--log_level**
[*level*] Specify the level of logging to perform. Levels are *debug*,
*info*, *warning*, *error*, *critical*. Default is *info*

**--ignore_cards**
[*filename*] A file containing a list of card numbers to ignore. Default is not to
ignore any cards.

**--ignore_iins**
[*filename*] A file containing a list of ISO/IEC 7812 Issuer Identification Numbers (IIN)
to ignore. The IIN is between 1 and 6 digits. Examples of IINs:

* **4** - Visa
* **51** - MasterCard
* **34** - American Express
* **1** - UATP
* **6011** - Discover Card

The central list of IINs is not publically available, but a list of updated IINs is available
at https://en.wikipedia.org/wiki/Payment_card_number

**--ignore_industries**
[*filename*] A file containing a list of major industry identifiers to ignore. This
list contains just single digits from the start of each card number. These numbers are

* **0** - ISO/TC 68 and other industry assignments
* **1** - Airlines
* **2**	- Airlines, financial and other future industry assignments
* **3**	- Travel and entertainment
* **4**	- Banking and financial
* **5**	- Banking and financial
* **6**	- Merchandising and banking/financial
* **7**	- Petroleum and other future industry assignments
* **8**	- Healthcare, telecommunications and other future industry assignments
* **9**	- For assignment by national standards bodies

**--include_deprecated**
[*boolean*] Include known deprecated card IIN issuers.

**--ignore_paths**
[*filename*] A file containing a list of paths to ignore. Default is to scan all paths
recursively.

**--minimum_digits**
[*integer*] Only find cards with this minimum number of digits or larger. Default *12*

**--maximum_digits**
[*integer*] Only find cards up to this maximum number of digits in length. Default *19*

**--cards_per_file**
[*integer*] Stop processing a file once this number of cards have been found. Zero will find
all card numbers in each file. Default *0*

**--ignore_file_extensions**
[*filename*] A file containing a list of file extensions to ignore. Each extension must
be listed including the leading period (.), for example .dll, .exe, .ttf

**--unmask_card_number**
[*boolean*] Show the full card number. By default the central account number
portion of the card number is masked with 'X'. Default *False*

**--max_group_count**
[*integer*] Specify the maximum number of digit groups to find within each file. Sometimes
when cards are stored, they are stored in their groupings like this 4 group card number:

`1234-5678-9012-3456`

Some card types use more or less groupings. Specifying zero includes any number of groupings
per card. Default *0*

**--max_group_distance**
[*integer*] Specify the maximum string distance between the first character of the first
card group and the first character of the last card group. If cards appear in a file, the
groupings are commonly quite close together, with probably a maximum of 1 character
between each group. Sometimes groups are stored in fields within databases, adding more space
in the file between each group. Speficying zero will set the group distance to the length of
the number plus 5. Default 0

**--output**
[*filename*] Send the found cards to this file in a CSV format containing the filename, issuer
and card number obeying the *--mask_card_number* option above.

**--verbose**
[*boolean*] Set to true to include more detail about the current scan status. Defaults to True

**--dir**
[*directory*] A directory to scan. Either --dir or --file must be specified otherwise
a scan will not occur.

**--file**
[*filename*] A file to scan. Either --dir or --file must be specified otherwise
a scan will not occur.

## Example configuration files

### Ignore UATP cards
Create these two files

**uatp.ini**
```
[default]
dir=/home
ignore_industries=ignore_uatp.txt
```

**ignore_uatp.txt**
```
1
```

Then run
```
python ./pantastic.py --config_file=uatp.ini
```

## Using the existing ignore paths and extensions
Two exclusion files are included in the project

* ignore_paths.txt
* ignore_extensions.txt

These files contain common exclusions on a Redhat type distribution of Linux. To
use these files, create a file called `pantastic.ini` and fill it with the following.

```
[default]
dir=/
ignore_paths=ignore_paths.txt
ignore_file_extensions=ignore_extensions.txt
```

Then just run

```
python ./pantastic.py
```

And it'll run a PAN scan.

## Notes
This is a very organic project and needs considerable tidying up. It does
comply to PEP8, but it's not particularly 'Pythonic'. It's a bit hacky in
parts as it required quick additions for certain situations, like supporting
UTF-16.

It's not the fastest scan in the world, but it is thorough. As they say:

*"Make it work, then make it fast"*

By default this is a very greedy script and will pick up a lot of valid
'cards'. Although these can technically be called false positives they
are cards that comply with the two simple checks of passing Luhn and
containing a valid IIN.

I suggest running the script in its default state to
start with and then working through why so many card numbers are being
picked up. For example, UATP cards are so broad in specification that
any Luhn compliant number beginning with 1 and complying to the UATP
card length will run a positive result. If you are sure that you will
never see a UATP card in your organisation, then add the IIN or major
industry number to the list of exclusions and run the script again.

Currently, this script does not deal with compressed files. It may in
the future, probably for the common .zip and .rar files. Currently it skips
over the following files with the extensions:

* .gz
* .zip
* .rar
* .7z
* .bzip
* .bz2

This was developed with Python V2, I suspect there's a little bit of work
to get it into V3.

The requirements are fairly straight forward, mostly standard python stuff. There
shouldn't be any other fancy requirements.

This has only been tested in Linux environments. Very interested to see if this
works fine in Windows or on OSX. Haven't made any provisions with the exception
of always using os.path.join() for file paths. Come to think of it, I use mmap
to read the data, and I think a couple of the options are different in Windows. YMMV.

## Stuff I might do
Add a max file size check

Actually do some testing in Windows and OSX

Add more logging for stuff other than info()

Add some kind of progress feedback that you can turn on/off for when you run the
script manually.

Add output options for XML, JSON, HTML etc. Currently only does CSV.

Actually start on compressed file support. http://stackoverflow.com/questions/5127921/can-mmap-and-gzip-collaborate

Provide PIP and other types of installs