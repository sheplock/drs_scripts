# drs_scripts

## Example:
First creat `./processed/` and `./unprocessed/` in the `drs_scripts` folder (specified in `./postprocessMultiChan.py`).
Put all `.dat` and `.csv` files in `./unprocessed`, run the command using `-b` and `-c` to specify path to
`.dat` and `.csv`'s respectively:

```python
python ./processMultiChanBinary.py -b ./unprocessed -c ./unprocessed
# this will creact a .root file for each .dat in ./processed
# for each .root file, ALL .csv files will be used to search timestamps.
```

Next, run `python ./postprocessMultiChan.py ./processed/xxx.root/` to add branches into the root file (area, height etc.)
