import argparse
import json
import logging
import os

from scholarly import ProxyGenerator
from scholarly import scholarly

# JvR: note: this script does not allow for the successful download of OpenML citations, 
# since the Google Scholar API blocks all requests after pagination 100 (first 1000 results)
# could be fixed by further specifying the query (e.g., download all citations per year)
# but that requires additional digging in the scholarly API. 
def read_cmd():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scraper_api_key', default=None, type=str)
    parser.add_argument('--publication_id', default='17799286834300265378', type=str)
    parser.add_argument('--result_limit', default=10, type=int)
    parser.add_argument('--start_index', default=0, type=int)
    parser.add_argument('--output_directory', default=os.path.expanduser('~/experiments/citations'), type=str)
    args_, misc = parser.parse_known_args()

    return args_


def process_results(publication_id, start_index, result_limit):
    all_results_raw = scholarly.search_citedby(publication_id)
    all_results = []
    for result in all_results_raw:
        all_results.append(result)
        
        if result_limit is None:
            logging.info('[%s %d] Processed %d results ' % (publication_id, start_index, len(all_results)))
        else:
            logging.info('[%s %d] Processed %d/%d results ' % (publication_id, start_index, len(all_results), result_limit))
        
        if result_limit is not None and len(all_results) > result_limit:
            return all_results
    
    return all_results


def run(args):
    if args.scraper_api_key is not None:
        logging.info('Using Scraper API, key %s' % args.scraper_api_key)
        pg = ProxyGenerator()
        success = pg.ScraperAPI(args.scraper_api_key)
        scholarly.use_proxy(pg)
    else:
        logging.info('No Scraper API key given, not using any proxy')
    
    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)
    
    results = process_results(args.publication_id, args.start_index, args.result_limit)
    
    start_index = args.start_index
    if args.start_index is None:
        start_index = 0
    
    output_file = '%s/citations_%s_%s.json' % (args.output_directory, start_index, args.publication_id)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        logging.info('Saved %d results to file: %s' % (len(results), output_file))


if __name__ == '__main__':
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    run(read_cmd())
