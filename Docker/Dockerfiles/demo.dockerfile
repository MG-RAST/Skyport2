FROM ubuntu:latest
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
autoconf \
automake \
build-essential \
ncbi-blast+ \
wget

# vsearch 2.4.4
RUN cd /root \
	&& wget https://github.com/torognes/vsearch/archive/v2.4.4.tar.gz \
	&& tar xzf v2*.tar.gz \
	&& cd vsearch-2* \
	&& ./autogen.sh \
	&& ./configure --prefix=/usr/local/ \
	&& make \
	&& make install \
	&& make clean \
	&& cd .. \
  && rm -rf /root/vsearch-* /root/v2*.tar.gz
