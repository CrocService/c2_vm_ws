FROM python
MAINTAINER Andrey Maksimov 'maksimov.andrei@gmail.com'
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000

CMD [ "python", "c2_vm_ws.py" ]
