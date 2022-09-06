from flask import Flask, request, jsonify, Response
import requests
from contextlib import closing
from jaeger_client import Config
from opentracing.propagation import Format
import os

app = Flask(__name__)

config = Config(
        config={ # usually read from some yaml config
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': os.environ.get('JAEGER_COLLECTOR'),
                'reporting_port': os.environ.get('JAEGER_PORT'),
            },
            'logging': True,
        },
        service_name='RFAgent',
        validate=True,
    )
# this call also sets opentracing.tracer
tracer = config.initialize_tracer()
def before_request():
    headers = dict()
    for name, value in request.headers:
        if name != "User-Agent" and name != "Accept-Encoding" and name != "Accept" : 
            headers[name] = value
        else:
            print(name, value)
    span_ctx = tracer.extract(Format.HTTP_HEADERS, headers)
    with tracer.start_span("RF_AGENT",child_of=span_ctx) as span:
        span.set_baggage_item('fault', '1')
        base_url = request.url
        method = request.method
        data = request.data or request.form or None
        uri = '/'.join(base_url.split('/')[3:]) 
        tracer.inject(span, Format.HTTP_HEADERS, headers)
        target_ip = os.environ.get('TARGET_SVC')
        target_port =  os.environ.get('TARGET_SVC_PORT')
        target_uri = "http://"+target_ip+":"+target_port+"/"
        url = target_uri + uri
        with closing(  requests.request(method, url, headers=headers, data=data, stream=True, allow_redirects = False) ) as r:
            resp_headers = []
            for name, value in r.headers.items():
                if name.lower() in ('content-length','connection','content-encoding'):
                    continue
                resp_headers.append((name, value))
            resp = Response(r.content, status=r.status_code, headers=resp_headers)
    return resp

if __name__ == "__main__":
    
    app.config.from_pyfile("settings.py")
    app.run(host = '0.0.0.0',
        port = 5000,  
        debug = True )