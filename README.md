# MicroFI

## Requirements
- A kubernetes cluster that is deployed with service mesh (Istio).
- A microservice system with distributed tracing.
- A tracing system to collect and store the tracing data produced by the application.
## running results

- The injection solutions exploration results on three applications.

## codes:

### Non-intrusive Request Marker

- `./RM-opentracing` contains the the code and the deployment files of non-intrusive Request Marker that applied in Open Tracing standard. 
    - `RF.py`, `requirements.txt` and `Dockerfile` are the implementation code, the requirement of libraray and the text document to assemble an image.
    - `rfagntservice.yaml` is the deployment file that can be used to deploy the Request Marker in a Kubernetes cluster.
- `./RM-otel` contains the the code and the deployment files of non-intrusive Request Marker that applied in Open Telemetry standard. 
    - the same as `./RM-opentracing`.
- `demos` contains three microservice demos including `hipster-shop`, `hotel reservation` and `train ticket`.
### Fault Injector Orchestrator
- `basic_ldfi.py` contains the implementation codes about the basic LDFI approach.
- `multi_prune_basic_ldfi.py` contains the implementation codes for multiple business function testing with the basic LDFI and injection space pruning.
- `multi_prune_pr_ldfi.py` contains the implementation codes for multiple business function testing with the basic LDFI, APIRank and injection space pruning.
- `parallel_start.py` contains the implementation codes for boostraping the Fault Injector Orchestator and making them running in parallel.
