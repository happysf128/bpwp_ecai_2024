
import datetime
import importlib
import json
import os

import sys
import traceback
from optparse import OptionParser
import pytz


import logging
import forward_pddl_model as pddl_model
# import pddl_model as pddl_model

from pddl_parser import PDDLParser
from latex_converter import epgoal2latex
# import util
from util import setup_logger_handlers,setup_logger

TIMEZONE = pytz.timezone('Australia/Melbourne')
DATE_FORMAT = '%d-%m-%Y_%H-%M-%S'
LOGGER_NAME = "instance_runner"
LOGGER_LEVEL = logging.INFO
# LOGGER_LEVEL = logging.DEBUG

class Instance:
    problem_path = ""
    domain_path = ""
    instance_name = ""
    external_function = None
    search = None
    
    def __init__(self,instance_name="",problem_path="",domain_path="",external_function= "",search= "", debug=False):
        self.problem_path = ""
        self.domain_path = ""
        self.instance_name = ""
        self.external_function = None
        self.search = None
        
        self.instance_name = instance_name
        self.problem_path = problem_path
        self.domain_path = domain_path
        self.external_function = external_function
        self.search = search


    def solve(self,timeout=300,log_debug = False, output_path = '', time_debug =False, belief_mode = -1):
        
        start_time = datetime.datetime.now().astimezone(TIMEZONE)
        result = dict()
        if output_path == '':
            output_path = f"output/{start_time.strftime(DATE_FORMAT)}"
            
        if not os.path.isdir(output_path):
            os.makedirs(output_path)
        
        if log_debug:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO  
        
        # Set up root logger, and add a file handler to root logger
        # logging.basicConfig(filename = f'{output_path}/{self.instance_name}.log',
        #                     level = debug_level,
        #                     format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')
        logger_handlers = setup_logger_handlers(f'{output_path}/{self.instance_name}.log', c_logger_level=log_level, c_display=False)
        logger = setup_logger(LOGGER_NAME,logger_handlers,logger_level=LOGGER_LEVEL) 

        # read the pddl files
        pddl_parser = PDDLParser(logger_handlers)


        logger.info(f"loading problem file: {self.problem_path}")
        variable_domains,i_state,g_states,agent_index,obj_index,variables,vd_name,p_name= pddl_parser.problemParser(self.problem_path)
        logger.info(f"finish loading problem file: {p_name}")

        logger.info(f"loading domain file: {self.domain_path}")
        actions,domain_name = pddl_parser.domainParser(f"{self.domain_path}")
        logger.info(f"finish loading domain file: {domain_name}")        
        
        if type(self.search) ==str:
            logger.info(f"loading search algorithm: {self.search}")
            search_path = self.search
            search_path = search_path.replace('.py','').replace('\\','.').replace('/','.').replace('..','')
            
            try:
                self.search = importlib.import_module(search_path)
                # self.search = __import__(search_path)
                # logger.info(f"finish loading search algorithm:")
            except (NameError, ImportError, IOError):
                traceback.print_exc()
                exit()
            except:
                traceback.print_exc()
                exit()
        else:
            logger.info(f"Search algorithm exists")
        
        
        if type(self.external_function) ==str:
            logger.info(f"loading external function: {self.external_function}")
            external_path = self.external_function
            external_path = external_path.replace('.py','').replace('\\','.').replace('/','.').replace('..','')
            try:
                external_module = importlib.import_module(external_path)
                self.external_function = external_module.ExternalFunction(logger_handlers)
                
                logger.info(f"finish loading external function")
            except (NameError, ImportError, IOError):
                traceback.print_exc()
                exit()
            except:
                traceback.print_exc()
                exit()
        else:
            self.external_function.logger.handlers = logger.handlers
            logger.info(f"External function exists")
            
            
        logger.info(f'Initialize problem')
        problem = pddl_model.Problem(variable_domains,i_state,g_states,agent_index,obj_index,variables,actions,self.external_function,belief_mode=belief_mode,handlers=logger_handlers)
        problem.logger.handlers = logger.handlers

        logger.info(f'starting search')
        start_search_time = datetime.datetime.now().astimezone(TIMEZONE)
        import func_timeout
        
        if time_debug:
            search_algorithm = self.search.Search(logger_handlers)

            result = search_algorithm.searching(problem,self.external_function.filterActionNames)
        else:
            
            try:
                search_algorithm = self.search.Search(logger_handlers)
                result = func_timeout.func_timeout(timeout, search_algorithm.searching,args=(problem,self.external_function.filterActionNames))
            except func_timeout.FunctionTimedOut:
                result.update({"running": f"timeout after {timeout}"})
            except:
                traceback.print_exc()
                exit()

        
        # result = self.search.searching(problem,self.external_function.filterActionNames)
        end_search_time = datetime.datetime.now().astimezone(TIMEZONE)
        
        init_time = start_search_time - start_time
        search_time = end_search_time - start_search_time
        
        ep_dict = problem.goals.epistemic_dict
        ep_goal_latex_str = epgoal2latex(ep_dict)

        logger.info(f'initialization time: { init_time}')
        logger.info(f'search time: {search_time }') 
            
            
        result.update({'domain_name':domain_name})  
        result.update({'problem':p_name})
        result.update({'search':self.instance_name.split('_')[0]})
        result.update({'init_time':init_time.total_seconds()})
        result.update({'search_time':search_time.total_seconds()})
        # maybe ontic goal as well?
        result.update({'goals':ep_goal_latex_str})
        
        

        print(result)
        with open(f"{output_path}/{self.instance_name}.json",'w') as f:
            json.dump(result,f) 
        
        return 

def loadParameter():

    """
    Processes the command line input for running the tournament
    """
    usageStr = """
    USAGE:      python runner.py <options>

    """
    parser = OptionParser(usageStr)

    parser.add_option('-d', '--domain', dest="domain_path", help='path to the domain file', default='')
    parser.add_option('-p', '--problem', dest="problem_path", help='path to the problem file', default='')
    parser.add_option('-e', '--external', dest="external_path", help='path to the external function file', default='')
    parser.add_option('-o', '--output', dest="output_path", help='output directory for the running results (default: output/timestamp)',default='')
    parser.add_option('-s', '--search', dest="search_path", help='the name of the search algorithm', default='bfs')
    parser.add_option('--log_debug', dest="log_debug", action='store_true', help='enable logging level to debug', default=False)
    parser.add_option('-b', '--belief_mode', dest="belief_mode", type='int', help='should between 0-3', default=1)
    parser.add_option('--time_debug', dest="time_debug", action='store_true', help='enable cProfile', default=False)
    parser.add_option('-t', '--timeout', dest="timeout", help='timeout, default 300s', type='int', default=300)
    
    options, otherjunk = parser.parse_args(sys.argv[1:] )
    assert len(otherjunk) == 0, "Unrecognized options: " + str(otherjunk)

    return options


if __name__ == '__main__':

    start_time = datetime.datetime.now().astimezone(TIMEZONE)
    options = loadParameter()
    
    problem_path = options.problem_path
    domain_path = options.domain_path
    # initialise with path, the function will load it later
    external_function = options.external_path
    search = options.search_path
    output_path = ''

    
    
    if '\\' in search:
        domain_name = domain_path.split('\\')[2]
        problem_name = problem_path.split('\\')[-1].replace('.pddl','')
        search_name = search.split('\\')[-1].replace('.py','')
    elif '/' in search:
        domain_name = domain_path.split('/')[2]
        problem_name = problem_path.split('/')[-1].replace('.pddl','')
        search_name = search.split('/')[-1].replace('.py','')        
    instance_name = f"{search_name}_{domain_name}_{problem_name}"
    
    if options.output_path == '':
        output_path = f"output/{start_time.strftime(DATE_FORMAT)}"
    if not os.path.isdir(output_path):
        os.makedirs(output_path)
    
        
    if options.time_debug:
        import cProfile
        import pstats, math
        import io
        import pandas as pd
        print("starting profiling")
        pr = cProfile.Profile()
        pr.enable()
        ins = Instance(instance_name=instance_name,problem_path=problem_path,domain_path=domain_path,external_function= external_function,search= search, )
        ins.solve(timeout=options.timeout,log_debug = options.log_debug, output_path = output_path, time_debug= options.time_debug,belief_mode=options.belief_mode)
        
        
        pr.disable()
        
        result = io.StringIO()
        pstats.Stats(pr,stream=result).print_stats()
        result=result.getvalue()
        # chop the string into a csv-like buffer
        result='ncalls'+result.split('ncalls')[-1]
        result='\n'.join([','.join(line.rstrip().split(None,5)) for line in result.split('\n')])
        # save it to disk
        file_path = f"{output_path}/{instance_name}_cprofile.csv"
        print(file_path)
        with open(f"{output_path}/{instance_name}_cprofile.csv", 'w+') as f:
            #f=open(result.rsplit('.')[0]+'.csv','w')
            f.write(result)
            f.close()

        
    else:
        ins = Instance(instance_name=instance_name,problem_path=problem_path,domain_path=domain_path,external_function= external_function,search= search)
        ins.solve(timeout=options.timeout,log_debug = options.log_debug, output_path = output_path, time_debug= options.time_debug,belief_mode=options.belief_mode)

