FROM ubuntu
MAINTAINER Noel Burton-Krahn <noel@burton-kahn.com>
WORKDIR /app
ADD etc /etc
ADD . .
RUN apt-key add /etc/apt/heroku.release.key
RUN apt-get update && apt-get -y install \
  make \
  python \
  python-pip \
  python-dev \
  ncurses-dev \
  mongodb \
  heroku \
  curl \
  tcpdump
# to install heroku commandline
RUN heroku --help
RUN pip install --upgrade pip && pip install --upgrade -r requirements.txt
CMD make run



