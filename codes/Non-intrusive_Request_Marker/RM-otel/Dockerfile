FROM python:3.7-slim
RUN apt-get update -qqy && \
	apt-get -qqy install wget g++ procps curl vim iproute2 && \
	rm -rf /var/lib/apt/lists/*
# show python logs as they occur
ENV PYTHONUNBUFFERED=0


# get packages
WORKDIR /RFAgent
COPY requirements.txt requirements.txt
COPY settings.py settings.py
RUN pip install -r requirements.txt

# add files into working directory
COPY . .

# set listen port
ENV PORT "5000"
EXPOSE 5000

# ENTRYPOINT ["python3", "/RFAgent/RF.py"]
CMD gunicorn -w 1 RF:app

