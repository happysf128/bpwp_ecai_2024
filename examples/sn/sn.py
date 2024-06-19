# from model import Problem,E_TYPE,PDDL_TERNARY
import logging 
import math
from typing import Tuple
import numpy as np
import traceback

import re

from util import PDDL_TERNARY
from util import EpistemicQuery,E_TYPE
AGENT_ID_PREFIX = "agent_at-"
AGENT_LOC_PREFIX = 'agent_at-'
OBJ_LOC_PREFIX = 'shared-s'

AGENT_ID_PREFIX = "post_p1_"

# logger = logging.getLogger("sn")
LOGGER_NAME = "sn"
LOGGER_LEVEL = logging.INFO
from util import setup_logger
 
# declare common variables
common_constants = {

}

class ExternalFunction:
    logger = None
    
    def __init__(self, handlers):
        self.logger = setup_logger(LOGGER_NAME,handlers,logger_level=logging.INFO) 

    # # customized evaluation function

    # extract variables from the query
    def extractVariables(self,eq):
        # expected output would be a list of (var_name,value)
        if not type(eq) == EpistemicQuery:
            # print(eq)
            # default is a single pair of var_name and value
            if not re.search("\([0-9a-z _\-\'\"]*,[0-9a-z _\'\"]*\)",eq) == None:
                var_name = eq.split(",")[0][1:]
                value = eq.split(",")[1][:-1]
                return [(var_name.replace('"','').replace("'",''),value.replace('"','').replace("'",''))]
            else:
                # customized function here
                pass
        else:
            return self.extractVariables(eq.q_content)

    def extractAgents(self,eq):
        if not type(eq) == EpistemicQuery:
            return []
        else:
            
            return eq.q_group + self.extractVariables(eq.q_content)    

    # customized evaluation function
    def evaluateS(self,world,statement):
        self.logger.debug("evaluate seeing: {} in the world: {}, {}, {}",statement,world,type(statement),len(statement))
        #default evaluation for variables
        if world == {}:
            return 2
        if not re.search("\([0-9a-z _\-\'\"]*,[0-9a-z _\'\"]*\)",statement) == None:
            var_name = statement.split(",")[0][1:].replace("'",'').replace('"','')
            value = statement.split(",")[1][:-1].replace("'",'').replace('"','')
            if var_name in world:
                return 1
            else:
                return 0
        else:
            self.logger.warning("the evaluation of the seeing equation has not defined")
            return 0

    def agentsExists(self,path,g_group_index):
        state = path[-1][0]
        for agt_id in g_group_index:
            if not AGENT_ID_PREFIX+agt_id in state.keys():
                return False
        return True


    def checkVisibility(self,state,agt_index,var_index,entities,variables):
        
        self.logger.debug("checkVisibility(_,_,{},{})",agt_index,var_index)
        try:
            self.logger.debug('checking seeing for agent {} on {}',agt_index,var_index)
            tgt_index = variables[var_index].v_parent
            
            # check if the agt_index can be found
            assert(entities[agt_index].e_type==E_TYPE.AGENT)
            
            if entities[tgt_index].e_type==E_TYPE.AGENT:
                if state[f'friended-{agt_index}-{tgt_index}'] ==1:
                    return PDDL_TERNARY.TRUE
                else:
                    return PDDL_TERNARY.FALSE
            else:
                # print(entities)
                for name,entity in entities.items():
                    if entity.e_type == E_TYPE.AGENT:
                        if state[f'post-{tgt_index}-{name}'] == 1:
                            if state[f'friended-{agt_index}-{name}'] ==1:
                                return PDDL_TERNARY.TRUE
            
            # if 'shared' in var_index or 'secret' in var_index:
            #     tgt_loc = state[f'shared-{tgt_index}']
            #     if type(tgt_loc) == str:
            #         tgt_loc = int(state[f'shared-{tgt_index}'])

            #     # agent should know their own secret before sharing
            #     if tgt_index == agt_index:
            #         return PDDL_TERNARY.TRUE
                
            #     # if the secret has not been shared
            #     if tgt_loc == 0:
                    
            #         return PDDL_TERNARY.FALSE
            # else:
            #     # the target is an agent, it has its own location
            #     tgt_loc = int(state[f'agent_at-{tgt_index}'])



            # agt_loc = int(state[f'agent_at-{agt_index}'])

            
            # # extract necessary common constants from given domain
            # # logger.debug(f"necessary common constants from given domain")

            # # logger.debug(f'checking seeing with agent location: {agt_loc} and target location: {tgt_loc}')
            # # agent is able to see anything in the same location
            # if tgt_loc == agt_loc:
            #     return PDDL_TERNARY.TRUE


            # seeing relation for corridor is in the same room or adjuscent room
            if False:
                return PDDL_TERNARY.TRUE
            else:
                return PDDL_TERNARY.FALSE

        except KeyError:
            self.logger.warning(traceback.format_exc())
            self.logger.warning("variable not found when check visibility")
            # logging.error("error when checking visibility")
            return PDDL_TERNARY.UNKNOWN
        except TypeError:
            self.logger.warning(traceback.format_exc())
            self.logger.warning("variable is None d when check visibility")
            # logging.error("error when checking visibility")
            return PDDL_TERNARY.UNKNOWN

    # customise action filters
    # to filter out the irrelevant actions
    def filterActionNames(self,problem,action_dict):
        return action_dict.keys()
