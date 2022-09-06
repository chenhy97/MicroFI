  # -*- coding: utf-8 -*
from traces_preprocesses.query import *
from send_reqs.reqs import *
from traces_preprocesses.trace_utils import *
from utils.general_util import *
import time

def collect_page_rank_trace(timestamp):
    endTime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")-timedelta(minutes=1)
    startTime = endTime - timedelta(minutes=5)
    startTime = datetime.strftime(startTime,  "%Y-%m-%d %H:%M:%S")
    endTime = datetime.strftime(endTime, "%Y-%m-%d %H:%M:%S")
    path_list = dict()
    span_list = get_span(start=str2f(startTime), end=str2f(endTime))
    if len(span_list) > 0:
        path_list, trace_list = path_aggregate(span_list, path_list)
        return trace_list,span_list
    else:
        return [],[]

def trace_pagerank(pod_pod, pod_trace, trace_pod, pr_trace):
    pod_length = len(pod_pod)
    trace_length = len(pod_trace)
    p_ss = np.zeros((pod_length, pod_length), dtype=np.float32)
    p_sr = np.zeros((pod_length, trace_length), dtype=np.float32)
    p_rs = np.zeros((trace_length, pod_length), dtype=np.float32)
    pr = np.zeros((trace_length, 1), dtype=np.float32)
    node_list = []
    for key in pod_pod.keys():
        node_list.append(key)
    trace_list = []
    for key in pod_trace.keys():
        trace_list.append(key)
    for pod in pod_pod:
        child_num = len(pod_pod[pod])
        for child in pod_pod[pod]:
            p_ss[node_list.index(child)][node_list.index(pod)] = 1.0 / child_num
    for trace_id in pod_trace:
        child_num = len(pod_trace[trace_id])
        for child in pod_trace[trace_id]:
            p_sr[node_list.index(child)][trace_list.index(trace_id)] \
                = 1.0 / child_num
    for pod in trace_pod:
        child_num = len(trace_pod[pod])
        for child in trace_pod[pod]:
            p_rs[trace_list.index(child)][node_list.index(pod)] \
                = 1.0 / child_num
    kind_list = np.zeros(len(trace_list))
    p_srt = p_sr.T
    for i in range(len(trace_list)):
        index_list = [i]
        if kind_list[i] != 0:
            continue
        n = 0
        for j in range(i, len(trace_list)):
            if (p_srt[i] == p_srt[j]).all():
                index_list.append(j)
                n += 1
        for index in index_list:
            kind_list[index] = n
    num_sum_trace = 0
    kind_sum_trace = 0
    for trace_id in pr_trace:
        num_sum_trace += 1 / kind_list[trace_list.index(trace_id)]
    for trace_id in pr_trace:
        pr[trace_list.index(trace_id)] = 1 / kind_list[trace_list.index(trace_id)] / num_sum_trace
    
    result = pageRank(p_ss, p_sr, p_rs, pr, pod_length, trace_length)
    return result

def pageRank(p_ss, p_sr, p_rs, v, operation_length, trace_length, d=0.85, alpha=0.01):
    service_ranking_vector = np.ones((operation_length, 1)) / float(operation_length + trace_length)
    request_ranking_vector = np.ones((trace_length, 1)) / float(operation_length + trace_length)
    for i in range(25):
        updated_service_ranking_vector = d * (np.dot(p_sr, request_ranking_vector) + alpha * np.dot(p_ss, service_ranking_vector))
        updated_request_ranking_vector = d * np.dot(p_rs, service_ranking_vector) + (1.0 - d) * v
        service_ranking_vector = updated_service_ranking_vector / np.amax(updated_service_ranking_vector)
        request_ranking_vector = updated_request_ranking_vector / np.amax(updated_request_ranking_vector)
    normalized_service_ranking_vector = service_ranking_vector / np.amax(service_ranking_vector)
    return normalized_service_ranking_vector

def get_svc_scores(trace_pod,page_rank_scores):
    svc_scores = {}
    for i in range(len(trace_pod.keys())):
        pod_name = trace_pod.keys()[i]
        svc = pod_name.split("-")[0][:-1]
        if svc not in svc_scores.keys():
            if svc == "fronten":
                svc_scores[svc+"d"] = [page_rank_scores[i][0]]
            else:
                svc_scores[svc] = [page_rank_scores[i][0]]
        else:
            if svc == "fronten":
                svc_scores[svc+"d"].append(page_rank_scores[i][0])
            else:
                svc_scores[svc].append(page_rank_scores[i][0])
    for pod, scores in svc_scores.items():
        average = 0
        for score in scores:
            average = average+score
        average = average/len(scores)
        svc_scores[pod] = average

    return svc_scores

def get_operation_scores(trace_operation, operation_page_rank_scores):
    operation_scores = {}
    for i in range(len(trace_operation.keys())):
        operation_name = trace_operation.keys()[i]
        if operation_name not in operation_scores.keys():
            operation_scores[operation_name] = [operation_page_rank_scores[i][0]]
        else:
            operation_scores[operation_name].append(operation_page_rank_scores[i][0])
    for operation, scores in operation_scores.items():
        average = 0
        for score in scores:
            average = average+score
        average = average/len(scores)
        operation_scores[operation] = average
    return operation_scores

def get_pagerank_scores():
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
    recorded_traceid = []
    trace_list, span_list = collect_page_rank_trace(ts)
    pod_pod, pod_trace, trace_pod, pr_trace = get_pagerank_graph(trace_list.keys(),span_list)
    operation_operation, operation_trace, trace_operation, pr_trace = get_pagerank_operation_graph(trace_list.keys(), span_list)

    pod_page_rank_scores = trace_pagerank(pod_pod, pod_trace, trace_pod, pr_trace)
    operation_page_rank_scores = trace_pagerank(operation_operation, operation_trace, trace_operation, pr_trace)
    pod_svc_scores = get_svc_scores(trace_pod,pod_page_rank_scores)
    pod_svc_scores = sorted(pod_svc_scores.items(), key=lambda item:item[1],reverse=True)

    svc_operation_scores = get_operation_scores(trace_operation, operation_page_rank_scores)
    svc_operation_scores = sorted(svc_operation_scores.items(), key=lambda item:item[1],reverse=True)

    svc_scores = {}
    for item in pod_svc_scores:
        svc_scores[item[0]] = item[1]

    operation_scores = {}
    for item in svc_operation_scores:
        operation_scores[item[0]] = item[1]
    return operation_scores
