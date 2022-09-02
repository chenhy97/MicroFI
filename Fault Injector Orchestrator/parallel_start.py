from multiprocessing import  Process
import os

def test_business_function(test_case_name):
    print(test_case_name)
    os.system("python multi_prune_pr_ldfi.py "+test_case_name)

test_case_list=["/","/cart","/product/*","/cart/checkout","/setCurrency"]

process_list = []
for i in range(len(test_case_list)):
    p = Process(target=test_business_function,args=(test_case_list[i],))
    p.start()
    process_list.append(p)
for i in process_list:
    p.join()