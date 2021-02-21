# set base image (host OS)
FROM python:3.8

# set the working directory in the container
WORKDIR /App

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN apt-get update && apt-get -y install cmake protobuf-compiler
RUN pip install -r requirements.txt

# command to run on container start
CMD [ "python", "./App/api_server.py" ]
