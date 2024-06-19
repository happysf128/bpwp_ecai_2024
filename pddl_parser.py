import os
import logging
import datetime
import pytz
import re
import traceback
TIMEZONE = pytz.timezone('Australia/Melbourne')
DATE_FORMAT = '%d-%m-%Y_%H-%M-%S'
timestamp = datetime.datetime.now().astimezone(TIMEZONE).strftime(DATE_FORMAT)
# logging.basicConfig(filename=f'logs/{timestamp}.log', level=logging.DEBUG)



LOGGER_NAME = "pddl_parser"
LOGGER_LEVEL = logging.INFO
# LOGGER_LEVEL = logging.DEBUG
from util import setup_logger

class PDDLParser:
    logger = None
    def __init__(self,handlers):
        self.logger = setup_logger(LOGGER_NAME,handlers,logger_level=LOGGER_LEVEL) 
        self.logger.debug("PDDL PARSER initialized")
    
    def formatDocument(self,str):
        # . match anything but the endline
        # * match 0 or more preceding RE
        # $ matchs end line
        str = re.sub(';.*$',"",str,flags=re.MULTILINE).lower()
        self.logger.debug(repr(str))
        
        # removing useless space
        # ^ match any start of the newline in multiline mode
        str = re.sub('^ *| *$|^\n',"",str,flags=re.MULTILINE)
        str = re.sub(' *, *',",",str,flags=re.MULTILINE)
        str = re.sub(' *- *',"-",str,flags=re.MULTILINE)
        str = re.sub('\[ *',"[",str,flags=re.MULTILINE)
        str = re.sub(' *\]',"]",str,flags=re.MULTILINE)
        str = re.sub(':goal *',":goal",str,flags=re.MULTILINE)
        str = re.sub(':action *',":action ",str,flags=re.MULTILINE)
        str = re.sub(':parameters *',":parameters",str,flags=re.MULTILINE)
        str = re.sub(':precondition *',":precondition",str,flags=re.MULTILINE)
        str = re.sub(':effect *',":effect",str,flags=re.MULTILINE)
        self.logger.debug(repr(str))
        
        # removing useless \n
        str = re.sub('\( *|(\n)*\((\n)*',"(",str,flags=re.MULTILINE)
        str = re.sub(' *\)|(\n)*\)(\n)*',")",str,flags=re.MULTILINE)
        str = re.sub('\)\n',")",str,flags=re.MULTILINE)
        self.logger.debug(repr(str))
        
        str = re.sub('\n'," ",str,flags=re.MULTILINE)
        self.logger.debug(repr(str)) 
        return str      

    def problemParser(self,file_path):
        domains = {'agent':{'basic_type':'agent','values':[]},}
        i_state = {}
        g_states = {}
        agent_index = []
        obj_index = []
        variables = {}
        d_name = ""
        p_name = ""
        
        self.logger.debug("reading problem file:")
        
        with open(file_path,"r") as f:
            file = f.read()
            self.logger.debug(repr(file))
            
            self.logger.debug("formating problem file")
            str = self.formatDocument(file)
            self.logger.debug(repr(str))
            
            if not str.startswith("(define"):
                self.logger.error("the problem file does not start with '(define'")
                self.logger.error(traceback.format_exc())
                exit()
            elif not str.endswith(")"):
                self.logger.error("the problem file does not end with ')'")
                self.logger.error(traceback.format_exc())
                exit()
            str = str[7:-1:]
            self.logger.debug(repr(str))
            
            self.logger.debug("extract p_name")
            try:
                found = re.search('\(problem [0-9a-z_]*\)',str).group(0)
                p_name = found[9:-1:]
                self.logger.info(f"parsing problem: [{p_name}]")
                # self.logger.debug(p_name)
            except AttributeError:
                self.logger.error("error when extract problem name")
                self.logger.error(traceback.format_exc())
                exit()
                
            self.logger.debug("extract d_name")
            try:
                found = re.search('\(:domain [0-9a-z_]*\)',str).group(0)
                d_name = found[9:-1:]
                self.logger.debug(d_name)
            except AttributeError:
                self.logger.error("error when extract domain name")
                self.logger.error(traceback.format_exc())
                exit()            

            self.logger.debug("extract agents")
            try:
                found = re.search('\(:agents [0-9a-z_ ]*\)',str).group(0)
                agent_index = found[9:-1:].split(" ")
                self.logger.debug(agent_index)
            except AttributeError:
                self.logger.error("error when extract agents")
                self.logger.error(traceback.format_exc())
                exit()

            self.logger.debug("extract objects")
            try:
                found = re.search('\(:objects [0-9a-z_ ]*\)',str).group(0)
                obj_index = found[10:-1:].split(" ")
                self.logger.debug(obj_index)
            except AttributeError:
                self.logger.error("error when extract objects")
                self.logger.error(traceback.format_exc())
                exit()

            self.logger.debug("extract variables")
            try:
                found = re.search('\(:variables([(][0-9a-z_ \[\],]*[)])*\)',str).group(0)
                self.logger.debug( found)
                vars_list = re.findall('\([0-9a-z_ \[\],]*\)',found[10:-1:])
                self.logger.debug(vars_list)
                for var_str in vars_list:
                    var_str = var_str[1:-1:].split(' ')
                    variable_name = var_str[0]
                    target_entities_list =[] 
                    for entities in var_str[1:]:
                        target_entities_list.append(entities[1:-1:].split(","))
                    variables.update({variable_name:target_entities_list})
                self.logger.debug(variables)
            except AttributeError:
                self.logger.error("error when extract variables")
                self.logger.error(traceback.format_exc())
                exit()
                
            self.logger.debug("extract init")
            try:
                found = re.search("\(:init(\(= \([0-9a-z_ ]*\) [0-9a-z_\'\"]*\))*\)",str).group(0)
                self.logger.debug( found)
                init_list = re.findall('\(= \([0-9a-z_ ]*\) [0-9a-z_\'\"]*\)',found[6:-1:])
                self.logger.debug(init_list)
                for init_str in init_list:
                    init_str = init_str[3:-1:]
                    i,j = re.search("\(.*\)", init_str).span()
                    var_str = init_str[i+1:j-1:].replace(" ","-")
                    value = init_str[j+1::]
                    # value = re.search('".*"',init_str[j+1::]).group(0)
                    if "'" in value:
                        value = value.replace("'","")
                    elif '"' in value:
                        value = value.replace('"',"")
                    else:
                        value =int(value)
                    i_state.update({var_str:value})
                    
                self.logger.debug(i_state)
            except AttributeError:
                self.logger.error("error when extract init")
                self.logger.error(traceback.format_exc())
                exit()            

            self.logger.debug("extract goal")
            try:
                
                found = re.search("\(:goal\(and\([=><] \([:0-9a-z_ \- \[\],]*(\(.*\)\)|\))[0-9a-z_ \"\'\-]*\)*\)\)",str).group(0)
                self.logger.debug( found)
                
                # loading ontic goals
                self.logger.debug("extract ontic goal propositions")
                g_states["ontic_g"] = list()
                # ontic_goal_list = re.findall('\(= \([0-9a-z_ ]*\) [0-9a-z_\'\"]*\)',found[10:-1:])
                ontic_goal_list = re.findall('\(= \(:ontic[ 0-9a-z_\[\],]*\([=><] \([ 0-9a-z_]*\) [0-9a-z_\'\"-]*\)\) [0-9a-z_\'\"-]*\)',found[10:-1:])  
                ontic_prefix = "(= (:ontic ("
                ontic_surfix = ")"
                self.logger.debug('ontic goal list: [%s]',ontic_goal_list)
                for goal_str in ontic_goal_list:
                    self.logger.debug(goal_str)
                    key = goal_str.replace(' ?',"?")
                    goal_str = goal_str[len(ontic_prefix):-len(ontic_surfix):]
                    self.logger.debug(goal_str)
                    goal_str_list = goal_str.split(" ")
                    symbol  = goal_str_list[0]
                    value = goal_str_list[-1]
                    goal_str = goal_str[(len(symbol)+2):-(len(value)+3):]
                    self.logger.debug(goal_str)
                    goal_list = goal_str.split(') ')
                    variable = goal_list[0].replace(' ?','?').replace(' ','-')
                    v_value = goal_list[1]
                    if "'" in v_value:
                        v_value = v_value.replace("'","")
                    elif '"' in v_value:
                        v_value = v_value.replace('"',"")
                    elif '?' in v_value:
                        v_value = v_value.replace(' ?',"?").replace(')','').replace('(','')
                    else:
                        v_value =int(v_value)                            
                    
                    self.logger.debug("ontic_g: [%s]",(key,symbol,variable,v_value,value))

                    g_states["ontic_g"].append((key,symbol,variable,v_value,value))
                
                # loading epismetic goals
                self.logger.debug("extract epistemic goal propositions")
                g_states["epistemic_g"] = list()
                self.logger.debug("found [%s]",found)
                self.logger.debug("found[10:-1:] [%s]",found[10:-1:])
                self.logger.debug("found replaced [%s]",found[10:-1:].replace(")-1)",") -1)"))
                epistemic_goal_list = re.findall('\(= \(:epistemic[\? 0-9a-z_\[\],]*\((?:>|<|=|>=|<=)+ \([ 0-9a-z_\? ]*\) (?:[0-9a-z_\'\"-]+|\([0-9a-z_ ]+\))\)\) [0-9a-z-]*\)',found[10:-1:].replace(")-1)",") -1)"))  
                epistemic_prefix = "(= (:epistemic "
                epistemic_surfix = ")"
                self.logger.debug(epistemic_goal_list)
                for goal_str in epistemic_goal_list:
                    self.logger.debug("goal string 1: [%s]",goal_str)
                    key = goal_str.replace(' ?',"?")
                    goal_str = goal_str[len(epistemic_prefix):-len(epistemic_surfix):]
                    self.logger.debug("goal string 2: [%s]",goal_str)
                    goal_str_list = goal_str.split(" ")
                    # symbol  = goal_str_list[0]
                    value = goal_str_list[-1]
                    goal_str = goal_str[:-(len(value)+2):]
                    value = int(value)
                    query = goal_str
                    self.logger.debug("goal string 3: [%s]",goal_str)
                    
                    # i,j = re.search('\)\) .*',goal_str).span()
                    # value1 = int(goal_str[i+3:j:])
                    
                    p,q = re.search('(?:>|<|=|>=|<=)+ \([ 0-9a-z_\? ]*\) (?:[0-9a-z_\'\"-]+|\([0-9a-z_ ]+\))\)',goal_str).span()
                    # query = goal_str[:p-1]
                    goal_str = goal_str[p:q-1]
                    self.logger.debug("goal string 4: [%s]",goal_str)
                    
                    
                    goal_list = goal_str.split(' ')
                    symbol = goal_list[0]
                    goal_str = goal_str[(len(symbol)+2)::]
                    goal_list = goal_str.split(') ')
                    old_variable = goal_list[0]
                    variable = goal_list[0].replace(' ?','?').replace(' ','-')
                    self.logger.debug("old variable string: [%s]",old_variable)
                    self.logger.debug("new variable string: [%s]",variable)
                    self.logger.debug("query string: [%s]",query)
                    query = query.replace(old_variable,variable) 
                    self.logger.debug("query string: [%s]",query)
                    key = key.replace(old_variable,variable)
                    v_value = goal_list[1]
                    if "'" in v_value:
                        v_value = v_value.replace("'","")
                    elif '"' in v_value:
                        v_value = v_value.replace('"',"")
                    elif '?' in v_value:
                        v_value = v_value.replace(' ?',"?").replace(')','').replace('(','')
                    elif "(" in v_value and ")" in v_value:
                        
                        v_value = v_value[1:-1]
                        old_v_value = v_value
                        v_value = v_value.replace(" ","-")
                        query = query.replace(old_v_value,v_value)
                    else:
                        v_value =int(v_value)

                    self.logger.debug("epistemic_p: [%s]",(key,symbol,query,variable,v_value,value))
                    g_states["epistemic_g"].append((key,symbol,query,variable,v_value,value))

                    
                self.logger.debug(g_states)
            except AttributeError:
                self.logger.error("error when extract goal")
                self.logger.error(traceback.format_exc())
                traceback.print_exc()
                exit()   
                            
            self.logger.debug("extract domains")
            try:
                self.logger.debug(str)
                
                found = re.search('\(:domains(\([0-9a-z_ \[\],\'\"]*\))*\)',str).group(0)
                self.logger.debug( found)
                domains_list = re.findall('\([0-9a-z_ \[\],\'\"]*\)',found[9:-1:])
                self.logger.debug(domains_list)
                for domain_str in domains_list:
                    domain_str = domain_str[1:-1:].split(' ')
                    if not domain_str[1] in ['enumerate','integer','string']:
                        self.logger.error(f"domain {domain_str[0]}'s basic_type {domain_str[1]} does not exist")
                        assert(f"domain {domain_str[0]}'s basic_type {domain_str[1]} does not exist")
                    else:
                        if "'" in domain_str[2]:
                            value = domain_str[2].replace("'","")[1:-1:].split(",")
                        elif '"' in domain_str[2]:
                            value = domain_str[2].replace('"',"")[1:-1:].split(",")
                        else:
                            value = [ int(i) for i in domain_str[2][1:-1:].split(",")]
                        domains.update({domain_str[0]:{"basic_type":domain_str[1],"values":value}})
                self.logger.debug(domains)
            except AttributeError:
                
                self.logger.error("error when extract domains")
                self.logger.error(traceback.format_exc())
                exit()
                
            return domains,i_state,g_states,agent_index,obj_index,variables,d_name,p_name
        
    def domainParser(self,file_path):
        actions = {}
        d_name = ""

        
        self.logger.debug("reading domain file:")
        
        with open(file_path,"r") as f:
            file = f.read()
            self.logger.debug(repr(file))
            
            self.logger.debug("formating domain file")
            str = self.formatDocument(file)
            self.logger.debug(repr(str))
            
            if not str.startswith("(define"):
                self.logger.error("the domain file does not start with '(define'")
                exit()
            elif not str.endswith(")"):
                self.logger.error("the domain file does not end with ')'")
                exit()
            str = str[7:-1:]
            self.logger.debug(repr(str))
            
            self.logger.debug("extract d_name")
            try:
                found = re.search('\(domain [0-9a-z_]*\)',str).group(0)
                d_name = found[8:-1:]
                self.logger.info(f"parsing domain: [{d_name}]")
                # self.logger.debug(d_name)
            except AttributeError:
                
                self.logger.error("error when extract domain name")
                self.logger.error(traceback.format_exc())
                exit()  
            
            
            self.logger.debug("extract actions")
            try:
                action_list = str.split("(:action ")[1::]

                for action_str in action_list:
                    parameters = []
                    preconditions = {}
                    effects = []
                    action_str = action_str[:-1:]
                    action_name = action_str.split(" ")[0]
                    
                    # decode parameters
                    parameters_str = re.search(':parameters\(.*\):precondition',action_str).group()
                    self.logger.debug('parameters_str: [%s]',parameters_str)
                    for p_str in parameters_str[12:-14:].split(","):
                        if p_str == '':
                            continue
                        self.logger.debug('single parameters_str: [%s]',p_str)
                        p = p_str.split("-")
                        parameters.append((p[0],p[1]))
                    self.logger.debug('parameters: [%s]',parameters)
                    
                    self.logger.debug("extract preconditions")
                    try:
                        
                        preconditions_str = re.search(':precondition\(and.*\):effect', action_str).group()
                        preconditions_str = preconditions_str[17:-8:]
                        self.logger.debug(preconditions_str)
                        
                        # loading ontic precondition
                        self.logger.debug("extract ontic preconditions propositions")

                        preconditions["ontic_p"] = list()
                        # ontic_goal_list = re.findall('\(= \([0-9a-z_ ]*\) [0-9a-z_\'\"]*\)',found[10:-1:])
                        # (= (:ontic (= (agent_at-a) (secret_at ?s))) 1)
                        ontic_pre_list = re.findall('\(= \(:ontic[ 0-9a-z_\[\],]*\([=><] \([ 0-9a-z_\-\?]*\) [\(\)\?0-9a-z_\'\" ]*\)\) [0-9a-z_\'\"-]*\)',preconditions_str)  

                        ontic_prefix = "(= (:ontic ("
                        ontic_surfix = ")"
                        self.logger.debug('ontic preconditions list: [%s]',ontic_pre_list)
                        for pre_str in ontic_pre_list:
                            key = pre_str.replace(' ?',"?")
                            self.logger.debug(pre_str)
                            pre_str = pre_str[len(ontic_prefix):-len(ontic_surfix):]
                            self.logger.debug(pre_str)
                            pre_str_list = pre_str.split(" ")
                            symbol  = pre_str_list[0]
                            value = pre_str_list[-1]
                            pre_str = pre_str[(len(symbol)+2):-(len(value)+3):]
                            self.logger.debug(pre_str)
                            
                            self.logger.debug('single goal_str [%s]',pre_str)
                            
                            goal_list = pre_str.split(') ')
                            variable = goal_list[0].replace(' ?','?').replace(' ','-')
                            v_value = goal_list[1]
                            if "'" in v_value:
                                v_value = v_value.replace("'","")
                            elif '"' in v_value:
                                v_value = v_value.replace('"',"")
                            elif '?' in v_value:
                                v_value = v_value.replace(' ?',"?").replace(')','').replace('(','')
                            else:
                                v_value =int(v_value)
                            self.logger.debug("ontic_p: [%s]",(key,symbol,variable,v_value,value))
                            preconditions["ontic_p"].append((key,symbol,variable,v_value,value))
                                
                        # loading epismetic goals
                        self.logger.debug("extract epistemic precondition propositions")
                        self.logger.debug("input pre str: [%s]",preconditions_str)
                        preconditions["epistemic_p"] = list()
                        epistemic_pre_list = re.findall('\(= \(:epistemic[\? 0-9a-z_\[\],]*\((?:>|<|=|>=|<=)+ \([ 0-9a-z_\? ]*\) (?:[0-9a-z_\'\"-]+|\([0-9a-z_ ]+\))\)\) [0-9a-z-]*\)',preconditions_str)  
                        epistemic_prefix = "(= (:epistemic "
                        epistemic_surfix = ")"
                        self.logger.debug(epistemic_pre_list)
                        for pre_str in epistemic_pre_list:
                            key = pre_str.replace(' ?',"?")
                            self.logger.debug(pre_str)
                            pre_str = pre_str[len(epistemic_prefix):-len(epistemic_surfix):]
                            self.logger.debug(pre_str)
                            pre_str_list = pre_str.split(" ")
                            # symbol  = goal_str_list[0]
                            value = pre_str_list[-1]
                            pre_str = pre_str[:-(len(value)+2):]
                            value = int(value)
                            query = pre_str
                            self.logger.debug(pre_str)
                            
                            # i,j = re.search('\)\) .*',goal_str).span()
                            # value1 = int(goal_str[i+3:j:])
                            
                            p,q = re.search('(?:>|<|=|>=|<=)+ \([ 0-9a-z_\? ]*\) (?:[0-9a-z_\'\"-]+|\([0-9a-z_ ]+\))\)',pre_str).span()
                            # query = pre_str[:p-1]
                            pre_str = pre_str[p:q-1]
                            
                            
                            pre_str_list = pre_str.split(' ')
                            symbol = pre_str_list[0]
                            pre_str = pre_str[(len(symbol)+2)::]
                            pre_str_list = pre_str.split(') ')
                            old_variable = pre_str_list[0]
                            variable = pre_str_list[0].replace(' ?','?').replace(' ','-')
                            self.logger.debug("old variable string: [%s]",old_variable)
                            self.logger.debug("new variable string: [%s]",variable)
                            self.logger.debug("query string: [%s]",query)
                            query = query.replace(old_variable,variable) 
                            self.logger.debug("query string: [%s]",query)
                            key = key.replace(old_variable,variable)
                            v_value = pre_str_list[1]
                            if "'" in v_value:
                                v_value = v_value.replace("'","")
                            elif '"' in v_value:
                                v_value = v_value.replace('"',"")
                            elif '?' in v_value:
                                v_value = v_value.replace(' ?',"?").replace(')','').replace('(','')
                            elif "(" in v_value and ")" in v_value:
                                old_v_value = v_value
                                v_value = v_value[1:-1]
                                v_value = v_value.replace(" ","-")
                                query = query.replace(old_v_value,v_value)
                                
                                
                            else:
                                v_value =int(v_value)
                            self.logger.debug("epistemic_p: [%s]",(key,symbol,query,variable,v_value,value))
                            preconditions["epistemic_p"].append((key,symbol,query,variable,v_value,value))
                    except AttributeError:
                        
                        self.logger.error("error when extract precondition")
                        self.logger.error(traceback.format_exc())
                        traceback.print_exc()
                        exit() 
                    
                    #decode effects
                    effects_str = re.search(':effect\(and\(.*\)\)',action_str).group()
                    self.logger.debug('effects_str: [%s]',effects_str)  
                    for e_str in effects_str[11:-2:].split("(= "):
                        if e_str == '':
                            continue
                        self.logger.debug('single effect_str: [%s]',e_str)
                        e_list = e_str[1:].split(") ")
                        # if len(e_list) == 1:
                        #     e_list = e_list[0].split(" ")
                        effects.append((e_list[0].replace(" ?","?").replace(" ","-").replace("(","").replace(")",""),e_list[1].replace(" ","").replace("(","").replace(")","").replace('"','').replace("'",'')))
                    self.logger.debug('effects: [%s]',effects)
                    
                    actions.update({action_name: {"parameters":parameters,"precondition":preconditions,"effect":effects}})
                self.logger.debug(actions)
            except AttributeError:
                self.logger.error("error when extract actions")
                self.logger.error(traceback.format_exc())
                exit()          
            return actions,d_name
    
