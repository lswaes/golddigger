#!/bin/bash

# Set PATH
export PATH=$PATH:/opt/homebrew/bin

# Run your Python script SJC
cd /Users/minhtien/code/Gold-digger
/Library/Frameworks/Python.framework/Versions/3.12/bin/python3 ./main_sjc.py >> ./result.log 2>&1