"""
This file will be invoked by python when called with th `-m` options:
```
python -m km3net_testdata offline/km3net_offline.root
```
"""
import argparse
from . import data_path

if __name__ == "__main__":
    description = "Expand a testing dataset path to a full path."
    parser = argparse.ArgumentParser(prog="km3net_testdata")
    parser.add_argument("file_path", help="path to expand", type=str)
    args = parser.parse_args()

    path = data_path(args.file_path)
    print(path)
