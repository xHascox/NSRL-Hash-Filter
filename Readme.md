# NSRL Hash Filter

This program allows to filter the [NSRL RDS Hash Set](https://www.nist.gov/itl/ssd/software-quality-group/national-software-reference-library-nsrl/nsrl-download/current-rds) for:
* Manufacturer
* OS
* Product Type
* Product Name

And export the corresponding Hashes to a .txt file.

### How To:

Run the [Windows Executable](https://github.com/xHascox/NSRL-Hash-Filter/blob/master/EXE/NSRLHashExporter_best.exe) or run the [Python Script](https://github.com/xHascox/NSRL-Hash-Filter/tree/master/Source) on Linux.

Select an NSRL .iso file (RDS_modern.iso) andclick extract

Wait a moment

Now you can type in what you want to filter for:
* Only exact matches will be included in the export, so make sure to choose one of suggestions (or you are likely to misspell a name, there are weird dots and whitespaces in the NSRL file). 
* You can filter for multiple things by separating them with commas ","
* No input or an input ending with a comma will be considered as a Wildcard

Click the left Button to export to a .txt file without a header ("md5") or the right Button to export with a header ("md5").

### Third Program uses:

[pycdlib](https://github.com/clalancette/pycdlib)

### Tested Python Version:

* 3.5
