# Game Asset DB (GADB)

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

You can either copy the `gadb/__init__.py` file as `gadb.py` to your directory and run it like this:

    python gadb.py

or

    python gadb.py -c myConfigFile.yml

if you want to use a custom config file name.
The script then tries to read any old gadb.csv file, list the current files and merge the data from the old file into the new list of files.

The other way would be to install `cpfr-gadb` via PIP, so you can just run it as

    gadb

or

    gadb -c myConfigFile.yml
