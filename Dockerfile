FROM python:3.7.7

# set base dir
WORKDIR /usr/src/app

# copy all
COPY . .

# install pip reqs
RUN pip install --no-cache-dir -r requirements.txt

# tell the port number the container should expose
EXPOSE 80

# run flask
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

#docker build -t starlink-api-init .
#docker run -i -p 80:80 starlink-api-init