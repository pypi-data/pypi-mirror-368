"""
┌───────────────────────────────┐
│         GAME ASSET DB         │
└───────────────────────────────┘
The game asset DB script crawls your asset directory for files you specify via wildcard patterns
and writes the list into a CSV file. You can also specify columns you wish to add for metadata.
This way, you can easily track metadata for your assets (for example where you downloaded the asset,
who the author is and what the license terms are).
It is recommended to store the csv file under version control (such as git) to track changes to your assets
and to run the script frequently. You can then open it up in your favorite spreadsheet application and
manage the metadata for your assets or create exports for credits, license audits etc.

The script uses a yaml config file (usually 'gadb.yml', but it can be changed using the '-c' command line option).
A sample config file looks like the following:

gadb.yml
```
db: gadb.csv
delimiter: ","
wildcards:
- assets/**/*.xcf
- assets/**/*.ogg
columns:
- URL
- Description
- Author
- Date
- License
```

In the example, the CSV database file is specified as 'gadb.csv'.
The delimiter for the CSV im- and export is specified as ',' (which is important for languages where the comma is used for number formatting)
The wildcards option specifies which files are being crawled
And the columns list specifies which metadata columns should be used in the CSV.

You can run the script as follows:

    python gadb.py

or

    python gadb.py -c myConfigFile.yml

if you want to use a custom config file name.
The script then tries to read any old gadb.csv file, list the current files and merge the data from the old file into the new list of files.
"""

import argparse
import csv
import glob
import os
import yaml

def readCsv(csvpath, delimiter):
    """
    Read a CSV DB from the given path. The first column is expected to be the path to the file.
    The result is a tuple containing a list of the headers and a dict containing the contents of each row.
    The headers don't contain the Path.

    `([header1, header2, ... headerN], { "path/to/file" : [ column1, column2, ... columnN] })`
    """
    with open(csvpath) as csvfile:
        lines_read = csv.reader(csvfile, delimiter=delimiter)
        headers = list(next(lines_read))[1:]
        lines = {}
        for line in lines_read:
            lines[line[0]] = line[1:]
        return (headers, lines)


def writeCsv(csvpath, delimiter, data):
    """
    Writes the given data with the configured delimiter (for example Germans uses semicolons instead of commas for CSV due to number formats)
    The data parameter is expected to be a list of lists containing the cell values
    """
    with open(csvpath, "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(data)


def listFiles(config):
    """
    Lists all files according to the configured wildcards.
    The result is a tuple containing a list of the headers and a dict containing empty strings as the contents of each row.
    The headers don't contain the Path.

    `([header1, header2, ... headerN], { "path/to/file" : [ "", "", ... ""] })`
    """
    headers = config["columns"]
    lines = {}
    for wildcard in config["wildcards"]:
        files = glob.glob(wildcard)

        for file in files:
            lines[file] = len(headers) * [""]

    return (headers, lines)


def getMapping(oldHeaders, newHeaders):
    '''
    from old line column to new line column
    `mapping[oldIndex] == newIndex`
    oldHeaders and newHeaders are expected to be lists of strings. They should not contain the first "Path" column
    '''
    output = []
    for header in oldHeaders:
        output.append(newHeaders.index(header) if header in newHeaders else None)
    return output


def mergeOldIntoNew(oldHeaders, oldLines, newHeaders, newLines):
    """
    Merges the values of the old lines into the structure of the new ones.
    This is important, since you want to keep the data of the old ones, even
    if the structure changes according to the config.
    """
    mapping = getMapping(oldHeaders, newHeaders)
    for path, oldLine in oldLines.items():
        if path in newLines:
            newLine = newLines[path]
            for i in range(len(oldLine)):
                if mapping[i] is not None:
                    newLine[mapping[i]] = oldLine[i]
                else:
                    newLine[mapping[i]] = ""


def convertDictToListOfLists(lines):
    """
    converts a dictionary with the path as key and the columns
    as value into a list of lists containing the path as the
    first element of each row.
    """
    for path, line in lines.items():
        yield [ path ] + line


def convertData(headers, lines):
    """
    converts a dictionary with the path as key and the columns
    as value into a list of lists containing the path as the
    first element of each row.
    Further, it sorts all the rows and adds the "Path" to the headers.
    """
    data = list(convertDictToListOfLists(lines))
    data.sort()
    return [["Path"] + headers] + data


def run():
    print("┌───────────────────────────────┐\n│         GAME ASSET DB         │\n└───────────────────────────────┘")
    parser = argparse.ArgumentParser(
        prog = "python gadb.py",
        description = "This tool crawls your asset directory and provides a CSV 'DB' to store meta information."
    )
    parser.add_argument("-c", "--config-file", default="gadb.yml", help="Use this to specify which config file should be used (default is 'gadb.yml')")
    args = parser.parse_args()

    print("Reading config file: '%s'..." % args.config_file)

    config = {}
    if not os.path.isfile(args.config_file):
        print("config file '%s' could not be found!" % args.config_file)
        return

    with open(args.config_file, "r") as stream:
        config = yaml.safe_load(stream)

    csvpath = config["db"] if "db" in config else "gadb.csv"
    delimiter = config["delimiter"] if "delimiter" in config else ","

    print("CSV delimiter is: '%s'" % delimiter)

    # -- read old DB --
    if os.path.isfile(csvpath):
        print("Reading old CSV DB file: '%s'..." % csvpath)
        oldHeaders, oldLines = readCsv(csvpath, delimiter)
        print("Found %d existing files formatted in %d columns" % (len(oldLines), len(oldHeaders)))
    else:
        oldHeaders, oldLines = ([], {})
        print("No old CSV DB file found")

    # -- list files --
    print("Listing files according to wildcard patterns...")
    newHeaders, newLines = listFiles(config)

    mergeOldIntoNew(oldHeaders, oldLines, newHeaders, newLines)

    print("Writing %d lines formatted in %d columns to '%s'" % (len(newLines), len(newHeaders), csvpath))
    writeCsv(csvpath, delimiter, convertData(newHeaders, newLines))
        
if __name__ == "__main__":
    run()