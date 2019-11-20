## Non-built in dependence
* ROOT
* numpy
* matplotlib


## Example:
First create a folder or folders to store data in the `drs_scripts` directory. For example, `./unprocessed/` for the `.dat` binary files from the DRS, `./currentMonitor/` for the Keithley I-V data, and `./processed/` for the output `.root` files.

Run the command using `-b` and `-c` to specify path to `.dat` and `.csv`'s respectively, and `-o` to specify path for output.

```python
python ./processMultiChanBinary.py -b ./unprocessed/ -c ./currentMonitor/ -o ./processed/
```

This will create a `.root` file in `./processed/` for each `.dat` in `./unprocessed/`. For each `.dat`, ALL `.csv` files in `./currentMonitor/` are searched to match oscilloscope timestamp with the corresponding bias voltage recorded by the Keithley.

## processMultiChanBinary.py
The first step is to parse the binary DRS output to extract 1024 (time, voltage) measurements for each channel for each event, which are stored in ROOT branches.

Then, the `postprocess` function defined in `utils.py` is called to add higher level event information (noise, offset, pulse area, etc.) to the ROOT tree.
