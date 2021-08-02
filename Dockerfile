FROM ubuntu

ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update

RUN apt-get install -y python3.8
RUN apt-get install -y pip
RUN apt-get install -y python-dev

RUN pip3 install pycrypto
RUN pip3 install thread6
RUN pip3 install regex

RUN mkdir /home/Delta_T3
RUN cd /home/Delta_T3

RUN mkdir main_folder client server

COPY ./server.py /home/Delta_T3/server
RUN chmod +x /home/Delta_T3/server/server.py
COPY ./client.py /home/Delta_T3/client
RUN chmod +x /home/Delta_T3/client/client.py

RUN cd /home/Delta_T3/main_folder
RUN mkdir sysAd webDev appDev
