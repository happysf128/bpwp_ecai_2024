import logging

from util import setup_logger, PriorityQueue, PDDL_TERNARY, ROOT_NODE_ACTION
# import util


LOGGER_NAME = "forward_search:astargctbgc"
LOGGER_LEVEL = logging.INFO
# LOGGER_LEVEL = logging.DEBUG
SPLIT_KEY_WORD = "@"

class Search:
    def __init__(self,handlers):
        self.logger = setup_logger(LOGGER_NAME,handlers,logger_level=LOGGER_LEVEL) 
        self.expanded = 0
        self.goal_checked = 0
        self.generated = 0
        self.pruned = 0
        self.pruned_by_unknown = 0
        self.pruned_by_visited = 0
        self.visited = []
        self.short_visited = []
        self.result = dict()
        self.branch_factors = []
        self.p_path = {}

    class SearchNode:
        state = None
        goal_p_dict = dict()
        remaining_goal = 9999
        path = []

        def __init__(self,state,goal_p_dict,path):
            self.state = state
            self.goal_p_dict = goal_p_dict
            self.path = path




    #BFS with duplicate check on the state + epistemic formula
    # for novelty checking purpose, we need to move the goal check process at where the node is generated
    def searching(self,problem, filterActionNames = None):
        
        
        self.logger.info(f'starting searching using {LOGGER_NAME}')
        max_goal_num = len(problem.goals.ontic_dict)+len(problem.goals.epistemic_dict)
        self.logger.debug("goal size is: [%s]",max_goal_num)
        # self.logger.info(f'the initial is {problem.initial_state}')
        # self.logger.info(f'the variables are {problem.variables}')
        # self.logger.info(f'the domains are {problem.domains}')
        
        # check whether the initial state is the goal state
        init_state = problem.initial_state
        init_path = [(problem.initial_state,ROOT_NODE_ACTION)]
        init_goal_p_dict = dict()
        
        init_node = Search.SearchNode(init_state,init_goal_p_dict,init_path)
        # self.group_eg_dict = self.group_epistemic_goals(problem)
        
        # self.landmarks_dict = problem.external.generate_constrain_dict(problem,self.group_eg_dict)
        # print(landmarks_dict)
        # exit()
        # print(constrain_dict)
        # print(group_eg_dict)
        # return
        
        
        
        open_list = PriorityQueue()
        p,p_dict = self._f(init_node,problem,self.p_path)
        init_node.remaining_goal =  p-self._gn(init_node)
        init_node.goal_p_dict.update(p_dict)
        # remaining_g = p-_gn(init_node)
        open_list.push(item=init_node, priority=p)
        
        
        while not open_list.isEmpty():
            # logger.debug(f"queue length {len(queue)}")
            current_p , _, current_node = open_list.pop_full()

            state = current_node.state
            goal_p_dict = current_node.goal_p_dict
            path = current_node.path
            action_path = [ a  for s,a in path]
            action_path = action_path[1:]
            self.logger.debug("expanding node with path: [%s]",action_path)
            # self.goal_checked += 1
            # if len(path) >3:
            #     return
            # Goal Check
            # is_goal, temp_goal_p_dict = problem.isGoalN(state,path)
            # print(temp_goal_p_dict)
            # remaining_g = current_p - _gn(current_node)
            # print(f"p:{current_p}, g:{ _gn(current_node)}, r:{remaining_g}")
            # is_goal = self._isGoal(current_p,current_node)
            is_goal = (0 == current_node.remaining_goal)
            if is_goal:
                # self.logger.info(path)
                action_path = [ a  for s,a in path]
                action_path = action_path[1:]
                self.logger.info(f'plan is: {action_path}')
                self.logger.info(f'Goal found')
                self.result.update({'solvable': True})
                self.result.update({'plan':action_path})
                self._finalise_result(problem)
                return self.result
            
            # check whether the node has been visited before
            # goal_p_dict.update(goal_p_dict)
            
            
            actions = problem.getAllActions(state,path)
            # self.logger.debug(actions)
            filtered_action_names = filterActionNames(problem,actions)

            ontic_pre_dict = {}
            epistemic_pre_dict = {}
            for action_name in filtered_action_names:
                action = actions[action_name]
                ontic_pre_dict.update({action_name:action.a_preconditions.ontic_dict})
                epistemic_pre_dict.update({action_name:action.a_preconditions.epistemic_dict})

            
            
            flag_dict,e_pre_dict,p_dict = problem.checkAllPreconditions(state,path, ontic_pre_dict,epistemic_pre_dict,self.p_path)
            self.logger.debug("flag_dict [%s]", flag_dict)
            
            
            e_pre_dict.update(state)
            e_pre_dict.update(goal_p_dict)
            e_pre_dict.update(p_dict)
            
            # assert(len(path) <=4)
            ep_state_str = state_to_string(e_pre_dict)
            # self.logger.info(action_path)
            # self.logger.info(ep_state_str)
            
            
            
            if not ep_state_str in self.visited:
                # self.logger.debug(goal_p_dict)
            # if True:
                # self.branch_factors.append(flag_dict.values().count(True))
                
                
                self.expanded +=1
                temp_successor = 0
                temp_actions = []
                # print(expanded)
                # update the visited list
                # self.short_visited.append(temp_str)
                self.visited.append(ep_state_str)
                
                for action_name in filtered_action_names:

                    

                    if flag_dict[action_name]: 
                        action = actions[action_name]
                        # passed the precondition
                        succ_state = problem.generateSuccessor(state, action,path)
                        # self.visited.append(e_dict)
                        self.goal_checked += 1
                        succ_node = self.SearchNode(succ_state,{},path + [(succ_state,action_name)])
                        p,goal_p_dict = self._f(succ_node,problem,self.p_path)
                        
                        succ_node.remaining_goal = self._remainingGoalNum(p,succ_node)

                        self.logger.debug("remaining goal number is: [%s]", succ_node.remaining_goal)
                        if succ_node.remaining_goal <= max_goal_num:
                            succ_node.goal_p_dict = goal_p_dict
                                
                            self.generated += 1

                        
                            open_list.push(item=succ_node, priority=p)
                            temp_successor +=1
                            temp_actions.append(action_name)
                        else:
                            self.pruned_by_unknown +=1
                            self.logger.debug('action [%s] not generated in state [%s] due to impossible to reach goal ([%s])',action_name,state,max_goal_num)

                    else:
                        self.logger.debug('action [%s] not generated in state [%s] due to not pass precondition',action_name,state)
                self.logger.debug('num of successor: %s',temp_successor)
                self.logger.debug('with actions %s',temp_actions)
            else:
                self.logger.debug("pruned by visited")
                # print(self.pruned_by_visited)
                self.pruned_by_visited += 1
            
            
        self.logger.info(f'Problem is not solvable')
        self.result.update({'plan':[]})
        self.result.update({'solvable': False})
        
        self._finalise_result(problem)
        return self.result

    
    




    def _finalise_result(self,problem):
        # logger output


        self.logger.info(f'[number of node pruned_by_unknown]: {self.pruned_by_unknown}')
        self.logger.info(f'[number of node pruned_by_visited]: {self.pruned_by_visited}')
        self.pruned = self.pruned_by_unknown + self.pruned_by_visited
        self.logger.info(f'[number of node pruned]: {self.pruned}')

        self.logger.info(f'[number of node goal_checked]: {self.goal_checked}')
        self.logger.info(f'[number of node expansion]: {self.expanded}')
        self.logger.info(f'[number of node generated]: {self.generated}')
        self.logger.info(f'[number of epistemic formulas evaluation: {problem.epistemic_calls}]')
        self.logger.info(f'[time in epistemic formulas evaluation: {problem.epistemic_call_time}]')
        # file output
        self.result.update({'pruned':self.pruned})
        self.result.update({'goal_checked':self.goal_checked})
        self.result.update({'expanded':self.expanded})
        self.result.update({'generated':self.generated})
        self.result.update({'epistemic_calls':problem.epistemic_calls})
        self.result.update({'epistemic_call_time':problem.epistemic_call_time.total_seconds()})

    def group_epistemic_goals(self,problem):
        group_eg_dict = {}
        for eq_str,value in problem.goals.epistemic_dict.items():
            var_str = eq_str.split(" ")[-1].split(",")[0][2:-1]
            if var_str in group_eg_dict:
                group_eg_dict[var_str].append((eq_str,value))
            else:
                group_eg_dict.update({var_str:[(eq_str,value)]})
        return group_eg_dict



    def _f(self,node,problem,p_path):
        heuristic = self.goal_counting
        g = self._gn(node)
        h,p_dict = heuristic(node,problem,p_path)
        f = g*1+h*1.01
        return f,p_dict

    def _remainingGoalNum(self,current_p,current_node):
        return (current_p - self._gn(current_node)*1)/1.01

    # def _isGoal(self,current_p, current_node):
    #     return self._remainingGoalNum(current_p,current_node) == 0

    def _gn(self,node):
        path = node.path
        return len(path)-1

    # it is not admissible
    def goal_counting(self,node,problem,p_path):
        remain_goal_number = 0
        state = node.state
        path = node.path
        
        p_dict,epistemic_dict,goal_dict = problem.isGoal(state,path,p_path)

        
        remain_goal_number = list(goal_dict.values()).count(False)
        self.logger.debug("goal dict is: \n [%s]",goal_dict)
        for key,value in goal_dict.items():
            if str(PDDL_TERNARY.UNKNOWN.value) in key and not value:
                self.logger.debug('Unknown been updated, goal is impossible')
                return 9999,epistemic_dict      
        return remain_goal_number,p_dict
        # print(state)
        # print(goal_p_dict)
        # print(remain_goal_number)
        # {'secret-b': [("b [a] ('secret-b','t')", 1), ("b [d] b [a] ('secret-b','f')", 1)], 
        #  'secret-c': [("b [b] ('secret-c','t')", 1), ("b [c] b [b] ('secret-c','f')", 1)], 
        #  'secret-d': [("b [c] ('secret-d','t')", 1), ("b [b] b [c] ('secret-d','f')", 1)], 
        #  'secret-a': [("b [d] ('secret-a','t')", 1), ("b [a] b [d] ('secret-a','f')", 1)]}
        # print(goal_dict)
        # {"b [a] ('secret-b','t') 1": False, 
        #  "b [b] ('secret-c','t') 1": False, 
        #  "b [c] ('secret-d','t') 1": False, 
        #  "b [d] ('secret-a','t') 1": False, 
        #  "b [d] b [a] ('secret-b','f') 1": False, 
        #  "b [c] b [b] ('secret-c','f') 1": False, 
        #  "b [b] b [c] ('secret-d','f') 1": False, 
        #  "b [a] b [d] ('secret-a','f') 1": False}
        # exit()
        heuristic_value = remain_goal_number
        
        # landmark_constrain = []
        temp_v_name_list = []
        for v_name, ep_goals in self.group_eg_dict.items():
            for ep_str,value in ep_goals:
                if not goal_dict[f"{ep_str} {value}"]:
                    temp_v_name_list.append(v_name)
                    # heuristic_value +=1
                    break
        
        # for v_name in temp_v_name_list:
        #     temp_pair_dict = {}
        #     for ep_str,value in group_eg_dict[v_name]:
        #         ep_value = ep_str.split(v_name)[1][3:-2]
        #         ep_front = ep_str.split(v_name)[0]
        #         ep_header = format_ep(ep_value,value)
        temp_landmark = set()
                
        for temp_v_name in temp_v_name_list:
            # flag = True
            for temp_state in self.landmarks_dict[temp_v_name]:
                if not str(sorted(temp_state)) in temp_landmark:
                    temp_flag = True
                    for key,value in temp_state.items():
                        if key in state.keys():
                            if not state[key]==value:
                                temp_flag = False
                                break
                    if temp_flag:
                        heuristic_value +=1
                        temp_landmark.add(str(sorted(temp_state)))
                        break
                
            # if flag:
            #     heuristic_value +=1
                
                
        
        
        # if 'secret-a' in temp_v_name_list:
        #     landmark_constrain.append(('agent_at-b','agent_at-d'))
        # elif 'secret-c' in temp_v_name_list:
        #     landmark_constrain.append(('agent_at-b','agent_at-d'))
        # if 'secret-b' in temp_v_name_list:
        #     landmark_constrain.append(('agent_at-c','agent_at-a'))
        # elif 'secret-d' in temp_v_name_list:
        #     landmark_constrain.append(('agent_at-c','agent_at-a'))
            
        # for v1,v2 in landmark_constrain:
        #     if state[v1] == state[v2]:
        #         heuristic_value +=1
        
        # print(f' h is: {heuristic_value}, gc is: {remain_goal_number}')
        # if remain_goal_number == 0:
        #     print(f' h is: {heuristic_value}, gc is: {remain_goal_number}')
            
        
        return heuristic_value,epistemic_dict



def state_to_string(dicts):
    output = []
    # print(dicts)
    for key,value in dicts.items():
        output.append(f'{key}:{value}')
    output.sort() 
    return str(output)
