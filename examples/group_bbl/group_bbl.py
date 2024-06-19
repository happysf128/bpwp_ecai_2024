# from model import Problem,E_TYPE,PDDL_TERNARY
import logging 
import math
from typing import Tuple
import numpy as np
import traceback

import re

from util import PDDL_TERNARY
from util import EpistemicQuery,E_TYPE
AGENT_ID_PREFIX = "dir-"
# not applicable as it using x and y
# AGENT_LOC_PREFIX = 'agent_at-'
# OBJ_LOC_PREFIX = 'shared-s'


LOGGER_NAME = "bbl"
LOGGER_LEVEL = logging.INFO
# LOGGER_LEVEL = logging.DEBUG
from util import setup_logger
 
# declare common variables
# common_constants = {

# }
common_constants = {
    'angle-a': 90,
    'angle-b': 90,
}

dir_dict = {
    'n': 90,
    'ne': 45,
    'e':0,
    'se':-45,
    's':-90,
    'sw':-135,
    'w':180,
    'nw':135,
}

class ExternalFunction:
    logger = None
    
    def __init__(self, handlers):
        self.logger = setup_logger(LOGGER_NAME,handlers,logger_level=LOGGER_LEVEL) 


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
            
    # customized evaluation function
    def evaluateS(self,world,statement):

        #default evaluation for variables
        if world == {}:
            self.logger.debug("unknown due to the world is empty")
            return 2
        if not re.search("\([0-9a-z _\-\'\"]*,[0-9a-z _\'\"]*\)",statement) == None:
            var_name = statement.split(",")[0][1:].replace("'",'').replace('"','')
            value = statement.split(",")[1][:-1].replace("'",'').replace('"','')
            
            self.logger.debug("var_name is {} in the world {}",var_name,world)
            if var_name in world:
                self.logger.debug("True")
                return 1
            else:
                self.logger.debug("False")
                return 0
        else:
            self.logger.warning("the evaluation of the seeing equation has not defined")
            self.logger.debug("Undefined, return 0. unknown due to the world is empty")
            return 0

    def agentsExists(self,path,g_group_index):
        state = path[-1][0]
        for agt_id in g_group_index:
            if not AGENT_ID_PREFIX+agt_id in state.keys():
                return False
        return True


    def checkVisibility(self,state,agt_index,var_index,entities,variables):
        
        self.logger.debug("checkVisibility(_,_,[%s],[%s])",agt_index,var_index)
        
        try:
            tgt_index = variables[var_index].v_parent
            # check if the agt_index can be found
            assert(entities[agt_index].e_type== E_TYPE.AGENT)
            
            #extract necessary variables from state
            self.logger.debug("tgt_index [%s]",tgt_index)
            
            tgt_x = state[f"x-{tgt_index}"]
            tgt_y = state[f"y-{tgt_index}"]
            agt_x = state[f"x-{agt_index}"]
            agt_y = state[f"y-{agt_index}"]
            agt_dir = dir_dict[state[f"dir-{agt_index}"]]
            self.logger.debug("[%s][%s][%s][%s][%s]",tgt_x,tgt_y,agt_x,agt_y,agt_dir)
            
            # extract necessary common constants from given domain
            # logger.debug(f"necessary common constants from given domain")
            agt_angle = common_constants[f"angle-{agt_index}"]
            
            # agent is able to see anything in the same location
            if tgt_x == agt_x and tgt_y == agt_y:
                return PDDL_TERNARY.TRUE
            
            # generate two vector
            v1 = np.array((tgt_y - agt_y,tgt_x - agt_x))
            
            v1 = v1 / np.linalg.norm(v1)
            self.logger.debug("v1 [%s]",v1)
            radians = math.radians(agt_dir)
            self.logger.debug("radians [%s]",radians)
            v2 = np.array((math.cos(radians),math.sin(radians)))
            self.logger.debug("v2 [%s]",v2)

            cos_ = round(v1.dot(v2),3)
            self.logger.debug("cos_ [%s]",cos_)
            d_radians = math.acos(cos_)
            self.logger.debug("d_radians [%s]",d_radians)
            d_degrees = math.degrees(d_radians)
            # logger.debug(f'delta angle degree is {round(d_degrees,3)}')
            
            if d_degrees <= agt_angle/2.0 and d_degrees >= - agt_angle/2.0:
                inside = PDDL_TERNARY.TRUE
            else:
                inside =PDDL_TERNARY.FALSE
            # logger.debug(f'visibility is {inside}')
            return inside
        except KeyError:
            # logger.warning(traceback.format_exc())
            # logger.warning(f"variable {agt_index} not found when check visibility in state {state}")
            # logging.error("error when checking visibility")
            self.logger.debug(traceback.format_exc())
            self.logger.debug("variable {} not found when check visibility in state {}",agt_index,state)
            return PDDL_TERNARY.UNKNOWN
        except TypeError:
            # logger.warning(traceback.format_exc())
            # logger.warning("variable is None d when check visibility in state {state}")
            self.logger.debug(traceback.format_exc())
            self.logger.debug("variable {} not found when check visibility in state {}",agt_index,state)
            # logging.error("error when checking visibility")
            return PDDL_TERNARY.UNKNOWN

    # customise action filters
    # to filter out the irrelevant actions
    def filterActionNames(self,problem,action_dict):
        return action_dict.keys()

# if __name__ == "__main__":
    
#     pass
    

    