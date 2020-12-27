# exsnap

Automate the downloading of Snapchat memories using `memories_history.json` 
from a data export request.

# How to use

1. Install the package via `pip install exnsap`.
2. Perform a [data request](https://accounts.snapchat.com/accounts/downloadmydata) with Snapchat.
3. Download your data zip when created and extract `json/memories_history.json`.
4. Run `exsnap` in the folder of your choice.
    - You can specify `-i` for the location of the JSON if not in the current working directory,
      or it has a different name.
    - You can specify `-o` for the output folder if you don't want the current working directory.
