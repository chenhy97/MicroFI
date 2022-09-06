import json
import urllib
import urllib2
# import urllib
base_url = "http://10.0.10.1:8181"
# get latest trace
def req(url):
    url_form = {"url" : url}
    data_string = urllib.urlencode(url_form)
    new_url = base_url + "?" + data_string
    try:
        response = urllib2.urlopen(new_url)
        if response.getcode() == 200:
            trace_data = json.loads(response.read().decode())
            print(trace_data[0])
            return trace_data
    except:
        return False
def fault_inject(req, svc, api, subset):
    formdata = {
        "url": req,
        "svc": svc,
        "api": api,
        "subset":subset,
        "inject_flag": "inject"
    }
    data = json.dumps(formdata)
    data = bytes(data, "utf-8")
    req = urllib.request.Request(url = base_url, data = data)
   
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            return True, svc+"_"+api+"_"+subset
    except:
        return False,_

def recover(req, svc, api, subset):
    formdata = {
        "url": req,
        "svc": svc,
        "api": api,
        "subset":subset,
        "inject_flag": "recover"
    }
    data = json.dumps(formdata)
    data = bytes(data, "utf-8")
    req = urllib.request.Request(url = base_url, data = data)
   
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            return True
    except:
        return False