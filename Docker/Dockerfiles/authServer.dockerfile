
# docker build -t mgrast/auth-server -f Docker/Dockerfiles/authServer.dockerfile .
# docker rm auth-server ; docker run -d --name auth-server -p 7000:80  mgrast/auth-server

FROM httpd:2.4

# ARG service-dir=./

# Dependencies
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
  make \
  perl-modules \
  less \
  liburi-perl \
  liburi-encode-perl \
  libwww-perl \
  libjson-perl \
  libdbi-perl \
  libdbd-mysql-perl \
  libdbd-sqlite3-perl \
  libdigest-md5-perl \
  libfile-slurp-perl \
  libhtml-strip-perl \
  liblist-moreutils-perl \
  libcache-memcached-perl \
  libhtml-template-perl \
  libdigest-md5-perl \
  libdigest-md5-file-perl \
  libdatetime-perl \
  libdatetime-format-ISO8601-perl \
  liblist-allutils-perl \
  libposix-strptime-perl \
  libuuid-tiny-perl \
  libmongodb-perl \
  libfreezethaw-perl \
  libtemplate-perl \
  libclass-isa-perl

RUN apt-get install -y \
  vim

ENV PERL_MM_USE_DEFAULT 1
RUN apt-get install -y default-mysql-client

# Customization
COPY Services/authServer/html /usr/local/apache2/htdocs/
COPY Services/authServer/cgi-bin /usr/local/apache2/htdocs/cgi-bin
COPY Config/authServer/httpd.conf /usr/local/apache2/conf/
COPY Config/authServer/OAuthConfig.pm /usr/local/apache2/htdocs/cgi-bin/
COPY Config/authServer/ClientConfigAWE.pm /usr/local/apache2/htdocs/cgi-bin/
COPY Config/authServer/ClientConfigShock.pm /usr/local/apache2/htdocs/cgi-bin/
COPY Config/authServer/clientAWE.cgi /usr/local/apache2/htdocs/cgi-bin/
COPY Config/authServer/clientShock.cgi /usr/local/apache2/htdocs/cgi-bin/
COPY Config/authServer/setup.sh /usr/local/bin/
COPY Config/authServer/dbsetup.demo.mysql /tmp/
RUN chmod a+x /usr/local/apache2/htdocs/cgi-bin/*.cgi
RUN chmod a+x /usr/local/bin/setup.sh
#CMD ["httpd-foreground"]
CMD ["setup.sh"]
