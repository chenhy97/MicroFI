  # -*- coding: utf-8 -*
from z3 import *
# cnf = [[(u's1', u's2'), (u's2', u's6')], [(u's1', u's3'), (u's3', u's6')], [(u's1', u's4'), (u's4', u's6')], [(u's1', u's5'), (u's5', u's6')]]
# cnf = [[u'/_frontend_/_v2', u'/_currencyservice_GetSupportedCurrencies_v2', u'/_productcatalogservice_ListProducts_v1', u'/_cartservice_GetCart_v2', u'/_currencyservice_Convert_v1', u'/_adservice_GetAds_v1'],
#  [u'/_frontend_/_v1', u'/_currencyservice_GetSupportedCurrencies_v2', u'/_productcatalogservice_ListProducts_v2', u'/_cartservice_GetCart_v1', u'/_currencyservice_Convert_v2', u'/_adservice_GetAds_v2'],
#   [u'/_frontend_/_v2', u'/_currencyservice_GetSupportedCurrencies_v1', u'/_productcatalogservice_ListProducts_v2', u'/_cartservice_GetCart_v1', u'/_currencyservice_Convert_v2', u'/_adservice_GetAds_v1'], 
# [u'/_frontend_/_v1', u'/_currencyservice_GetSupportedCurrencies_v1', u'/_productcatalogservice_ListProducts_v2', u'/_cartservice_GetCart_v2', u'/_currencyservice_Convert_v1', u'/_adservice_GetAds_v2']]
# cnf = [["1","2","3","4", "5","6"]]
# cnf = [["A","B","C","D"],["A","B","C","D'"]]
cnf = [["A","1"],["A","2"],["B","1"],["B","2"]]
def get_cnf_solver(cnf):
    s = Solver()
    formulas = []
    myvars = []
    for formula in cnf:
        clauses = []
        for clause in list(formula):
            clause_str = str(clause)
            clause_bool = Bool(clause_str)
            clauses.append(clause_bool)
            myvars.append(clause_bool)
        formulas.append(Or(clauses))
    s.add(formulas)
    return s, myvars
def get_incomplete_hypotheses(solver,triedHypotheses):
    #存在新的执行路径，需要考虑在已注入故障的前提，加入新路径后如何求解
    print("sat",triedHypotheses)
    if triedHypotheses :
        for item in triedHypotheses:
            # print(item)
            solver.add(Bool(item) == True)
    res = solver.check()
    solutions = []
    while res == sat:
        m = solver.model()
        solution = []
        for d in m.decls():
            if m[d] == True:
                solution.append(d.name())
        solutions.append(solution)
        block = []
        for var in m:
            block.append(var() != m[var])
        solver.add(Or(block))
        res = solver.check()
    for solution in solutions:
        if set(solution) > set(triedHypotheses):
            for hypothesis in triedHypotheses:
                try:
                    solution.remove(hypothesis)
                except Exception as e:
                    import pdb;pdb.set_trace()
            # print(solution)
        else:
            print("----",solution)
    # import pdb; pdb.set_trace()
    return solutions
#得到的可注入故障的解过多，废置
def get_all_hypotheses(solver,myvars):
    res = solver.check()
    solutions = []
    while res == sat:
        m = solver.model()
        block = []
        solution = []
        for var in myvars:
            v = m.evaluate(var, model_completion = True)
            if v == True:
                solution.append(var)
            block.append(var != v)
        solutions.append(solution)
        solver.add(Or(block))
        res = solver.check()
    return solutions
def remove_redundant_hypotheses(hypotheses,formulas):
    # clauses_dict = 
    new_hypotheses = []
    str_formulas = []
    for formula in formulas:
        str_formulas.append(map(str,formula))
    formulas_len = len(str_formulas)
    hypo_formula_count = {}
    for hypothesis in hypotheses:
        for i in range(formulas_len):
            hypo_formula_count[i] = 0
        for sub_hypo in hypothesis:
            for i in range(formulas_len):
                formula = str_formulas[i]
                if sub_hypo in formula:
                    hypo_formula_count[i] = hypo_formula_count[i] + 1
        add_flag = True
        for key,value in hypo_formula_count.items():
            if value > 1:
                add_flag = False
                break
        if add_flag == True:
            new_hypotheses.append(hypothesis)
    minimum_hypotheses = []
    for i in range(len(new_hypotheses)):
        is_exist = False
        for j in range(len(minimum_hypotheses)):
            if set(minimum_hypotheses[j]).issubset(set( new_hypotheses[i])):
                is_exist = True
                break
        if is_exist == False:
            minimum_hypotheses.append(new_hypotheses[i])

    return minimum_hypotheses

# triedHypotheses = ['/_productcatalogservice_ListProducts_v1']
# triedHypotheses = ['D']
# solver,myvars = get_cnf_solver(cnf)
# hypotheses = get_incomplete_hypotheses(solver,triedHypotheses)
# print(hypotheses)
# hypotheses = remove_redundant_hypotheses(hypotheses,cnf)
# print(hypotheses)