# from model import Problem,E_TYPE,PDDL_TERNARY
import logging 
import math
from typing import Tuple
import numpy as np
import traceback
# import model
import re

from util import PDDL_TERNARY,convertBooltoPDDL_TERNARY
from util import EpistemicQuery,E_TYPE


AGENT_ID_PREFIX = "peeking_"



LOGGER_NAME = "Group_NUMBER"
LOGGER_LEVEL = logging.INFO
from util import setup_logger
 
# declare common variables
common_constants = {

}

class ExternalFunction:
    logger = None
    
    def __init__(self, handlers):
        self.logger = setup_logger(LOGGER_NAME,handlers,logger_level=logging.INFO) 


    # extract variables from the query
    def extractVariables(self,eq):
        self.logger.debug(eq)
        # expected output would be a list of (var_name,value)
        if type(eq.q_content) == str:
            # default is a single pair of var_name and value
            if not re.search("\([0-9a-z _\-\'\"]*,[0-9a-z _\'\"]*\)",eq.q_content) == None:
                var_name = eq.q_content.split(",")[0][1:]
                value = eq.q_content.split(",")[1][:-1]
                var_name = var_name.replace("'","").replace('"','')
                value = value.replace("'","").replace('"','')
                return [(var_name,value)]
            else:
                # customized function here
                pass
        else:
            return self.extractVariables(eq.q_content)
            
    # customized evaluation function
    def evaluateS(self,world,statement):
        #default evaluation for variables
        if world == {}:
            return 2
        if not re.search("\([0-9a-z _\-\'\"]*,[0-9a-z _\'\"]*\)",statement) == None:
            var_name = statement.split(",")[0][1:]
            value = statement.split(",")[1][:-1]
            var_name = var_name.replace("'","").replace('"','')
            value = value.replace("'","").replace('"','')
            if var_name in world.keys():
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
        
        self.logger.debug("checkVisibility(_,{},{},{})",state,agt_index,var_index)
        try:
            tgt_index = variables[var_index].v_parent
            # check if the agt_index can be found
            assert(entities[agt_index].e_type==E_TYPE.AGENT)
            
            # agents are able to see each other
            if entities[tgt_index].e_type==E_TYPE.AGENT:
                return convertBooltoPDDL_TERNARY(True)
            else:
                # this might be needed to change to UNKNOWN
                #extract necessary variables from state
                return  convertBooltoPDDL_TERNARY(state[f"peeking-{agt_index}"]=='t')
            
        #     # extract necessary common constants from given domain
        #     # logger.debug(f"necessary common constants from given domain")
        #     agt_angle = common_constants[f"angle-{agt_index}"]
            
        #     # agent is able to see anything in the same location
        #     if tgt_x == agt_x and tgt_y == agt_y:
        #         return model.PDDL_TERNARY.TRUE
            
        #     # generate two vector
        #     v1 = np.array((tgt_y - agt_y,tgt_x - agt_x))
        #     v1 = v1 / np.linalg.norm(v1)
        #     radians = math.radians(agt_dir)
        #     v2 = np.array((math.cos(radians),math.sin(radians)))
        #     # logger.debug(f'v1 {v1}, v2 {v2}')
        #     cos_ = v1.dot(v2)
        #     d_radians = math.acos(cos_)
        #     d_degrees = math.degrees(d_radians)
        #     # logger.debug(f'delta angle degree is {round(d_degrees,3)}')
            
        #     if d_degrees <= agt_angle/2.0 and d_degrees >= - agt_angle/2.0:
        #         inside = model.PDDL_TERNARY.TRUE
        #     else:
        #         inside =model.PDDL_TERNARY.FALSE
        #     # logger.debug(f'visibility is {inside}')
        #     return inside
        except KeyError:
            self.logger.warning(traceback.format_exc())
            self.logger.warning("variable not found when check visibility")
            # logger.error("error when checking visibility")
            return PDDL_TERNARY.UNKNOWN

    # customise action filters
    # to filter out the irrelevant actions
    def filterActionNames(self,problem,action_dict):
        return action_dict.keys()

    # if __name__ == "__main__":
        
    #     pass
        

    