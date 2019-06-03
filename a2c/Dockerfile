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

RUN service docker start

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

RUN apt-get update && \
      apt-get -y install sudo

RUN apt-get update
RUN apt-get -y install python3-pip
 
RUN useradd -m docker1 && echo "docker1:docker1" | chpasswd && adduser docker1 sudo

USER docker1

RUN mkdir /home/docker1/a2c
RUN chmod 777 /home/docker1/a2c
RUN chown docker1 /home/docker1/a2c
WORKDIR /home/docker1/a2c
COPY --chown=docker1:docker1 ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install pyinstaller

COPY --chown=docker1:docker1 . .

RUN /home/docker1/.local/bin/pyinstaller --onefile app.py

WORKDIR /home/docker1
RUN mv ./a2c/dist/app app
RUN rm -rf a2c
RUN chmod +x app

EXPOSE 8090
CMD ["./app"]
