FROM python:2.7.15-alpine3.8

RUN apk --no-cache add gcc musl-dev jpeg jpeg-dev zlib zlib-dev

COPY lovelyeggs /lovelyeggs

RUN mkdir /wheels
COPY requirements.txt requirements.txt
COPY pip.conf /etc/pip.conf

# force no binary for some packages because the built wheels are not compatible because of the
# underlying libs used by the prebuilt packages
RUN pip wheel --no-deps --wheel-dir /wheels -r requirements.txt -f /lovelyeggs/ --no-binary=gevent,greenlet,zope.interface,pillow

FROM python:2.7.15-alpine3.8

# set timezone
RUN apk --no-cache add tzdata jpeg libmagic && \
    pip install --upgrade pip
  RUN apk --no-cache add tzdata
RUN ln -sf /usr/share/zoneinfo/Europe/Zurich /etc/localtime

COPY --from=0 /wheels /wheels

RUN pip install --no-index --no-deps /wheels/* && rm -rf /wheels requirements.txt

COPY sdist/ /sdist
RUN pip install --no-deps /sdist/*.tar.gz && rm -rf /sdist

ENTRYPOINT ["iris-service"]
