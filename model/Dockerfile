FROM python:3.10

CMD  pip3 install -r requirements.txt 

ADD model.py model/model.python
ADD requirements.txt  model/requirements.txt 


WORKDIR model/

EXPOSE 8000
CMD python3 model.py
