FROM gliderlabs/alpine:3.3

# Install requirements
#
RUN apk --no-cache add gcc \
                       python py-pip python-dev && \
    pip install --upgrade pip

RUN pip install elasticsearch==1.9.0

RUN mkdir helpers
ADD es_copyindex.py .
