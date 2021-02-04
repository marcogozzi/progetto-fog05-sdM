FROM marcogozzi/upy:1

RUN mkdir -p /home/fos/config && mkdir /tmp/fos

COPY main-app-t.py /home/fos
COPY ./config /home/fos/config

VOLUME /tmp/fos


ENTRYPOINT ["python3"]


CMD ["/home/fos/main-app-t.py","-c","/home/fos/config/config.json"]
