# cTez Drift Stats
This application collects ctez drift and target information from the better-call.dev interface

## Installation: 
- `sudo apt-get install Python3.9`
- `sudo git clone https://github.com/hclivess/ctez_stats`

## Running: 
- `cd ctez_stats`
- `Python3.9 drift.py`
- open browser at http://localhost:8888 to access the menu

## Notes:
Notice that URLs are programmable, required parameters:

### chart 
- Type of the chart to draw, wither `drift` or `target`.
### start
- The starting block of the chart. If a negative number is supplied, the value is subtracted from the `end` parameter. Also accepts `min` value, which returns the first collected block.
### end
- The ending block of the chart. Also accepts `max` value, which returns the last collected block.
### resolution
- Number of points to display in the chart, also accepts `max` value, which returns the range between `start` and `end`.