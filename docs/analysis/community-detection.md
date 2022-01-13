## Summary

'''
'''

| | | |
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


This command will return a clutering results from the input kgtk file.
The algorithms are provided by graph_tool (blockmodel, nested and mcmc)

### Input File

The input file should be a KGTK Edge file with the following columns or their aliases:

- `node1`: the subject column (source node)
- `label`: the predicate column (property name)
- `node2`: the object column (target node)

### Processing an Input File that is Not a KGTK Edge File

If your input file doesn't have `node1`, `label`, or `node2` columns (or their aliases) at all, then it is
not a valid KGTK Edge file.  In this case, you also have to pass the following command line option:

- `--input-mode=NONE`

### The Output File

The output file is an edge file that contains the following columns:

- `node1`: this column contains each node
- `label`: this column contains only 'in'
- `node2`: this column contains the resulting cluster
- `node2;prob`: this column contains the probability/confidence of clustering


## Usage
```
usage: kgtk community-detection [-h] [-i INPUT_FILE] [-o OUTPUT_FILE]
                                [--method METHOD]
                                [--old-id-column-name COLUMN_NAME]
                                [--new-id-column-name COLUMN_NAME]
                                [--overwrite-id [optional true|false]]
                                [--verify-id-unique [optional true|false]]
                                [--id-style {node1-label-node2,node1-label-num,node1-label-node2-num,node1-label-node2-id,empty,prefix###,wikidata,wikidata-with-claim-id}]
                                [--id-prefix PREFIX] [--initial-id INTEGER]
                                [--id-prefix-num-width INTEGER]
                                [--id-concat-num-width INTEGER]
                                [--value-hash-width VALUE_HASH_WIDTH]
                                [--claim-id-hash-width CLAIM_ID_HASH_WIDTH]
                                [--claim-id-column-name CLAIM_ID_COLUMN_NAME]
                                [--id-separator ID_SEPARATOR]
                                [-v [optional True|False]]

Creating community detection from graph-tool using KGTK file, available options are blockmodel, nested and mcmc

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FILE, --input-file INPUT_FILE
                        The KGTK input file. (May be omitted or '-' for
                        stdin.)
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        The KGTK output file. (May be omitted or '-' for
                        stdout.)
  --method METHOD       Specify the clustering method to use.
  --old-id-column-name COLUMN_NAME
                        The name of the old ID column. (default=id).
  --new-id-column-name COLUMN_NAME
                        The name of the new ID column. (default=id).
  --overwrite-id [optional true|false]
                        When true, replace existing ID values. When false,
                        copy existing ID values. When --overwrite-id is
                        omitted, it defaults to False. When --overwrite-id is
                        supplied without an argument, it is True.
  --verify-id-unique [optional true|false]
                        When true, verify ID uniqueness using an in-memory set
                        of IDs. When --verify-id-unique is omitted, it
                        defaults to False. When --verify-id-unique is supplied
                        without an argument, it is True.
  --id-style {node1-label-node2,node1-label-num,node1-label-node2-num,node1-label-node2-id,empty,prefix###,wikidata,wikidata-with-claim-id}
                        The ID generation style. (default=prefix###).
  --id-prefix PREFIX    The prefix for a prefix### ID. (default=E).
  --initial-id INTEGER  The initial numeric value for a prefix### ID.
                        (default=1).
  --id-prefix-num-width INTEGER
                        The width of the numeric value for a prefix### ID.
                        (default=1).
  --id-concat-num-width INTEGER
                        The width of the numeric value for a concatenated ID.
                        (default=4).
  --value-hash-width VALUE_HASH_WIDTH
                        How many characters should be used in a value hash?
                        (default=6)
  --claim-id-hash-width CLAIM_ID_HASH_WIDTH
                        How many characters should be used to hash the claim
                        ID? 0 means do not hash the claim ID. (default=8)
  --claim-id-column-name CLAIM_ID_COLUMN_NAME
                        The name of the claim_id column. (default=claim_id)
  --id-separator ID_SEPARATOR
                        The separator user between ID subfields. (default=-)

  -v [optional True|False], --verbose [optional True|False]
                        Print additional progress messages (default=False).
```

## Examples


### Default model (blockmodel)

The following file will be used to illustrate some of the capabilities of `kgtk reachable-nodes`.

```bash
head arnold_family.tsv
```

node1	label	node2
'Christopher Lawford'@en	P22	'Peter Lawford'@en
'Christopher Lawford'@en	P25	'Patricia Kennedy Lawford'@en
'Christopher Lawford'@en	P26	'Jean Edith Olssen'@en
'Christopher Lawford'@en	P3373	'Victoria Lawford'@en
'Christopher Lawford'@en	P3373	'Sydney Lawford'@en
'Christopher Lawford'@en	P3373	'Robin Lawford'@en
'Christopher Lawford'@en	P3448	'Mary Rowan'@en
'Christopher Lawford'@en	P3448	'Deborah Gould'@en
'Christopher Lawford'@en	P3448	'Patricia Seaton'@en

Find the communities using blockmodel.

```bash
kgtk community-detection -i arnold_family.tsv --method blockmodel
```

node1	label	node2
'Christopher Lawford'@en	in	cluster_2
'Peter Lawford'@en	in	cluster_2
'Patricia Kennedy Lawford'@en	in	cluster_7
'Jean Edith Olssen'@en	in	cluster_2
'Victoria Lawford'@en	in	cluster_2
'Sydney Lawford'@en	in	cluster_2
'Robin Lawford'@en	in	cluster_2
'Mary Rowan'@en	in	cluster_2
'Deborah Gould'@en	in	cluster_2
'Patricia Seaton'@en	in	cluster_2
'David Christopher Lawford'@en	in	cluster_2
'Savannah Rose Lawford'@en	in	cluster_2
'Matthew Valentine Lawford'@en	in	cluster_2
'Andrew Cuomo'@en	in	cluster_33
'Kerry Kennedy'@en	in	cluster_33
'Ted Kennedy'@en	in	cluster_27
'John F. Kennedy'@en	in	cluster_7
'Joseph P. Kennedy Sr.'@en	in	cluster_19
'Rose Kennedy'@en	in	cluster_19
'Joan Bennett Kennedy'@en	in	cluster_20
'Victoria Reggie Kennedy'@en	in	cluster_52
'Robert F. Kennedy'@en	in	cluster_22
'Rosemary Kennedy'@en	in	cluster_19
'Kathleen Cavendish, Marchioness of Hartington'@en	in	cluster_19
'Jean Kennedy Smith'@en	in	cluster_19
'Eunice Kennedy Shriver'@en	in	cluster_27
'Joseph P. Kennedy Jr.'@en	in	cluster_19
'Kara Kennedy'@en	in	cluster_20
'Edward M. Kennedy Jr.'@en	in	cluster_20
'Patrick J. Kennedy'@en	in	cluster_20
'Robert F. Kennedy Jr.'@en	in	cluster_33
'Ethel Skakel Kennedy'@en	in	cluster_33
'Joseph P. Kennedy II'@en	in	cluster_33
'Michael LeMoyne Kennedy'@en	in	cluster_33
'David A. Kennedy'@en	in	cluster_33
'Rory Kennedy'@en	in	cluster_33
'Kathleen Kennedy Townsend'@en	in	cluster_33
'Christopher G. Kennedy'@en	in	cluster_33
'Courtney Kennedy Hill'@en	in	cluster_33
'Douglas Harriman Kennedy'@en	in	cluster_33
'Max Kennedy'@en	in	cluster_33
'Jacqueline Kennedy Onassis'@en	in	cluster_45
'Caroline Kennedy'@en	in	cluster_45
'John F. Kennedy Jr.'@en	in	cluster_45
'Patrick Bouvier Kennedy'@en	in	cluster_45
'Arabelle Kennedy'@en	in	cluster_45
'Maria Shriver'@en	in	cluster_52
'Sargent Shriver'@en	in	cluster_52
'Arnold Schwarzenegger'@en	in	cluster_57
'Bobby Shriver'@en	in	cluster_52
'Timothy Shriver'@en	in	cluster_52
'Anthony Shriver'@en	in	cluster_52
'Mark Shriver'@en	in	cluster_52
'Christina Schwarzenegger'@en	in	cluster_57
'Christopher Schwarzenegger'@en	in	cluster_57
'Katherine Schwarzenegger'@en	in	cluster_57
'Patrick Schwarzenegger'@en	in	cluster_57
'Joseph Baena'@en	in	cluster_57
'Mildred Patricia Baena'@en	in	cluster_57
'Aurelia Schwarzenegger'@en	in	cluster_57
'Gustav Schwarzenegger'@en	in	cluster_57
'Jadrny'@en	in	cluster_57
'Meinhard Schwarzenegger'@en	in	cluster_57
'Patrick M. Knapp Schwarzenegger'@en	in	cluster_57
'Robert Sargent Shriver'@en	in	cluster_52
'Hilda Shriver'@en	in	cluster_52
'Malissa Feruzzi'@en	in	cluster_52
'Jack Pratt'@en	in	cluster_57
'Chris Pratt'@en	in	cluster_57
'Anna Faris'@en	in	cluster_57
'Alina Shriver'@en	in	cluster_52
'Rogelio Baena'@en	in	cluster_57
'Marilyn Monroe'@en	in	cluster_45


### nested model

```bash
kgtk community-detection -i arnold_family.tsv --method nested
```

'Christopher Lawford'@en	in	cluster_0_3_20
'Peter Lawford'@en	in	cluster_0_3_20
'Patricia Kennedy Lawford'@en	in	cluster_0_6_52
'Jean Edith Olssen'@en	in	cluster_0_9_20
'Victoria Lawford'@en	in	cluster_0_9_20
'Sydney Lawford'@en	in	cluster_0_9_20
'Robin Lawford'@en	in	cluster_0_4_20
'Mary Rowan'@en	in	cluster_0_4_20
'Deborah Gould'@en	in	cluster_0_4_20
'Patricia Seaton'@en	in	cluster_0_9_20
'David Christopher Lawford'@en	in	cluster_0_6_20
'Savannah Rose Lawford'@en	in	cluster_0_6_20
'Matthew Valentine Lawford'@en	in	cluster_0_4_20
'Andrew Cuomo'@en	in	cluster_0_6_58
'Kerry Kennedy'@en	in	cluster_0_9_58
'Ted Kennedy'@en	in	cluster_0_3_51
'John F. Kennedy'@en	in	cluster_0_9_6
'Joseph P. Kennedy Sr.'@en	in	cluster_0_4_26
'Rose Kennedy'@en	in	cluster_0_9_26
'Joan Bennett Kennedy'@en	in	cluster_0_6_70
'Victoria Reggie Kennedy'@en	in	cluster_0_4_26
'Robert F. Kennedy'@en	in	cluster_0_4_22
'Rosemary Kennedy'@en	in	cluster_0_6_26
'Kathleen Cavendish, Marchioness of Hartington'@en	in	cluster_0_4_26
'Jean Kennedy Smith'@en	in	cluster_0_4_26
'Eunice Kennedy Shriver'@en	in	cluster_0_6_51
'Joseph P. Kennedy Jr.'@en	in	cluster_0_3_26
'Kara Kennedy'@en	in	cluster_0_9_70
'Edward M. Kennedy Jr.'@en	in	cluster_0_9_70
'Patrick J. Kennedy'@en	in	cluster_0_4_70
'Robert F. Kennedy Jr.'@en	in	cluster_0_3_58
'Ethel Skakel Kennedy'@en	in	cluster_0_4_58
'Joseph P. Kennedy II'@en	in	cluster_0_9_58
'Michael LeMoyne Kennedy'@en	in	cluster_0_3_58
'David A. Kennedy'@en	in	cluster_0_9_58
'Rory Kennedy'@en	in	cluster_0_9_58
'Kathleen Kennedy Townsend'@en	in	cluster_0_3_58
'Christopher G. Kennedy'@en	in	cluster_0_4_58
'Courtney Kennedy Hill'@en	in	cluster_0_6_58
'Douglas Harriman Kennedy'@en	in	cluster_0_9_58
'Max Kennedy'@en	in	cluster_0_4_58
'Jacqueline Kennedy Onassis'@en	in	cluster_0_6_8
'Caroline Kennedy'@en	in	cluster_0_9_8
'John F. Kennedy Jr.'@en	in	cluster_0_9_8
'Patrick Bouvier Kennedy'@en	in	cluster_0_9_8
'Arabelle Kennedy'@en	in	cluster_0_9_8
'Maria Shriver'@en	in	cluster_0_6_28
'Sargent Shriver'@en	in	cluster_0_9_43
'Arnold Schwarzenegger'@en	in	cluster_0_9_5
'Bobby Shriver'@en	in	cluster_0_6_43
'Timothy Shriver'@en	in	cluster_0_9_43
'Anthony Shriver'@en	in	cluster_0_3_43
'Mark Shriver'@en	in	cluster_0_4_43
'Christina Schwarzenegger'@en	in	cluster_0_4_5
'Christopher Schwarzenegger'@en	in	cluster_0_4_5
'Katherine Schwarzenegger'@en	in	cluster_0_6_5
'Patrick Schwarzenegger'@en	in	cluster_0_6_5
'Joseph Baena'@en	in	cluster_0_3_5
'Mildred Patricia Baena'@en	in	cluster_0_6_5
'Aurelia Schwarzenegger'@en	in	cluster_0_4_5
'Gustav Schwarzenegger'@en	in	cluster_0_4_5
'Jadrny'@en	in	cluster_0_9_5
'Meinhard Schwarzenegger'@en	in	cluster_0_9_5
'Patrick M. Knapp Schwarzenegger'@en	in	cluster_0_4_5
'Robert Sargent Shriver'@en	in	cluster_0_9_43
'Hilda Shriver'@en	in	cluster_0_9_43
'Malissa Feruzzi'@en	in	cluster_0_9_43
'Jack Pratt'@en	in	cluster_0_4_5
'Chris Pratt'@en	in	cluster_0_9_5
'Anna Faris'@en	in	cluster_0_9_5
'Alina Shriver'@en	in	cluster_0_9_43
'Rogelio Baena'@en	in	cluster_0_9_5
'Marilyn Monroe'@en	in	cluster_0_9_8

### MCMC model

```bash
kgtk community-detection -i arnold_family.tsv --method mcmc
```

|node1                                        |label|node2    |node2;prob         |
|---------------------------------------------|-----|---------|-------------------|
|Christopher Lawford                          |in   |cluster_0|1.0                |
|Peter Lawford                                |in   |cluster_0|1.0                |
|Patricia Kennedy Lawford                     |in   |cluster_1|0.806980698069807  |
|Jean Edith Olssen                            |in   |cluster_0|1.0                |
|Victoria Lawford                             |in   |cluster_0|1.0                |
|Sydney Lawford                               |in   |cluster_0|1.0                |
|Robin Lawford                                |in   |cluster_0|1.0                |
|Mary Rowan                                   |in   |cluster_0|0.9998999899989999 |
|Deborah Gould                                |in   |cluster_0|0.9998999899989999 |
|Patricia Seaton                              |in   |cluster_0|1.0                |
|David Christopher Lawford                    |in   |cluster_0|0.9998999899989999 |
|Savannah Rose Lawford                        |in   |cluster_0|0.9998999899989999 |
|Matthew Valentine Lawford                    |in   |cluster_0|0.9997999799979999 |
|Andrew Cuomo                                 |in   |cluster_2|0.9457945794579458 |
|Kerry Kennedy                                |in   |cluster_2|1.0                |
|Ted Kennedy                                  |in   |cluster_3|0.8140814081408141 |
|John F. Kennedy                              |in   |cluster_3|0.9794979497949795 |
|Joseph P. Kennedy Sr.                        |in   |cluster_4|0.9993999399939995 |
|Rose Kennedy                                 |in   |cluster_4|0.9992999299929993 |
|Joan Bennett Kennedy                         |in   |cluster_5|0.7872787278727873 |
|Victoria Reggie Kennedy                      |in   |cluster_5|0.48514851485148514|
|Robert F. Kennedy                            |in   |cluster_6|1.0                |
|Rosemary Kennedy                             |in   |cluster_4|0.9994999499949995 |
|Kathleen Cavendish, Marchioness of Hartington|in   |cluster_4|0.9991999199919992 |
|Jean Kennedy Smith                           |in   |cluster_4|0.9995999599959996 |
|Eunice Kennedy Shriver                       |in   |cluster_1|0.866986698669867  |
|Joseph P. Kennedy Jr.                        |in   |cluster_4|0.9990999099909991 |
|Kara Kennedy                                 |in   |cluster_5|0.7872787278727873 |
|Edward M. Kennedy Jr.                        |in   |cluster_5|0.7872787278727873 |
|Patrick J. Kennedy                           |in   |cluster_5|0.787078707870787  |
|Robert F. Kennedy Jr.                        |in   |cluster_2|1.0                |
|Ethel Skakel Kennedy                         |in   |cluster_2|1.0                |
|Joseph P. Kennedy II                         |in   |cluster_2|1.0                |
|Michael LeMoyne Kennedy                      |in   |cluster_2|1.0                |
|David A. Kennedy                             |in   |cluster_2|1.0                |
|Rory Kennedy                                 |in   |cluster_2|1.0                |
|Kathleen Kennedy Townsend                    |in   |cluster_2|1.0                |
|Christopher G. Kennedy                       |in   |cluster_2|1.0                |
|Courtney Kennedy Hill                        |in   |cluster_2|1.0                |
|Douglas Harriman Kennedy                     |in   |cluster_2|1.0                |
|Max Kennedy                                  |in   |cluster_2|1.0                |
|Jacqueline Kennedy Onassis                   |in   |cluster_5|1.0                |
|Caroline Kennedy                             |in   |cluster_5|1.0                |
|John F. Kennedy Jr.                          |in   |cluster_5|1.0                |
|Patrick Bouvier Kennedy                      |in   |cluster_5|0.9998999899989999 |
|Arabelle Kennedy                             |in   |cluster_5|1.0                |
|Maria Shriver                                |in   |cluster_7|0.9790979097909791 |
|Sargent Shriver                              |in   |cluster_7|0.9998999899989999 |
|Arnold Schwarzenegger                        |in   |cluster_8|1.0                |
|Bobby Shriver                                |in   |cluster_7|0.9998999899989999 |
|Timothy Shriver                              |in   |cluster_7|0.9998999899989999 |
|Anthony Shriver                              |in   |cluster_7|1.0                |
|Mark Shriver                                 |in   |cluster_7|0.9998999899989999 |
|Christina Schwarzenegger                     |in   |cluster_8|0.9998999899989999 |
|Christopher Schwarzenegger                   |in   |cluster_8|1.0                |
|Katherine Schwarzenegger                     |in   |cluster_8|1.0                |
|Patrick Schwarzenegger                       |in   |cluster_8|1.0                |
|Joseph Baena                                 |in   |cluster_8|1.0                |
|Mildred Patricia Baena                       |in   |cluster_8|0.9997999799979999 |
|Aurelia Schwarzenegger                       |in   |cluster_8|0.9998999899989999 |
|Gustav Schwarzenegger                        |in   |cluster_8|0.9997999799979999 |
|Jadrny                                       |in   |cluster_8|0.987998799879988  |
|Meinhard Schwarzenegger                      |in   |cluster_8|1.0                |
|Patrick M. Knapp Schwarzenegger              |in   |cluster_8|0.98999899989999   |
|Robert Sargent Shriver                       |in   |cluster_7|0.9921992199219922 |
|Hilda Shriver                                |in   |cluster_7|0.9938993899389938 |
|Malissa Feruzzi                              |in   |cluster_7|0.9416941694169417 |
|Jack Pratt                                   |in   |cluster_8|0.9837983798379838 |
|Chris Pratt                                  |in   |cluster_8|0.9858985898589859 |
|Anna Faris                                   |in   |cluster_8|0.9840984098409841 |
|Alina Shriver                                |in   |cluster_7|0.9413941394139413 |
|Rogelio Baena                                |in   |cluster_8|0.9873987398739874 |
|Marilyn Monroe                               |in   |cluster_5|0.49194919491949196|
