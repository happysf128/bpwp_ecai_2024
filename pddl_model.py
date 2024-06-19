from datetime import datetime, timedelta
import logging
import os
import copy
import re
from typing import List
from epistemic_model import EpistemicModel
from forward_epistemic_model import EpistemicModel

LOGGER_NAME = "pddl_model"
LOGGER_LEVEL = logging.INFO
# LOGGER_LEVEL = logging.DEBUG

from util import setup_logger,PDDL_TERNARY

from util import Variable,Action
from util import Domain,D_TYPE,dTypeConvert
from util import Entity,E_TYPE,eTypeConvert
from util import Conditions

# Class of the problem
class Problem:
    initial_state = {}
    abstract_actions = {} 
    entities = {} # agent indicators, should be unique
    variables = {} #variable
    domains = {}
    initial_state = {}
    goals = {}
    external = None
    epistemic_calls = 0
    epistemic_call_time = timedelta(0)
    epistemic_model = None
    logger = None

    def __init__(self, domains,i_state,g_states,agent_index,obj_index,variables,actions, external=None,handlers=None):
        self.initial_state = {}
        self.abstract_actions = {} 
        self.entities = {} # agent indicators, should be unique
        self.variables = {} #variable
        self.domains = {}
        self.initial_state = {}
        self.goals = {}
        self.epistemic_calls = 0
        self.epistemic_call_time = timedelta(0)
        self.logger = None
        self.logger = setup_logger(LOGGER_NAME,handlers,logger_level=LOGGER_LEVEL) 
        self.logger.debug("initialize entities")
        
        self.entities = {}
        for i in agent_index:
            e_temp = Entity(i,E_TYPE.AGENT)
            self.entities.update({i:e_temp})
        for i in obj_index:
            e_temp = Entity(i,E_TYPE.OBJECT)
            self.entities.update({i:e_temp})        

        self.variables = {}
        for d_name,targets in variables.items():

            suffix_list = self._generateVariables(targets)

            for suffix in suffix_list:
                var_name = f"{d_name}{suffix}"
                v_parent = suffix.split('-')[1]
                v_temp = Variable(var_name,d_name,v_parent)
                self.variables.update({var_name:v_temp})
            
        # grounding all actions or do not ground any actions?    
        for a_name, parts in actions.items():
            
            p = [ (i,eTypeConvert(self.logger,t))for i,t in parts['parameters']]
            a_temp = Action(a_name, p,parts['precondition'], parts['effect'])
            self.abstract_actions.update({a_name:a_temp})
        self.logger.debug(self.abstract_actions)
        

        self.domains = {}
        for d_name in domains.keys():
            values = domains[d_name]['values']
            d_type = dTypeConvert(self.logger,domains[d_name]['basic_type'])
            if d_type == D_TYPE.INTEGER:
                bound = domains[d_name]['values']
                values = list(range(bound[0],bound[1]+1))

            domain_temp = Domain(d_name,values,d_name=='agent',d_type)
            self.domains.update({d_name:domain_temp})


        self.goals = Conditions(g_states['ontic_g'],g_states['epistemic_g'])
        self.logger.debug(self.goals)
        self.initial_state = i_state
        self.external = external
        self.epistemic_model = EpistemicModel(handlers,self.entities,self.variables,external)
    
        
    def isGoal(self,state,path):
        is_goal=True
        goal_dict = {}
        actions = [ a  for s,a in path]
        actions = actions[1:]


        for k,v in self.goals.ontic_dict.items():
            if not state[k] == v:
                is_goal = False
                goal_dict.update({k+" "+str(v):False})
            else:
                goal_dict.update({k+" "+str(v):True})
            
        # adding epistemic checker here
        current_time = datetime.now()
        self.epistemic_calls +=1
        p_dict,epistemic_dict = \
            self.epistemic_model.epistemicGoalsHandler(self.goals.epistemic_dict,"",path)
        self.epistemic_call_time += datetime.now() - current_time
        
        for k,v in self.goals.epistemic_dict.items():
            if not epistemic_dict[k].value == v:
                is_goal = False
                goal_dict.update({k+" "+str(v):False})
            else:
                goal_dict.update({k+" "+str(v):True})
        return is_goal,p_dict,epistemic_dict,goal_dict
    
    def isGoalP(self,state,path):
        is_goal=True
        # let's keep iw1 version and extend it later
        epistemic_items_set = {}
        p_dict = {}

        actions = [ a  for s,a in path]
        actions = actions[1:]

        for k,i in self.goals.ontic_dict.items():
            if not state[k] == i:
                is_goal = False
                break
            
        # adding epistemic checker here

        for eq,value in self.goals.epistemic_dict:
            self.epistemic_calls +=1
            current_time = datetime.now()
            temp_e_v, temp_p_dict = self.epistemic_model.checkingEQstrP(self.external,eq,path,state,self.entities,self.variables)
            self.epistemic_call_time += datetime.now() - current_time
            if not temp_e_v == value:
                is_goal=False
            p_dict.update(temp_p_dict)
        return is_goal,p_dict    
    
    def getAllActions(self,state,path):
        all_actions = {}
        
        # get all type of actions
        for a_name, abstract_a in self.abstract_actions.items():
            self.logger.debug(f'action: {abstract_a} ')
            # generate all possible combination parameters for each type of action
            if abstract_a.a_parameters == []:
                a_temp_name = a_name
                a_temp_parameters = copy.deepcopy(abstract_a.a_parameters)
                a_temp_pre = copy.deepcopy(abstract_a.a_preconditions)
                a_temp_pre_dict = {'ontic_p':a_temp_pre.ontic_dict,'epistemic_p':a_temp_pre.epistemic_dict}
                a_temp_effects = copy.deepcopy(abstract_a.a_effects)
                # if self._checkPreconditions(state,a_temp_precondition,path):
                all_actions.update({a_temp_name:Action(a_temp_name,a_temp_parameters,a_temp_pre_dict,a_temp_effects)})
            else:
                for params in self._generateParams(abstract_a.a_parameters):
                    a_temp_name = a_name
                    a_temp_parameters = copy.deepcopy(abstract_a.a_parameters)

                    
                    a_temp_ontic_p_list = copy.deepcopy(list(abstract_a.a_preconditions.ontic_dict.items()))
                    a_temp_epistemic_p_list = copy.deepcopy(list(abstract_a.a_preconditions.epistemic_dict.items()))
                    a_temp_effects = copy.deepcopy(abstract_a.a_effects)
                    for i,v in params:
                        a_temp_name = a_temp_name + "-" + v
                        for j in range(len(a_temp_parameters)):
                            v_name, v_effects = a_temp_parameters[j]
                            v_name = v_name.replace(f'{i}',f'-{v}')
                            a_temp_parameters[j] = (v_name,v_effects)
                        
                        # update parameters in the ontic precondition
                        self.logger.debug(f"a_temp_ontic_p_list{a_temp_ontic_p_list}")
                        for j in range(len(a_temp_ontic_p_list)):
                            v_name, v_effects = a_temp_ontic_p_list[j]
                            v_name = v_name.replace(f'{i}',f'-{v}')
                            if type(v_effects) == str:
                                v_effects = v_effects.replace(f'{i}',f'-{v}')
                            a_temp_ontic_p_list[j] = (v_name,v_effects)

                        # update parameters in the epistemic precondition
                        for j in range(len(a_temp_epistemic_p_list)):
                            v_name, v_effects = a_temp_epistemic_p_list[j]
                            v_name = v_name.replace(f'{i}',f'-{v}').replace('[-','[').replace(',-',',')
                            # precondition effect of epistemic is only going to be int
                            # v_effects = v_effects.replace(f'{i}',f'-{v}')
                            a_temp_epistemic_p_list[j] = (v_name,v_effects)                            
                        
                        # update parameters in the effects
                        for j in range(len(a_temp_effects)):
                            v_name, v_effects = a_temp_effects[j]
                            v_name = v_name.replace(f'{i}',f'-{v}')
                            v_effects = v_effects.replace(f'{i}',f'-{v}')
                            a_temp_effects[j] = (v_name,v_effects)

                    a_temp_pre_dict = {'ontic_p':dict(a_temp_ontic_p_list),'epistemic_p':dict(a_temp_epistemic_p_list)}
                    all_actions.update({a_temp_name:Action(a_temp_name,a_temp_parameters,a_temp_pre_dict,a_temp_effects)})
                    
        return all_actions

    def checkAllPreconditions(self,state,path,ontic_pre_dict,epistemic_pre_dict):

        pre_dict = {}
        flag_dict = {}
        
        # checking ontic preconditions
        for action_name,ontic_pre in ontic_pre_dict.items():
            pre_dict[action_name] = {}
            flag_dict[action_name] = True
            for k,e in ontic_pre.items():
                try:
                    if k in state.keys():
                        if e in state.keys():
                            if not state[k] == state[e]:
                                flag_dict[action_name] = False
                                pre_dict[action_name].update({k+":"+str(e):False})
                            else:
                                pre_dict[action_name].update({k+":"+str(e):True})
                        elif not state[k] == e:
                            flag_dict[action_name] = False
                            pre_dict[action_name].update({k+":"+str(e):False})
                        else:
                            pre_dict[action_name].update({k+":"+str(e):True})
                    else:
                        self.logger.error(f'variable {k} not in state {state}')
                        
                except:
                    self.logger.error("Error when checking precondition: {}\n with state: {}")
                    
                    flag_dict[action_name] = False


        # get all ep_pre into one dict
        temp_ep_dict = {}
        self.logger.debug(f"epistemic_pre_dict: {epistemic_pre_dict}")
        for action_name,ep_pre in epistemic_pre_dict.items():
            temp_ep_dict.update(ep_pre) 
              
        current_time = datetime.now()
        self.epistemic_calls +=1
        p_dict,epistemic_dict = self.epistemic_model.epistemicGoalsHandler(temp_ep_dict,"",path)
        self.epistemic_call_time += datetime.now() - current_time

        ep_dict = {}
        for action_name,ep_pre in epistemic_pre_dict.items():
            ep_dict[action_name] = {}
            for k,v in ep_pre.items():
                if not epistemic_dict[k].value == v:
                    flag_dict[action_name] = False
                    pre_dict[action_name].update({k+":"+str(e):False})
                    # pre_flag = False
                    # pre_dict.update({k+" "+str(v):False})
                else:
                    pre_dict[action_name].update({k+":"+str(e):True})
        
        return flag_dict,p_dict,epistemic_dict,pre_dict    



    # generate all possible parameter combinations
    def _generateVariables(self,params):
        # self.logger.debug(f'params: {params}')
        param_list = []

        if params == []:
            return []
        else:
            
            for i in params[0]:
                next_param = copy.deepcopy(params[1:])
                rest = self._generateVariables(next_param)
                if len(rest) == 0:
                    param_list = param_list + [f"-{i}"]
                else:
                    param_list = param_list + [ f"-{i}{t}" for t in rest ]
        return param_list

    # generate all possible parameter combinations
    def _generateParams(self,params):
        param_list = []

        if params == []:
            return []
        else:
            i,v = params[0]

            for k,l in self.entities.items():

                if l.e_type == v:
                    next_param = copy.deepcopy(params[1:])
                    rest = self._generateParams(next_param)
                    if len(rest) == 0:
                        param_list = param_list + [[(i,k)]]
                    else:
                        param_list = param_list + [ [(i,k)]+ t for t in self._generateParams(next_param) ]
        return param_list
                    
    # TODO adding action cost
    def generateSuccessor(self,state,action,path):
        
        # TODO valid action
        # need to go nested on the brackets

        new_state = copy.deepcopy(state)
        
        for v_name,update in action.a_effects:
            old_value = state[v_name]
            # v_name = v_name.replace('?','-')
            # # self.logger.debug(f'single effect update: {v_name}/{old_value}/{update}')
            # if update in state:
            #     new_state[v_name] = state[update]
            # elif '-' in update:
            if update.startswith('-'):
                delta_value = int(update.split('-')[1])
                domain_name = self.variables[v_name].v_domain_name

                if self.domains[domain_name].d_type == D_TYPE.ENUMERATE:
                    index = self.domains[domain_name].d_values.index(old_value)
                    new_index = (index-delta_value) % len(self.domains[domain_name].d_values)
                    new_value = self.domains[domain_name].d_values[new_index]
                    new_state[v_name] = new_value
                elif self.domains[domain_name].d_type == D_TYPE.INTEGER:
                    old_int = int(old_value)
                    # # self.logger.debug(f'old_int: {old_int}')
                    new_value = old_int - delta_value

                    new_state[v_name] = new_value
                    
            elif update.startswith('+'):
                delta_value = int(update.split('+')[-1])
                domain_name = self.variables[v_name].v_domain_name
                if self.domains[domain_name].d_type == D_TYPE.ENUMERATE:
                    index = self.domains[domain_name].d_values.index(old_value)
                    new_index = (index+delta_value) % len(self.domains[domain_name].d_values)
                    new_state[v_name] = self.domains[domain_name].d_values[new_index]
                elif self.domains[domain_name].d_type == D_TYPE.INTEGER:
                    old_int = int(old_value)
                    new_value = old_int + delta_value
                    new_state[v_name] = new_value
            else:
                
                domain_name = self.variables[v_name].v_domain_name
                if self.domains[domain_name].d_type == D_TYPE.INTEGER:
                    if re.search("[a-z]|[A-Z]", update):
                        update = state[update]
                    new_state[v_name] = int(update)
                else:
                    new_state[v_name] = update
        return new_state
        
        
    
    def __str__(self):
        return f"Problem: \n\t entities: {self.entities}\n\t variables: {self.variables}\n\t abstract_actions: {self.abstract_actions}\n\t domains: {self.domains}\n\t initial_state: {self.initial_state}\n\t goals: {self.goals}\n"


    


    
