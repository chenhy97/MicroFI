  # -*- coding: utf-8 -*
from utils.z3_solver import *
from utils.client import *
import time
from datetime import timedelta, datetime
import os
import json
import copy
import logging
import sys

def print_formulas(formulas):
    disjunction_symbol = " ∨ "
    conjunction_symbol = " ∧ "
    temp_formula = []
    for formula in formulas:
        temp_formula.append("("+ disjunction_symbol.join([str(clause) for clause in list(formula)])+")")
    print(conjunction_symbol.join(temp_formula))

def getNewClause(url):
    path_formula = req(url)
    if path_formula != False:
        path_formulas = [path_formula]
        print_formulas(path_formulas)
        return path_formulas


def fault_injection(url, svc, api, subset):
    formdata = {
        "url": url,
        "svc": svc,
        "api": api,
        "subset":subset,
        "inject_flag": "inject"
    }
    data = json.dumps(formdata)
    data = data.encode("utf-8")
    req = urllib2.Request(url = base_url, data = data)
   
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib2.urlopen(req)
        if response.getcode() == 200:
            return True, url+"_"+svc+"_"+api+"_"+subset
    except:
        return False,_

def recover(url, svc, api, subset):
    formdata = {
        "url": url,
        "svc": svc,
        "api": api,
        "subset":subset,
        "inject_flag": "recover"
    }
    data = json.dumps(formdata)
    data = data.encode("utf-8")
    req = urllib2.Request(url = base_url, data = data)
   
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib2.urlopen(req)
        if response.getcode() == 200:
            return True
    except:
        return False

def restoreStep(blade_ids):
    if isinstance(blade_ids,list):
        for blade_id in blade_ids:
            req = blade_id.split("_")[0]
            svc = blade_id.split("_")[1]
            api = blade_id.split("_")[2]
            subset = blade_id.split("_")[3]
            recover(req, svc, api, subset)
    else:
        req = blade_ids.split("_")[0]
        svc = blade_ids.split("_")[1]
        api = blade_ids.split("_")[2]
        subset = blade_ids.split("_")[3]
        recover(req, svc, api, subset)

def verifyCorrectness(url):
    if req(url) != False:
        return True
    else:
        return False

def forwardStep(test_case_name, base_triedHypotheses, hypothesis,recorded_traceid):
    blade_ids = []
    for sub_hypo in hypothesis:
        if sub_hypo not in base_triedHypotheses:
            url = sub_hypo.split("_")[0]
            service = sub_hypo.split("_")[1]
            api = sub_hypo.split("_")[2]
            subset = sub_hypo.split("_")[3]
            inject_flag, blade_id = fault_injection(url , service, api, subset)
            if inject_flag == True:
                blade_ids.append(blade_id)
    correctness = verifyCorrectness(test_case_name)
    return correctness, blade_ids

def backwardStep(test_case_name, formulas, triedHypotheses, recorded_traceid):
    newClause = getNewClause(test_case_name) # get new execution path and travese it to new clause
    for clause in newClause:
        if set(clause) not in formulas:
            formulas.append(set(clause))
    starttime = datetime.now()
    print("SAT Solving.....")
    # print(formulas)
    solver,myvars = get_cnf_solver(formulas)
    hypotheses = get_incomplete_hypotheses(solver,triedHypotheses)
    hypotheses = remove_redundant_hypotheses(hypotheses,formulas)
    print(hypotheses)
    endtime = datetime.now()
    return hypotheses,starttime,endtime

def evaluator(test_case_name, base_triedHypotheses, total_triedHypotheses, hypothesis, formulas, solutions, blades_ids, recorded_traceid, parent_index):
    correctness, blade_ids = forwardStep(test_case_name, base_triedHypotheses, hypothesis,recorded_traceid)
    total_triedHypotheses.append(sorted(list(set(base_triedHypotheses + hypothesis))))
    if correctness == True or len(hypothesis) == 0:
        hypotheses,starttime,endtime = backwardStep(test_case_name, formulas,[], recorded_traceid)
        restoreStep(blade_ids)
        global global_index
        print_str = "{}. {} {}: {}".format(global_index,parent_index,hypothesis,hypotheses)
        logger.info((print_str))
        global_index = global_index + 1
        print("SAT Solving Cost:" + str((endtime - starttime).seconds) + " Seconds")
        if len(hypotheses) != 0:
            res_solutions,triedHypotheses = evaluateHypotheses(test_case_name, base_triedHypotheses, total_triedHypotheses, hypotheses,formulas,solutions, blades_ids, recorded_traceid,global_index - 1)
            
            print("SAT Solving Cost:" + str((endtime - starttime).seconds) + " Seconds")
            return res_solutions,blades_ids
        else:
            return [],blades_ids
    else:
        global global_index
        restoreStep(blade_ids)
        print_str = "{}. {} {}: {}".format(global_index,parent_index,hypothesis,"True")
        logger.info((print_str))
        global_index = global_index + 1
        solutions.append(sorted(list(set(base_triedHypotheses + hypothesis))))

        return solutions,blades_ids

def evaluateHypotheses(test_case_name, base_triedHypotheses, total_triedHypotheses, hypotheses,formulas,solutions, blades_ids, recorded_traceid,parent_index):
    if len(hypotheses) == 0:
        return solutions,total_triedHypotheses
    for index in range(len(hypotheses)):
        temp_base_triedHypotheses = copy.deepcopy(base_triedHypotheses)
        hypothesis = hypotheses[index]
        validate_solution_flags = False
        for solution in solutions:
            if set(solution) <= set(sorted(hypothesis)):
                validate_solution_flags = True
                break
        if (not total_triedHypotheses or hypothesis not in total_triedHypotheses)  and (set(hypothesis)<set(base_triedHypotheses)) == False and validate_solution_flags == False:
            sols,blades_ids = evaluator(test_case_name, temp_base_triedHypotheses, total_triedHypotheses, hypothesis ,formulas,solutions, blades_ids, recorded_traceid,parent_index)
            
            return evaluateHypotheses(test_case_name, base_triedHypotheses, total_triedHypotheses,  hypotheses[index+1:], formulas, sols, blades_ids, recorded_traceid,parent_index)
        else:
            return evaluateHypotheses(test_case_name, base_triedHypotheses, total_triedHypotheses,  hypotheses[index+1:], formulas, solutions, blades_ids, recorded_traceid,parent_index)


def concreteEvaluator(test_case_name, hypothesis, formulas, recorded_traceid):
    if len(hypothesis) == 0:
        solutions = []
        base_triedHypotheses = []
        total_triedHypotheses = []
        blades_ids = []
        solutions,_ = evaluator(test_case_name, base_triedHypotheses, total_triedHypotheses, hypothesis, formulas, solutions, blades_ids, recorded_traceid,0)
        return solutions, total_triedHypotheses


def Evaluate(recorded_traceid, test_case_name = "index", inject_flag = True):
    formulas = []
    if inject_flag == True:
        return concreteEvaluator(test_case_name, [], formulas, recorded_traceid)
    else:
        backwardStep(test_case_name, formulas, [], recorded_traceid)
        return None, None


def test(test_case_name):
    recorded_traceid = []
    solutions, triedHypotheses = Evaluate(recorded_traceid, test_case_name, True)
    return solutions, triedHypotheses
logger = logging.getLogger(__name__)
log_path = "./logs/new_basic_" + datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + "LDFI solve logs"
file_handler = logging.FileHandler(log_path)
formatter = logging.Formatter("%(asctime)s\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
global_index = 0
test_case_name = sys.argv[1]
solutions, triedHypotheses = test(test_case_name)
logger.info((solutions))
logger.info((triedHypotheses))
solution_path = "./solutions/" + datetime.now().strftime("%Y-%m-%d-%H:%M:%S") + "_solutions.txt"
with open(solution_path,'w') as f:
    for item in solutions:
        temp = ' '.join(map(lambda x:str(x),item))
        f.write(temp+'\n')