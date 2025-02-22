import os
import sys
import time
import traceback
from optparse import OptionParser
import json 




def loadParameter():
    
    """
    Processes the command line input for running the tournament
    """
    usageStr = """
    USAGE:      python experiment_runner.py <options>
    EXAMPLES:   (1) 



    """
    
    # logger.info("Parsing Options")
    parser = OptionParser(usageStr)
    
    # parser.add_option('-t', '--timeout', dest="timeout", help='timeout, default 300s', type='int', default=300)
    # parser.add_option('-o','--output', dest="output_path", help='output directory for the running results (default: output/<timestamp>)',default='')
    # parser.add_option('-s', '--search', dest="search_path", help='the name of the search algorithm', default='bfs')
    # parser.add_option('-d','--debug', dest="enable_debug", action='store_true', help='enable logging level to debug', default=False)
    # parser.add_option('-i','--input', dest="input_path", help='input directory for the experiments (default: examples/*)',default='examples')
    parser.add_option('-i','--input', dest="input_domain_names", help='input for the experiment config (default: examples/*)',default='examples/CONFIG')
    parser.add_option('-o','--output', dest="output_path", help='output_folder_path',default=None)
    # parser.add_option('-s','--savefiles', action='store_true', help='keep the student repos', default=False)
    # parser.add_option('--tag', help='the tag for submission', default='submission')
    options, otherjunk = parser.parse_args(sys.argv[1:] )
    assert len(otherjunk) == 0, "Unrecognized options: " + str(otherjunk)


    return options


import pandas as pd






if __name__ == '__main__':
    options=loadParameter()
    data_json = []
    # domain_name_list = []
    # with open(options.input, 'r') as f:
    #     domain_name_str = f.readline()
    #     domain_name_list = domain_name_str.split(" ")
    
    
    for file_name in os.listdir(options.output_path):
        if '.json' in file_name:
            with open(f"{options.output_path}/{file_name}",'r') as f:
                json_item = json.load(f)
                data_json.append(json_item)
                
    print(data_json)
    # df_json = pd.read_json(‘DATAFILE.json’)
    df_json = pd.DataFrame(data_json)
    excel_file_name = options.output_path+options.output_path.replace('\\','_').replace('.','')+".xlsx"
    print(excel_file_name)
    df_json.to_excel(excel_file_name)


