
import os
import pandas
import json
from util import ActionList2DictKey,PDDL_TERNARY

DEF_COL_FIELEDS = ['problem' ,'expanded' ,'generated','common_max','common_average' ,'epistemic_calls', 'epistemic_call_time_avg', 'search_time', 'plan_length','goals']
COMMENTING_PREFIX = " \\\\ % "

# this is for converting json results of one domain into latex table (content)
# initialised by providing the directory that contents json files
class LatexConverter:
    

    def __init__(self, input_dir, output_dir, cols = DEF_COL_FIELEDS) -> None:
        self.dir = input_dir
        self.output = output_dir
        self.cols = cols
        # self.domain_name = ""
        pass



    def table_generator(self,):
        file_list = os.listdir(self.dir)
        result_json = list()

        for file_name in sorted(file_list):
            if '.json' in file_name:
                with open(os.path.join(self.dir,file_name),'r') as f:
                    json_item = json.load(f)
                    # print(json_item)
                    
                    for key,value in json_item.items():
                        if type(value) == float:
                            if key == 'common_average':
                                json_item[key] = str(round(value,1))
                            if key == 'epistemic_call_time_avg':
                                json_item[key] = str(round(value*1000,3))
                            else:
                                json_item[key] = str(round(value,3))
                        # elif self.domain_name == "" and key == "domain_name":
                        #     self.domain_name = value
                            
                    # display plan as comments
                    if "plan" in json_item.keys():
                        plan = json_item['plan']
                        json_item.update({"plan_length":len(plan)})
                        # print(len(plan_str_prefix_list))
                        # print(index)
                        plan_str = json_item['goals'] + COMMENTING_PREFIX + ActionList2DictKey(plan)
                        json_item.update({"goals":plan_str})
                    # search_str = json_item["search"] 

                    result_json.append(json_item)
        df_json = pandas.DataFrame.from_dict(result_json)
        # print(df_json.columns.values)
# cols = list(new_df.columns.values)[1:]+['plan']
        new_df = df_json[self.cols]
        pandas.set_option('display.max_colwidth', 1000)


        latex_df = new_df.to_latex(escape=False,index=False)
        # print(latex_df)
        # latex_df = "\n".join(latex_df.split("\n")[3:-3 ])

        # with open(os.path.join(self.output,self.domain_name+".tex"),'w') as f:
        with open(os.path.join(self.output,"result.tex"),'w') as f:
            f.write(latex_df)


def epgoal2latex(ep_cond_dict):
    output_str = "$"
    for key,item in ep_cond_dict.items():
        ep_value = item.value
        var_name = item.variable_name
        var_value = item.v_value
        query = item.query
        queryprefix = query.split("(")[0]
        qp_list = queryprefix.split(" ")
        if ep_value == PDDL_TERNARY.FALSE.value:
            output_str = output_str + "\\neg "
        i = 0
        while i < len(qp_list)-1:
        # for i in range():
            output_str = output_str + "\\" +qp_list[i] +"_"
            if "," in qp_list[i+1]:
                output_str = output_str + "\\{"+ qp_list[i+1].replace("[","").replace("]","") +"\\} "
            else:
                output_str = output_str + qp_list[i+1].replace("[","").replace("]","")  + " "
            i = i+2 
        output_str = output_str + var_name + "=" + str(var_value) + " "
        if ep_value == PDDL_TERNARY.UNKNOWN.value:
            output_str = output_str + " \\rightarrow \\unknown "
        
        output_str = output_str + "\\land "
    output_str = output_str[:len(output_str)-7]
    output_str = output_str + " $ "
    return output_str