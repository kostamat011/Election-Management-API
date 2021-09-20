FROM python:3

# create src folder in container
# p flag create all missing dirs in path
RUN mkdir -p /opt/src/official
WORKDIR /opt/src/official

# copy all files to container
COPY official/application.py ./application.py
COPY official/configuration.py ./configuration.py
COPY official/models.py ./models.py
COPY official/requirements.txt ./requirements.txt
COPY official/roleGuard.py ./roleGuard.py

# install all requirements
RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]
