from flask import Flask, request, jsonify, Response
import requests
from contextlib import closing
from opentelemetry import trace, baggage
from opentelemetry.propagate import inject,extract
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
import os
from opentelemetry.propagate import extract
app = Flask(__name__)
span_exporter = OTLPSpanExporter(
    # optional
    endpoint=os.environ.get('COLLECTOR_ADDR'),
    )

provider = TracerProvider()
processor = BatchSpanProcessor(span_exporter)
trace.set_tracer_provider(provider)

trace.get_tracer_provider().add_span_processor(processor)
tracer = trace.get_tracer(__name__)
print(tracer)
@app.before_request
def before_request():
    headers = dict()
    for name, value in request.headers:
        if name != "User-Agent" and name != "Accept-Encoding" and name != "Accept" : 
            headers[name] = value
        else:
            print(name, value)
    tracestate_value = "fault=1"
    headers["tracestate"] = tracestate_value
    headers["baggage"] = "a=1"
    with tracer.start_as_current_span("RF_AGENT", context = extract(headers)) as span:
        trace_id = format(span.get_span_context().trace_id, "032x")
        span_id = format(span.get_span_context().span_id, "016x")
        base_url = request.url
        method = request.method
        data = request.data or request.form or None
        uri = '/'.join(base_url.split('/')[3:]) 
        inject(headers) 
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