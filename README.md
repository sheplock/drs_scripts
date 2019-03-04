# drs_scripts

## Example:
First creat `./processed/` and `./unprocessed/` in the `drs_scripts` folder (specified in `./postprocessMultiChan.py`). Then
put your `.dat` binary file in the `./unprocessed/` folder then run `python ./processMultiChanBinary.py ./unprocessed/xxx.dat` to extract information
into a `.root` file to be outputed into `./processed` folder.

Next, run `python ./postprocessMultiChan.py ./processed/xxx.root/` to add branches into the root file (area, height etc.)
