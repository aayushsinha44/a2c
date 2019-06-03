FROM ubuntu:18.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common 
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - 
RUN apt-key fingerprint 0EBFCD88 
RUN add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable"
RUN apt-get update
RUN apt-get install -y docker-ce docker-ce-cli containerd.io

RUN apt-get update && \
      apt-get -y install sudo

RUN apt-get update
RUN apt-get -y install python3-pip
 
RUN useradd -m docker1 && echo "docker1:docker1" | chpasswd && adduser docker1 sudo

USER docker1

RUN pip3 install -r requirements.txt

COPY . ./a2c
WORKDIR ./a2c

EXPOSE 8090
CMD ["python3", "app.py"]
