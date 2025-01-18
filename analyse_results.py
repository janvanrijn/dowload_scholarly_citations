import argparse
import logging
import os
import pandas as pd
import re


def read_cmd():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results_directory', default='results', type=str)
    parser.add_argument('--output_directory', default=os.path.expanduser('~/experiments/citations'), type=str)
    args_, misc = parser.parse_known_args()

    return args_


def extract_from_directory(directory):
    results = dict()
    logging.info('Will extract from dir: %s' % directory)
    for file_name in os.listdir(directory):
        file_path = directory + '/' + file_name
        _, extension = os.path.splitext(file_path)
        if extension == '.json':
            logging.info('Will extract from file: %s' % file_path)
            df = pd.read_json(file_path)
            for title in df['title']:
                alpha_numeric = re.sub(r'\W+', '', title)
                if alpha_numeric in results:
                    logging.warning('Duplicate: %s' % title)
                results[alpha_numeric] = title


def run(args):
    for file_name in os.listdir(args.results_directory):
        file_path = args.results_directory + '/' + file_name
        if not os.path.isfile(file_path):
            results = extract_from_directory(file_path)
        

if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    run(read_cmd())
