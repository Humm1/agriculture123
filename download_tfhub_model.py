import argparse, os
parser = argparse.ArgumentParser()
parser.add_argument('--hub_url', required=True)
parser.add_argument('--output_dir', default='./models/tfhub_model/1')
args = parser.parse_args()
out = args.output_dir
os.makedirs(out, exist_ok=True)
print('This script will download TF Hub model during CI. In this environment it is a placeholder.')
