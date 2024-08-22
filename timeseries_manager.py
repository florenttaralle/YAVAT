import json, os, argparse as ap, re
import numpy as np, pandas as pd
from pandas.api.types import is_numeric_dtype


# Quick and dirty script to add/remove timesries in existing YAVAT File.
# To be used until a proper GUI is implemented in YAVAT.

parser = ap.ArgumentParser()
parser.add_argument('yavat_path')
parser.add_argument('-o', '--output_yavat_path', default=None)
parser.add_argument('-c', '--csv_path')
parser.add_argument('-f', '--frame_id_column')
parser.add_argument('-a', '--append_timeseries', action='append', default=[])
parser.add_argument('-r', '--remove_timeseries', action='append', default=[])
args = parser.parse_args()

# load yavat content
assert os.path.exists(args.yavat_path), f"YAVAT File not found: {args.yavat_path}"
with open(args.yavat_path) as yavat_file:
    yavat = json.load(yavat_file)
# ensure the timeseries key exists
if 'timeseries' not in yavat:
    yavat['timeseries'] = []

if args.append_timeseries and not args.csv_path:
    raise ValueError("Must provide a CSV file to append timeseries")

# load csv content if any provided
if args.csv_path:
    assert os.path.exists(args.csv_path), f"CSV File not found: {args.csv_path}"
    csv = pd.read_csv(args.csv_path)
else:
    csv = None

# check frame_id_column if any provided
if args.csv_path and args.frame_id_column:
    assert args.frame_id_column in csv.columns, f"No Column '{args.frame_id_column}' in CSV file"
    assert is_numeric_dtype(csv[args.frame_id_column].dtype), f"Column '{args.frame_id_column}' is not Numeric"

# add new timeseries
for timeseries_name in args.append_timeseries:
    assert timeseries_name in csv.columns, f"No Column '{timeseries_name}' in CSV file"
    assert is_numeric_dtype(csv[timeseries_name].dtype), f"Column '{timeseries_name}' is not Numeric"
    Y = csv[timeseries_name].values.astype(float)
    if args.frame_id_column:
        X = csv[args.frame_id_column].values.astype(float)
    else:
        X = np.arange(len(Y))
    xy_values   = list(zip(X, Y))
    y_min       = Y.min()
    y_max       = Y.max()
    yavat['timeseries'].append({
        'name':         timeseries_name,
        'xy_values':    xy_values,
        'y_min':        y_min,
        'y_max':        y_max,
    })

# rem existing timeseries    
for timeseries_pattern in args.remove_timeseries:
    yavat['timeseries'] = [
        timeseries for timeseries in yavat['timeseries']
        if re.match(timeseries_pattern, timeseries['name']) is None
    ]

# save result
output_yavat_path = args.output_yavat_path or args.yavat_path
with open(output_yavat_path, 'wt') as yavat_file:
    json.dump(yavat, yavat_file, indent=2)
