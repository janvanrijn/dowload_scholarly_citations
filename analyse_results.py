import argparse
import logging
import os
import pandas as pd
import re


def read_cmd():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results_directory', default='results', type=str)
    parser.add_argument('--output_directory', default=os.path.expanduser('~/experiments/citations'), type=str)
    parser.add_argument('--forbidden_titles', nargs='+', default=['Opleiding Informatica', 'Title not available'], type=str)
    args_, misc = parser.parse_known_args()

    return args_


def extract_from_directory(directory, paper_name, forbidden_titles, warn_duplicates):
    results = dict()
    index = set()
    logging.info('Will extract from dir: %s' % directory)
    for file_name in os.listdir(directory):
        file_path = directory + '/' + file_name
        _, extension = os.path.splitext(file_path)
        if extension == '.json':
            logging.info('Will extract from file: %s' % file_path)
            df = pd.read_json(file_path)
            for title in df['title']:
                if title in forbidden_titles:
                    continue
                alpha_numeric = re.sub(r'\W+', '', title)
                if alpha_numeric in index and warn_duplicates:
                    logging.warning('Duplicate: %s' % title)
                index.add(alpha_numeric)
                results[alpha_numeric] = title
    return results


def run(args):
    results_all_papers = {}
    all_keys = set()
    warn_on_duplicates = False
    for file_name in os.listdir(args.results_directory):
        file_path = args.results_directory + '/' + file_name
        if not os.path.isfile(file_path):
            results_paper = extract_from_directory(file_path, file_name, args.forbidden_titles, warn_on_duplicates)
            all_keys.update(results_paper.keys())
            logging.info("results: %d" % len(results_paper))
            results_all_papers[file_name] = results_paper
    
    results_pivot = []
    for key in all_keys:
        current_record = {
            'title': None
        }
        for paper in results_all_papers:
            if key in results_all_papers[paper]:
                current_record['title'] = results_all_papers[paper][key]
                current_record[paper] = True
            else:
                current_record[paper] = False
        results_pivot.append(current_record)
    df_pivot = pd.DataFrame(results_pivot)
    logging.info('Dataframe shape: %d,%d' % df_pivot.shape)
    
    for paper in results_all_papers:
        count = df_pivot[paper].sum()
        logging.info('Number of citations: %d' % count)
    
    output_file = args.output_directory + '/merged.csv'
    df_pivot.to_csv(output_file)
    logging.info('Saved to %s' % output_file)


if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    run(read_cmd())
