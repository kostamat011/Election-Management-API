FROM python:3

# create src folder in container
# p flag create all missing dirs in path
RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

# copy all files to container
COPY authentication/application.py ./application.py
COPY authentication/configuration.py ./configuration.py
COPY authentication/models.py ./models.py
COPY authentication/requirements.txt ./requirements.txt
COPY authentication/roleGuard.py ./roleGuard.py

# install all requirements
RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./application.py"]
