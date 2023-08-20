FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

RUN apt-get update
RUN apt-get -y install libgl1-mesa-glx

EXPOSE 8000

ENTRYPOINT [ "python", "main.py" ]
# CMD ["--options", ""]
