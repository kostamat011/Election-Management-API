FROM python:3

# create src folder in container
# p flag create all missing dirs in path
RUN mkdir -p /opt/src/dameon
WORKDIR /opt/src/dameon

# copy all files to container
COPY dameon/application.py ./application.py
COPY dameon/configuration.py ./configuration.py
COPY dameon/models.py ./models.py
COPY dameon/requirements.txt ./requirements.txt

ENV PYTHONPATH="/opt/src/dameon"

# install all requirements
RUN pip install -r ./requirements.txt
RUN pip install python-dateutil

ENTRYPOINT ["python", "./application.py"]
