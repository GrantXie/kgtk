41;370;0c>## Overview

The cat command combines (concatenates) one or more KGTK files, optionally
decompressing input files and compressing the output file, while managing the
KGTK column headers appropriately.  The input file(s) are read in the order
specified and edges are copied to the output file without deduplication.

### Merging Column Headers

Each column in the input file(s) becomes a column in the output file.  Input
columns with the same name in different files are merged into a single column.
Column names are case sensitive.

Input columns with one of KGTK's required column names will
also be merged into a single column even if their names do not
match exactly, so long as their names are matching KGTK aliases.
The first name or alias seen takes priority.  For example, if the first
input file has a "node1" column and the second input file has a "from" column, the two
columns will be combined as the "node1" column in the output file.

| Canonical Name | Alias Names |
| -------------- | ----------- |
| id             | ID          |
| label          | predicate relation relationship |
| node1          | from subject |
| node2          | to object |

### KGTK File Modes

Normally, the files being combined must be either all KGTK edge files or all
KGTK node files.  `kgtk cat` will complain if an input file is not a KGTK
edge or node file, or if `kgtk cat` is given a mixture of KGTK edge and node files.
These constraints can be overridden with the expert option `--mode=NONE`.

### Input File Format

Although KGTK commands use the KGTK File Format as their primary file format,
input files  can be  read in  another supported file  format using  the expert
option  `--input-format  INPUT_FORMAT`, where  `INPUT_FORMAT`  is  one of  the
format names shown in the table below:

| Format | Extension | Description |
| ------ | --------- | ----------- |
| kgtk   | .kgtk or .tsv | KGTK tab separated values file format. |
| csv    | .csv      | A simple comma separated value file with doubled quoting and column headers. |

When the `--input-format` option has not been specified, the default is to use `kgtk` format
for input files unless the filename extension (suffix) is `.csv` (optionally followed
by one of the compressed file extensions, see below.)

!!! note
    The expert option `--input-format INPUT_FORMAT` applies to all input files in
    the `kgtk cat` command, so it not possible at present to use `kgtk cat` to
    combine a file in KGTK format with a file in CSV format.  It is necessary to
    convert all input files to a common input format before using `kgtk cat` to combine them
    (although their compression format may vary, as described below).

!!! note
    CSV input file conversion is very simple at the moment.  It may be extended in the
    future to accomodate KGTK datatypes such as date/time.

### Input File Decompression

Input files may be decompressed using an algorithm selected
by the filename extension.  The following compression algorithms
are supported:

| Extension | Algorithm |
| --------- | ----------- |
| .bz2      | [bzip2][1]  |
| .gz       | [gzip][2]   |
| .lz4      | [LZ4][3]    |
| .xz       | [XZ Utils][4], based on LZMA |

[1]: https://en.wikipedia.org/wiki/Bzip2
[2]: https://en.wikipedia.org/wiki/Gzip
[3]: https://en.wikipedia.org/wiki/LZ4_(compression_algorithm)
[4]: https://en.wikipedia.org/wiki/XZ_Utils

When used, compression filename extensions must appear after any other
filename extensions, e.g. `.kgtk.gz`, `.csv.gz`.

Decompression may also be selected using the `--compression-type COMPRESSION_TYPE` option.
This is an expert option which does not appear in the normal
usage message (shown below).  The `COMPRESSION_TYPE` value is one of the extension values shown in the
table above, with or without the leading period.
This option may be used to specify decompression of standard input (`-`).

If `--compression-type` is not specified and the the filename extension is not
a recognized compression filename extension, the input file will not be
decompressed.

!!! Note
    When the `--compression type` expert option is specified, all input
    files will be decompressed using the specified compression type, ignoring their file extensions.

!!! note
    At the present time, decompression is not supported for file descriptor input
    files (filenames that begin with `<`, followed by a file descriptor number).

### Output File Format

Although KGTK commands use the KGTK File Format as their primary file format,
the output file can be written in a selection of formats other
than KGTK format by using the `--output-format FORMAT` option, where `FORMAT`
is one of the values in the table shown below.

| Format | Extension | Description |
| ------ | --------- | ----------- |
| kgtk   | .kgtk or .tsv | KGTK tab separated values file format. |
| csv    | .csv      | A simple comma separated value file with doubled quoting and column headers. |
| md	 | .md       | GitHub markdown tables. |
| json   | .json     | JSON list of lists of strings with column header line. |
| json-map | (none)  | JSON list of maps from column names to string values. |
| json-map-compact | (none)  | JSON list of maps from column names to string values with empty values suppressed. |
| jsonl  | .jsonl    | JSON lines of lists of strings  with column header line. |
| jsonl-map | (none)  | JSON lines of maps from column names to string values. |
| jsonl-map-compact | (none)  | JSON lines of maps from column names to string values with empty values suppressed. |
| tsv | (none) | Tab separated values.  Dates have their sigils removed, and strings have the backslash escape removed before pipes. |
| tsv-csvlike | (none) | Tab separated values.  Dates have their sigils removed, and strings are transformed into CSV-like double quoted strings, losing the language code if present. |
| tsv-unquoted | (none) | Tab separated values.  Dates have their sigils removed, and strings have their content exposed without quotes and without escapes before pipes. |
| tsv-unquoted-ep | (none) | Tab separated values.  Dates have their sigils removed, and strings have their content exposed without quotes ; pipes retain their preceeding escapes. |

Output formats may also be selected by the filename extension on the output file if `--output-format`
has not been specified.  For example,
writing an output file with the extension `.csv` will automatically generate an output file
in CSV format.  Any unrecognized extensions default to kgtk format unless
overridden by the `--output-format` option.

!!! note
    The csv and json* formats use very primitive conversions at the present time,
    which do not provide proper treatment for different data types: booleans,
    numbers, strings.

### Output File Compression

Output files may be compressed using an algorithm selected
by the file extension.  The following compression algorithms
are supported:

| Extension | Algorithm |
| --------- | ----------- |
| .bz2      | [bzip2][1]  |
| .gz       | [gzip][2]   |
| .lz4      | [LZ4][3]    |
| .xz       | [XZ Utils][4], based on LZMA |

When specified, compression format extensions must appear after output format
selection extensions, e.g. `.kgtk.gz`, `.csv.gz`, `.json.bz2`.

!!! note
    At the present time, the `--compression-type COMPRESSION_TYPE` option does not
    affect output files.  Standard output (`-`) and file descriptor output
    files (filesnames that begin with `>`, followed by a file descriptor number)
    will not be compressed.  This behavior may change at a later date.

## Fast Copies

When certain conditions are met, `kgtk cat` will use Unix system utilities to perform
decompression. concatenation, and compression.  The major constraints are:

 * The input files must have the same column header names (allowing for aliases)
   and order.
 * The input files must come from the filesystem, not standard input or a file
   descriptor number.
 * The input files must meet a minimum total size.
 * Various checking options must not be turned on.
 * The files must contain column names headers that are not
   overidden bu command line options.
   

## Usage

```bash
usage: kgtk cat [-h] [-i INPUT_FILE [INPUT_FILE ...]] [-o OUTPUT_FILE]
                [--output-format {csv,html,html-compact,json,json-map,json-map-compact,jsonl,jsonl-map,jsonl-map-compact,kgtk,md,table,tsv,tsv-csvlike,tsv-unquoted,tsv-unquoted-ep}]
                [--pure-python [True|False]]
                [--fast-copy-min-size FAST_COPY_MIN_SIZE]
                [-v [optional True|False]]

Concatenate two or more KGTK files, merging the columns appropriately. All files must be KGTK edge files or all files must be KGTK node files (unless overridden with --mode=NONE). 

Additional options are shown in expert help.
kgtk --expert cat --help

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE [INPUT_FILE ...], --input-files INPUT_FILE [INPUT_FILE ...]
                        KGTK input files (May be omitted or '-' for stdin.)
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        The KGTK output file. (May be omitted or '-' for
                        stdout.)
  --output-format {csv,html,html-compact,json,json-map,json-map-compact,jsonl,jsonl-map,jsonl-map-compact,kgtk,md,table,tsv,tsv-csvlike,tsv-unquoted,tsv-unquoted-ep}
                        The file format (default=kgtk)
  --pure-python [True|False]
                        When True, use Python code. (default=False)
  --fast-copy-min-size FAST_COPY_MIN_SIZE
                        The minium number of bytes before using OS tools for
                        fast copy (default=10000).

  -v [optional True|False], --verbose [optional True|False]
                        Print additional progress messages (default=False).
```

## Examples

### Sample Data

Suppose that `movies_reduced.tsv` contains the following table in KGTK format:

```bash
kgtk cat -i examples/docs/movies_reduced.tsv
```

| id | node1 | label | node2 |
| -- | -- | -- | -- |
| t1 | terminator | label | 'The Terminator'@en |
| t2 | terminator | instance_of | film |
| t3 | terminator | genre | action |
| t4 | terminator | genre | science_fiction |
| t5 | terminator | publication_date | ^1984-10-26T00:00:00Z/11 |
| t6 | t5 | location | united_states |
| t7 | terminator | publication_date | ^1985-02-08T00:00:00Z/11 |
| t8 | t7 | location | sweden |
| t9 | terminator | director | james_cameron |
| t10 | terminator | cast | arnold_schwarzenegger |
| t11 | t10 | role | terminator |
| t12 | terminator | cast | michael_biehn |
| t13 | t12 | role | kyle_reese |
| t14 | terminator | cast | linda_hamilton |
| t15 | t14 | role | sarah_connor |
| t16 | terminator | duration | 108 |
| t17 | terminator | award | national_film_registry |
| t18 | t17 | point_in_time | ^2008-01-01T00:00:00Z/9 |

Suppose that `tutorial_people_full.tsv` contains the following table in KGTK format:

```bash
kgtk cat -i examples/docs/tutorial_people_full.tsv
```

| id | node1 | label | node2 |
| -- | -- | -- | -- |
| h1 | james_cameron | label | "James Cameron" |
| h2 | james_cameron | instance_of | human |
| h3 | james_cameron | birth_date | ^1954-08-16T00:00:00Z/11 |
| h4 | james_cameron | country | Canada |
| h5 | arnold_schwarzenegger | label | "Arnold Schwarzenegger" |
| h6 | arnold_schwarzenegger | instance_of | human |
| h7 | arnold_schwarzenegger | birth_date | ^1947-07-30T00:00:00Z/11 |
| h8 | arnold_schwarzenegger | country | "Austria" |
| h9 | michael_biehn | label | "Michael Biehn" |
| h10 | michael_biehn | instance_of | human |
| h11 | michael_biehn | birth_date | ^1956-07-31T00:00:00Z/11 |
| h12 | michael_biehn | country | "United States of America" |
| h13 | linda_hamilton | label | "Linda Hamilton" |
| h14 | linda_hamilton | instance_of | human |
| h15 | linda_hamilton | birth_date | ^1956-09-26T00:00:00Z/11 |
| h16 | linda_hamilton | country | "United States of America" |
| h17 | edward_furlong | label | "Edward Furlong" |
| h18 | edward_furlong | instance_of | human |
| h19 | edward_furlong | birth_date | ^1977-08-02T00:00:00Z/11 |
| h20 | edward_furlong | country | "United States of America" |
| h21 | robert_patrick | label | "Robert Patrick" |
| h22 | robert_patrick | instance_of | human |
| h23 | robert_patrick | birth_date | ^1958-11-05T00:00:00Z/11 |
| h24 | robert_patrick | country | "United States of America" |

### Combine two KGTK files, sending the output to standard output.

These two files have only he 4 basic KGTK fields.

```bash
kgtk cat -i examples/docs/movies_reduced.tsv examples/docs/tutorial_people_full.tsv
```

The result will be the following file in KGTK format:

| id | node1 | label | node2 |
| -- | -- | -- | -- |
| t1 | terminator | label | 'The Terminator'@en |
| t2 | terminator | instance_of | film |
| t3 | terminator | genre | action |
| t4 | terminator | genre | science_fiction |
| t5 | terminator | publication_date | ^1984-10-26T00:00:00Z/11 |
| t6 | t5 | location | united_states |
| t7 | terminator | publication_date | ^1985-02-08T00:00:00Z/11 |
| t8 | t7 | location | sweden |
| t9 | terminator | director | james_cameron |
| t10 | terminator | cast | arnold_schwarzenegger |
| t11 | t10 | role | terminator |
| t12 | terminator | cast | michael_biehn |
| t13 | t12 | role | kyle_reese |
| t14 | terminator | cast | linda_hamilton |
| t15 | t14 | role | sarah_connor |
| t16 | terminator | duration | 108 |
| t17 | terminator | award | national_film_registry |
| t18 | t17 | point_in_time | ^2008-01-01T00:00:00Z/9 |
| h1 | james_cameron | label | "James Cameron" |
| h2 | james_cameron | instance_of | human |
| h3 | james_cameron | birth_date | ^1954-08-16T00:00:00Z/11 |
| h4 | james_cameron | country | Canada |
| h5 | arnold_schwarzenegger | label | "Arnold Schwarzenegger" |
| h6 | arnold_schwarzenegger | instance_of | human |
| h7 | arnold_schwarzenegger | birth_date | ^1947-07-30T00:00:00Z/11 |
| h8 | arnold_schwarzenegger | country | "Austria" |
| h9 | michael_biehn | label | "Michael Biehn" |
| h10 | michael_biehn | instance_of | human |
| h11 | michael_biehn | birth_date | ^1956-07-31T00:00:00Z/11 |
| h12 | michael_biehn | country | "United States of America" |
| h13 | linda_hamilton | label | "Linda Hamilton" |
| h14 | linda_hamilton | instance_of | human |
| h15 | linda_hamilton | birth_date | ^1956-09-26T00:00:00Z/11 |
| h16 | linda_hamilton | country | "United States of America" |
| h17 | edward_furlong | label | "Edward Furlong" |
| h18 | edward_furlong | instance_of | human |
| h19 | edward_furlong | birth_date | ^1977-08-02T00:00:00Z/11 |
| h20 | edward_furlong | country | "United States of America" |
| h21 | robert_patrick | label | "Robert Patrick" |
| h22 | robert_patrick | instance_of | human |
| h23 | robert_patrick | birth_date | ^1958-11-05T00:00:00Z/11 |
| h24 | robert_patrick | country | "United States of America" |


### Combine two gzipped KGTK files, sending the output to a bzip2 file.

```bash
kgtk cat -i examples/docs/movies_reduced.tsv.gz examples/docs/tutorial_people_full.tsv.gz -o ofile.tsv.bz2
```

### Expert Topic: Processing Files Not in KGTK Format

Suppose that `not-kgtk.tsv` contains the following data **not** in KGTK format
(`--mode=NONE` has been added to allow the file to be processed by `kgtk cat`):

```bash
kgtk cat -i examples/docs/not-kgtk.tsv --mode=NONE
```

| a | b | c | d |
| -- | -- | -- | -- |
| h21 | robert_patrick | label | "Robert Patrick" |
| h22 | robert_patrick | instance_of | human |
| h23 | robert_patrick | birth_date | ^1958-11-05T00:00:00Z/11 |
| h24 | robert_patrick | country | "United States of America" |

Trying to run the command without `--mode=NONE`:

```bash
kgtk cat -i examples/docs/not-kgtk.tsv
```

will result in an error message:

    In input 1 header 'a	b	c	d': Missing required column: id | ID
    Exit requested

We can force the `kgtk cat` command to process the file by using the `--mode NONE` option,
as shown above.

!!! note
    `--mode NONE` is implemented by KgtkReader.  It can be used by many KGTK commands.
    

### Read a CSV file

Here's an example of reading a CSV file, using the filename suffix to
establish the file format:

```bash
kgtk cat -i examples/docs/cat-csv-file.csv --mode=NONE
```

| AtomicNumber | Element | Symbol | AtomicMass | NumberofNeutrons | NumberofProtons | NumberofElectrons | Period | Group | Phase | Radioactive | Natural | Metal | Nonmetal | Metalloid | Type | AtomicRadius | Electronegativity | FirstIonization | Density | MeltingPoint | BoilingPoint | NumberOfIsotopes | Discoverer | Year | SpecificHeat | NumberofShells | NumberofValence |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 1 | Hydrogen | H | 1.007 | 0 | 1 | 1 | 1 | 1 | gas |  | yes |  | yes |  | Nonmetal | 0.79 | 2.2 | 13.5984 | 8.99E-05 | 14.175 | 20.28 | 3 | Cavendish | 1766 | 14.304 | 1 | 1 |
| 2 | Helium | He | 4.002 | 2 | 2 | 2 | 1 | 18 | gas |  | yes |  | yes |  | NobleGas | 0.49 |  | 24.5874 | 1.79E-04 |  | 4.22 | 5 | Janssen | 1868 | 5.193 | 1 |  |
| 3 | Lithium | Li | 6.941 | 4 | 3 | 3 | 2 | 1 | solid |  | yes | yes |  |  | AlkaliMetal | 2.1 | 0.98 | 5.3917 | 5.34E-01 | 453.85 | 1615 | 5 | Arfvedson | 1817 | 3.582 | 2 | 1 |
| 4 | Beryllium | Be | 9.012 | 5 | 4 | 4 | 2 | 2 | solid |  | yes | yes |  |  | AlkalineEarthMetal | 1.4 | 1.57 | 9.3227 | 1.85E+00 | 1560.15 | 2742 | 6 | Vaulquelin | 1798 | 1.825 | 2 | 2 |
| 5 | Boron | B | 10.811 | 6 | 5 | 5 | 2 | 13 | solid |  | yes |  |  | yes | Metalloid | 1.2 | 2.04 | 8.298 | 2.34E+00 | 2573.15 | 4200 | 6 | Gay-Lussac | 1808 | 1.026 | 2 | 3 |
| 6 | Carbon | C | 12.011 | 6 | 6 | 6 | 2 | 14 | solid |  | yes |  | yes |  | Nonmetal | 0.91 | 2.55 | 11.2603 | 2.27E+00 | 3948.15 | 4300 | 7 | Prehistoric |  | 0.709 | 2 | 4 |
| 7 | Nitrogen | N | 14.007 | 7 | 7 | 7 | 2 | 15 | gas |  | yes |  | yes |  | Nonmetal | 0.75 | 3.04 | 14.5341 | 1.25E-03 | 63.29 | 77.36 | 8 | Rutherford | 1772 | 1.04 | 2 | 5 |
| 8 | Oxygen | O | 15.999 | 8 | 8 | 8 | 2 | 16 | gas |  | yes |  | yes |  | Nonmetal | 0.65 | 3.44 | 13.6181 | 1.43E-03 | 50.5 | 90.2 | 8 | Priestley\|Scheele | 1774 | 0.918 | 2 | 6 |
| 9 | Fluorine | F | 18.998 | 10 | 9 | 9 | 2 | 17 | gas |  | yes |  | yes |  | Halogen | 0.57 | 3.98 | 17.4228 | 1.70E-03 | 53.63 | 85.03 | 6 | Moissan | 1886 | 0.824 | 2 | 7 |
| 10 | Neon | Ne | 20.18 | 10 | 10 | 10 | 2 | 18 | gas |  | yes |  | yes |  | Noble Gas | 0.51 |  | 21.5645 | 9.00E-04 | 24.703 | 27.07 | 8 | Ramsay_and_Travers | 1898 | 1.03 | 2 | 8 |
| 11 | Sodium | Na | 22.99 | 12 | 11 | 11 | 3 | 1 | solid |  | yes | yes |  |  | AlkaliMetal | 2.2 | 0.93 | 5.1391 | 9.71E-01 | 371.15 | 1156 | 7 | Davy | 1807 | 1.228 | 3 | 1 |
| 12 | Magnesium | Mg | 24.305 | 12 | 12 | 12 | 3 | 2 | solid |  | yes | yes |  |  | AlkalineEarthMetal | 1.7 | 1.31 | 7.6462 | 1.74E+00 | 923.15 | 1363 | 8 | Black | 1755 | 1.023 | 3 | 2 |
| 13 | Aluminum | Al | 26.982 | 14 | 13 | 13 | 3 | 13 | solid |  | yes | yes |  |  | Metal | 1.8 | 1.61 | 5.9858 | 2.70E+00 | 933.4 | 2792 | 8 | Wshler | 1827 | 0.897 | 3 | 3 |
| 14 | Silicon | Si | 28.086 | 14 | 14 | 14 | 3 | 14 | solid |  | yes |  |  | yes | Metalloid | 1.5 | 1.9 | 8.1517 | 2.33E+00 | 1683.15 | 3538 | 8 | Berzelius | 1824 | 0.705 | 3 | 4 |
| 15 | Phosphorus | P | 30.974 | 16 | 15 | 15 | 3 | 15 | solid |  | yes |  | yes |  | Nonmetal | 1.2 | 2.19 | 10.4867 | 1.82E+00 | 317.25 | 553 | 7 | BranBrand | 1669 | 0.769 | 3 | 5 |
| 16 | Sulfur | S | 32.065 | 16 | 16 | 16 | 3 | 16 | solid |  | yes |  | yes |  | Nonmetal | 1.1 | 2.58 | 10.36 | 2.07E+00 | 388.51 | 717.8 | 10 | Prehistoric |  | 0.71 | 3 | 6 |
| 17 | Chlorine | Cl | 35.453 | 18 | 17 | 17 | 3 | 17 | gas |  | yes |  | yes |  | Halogen | 0.97 | 3.16 | 12.9676 | 3.21E-03 | 172.31 | 239.11 | 11 | Scheele | 1774 | 0.479 | 3 | 7 |
| 18 | Argon | Ar | 39.948 | 22 | 18 | 18 | 3 | 18 | gas |  | yes |  | yes |  | NobleGas | 0.88 |  | 15.7596 | 1.78E-03 | 83.96 | 87.3 | 8 | Rayleigh_and_Ramsay | 1894 | 0.52 | 3 | 8 |


### Expert Topic: Adding Column Names

Suppose that you have a TSV (tab-separated values) data file
that looks like a KGTK data file but without the header line.
You can supply a header line with the expert option `--force-column-names`.
You can also use this option when concatenating several
data files, so long as they are all missing header lines and
they should all have the same header line.

Consider the following input file:

```bash
kgtk cat -i examples/docs/no-header.tsv --mode=NONE
```

| a | b | c | d |
| -- | -- | -- | -- |
| h21 | robert_patrick | label | "Robert Patrick" |
| h22 | robert_patrick | instance_of | human |
| h23 | robert_patrick | birth_date | ^1958-11-05T00:00:00Z/11 |
| h24 | robert_patrick | country | "United States of America" |

We can supply a valid header line as follows:

```bash
kgtk cat -i examples/docs/no-header.tsv \
         --force-column-names id node1 label node2
```

The result will be the following file in KGTK format:

| id | node1 | label | node2 |
| -- | -- | -- | -- |
| h21 | robert_patrick | label | "Robert Patrick" |
| h22 | robert_patrick | instance_of | human |
| h23 | robert_patrick | birth_date | ^1958-11-05T00:00:00Z/11 |
| h24 | robert_patrick | country | "United States of America" |

!!! note
    `---force-column-names` takes place before the input file is checked
    to see if it is a valid KGTK edge or node file.  Since we supplied
    valid KGTK edge column names in the example above, `--mode=NONE` is
    no longer needed.

### Expert Topic: Renaming Column Names on Input

There is a special KGTK command, `kgtk rename-columns`, for renaming columns.
However, you may want to rename columns while also using other features of
the `kgtk cat` command, such as combining multiple input files or sampling
data lines.

You have two main choices: override the column names on input, or rename the
column names on output.

Overriding the column names on input can be done by skipping the existing
header record and supplying a replacement list of column names.

```bash
kgtk cat -i examples/docs/not-kgtk.tsv \
	 --force-column-names id node1 label node2
```

The result will be the following file in KGTK format:

| id | node1 | label | node2 |
| -- | -- | -- | -- |
| h21 | robert_patrick | label | "Robert Patrick" |
| h22 | robert_patrick | instance_of | human |
| h23 | robert_patrick | birth_date | ^1958-11-05T00:00:00Z/11 |
| h24 | robert_patrick | country | "United States of America" |

!!! note
    When you rename columns on input, the change applies to all input files: they
    all must have the same column layout, for which you will provide a new set of
    column names.

### Expert Topic: Renaming All Column Names on Output

There is a special KGTK command, `kgtk rename_columns`, for renaming columns.
However, you may want to rename columns while also using other features of
the `kgtk cat` command, such as combining multiple input files or sampling
data lines.

You have two main choices: override the column names on input, or rename the
column names on output.

For example, suppose your input file contained the following table in almost KGTK format:

```bash
kgtk cat -i examples/docs/movies_origin_destination.tsv --mode=NONE
```

| origin | label | destination | years |
| -- | -- | -- | -- |
| terminator | label | 'The Terminator'@en | 4 |
| terminator | instance_of | film | 3 |

Renaming the column names on output can by done two ways.  First, you can name
all of the new column names using --output-columns.

```bash
kgtk cat -i examples/docs/movies_origin_destination.tsv --mode=NONE \
         --output-columns node1 label node2 years
```

The result will be the following table in KGTK format:

| node1 | label | node2 | years |
| -- | -- | -- | -- |
| terminator | label | 'The Terminator'@en | 4 |
| terminator | instance_of | film | 3 |

### Expert Topic: Renaming Selected Column Names on Output

Second, you can rename individual columns using --old-columns and --new-columns.

You want to rename the `origin` column to `node1`, and the `destination`
column to `node2`, leaving the other column names alone.

```bash
kgtk cat -i examples/docs/movies_origin_destination.tsv --mode=NONE \
         --old-columns origin destination \
	 --new-columns node1 node2
```

The result will be the following table in KGTK format:

| node1 | label | node2 | years |
| -- | -- | -- | -- |
| terminator | label | 'The Terminator'@en | 4 |
| terminator | instance_of | film | 3 |

!!! note
    Renaming column names on output can be done when you combine a
    disparate set of KGTK files.  The rename applies to the merged set of column
    names computed by `kgtk cat`.

### Expert Topic: Data Sampling: head

Limit the number of records read (like `head`).

```bash
kgtk cat -i examples/docs/movies_reduced.tsv --record-limit 4
```

The result will be the following table in KGTK format:

| id | node1 | label | node2 |
| -- | -- | -- | -- |
| t1 | terminator | label | 'The Terminator'@en |
| t2 | terminator | instance_of | film |
| t3 | terminator | genre | action |
| t4 | terminator | genre | science_fiction |

### Expert Topic: Data Sampling: skip

Skip some number of initial records, then begin processing.

```bash
kgtk cat -i examples/docs/movies_reduced.tsv --initial-skip-count 4
```

The result will be the following table in KGTK format:

| id | node1 | label | node2 |
| -- | -- | -- | -- |
| t5 | terminator | publication_date | ^1984-10-26T00:00:00Z/11 |
| t6 | t5 | location | united_states |
| t7 | terminator | publication_date | ^1985-02-08T00:00:00Z/11 |
| t8 | t7 | location | sweden |
| t9 | terminator | director | james_cameron |
| t10 | terminator | cast | arnold_schwarzenegger |
| t11 | t10 | role | terminator |
| t12 | terminator | cast | michael_biehn |
| t13 | t12 | role | kyle_reese |
| t14 | terminator | cast | linda_hamilton |
| t15 | t14 | role | sarah_connor |
| t16 | terminator | duration | 108 |
| t17 | terminator | award | national_film_registry |
| t18 | t17 | point_in_time | ^2008-01-01T00:00:00Z/9 |

### Expert Topic: Data Sampling: last 5

Process the last n records relative to the end (like `tail`).
You must know the number of data records in the file (the number of lines
in the file minus the header line).

```bash
kgtk cat -i examples/docs/movies_reduced.tsv --record-limit 15 --tail-count 3
```

The result will be the following table in KGTK format:

| id | node1 | label | node2 |
| -- | -- | -- | -- |
| t13 | t12 | role | kyle_reese |
| t14 | terminator | cast | linda_hamilton |
| t15 | t14 | role | sarah_connor |

!!! note
    If both --initial-skip-count # and --record-limit # --tail-count #
    are specified, the number of records skipped will be the maximum of
    the initial skip count and (record limit minus tail count).

### Expert Topic: Data Sampling: every n

Process every nth record (after skipping, but calculated relative to
the count of data lines read before skipping).  The following example will
process every second line.

```bash
kgtk cat -i examples/docs/movies_reduced.tsv --every-nth-record 2
```

The result will be the following table in KGTK format:

| id | node1 | label | node2 |
| -- | -- | -- | -- |
| t2 | terminator | instance_of | film |
| t4 | terminator | genre | science_fiction |
| t6 | t5 | location | united_states |
| t8 | t7 | location | sweden |
| t10 | terminator | cast | arnold_schwarzenegger |
| t12 | terminator | cast | michael_biehn |
| t14 | terminator | cast | linda_hamilton |
| t16 | terminator | duration | 108 |
| t18 | t17 | point_in_time | ^2008-01-01T00:00:00Z/9 |

### Expert Topic: Converting a CSV File to a quasi-KGTK File

The expert option `--input-format csv` may be used to read an
input file in CSV (comma-separated values) format.  The expert
option `--mode=NONE` will also be needed if the input file
does not have the required columns of a KGTK edge or node file.

```bash
kgtk cat -i examples/docs/periodic_table_of_elements_1-18.csv \
         --input-format csv --mode=NONE
```

The result will be the following table in quasi-KGTK format:

| AtomicNumber | Element | Symbol | AtomicMass | NumberofNeutrons | NumberofProtons | NumberofElectrons | Period | Group | Phase | Radioactive | Natural | Metal | Nonmetal | Metalloid | Type | AtomicRadius | Electronegativity | FirstIonization | Density | MeltingPoint | BoilingPoint | NumberOfIsotopes | Discoverer | Year | SpecificHeat | NumberofShells | NumberofValence |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 1 | Hydrogen | H | 1.007 | 0 | 1 | 1 | 1 | 1 | gas |  | yes |  | yes |  | Nonmetal | 0.79 | 2.2 | 13.5984 | 8.99E-05 | 14.175 | 20.28 | 3 | Cavendish | 1766 | 14.304 | 1 | 1 |
| 2 | Helium | He | 4.002 | 2 | 2 | 2 | 1 | 18 | gas |  | yes |  | yes |  | NobleGas | 0.49 |  | 24.5874 | 1.79E-04 |  | 4.22 | 5 | Janssen | 1868 | 5.193 | 1 |  |
| 3 | Lithium | Li | 6.941 | 4 | 3 | 3 | 2 | 1 | solid |  | yes | yes |  |  | AlkaliMetal | 2.1 | 0.98 | 5.3917 | 5.34E-01 | 453.85 | 1615 | 5 | Arfvedson | 1817 | 3.582 | 2 | 1 |
| 4 | Beryllium | Be | 9.012 | 5 | 4 | 4 | 2 | 2 | solid |  | yes | yes |  |  | AlkalineEarthMetal | 1.4 | 1.57 | 9.3227 | 1.85E+00 | 1560.15 | 2742 | 6 | Vaulquelin | 1798 | 1.825 | 2 | 2 |
| 5 | Boron | B | 10.811 | 6 | 5 | 5 | 2 | 13 | solid |  | yes |  |  | yes | Metalloid | 1.2 | 2.04 | 8.298 | 2.34E+00 | 2573.15 | 4200 | 6 | Gay-Lussac | 1808 | 1.026 | 2 | 3 |
| 6 | Carbon | C | 12.011 | 6 | 6 | 6 | 2 | 14 | solid |  | yes |  | yes |  | Nonmetal | 0.91 | 2.55 | 11.2603 | 2.27E+00 | 3948.15 | 4300 | 7 | Prehistoric |  | 0.709 | 2 | 4 |
| 7 | Nitrogen | N | 14.007 | 7 | 7 | 7 | 2 | 15 | gas |  | yes |  | yes |  | Nonmetal | 0.75 | 3.04 | 14.5341 | 1.25E-03 | 63.29 | 77.36 | 8 | Rutherford | 1772 | 1.04 | 2 | 5 |
| 8 | Oxygen | O | 15.999 | 8 | 8 | 8 | 2 | 16 | gas |  | yes |  | yes |  | Nonmetal | 0.65 | 3.44 | 13.6181 | 1.43E-03 | 50.5 | 90.2 | 8 | Priestley\|Scheele | 1774 | 0.918 | 2 | 6 |
| 9 | Fluorine | F | 18.998 | 10 | 9 | 9 | 2 | 17 | gas |  | yes |  | yes |  | Halogen | 0.57 | 3.98 | 17.4228 | 1.70E-03 | 53.63 | 85.03 | 6 | Moissan | 1886 | 0.824 | 2 | 7 |
| 10 | Neon | Ne | 20.18 | 10 | 10 | 10 | 2 | 18 | gas |  | yes |  | yes |  | Noble Gas | 0.51 |  | 21.5645 | 9.00E-04 | 24.703 | 27.07 | 8 | Ramsay_and_Travers | 1898 | 1.03 | 2 | 8 |
| 11 | Sodium | Na | 22.99 | 12 | 11 | 11 | 3 | 1 | solid |  | yes | yes |  |  | AlkaliMetal | 2.2 | 0.93 | 5.1391 | 9.71E-01 | 371.15 | 1156 | 7 | Davy | 1807 | 1.228 | 3 | 1 |
| 12 | Magnesium | Mg | 24.305 | 12 | 12 | 12 | 3 | 2 | solid |  | yes | yes |  |  | AlkalineEarthMetal | 1.7 | 1.31 | 7.6462 | 1.74E+00 | 923.15 | 1363 | 8 | Black | 1755 | 1.023 | 3 | 2 |
| 13 | Aluminum | Al | 26.982 | 14 | 13 | 13 | 3 | 13 | solid |  | yes | yes |  |  | Metal | 1.8 | 1.61 | 5.9858 | 2.70E+00 | 933.4 | 2792 | 8 | Wshler | 1827 | 0.897 | 3 | 3 |
| 14 | Silicon | Si | 28.086 | 14 | 14 | 14 | 3 | 14 | solid |  | yes |  |  | yes | Metalloid | 1.5 | 1.9 | 8.1517 | 2.33E+00 | 1683.15 | 3538 | 8 | Berzelius | 1824 | 0.705 | 3 | 4 |
| 15 | Phosphorus | P | 30.974 | 16 | 15 | 15 | 3 | 15 | solid |  | yes |  | yes |  | Nonmetal | 1.2 | 2.19 | 10.4867 | 1.82E+00 | 317.25 | 553 | 7 | BranBrand | 1669 | 0.769 | 3 | 5 |
| 16 | Sulfur | S | 32.065 | 16 | 16 | 16 | 3 | 16 | solid |  | yes |  | yes |  | Nonmetal | 1.1 | 2.58 | 10.36 | 2.07E+00 | 388.51 | 717.8 | 10 | Prehistoric |  | 0.71 | 3 | 6 |
| 17 | Chlorine | Cl | 35.453 | 18 | 17 | 17 | 3 | 17 | gas |  | yes |  | yes |  | Halogen | 0.97 | 3.16 | 12.9676 | 3.21E-03 | 172.31 | 239.11 | 11 | Scheele | 1774 | 0.479 | 3 | 7 |
| 18 | Argon | Ar | 39.948 | 22 | 18 | 18 | 3 | 18 | gas |  | yes |  | yes |  | NobleGas | 0.88 |  | 15.7596 | 1.78E-03 | 83.96 | 87.3 | 8 | Rayleigh_and_Ramsay | 1894 | 0.52 | 3 | 8 |

### Expert Topic: Converting a CSV File to a KGTK File

The expert option `--input-format csv` may be used to read an
input file in CSV (comma-separated values) format.  The expert
option `--mode=NONE` will also be needed if the input file
does not have the required columns of a KGTK edge or node file.

If we want the output file to be a KGTK file instead of a quasi-KGTK
file, and one of the columns is suitable to use as an `id` column,
we can rename that column on input or output.  In this example, we
rename the specific column on output.

```bash
kgtk cat -i examples/docs/periodic_table_of_elements_1-18.csv \
         --input-format csv --mode=NONE \
         --old-column AtomicNumber \
         --new-column id	 
```

The result will be the following table in KGTK format:

| id | Element | Symbol | AtomicMass | NumberofNeutrons | NumberofProtons | NumberofElectrons | Period | Group | Phase | Radioactive | Natural | Metal | Nonmetal | Metalloid | Type | AtomicRadius | Electronegativity | FirstIonization | Density | MeltingPoint | BoilingPoint | NumberOfIsotopes | Discoverer | Year | SpecificHeat | NumberofShells | NumberofValence |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 1 | Hydrogen | H | 1.007 | 0 | 1 | 1 | 1 | 1 | gas |  | yes |  | yes |  | Nonmetal | 0.79 | 2.2 | 13.5984 | 8.99E-05 | 14.175 | 20.28 | 3 | Cavendish | 1766 | 14.304 | 1 | 1 |
| 2 | Helium | He | 4.002 | 2 | 2 | 2 | 1 | 18 | gas |  | yes |  | yes |  | NobleGas | 0.49 |  | 24.5874 | 1.79E-04 |  | 4.22 | 5 | Janssen | 1868 | 5.193 | 1 |  |
| 3 | Lithium | Li | 6.941 | 4 | 3 | 3 | 2 | 1 | solid |  | yes | yes |  |  | AlkaliMetal | 2.1 | 0.98 | 5.3917 | 5.34E-01 | 453.85 | 1615 | 5 | Arfvedson | 1817 | 3.582 | 2 | 1 |
| 4 | Beryllium | Be | 9.012 | 5 | 4 | 4 | 2 | 2 | solid |  | yes | yes |  |  | AlkalineEarthMetal | 1.4 | 1.57 | 9.3227 | 1.85E+00 | 1560.15 | 2742 | 6 | Vaulquelin | 1798 | 1.825 | 2 | 2 |
| 5 | Boron | B | 10.811 | 6 | 5 | 5 | 2 | 13 | solid |  | yes |  |  | yes | Metalloid | 1.2 | 2.04 | 8.298 | 2.34E+00 | 2573.15 | 4200 | 6 | Gay-Lussac | 1808 | 1.026 | 2 | 3 |
| 6 | Carbon | C | 12.011 | 6 | 6 | 6 | 2 | 14 | solid |  | yes |  | yes |  | Nonmetal | 0.91 | 2.55 | 11.2603 | 2.27E+00 | 3948.15 | 4300 | 7 | Prehistoric |  | 0.709 | 2 | 4 |
| 7 | Nitrogen | N | 14.007 | 7 | 7 | 7 | 2 | 15 | gas |  | yes |  | yes |  | Nonmetal | 0.75 | 3.04 | 14.5341 | 1.25E-03 | 63.29 | 77.36 | 8 | Rutherford | 1772 | 1.04 | 2 | 5 |
| 8 | Oxygen | O | 15.999 | 8 | 8 | 8 | 2 | 16 | gas |  | yes |  | yes |  | Nonmetal | 0.65 | 3.44 | 13.6181 | 1.43E-03 | 50.5 | 90.2 | 8 | Priestley\|Scheele | 1774 | 0.918 | 2 | 6 |
| 9 | Fluorine | F | 18.998 | 10 | 9 | 9 | 2 | 17 | gas |  | yes |  | yes |  | Halogen | 0.57 | 3.98 | 17.4228 | 1.70E-03 | 53.63 | 85.03 | 6 | Moissan | 1886 | 0.824 | 2 | 7 |
| 10 | Neon | Ne | 20.18 | 10 | 10 | 10 | 2 | 18 | gas |  | yes |  | yes |  | Noble Gas | 0.51 |  | 21.5645 | 9.00E-04 | 24.703 | 27.07 | 8 | Ramsay_and_Travers | 1898 | 1.03 | 2 | 8 |
| 11 | Sodium | Na | 22.99 | 12 | 11 | 11 | 3 | 1 | solid |  | yes | yes |  |  | AlkaliMetal | 2.2 | 0.93 | 5.1391 | 9.71E-01 | 371.15 | 1156 | 7 | Davy | 1807 | 1.228 | 3 | 1 |
| 12 | Magnesium | Mg | 24.305 | 12 | 12 | 12 | 3 | 2 | solid |  | yes | yes |  |  | AlkalineEarthMetal | 1.7 | 1.31 | 7.6462 | 1.74E+00 | 923.15 | 1363 | 8 | Black | 1755 | 1.023 | 3 | 2 |
| 13 | Aluminum | Al | 26.982 | 14 | 13 | 13 | 3 | 13 | solid |  | yes | yes |  |  | Metal | 1.8 | 1.61 | 5.9858 | 2.70E+00 | 933.4 | 2792 | 8 | Wshler | 1827 | 0.897 | 3 | 3 |
| 14 | Silicon | Si | 28.086 | 14 | 14 | 14 | 3 | 14 | solid |  | yes |  |  | yes | Metalloid | 1.5 | 1.9 | 8.1517 | 2.33E+00 | 1683.15 | 3538 | 8 | Berzelius | 1824 | 0.705 | 3 | 4 |
| 15 | Phosphorus | P | 30.974 | 16 | 15 | 15 | 3 | 15 | solid |  | yes |  | yes |  | Nonmetal | 1.2 | 2.19 | 10.4867 | 1.82E+00 | 317.25 | 553 | 7 | BranBrand | 1669 | 0.769 | 3 | 5 |
| 16 | Sulfur | S | 32.065 | 16 | 16 | 16 | 3 | 16 | solid |  | yes |  | yes |  | Nonmetal | 1.1 | 2.58 | 10.36 | 2.07E+00 | 388.51 | 717.8 | 10 | Prehistoric |  | 0.71 | 3 | 6 |
| 17 | Chlorine | Cl | 35.453 | 18 | 17 | 17 | 3 | 17 | gas |  | yes |  | yes |  | Halogen | 0.97 | 3.16 | 12.9676 | 3.21E-03 | 172.31 | 239.11 | 11 | Scheele | 1774 | 0.479 | 3 | 7 |
| 18 | Argon | Ar | 39.948 | 22 | 18 | 18 | 3 | 18 | gas |  | yes |  | yes |  | NobleGas | 0.88 |  | 15.7596 | 1.78E-03 | 83.96 | 87.3 | 8 | Rayleigh_and_Ramsay | 1894 | 0.52 | 3 | 8 |

!!! note
    See [`kgtk add-id`](../add_id) for an example of
    converting a CSV file without an `id` column to a KGTK node file by adding an `id` column.

!!! note
    See [`kgtk normalize-nodes`](../normalize_nodes) for an example of
    converting a CSV file without an `id` column to a KGTK edge file.

### Expert Topic: Implying a Label Column

It is not uncommon to encounter two-column files (TSV or CSV) which represent an
edge with an implied `label` column value (`predicate`).  The `--implied-label VALUE`
option may be used to convert the input data into a three-column format.

Consider the following file, which lists some cities in the State of Massachusettes
and the year that they were founded.  Since this is neither a KGTK edge file
nor a KGTK node file, we need to specify `--mode=NONE` to bypass certain
validity checks:

```bash
kgtk cat --mode=NONE -i examples/docs/cat-two-columns.tsv
```

| node1 | node2 |
| -- | -- |
| Boston | 1630 |
| Concord | 1635 |
| Scituate | 1636 |
| Springfield | 1636 |
| Cambridge | 1638 |
| Lexington | 1642 |
| Worcester | 1673 |

We can convert this file into a KGTK edge file on input by
specifying an implied `label` column and value:

```bash
kgtk cat --implied-label=founded -i examples/docs/cat-two-columns.tsv
```

| node1 | node2 | label |
| -- | -- | -- |
| Boston | 1630 | founded |
| Concord | 1635 | founded |
| Scituate | 1636 | founded |
| Springfield | 1636 | founded |
| Cambridge | 1638 | founded |
| Lexington | 1642 | founded |
| Worcester | 1673 | founded |

!!! note
    The `--implied-label=VALUE` option is implemented by KgtkReader, and
    can be used with most KGTK subcommands.

### Expert Topic: Supressing the Output Header

Sometimes it is desired to produce a TSV file without an output header.

kgtk cat -i examples/docs/movies_reduced.tsv --no-output-header

The result will be the following file in KGTK format except
for missing the header line.


|  |  |  |  |
|---|---|---|---|
| t1 | terminator | label | 'The Terminator'@en |
| t2 | terminator | instance_of | film |
| t3 | terminator | genre | action |
| t4 | terminator | genre | science_fiction |
| t5 | terminator | publication_date | ^1984-10-26T00:00:00Z/11 |
| t6 | t5 | location | united_states |
| t7 | terminator | publication_date | ^1985-02-08T00:00:00Z/11 |
| t8 | t7 | location | sweden |
| t9 | terminator | director | james_cameron |
| t10 | terminator | cast | arnold_schwarzenegger |
| t11 | t10 | role | terminator |
| t12 | terminator | cast | michael_biehn |
| t13 | t12 | role | kyle_reese |
| t14 | terminator | cast | linda_hamilton |
| t15 | t14 | role | sarah_connor |
| t16 | terminator | duration | 108 |
| t17 | terminator | award | national_film_registry |
| t18 | t17 | point_in_time | ^2008-01-01T00:00:00Z/9 |



### Expert Topic: Reading Files without Header Records: Supply Column Names

Sometimes you may wish to read a TSV file that does not contain a
header record.

```
kgtk cat -i examples/docs/cat-file-without-header.tsv --mode=NONE
```

| john | woke | ^2020-05-02T00:00 |
| -- | -- | -- |
| john | woke | ^2020-05-00T00:00 |
| john | slept | ^2020-05-02T24:00 |
| lionheart | born | ^1157-09-08T00:00 |
| year0001 | starts | ^0001-01-01T00:00 |
| year9999 | ends | ^9999-12-31T11:59:59 |

Copy the file, supplying column names:

```
kgtk cat -i examples/docs/cat-file-without-header.tsv \
         --input-column-names node1 label node2
```

The result will be the following file in KGTK format:

| node1 | label | node2 |
| -- | -- | -- |
| john | woke | ^2020-05-00T00:00 |
| john | slept | ^2020-05-02T24:00 |
| lionheart | born | ^1157-09-08T00:00 |
| year0001 | starts | ^0001-01-01T00:00 |
| year9999 | ends | ^9999-12-31T11:59:59 |

### Expert Topic: Reading Files without Header Records: Automatic Column Names

Another approach to reading a file without a header record is to have KGTK
assign column names, which it will do beginning with COL1, COL2, etc.  It is
necessary to tell KGTK how many columns are in the file.  It is also necessary
to say `--mode=NONE`, since the generated column names do not match the definition
of a KGTK edge file or node file.

```
kgtk cat -i examples/docs/cat-file-without-header.tsv \
         --no-input-header \
         --supply-missing-column-names \
	 --number-of-columns 3 \
	 --mode=NONE
```

| COL1 | COL2 | COL3 |
| -- | -- | -- |
| john | woke | ^2020-05-02T00:00 |
| john | woke | ^2020-05-00T00:00 |
| john | slept | ^2020-05-02T24:00 |
| lionheart | born | ^1157-09-08T00:00 |
| year0001 | starts | ^0001-01-01T00:00 |
| year9999 | ends | ^9999-12-31T11:59:59 |

### Expert Topic: Reading Files without Header Records: Empty Column Names

Assume that you have a TSV file with the right number of columns in the
header record, but one or more missing column names.

```
kgtk cat -i examples/docs/cat-file-with-empty-column-names.tsv
```

    In input 1 header 'node1	label	node2		': Column 3 has an empty name in the file header
    Exit requested


You can ask the system to replace the empty column names with COLn:

```
kgtk cat -i examples/docs/cat-file-with-empty-column-names.tsv \
         --supply-missing-column-names
```

| node1 | label | node2 | COL4 | COL5 |
| -- | -- | -- | -- | -- |
| john | observed | ^2020-05-02T00:00 | fever | cough |
| john | observed | ^2020-05-00T00:00 | normal | normal |
| john | observed | ^2020-05-02T24:00 | normal | cough |


### Expert Topic: Requiring Certain Columns

Sometimes you may wish to require that an input file contains certain
named columns that are essential to your analysis.

```
kgtk cat -i examples/docs/cat-edges-with-totals.tsv
```

| node1 | label | node2 | node1;total |
| -- | -- | -- | -- |
| P10 | p585-count | 73 | 3879 |
| P1000 | p585-count | 16 | 266 |
| P101 | p585-count | 5 | 157519 |
| P1018 | p585-count | 2 | 177 |
| P102 | p585-count | 295 | 414726 |
| P1025 | p585-count | 26 | 693 |
| P1026 | p585-count | 40 | 6930 |
| P1027 | p585-count | 14 | 10008 |
| P1028 | p585-count | 1131 | 4035 |
| P1029 | p585-count | 4 | 2643 |
| P1035 | p585-count | 4 | 366 |
| P1037 | p585-count | 60 | 9317 |
| P1040 | p585-count | 1 | 45073 |
| P1050 | p585-count | 246 | 226380 |

Supposw you require that the `node1;total` column be present:

```
kgtk cat -i examples/docs/cat-edges-with-totals.tsv \
         --require-column-names  'node1;total'
```

This will succeed:

| node1 | label | node2 | node1;total |
| -- | -- | -- | -- |
| P10 | p585-count | 73 | 3879 |
| P1000 | p585-count | 16 | 266 |
| P101 | p585-count | 5 | 157519 |
| P1018 | p585-count | 2 | 177 |
| P102 | p585-count | 295 | 414726 |
| P1025 | p585-count | 26 | 693 |
| P1026 | p585-count | 40 | 6930 |
| P1027 | p585-count | 14 | 10008 |
| P1028 | p585-count | 1131 | 4035 |
| P1029 | p585-count | 4 | 2643 |
| P1035 | p585-count | 4 | 366 |
| P1037 | p585-count | 60 | 9317 |
| P1040 | p585-count | 1 | 45073 |
| P1050 | p585-count | 246 | 226380 |

Suppose you also require that an 'average' column be present, but it is missing:

```
kgtk cat -i examples/docs/cat-edges-with-totals.tsv \
         --require-column-names  'node1;total' average
```

This will result in an error message:

    In input 1 header 'node1	label	node2	node1;total': The following required columns were missing: ['average']
    Exit requested

### Expert Topic: Prohibiting Additional Columns

Sometimes you may want to prohibit additional columns.  There are several
special cases to consider:

 * Prohibiting additional columns for a standard KGTK node file.
 * Prohibiting additional columns for a standard KGTK edge file.
 * Requiring certain additional columns and prohibiting others.

Suppose that you have a standard KGTK edge file and you wish to
prohibit any additional columns.

Consider a standard KGTK node file without additional columns:

```
kgtk cat -i examples/docs/cat-nodes.tsv \
         --no-additional-columns
```

This command will succeed:

| id |
| -- |
| P10 |
| P100 |
| P1000 |

A KGTK node file with unexpected additional columns will fail:

```
kgtk cat -i examples/docs/cat-nodes-and-titles.tsv \
         --no-additional-columns
```

    In input 1 header 'id	titel': The following additional columns are unexpected: ['titel']
    Exit requested



Consider a standard KGTK edge file without additional columns:

```
kgtk cat -i examples/docs/cat-edges.tsv \
         --no-additional-columns
```

This command will succeed:

| node1 | label | node2 |
| -- | -- | -- |
| P10 | p585-count | 73 |
| P1000 | p585-count | 16 |
| P101 | p585-count | 5 |
| P1018 | p585-count | 2 |
| P102 | p585-count | 295 |
| P1025 | p585-count | 26 |
| P1026 | p585-count | 40 |
| P1027 | p585-count | 14 |
| P1028 | p585-count | 1131 |
| P1029 | p585-count | 4 |
| P1035 | p585-count | 4 |
| P1037 | p585-count | 60 |
| P1040 | p585-count | 1 |
| P1050 | p585-count | 246 |

Note: The `node1`, `label`, and `node2` columns (or their aliases) are allowed.
The `id` column is also allowed, although it is not required.

Consider a KGTK edge file with an undesired additional column:

```
kgtk cat -i examples/docs/cat-edges-with-totals.tsv \
         --no-additional-columns
```

This will fail with the following error message:

    In input 1 header 'node1	label	node2	node1;total': The following additional columns are unexpected: ['node1;total']
    Exit requested

If we want to accept the `node1;total` additional column, but prohibit
others, we can do so by explicitly listing the required columns.  All
required columns (e.g., `node1`, `label, `and node2`) must be listed:

```
kgtk cat -i examples/docs/cat-edges-with-totals.tsv \
         --require-column-names node1 label node2 'node1;total' \
         --no-additional-columns
```

This will succeed:

| node1 | label | node2 | node1;total |
| -- | -- | -- | -- |
| P10 | p585-count | 73 | 3879 |
| P1000 | p585-count | 16 | 266 |
| P101 | p585-count | 5 | 157519 |
| P1018 | p585-count | 2 | 177 |
| P102 | p585-count | 295 | 414726 |
| P1025 | p585-count | 26 | 693 |
| P1026 | p585-count | 40 | 6930 |
| P1027 | p585-count | 14 | 10008 |
| P1028 | p585-count | 1131 | 4035 |
| P1029 | p585-count | 4 | 2643 |
| P1035 | p585-count | 4 | 366 |
| P1037 | p585-count | 60 | 9317 |
| P1040 | p585-count | 1 | 45073 |
| P1050 | p585-count | 246 | 226380 |

An unexpected additional column will fail:

```
kgtk cat -i examples/docs/cat-edges-with-totals-and-averages.tsv \
         --require-column-names node1 label node2 'node1;total' \
         --no-additional-columns
```

    In input 1 header 'node1	label	node2	node1;total	average': The following additional columns are unexpected: ['average']
    Exit requested

We can add the `average` column to the list of required column names
and accept that file:

```
kgtk cat -i examples/docs/cat-edges-with-totals-and-averages.tsv \
         --require-column-names node1 label node2 'node1;total' average \
         --no-additional-columns
```

| node1 | label | node2 | node1;total | average |
| -- | -- | -- | -- | -- |
| P10 | p585-count | 73 | 3879 | 53.136986301369866 |
| P1000 | p585-count | 16 | 266 | 16.625 |
| P101 | p585-count | 5 | 157519 | 31503.8 |
| P1018 | p585-count | 2 | 177 | 88.5 |
| P102 | p585-count | 295 | 414726 | 1405.8508474576272 |
| P1025 | p585-count | 26 | 693 | 26.653846153846153 |
| P1026 | p585-count | 40 | 6930 | 173.25 |
| P1027 | p585-count | 14 | 10008 | 714.8571428571429 |
| P1028 | p585-count | 1131 | 4035 | 3.5676392572944295 |
| P1029 | p585-count | 4 | 2643 | 660.75 |
| P1035 | p585-count | 4 | 366 | 91.5 |
| P1037 | p585-count | 60 | 9317 | 155.28333333333333 |
| P1040 | p585-count | 1 | 45073 | 45073.0 |
| P1050 | p585-count | 246 | 226380 | 920.2439024390244 |

!!! note
    At the present time there is no option to list optional additional columns.

### Expert Topic: Requiring a Certain Number of Columns

Another way to ensure that a KGTK edge  file has only
[ `node1`, `label`, `node2`] columns is to require that the
file have 3 columns.  More generally, you can require that
a file have a certain number of columns without having to name
all the columns individually.

```
kgtk cat -i examples/docs/cat-edges.tsv \
         --number-of-columns 3
```

| node1 | label | node2 |
| -- | -- | -- |
| P10 | p585-count | 73 |
| P1000 | p585-count | 16 |
| P101 | p585-count | 5 |
| P1018 | p585-count | 2 |
| P102 | p585-count | 295 |
| P1025 | p585-count | 26 |
| P1026 | p585-count | 40 |
| P1027 | p585-count | 14 |
| P1028 | p585-count | 1131 |
| P1029 | p585-count | 4 |
| P1035 | p585-count | 4 |
| P1037 | p585-count | 60 |
| P1040 | p585-count | 1 |
| P1050 | p585-count | 246 |

```
kgtk cat -i examples/docs/cat-edges-with-totals.tsv \
         --number-of-columns 3
```

    In input 1 header 'node1	label	node2	node1;total': Expected 3 columns, got 4 in the header
    Exit requested

```
kgtk cat -i examples/docs/cat-edges-with-totals.tsv \
         --number-of-columns 4
```

| node1 | label | node2 | node1;total |
| -- | -- | -- | -- |
| P10 | p585-count | 73 | 3879 |
| P1000 | p585-count | 16 | 266 |
| P101 | p585-count | 5 | 157519 |
| P1018 | p585-count | 2 | 177 |
| P102 | p585-count | 295 | 414726 |
| P1025 | p585-count | 26 | 693 |
| P1026 | p585-count | 40 | 6930 |
| P1027 | p585-count | 14 | 10008 |
| P1028 | p585-count | 1131 | 4035 |
| P1029 | p585-count | 4 | 2643 |
| P1035 | p585-count | 4 | 366 |
| P1037 | p585-count | 60 | 9317 |
| P1040 | p585-count | 1 | 45073 |
| P1050 | p585-count | 246 | 226380 |

### Expert Topic: Pure Python Copies

The fast copy option can be disabled by specifying `--pure-python`.

```
kgtk cat -i examples/docs/cat-edges.tsv \
         -i examples/docs/cat-edges.tsv \
         --pure-python
```

| node1 | label | node2 |
| -- | -- | -- |
| P10 | p585-count | 73 |
| P1000 | p585-count | 16 |
| P101 | p585-count | 5 |
| P1018 | p585-count | 2 |
| P102 | p585-count | 295 |
| P1025 | p585-count | 26 |
| P1026 | p585-count | 40 |
| P1027 | p585-count | 14 |
| P1028 | p585-count | 1131 |
| P1029 | p585-count | 4 |
| P1035 | p585-count | 4 |
| P1037 | p585-count | 60 |
| P1040 | p585-count | 1 |
| P1050 | p585-count | 246 |
| P10 | p585-count | 73 |
| P1000 | p585-count | 16 |
| P101 | p585-count | 5 |
| P1018 | p585-count | 2 |
| P102 | p585-count | 295 |
| P1025 | p585-count | 26 |
| P1026 | p585-count | 40 |
| P1027 | p585-count | 14 |
| P1028 | p585-count | 1131 |
| P1029 | p585-count | 4 |
| P1035 | p585-count | 4 |
| P1037 | p585-count | 60 |
| P1040 | p585-count | 1 |
| P1050 | p585-count | 246 |

### Expert Topic: Changing the Fast Copy Minimum Size Throshold

Normally, `kgtk cat` will use the fast copy path with system commands only
when the total sizes of the input files pass a threshhold.  This is because
that are overheads on starting the system utilities as subprocesses, and for
very small files it may be faster to perform all processing directly in
Python.

The threshold may be changed.  For example, if you wanted the code to use
the fast copy path regardless of the size of the input files, use:

```
kgtk cat -i examples/docs/cat-edges.tsv \
         -i examples/docs/cat-edges.tsv \
         --fast-copy-min-size 0
```

| node1 | label | node2 |
| -- | -- | -- |
| P10 | p585-count | 73 |
| P1000 | p585-count | 16 |
| P101 | p585-count | 5 |
| P1018 | p585-count | 2 |
| P102 | p585-count | 295 |
| P1025 | p585-count | 26 |
| P1026 | p585-count | 40 |
| P1027 | p585-count | 14 |
| P1028 | p585-count | 1131 |
| P1029 | p585-count | 4 |
| P1035 | p585-count | 4 |
| P1037 | p585-count | 60 |
| P1040 | p585-count | 1 |
| P1050 | p585-count | 246 |
| P10 | p585-count | 73 |
| P1000 | p585-count | 16 |
| P101 | p585-count | 5 |
| P1018 | p585-count | 2 |
| P102 | p585-count | 295 |
| P1025 | p585-count | 26 |
| P1026 | p585-count | 40 |
| P1027 | p585-count | 14 |
| P1028 | p585-count | 1131 |
| P1029 | p585-count | 4 |
| P1035 | p585-count | 4 |
| P1037 | p585-count | 60 |
| P1040 | p585-count | 1 |
| P1050 | p585-count | 246 |


### Expert Topic: Overriding System Commands

The names of the system commands used by the fast copy path may
be overridden on the command line.

```
kgtk cat -i examples/docs/cat-edges.tsv \
         -i examples/docs/cat-edges.tsv \
         --bash-command /usr/bin/bash \
	 --bzip2-command /usr/bin/bzip2 \
	 --cat-command /usr/bin/cat \
	 --gzip-command /usr/bin/gzip \
	 --tail-command /usr/bin/tail \
	 --xz-command /usr/bin/xz
```

| node1 | label | node2 |
| -- | -- | -- |
| P10 | p585-count | 73 |
| P1000 | p585-count | 16 |
| P101 | p585-count | 5 |
| P1018 | p585-count | 2 |
| P102 | p585-count | 295 |
| P1025 | p585-count | 26 |
| P1026 | p585-count | 40 |
| P1027 | p585-count | 14 |
| P1028 | p585-count | 1131 |
| P1029 | p585-count | 4 |
| P1035 | p585-count | 4 |
| P1037 | p585-count | 60 |
| P1040 | p585-count | 1 |
| P1050 | p585-count | 246 |
| P10 | p585-count | 73 |
| P1000 | p585-count | 16 |
| P101 | p585-count | 5 |
| P1018 | p585-count | 2 |
| P102 | p585-count | 295 |
| P1025 | p585-count | 26 |
| P1026 | p585-count | 40 |
| P1027 | p585-count | 14 |
| P1028 | p585-count | 1131 |
| P1029 | p585-count | 4 |
| P1035 | p585-count | 4 |
| P1037 | p585-count | 60 |
| P1040 | p585-count | 1 |
| P1050 | p585-count | 246 |

