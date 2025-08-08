![Datoso](https://github.com/laromicas/datoso/blob/master/bearlogo.png)

# Datoso Seed FinalBurn Neo

Datoso is a WIP Python command line tool to download and organize your Dat Roms.
As today the tool supports dat-omatic, redump, and translated-english dats.
It merges all the dats in a tree folder structure thought to use with Emulators rather than dats.
The dat file format must be compatible with [ROMVault](https://www.romvault.com/).

FinalBurn Neo is an emulator for Arcade Games & Select Consoles.

## Installation

Datoso requires python 3.11+.

For latests dats it is needed to extract them from fbneo windows executable files.

Use pip (recommended to use a virtual environment):
If you only need this plugin you can install it directly

``` bash
pip install datoso_seed_fbneo

```


For latest dats (only tested on windows or wsl) you can use the following command:
``` bash
datoso config --set FBNEO.DownloadFrom finalburnneo # this needs someway to execute windows executables, doesn't work with linux executables

datoso config --set FBNEO.System win64 # or win32
```



## Usage

Check [Datoso](https://github.com/laromicas/datoso) for usage.


## TODO

-   Tests

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
