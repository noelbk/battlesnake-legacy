# This is a comment
FROM ubuntu-heroku
MAINTAINER Noel Burton-Krahn <noel@burton-kahn.com>
WORKDIR /app
ADD . .
RUN apt-get -y install $(cat requirements.apt)
RUN make install
ENTRYPOINT make run
