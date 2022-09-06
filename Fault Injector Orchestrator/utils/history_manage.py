import json
def check_history(evaluated_hypothesis,historical_file):
    try:
        with open(historical_file, "r") as f:
            history_dict = json.load(f)
        evaluated_hypothesis.sort()
        new_evaluated_hypothesis = []
        url = ""
        for item_str in evaluated_hypothesis:
            item  = item_str.split("_")[1:]
            url = item_str.split("_")[0]
            new_item_str = "_".join(item)
            new_evaluated_hypothesis.append(new_item_str)
        
        # if "currencyservice_Convert_v1" in new_evaluated_hypothesis and "currencyservice_Convert_v2" in new_evaluated_hypothesis and  "currencyservice_Convert_v3" in new_evaluated_hypothesis:
        #     import pdb; pdb.set_trace()
        new_evaluated_hypothesis.sort()
        evaluated_hypothesis_str = ".".join(new_evaluated_hypothesis)
        evaluated_flag = "NULL"
        for url, history_hypotheses in history_dict.items():
            for history_hypothesis, result in history_hypotheses.items():
                if evaluated_hypothesis_str == history_hypothesis:
                    evaluated_flag = False
                if  history_hypothesis in evaluated_hypothesis_str and result == True:
                    # import pdb; pdb.set_trace()
                    return "Pass"
                if (evaluated_hypothesis_str in history_hypothesis )and result == True:
                    items = history_hypothesis.split(".")
                    history_hypothesis_list = []
                    for item in items:
                        history_hypothesis_list.append(url+"_"+item)
                    return history_hypothesis_list
        return evaluated_flag
    except:
        return "NULL"

def write_2_history(url, evaluated_hypothesis, result,historical_file):
    try:
        with open(historical_file, "r") as f:
            history_dict = json.load(f)
    except:
        history_dict = {}
    evaluated_hypothesis.sort()
    new_evaluated_hypothesis = []
    for item_str in evaluated_hypothesis:
        item  = item_str.split("_")[1:]
        new_item_str = "_".join(item)
        new_evaluated_hypothesis.append(new_item_str)
    evaluated_hypothesis_str = ".".join(new_evaluated_hypothesis)
    if url not in history_dict.keys():
        history_dict[url] = {}
        history_dict[url][evaluated_hypothesis_str] = result
    else:
        history_dict[url][evaluated_hypothesis_str] = result
    json_str = json.dumps(history_dict, indent=2)
    with open(historical_file, "w") as json_file:
        json_file.write(json_str)