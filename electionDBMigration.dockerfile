FROM python:3

# create src folder in container
# p flag create all missing dirs in path
RUN mkdir -p /opt/src/administrator
WORKDIR /opt/src/administrator

# copy all files to container
COPY administrator/migrate.py ./migrate.py
COPY administrator/configuration.py ./configuration.py
COPY administrator/models.py ./models.py
COPY administrator/requirements.txt ./requirements.txt
COPY administrator/roleGuard.py ./roleGuard.py

# install all requirements
RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]
