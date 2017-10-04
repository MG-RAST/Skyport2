
# docker build -t mgrast/auth-server -f Docker/Dockerfiles/authServer.dockerfile .
# docker rm auth-server ; docker run -d --name auth-server -p 7000:80  mgrast/auth-server

FROM httpd:2.4

# ARG service-dir=./

# Dependencies
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
  make \
  perl-modules \
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

RUN mkdir -p /db && chmod a+w /db
COPY ./Services/authServer/user.db /db/user.db
RUN chmod a+w /db/user.db


# Customization 
COPY ./Services/authServer/cgi-bin ./Services/authServer/html /usr/local/apache2/htdocs/
COPY ./Services/authServer/httpd.conf /usr/local/apache2/conf/
COPY ./Config/authServer/OAuthConfig.pm /usr/local/apache2/htdocs/ 
COPY ./Config/authServer/setup.sh /usr/local/bin/
COPY ./Config/authServer/dbsetup.demo.mysql /tmp/
RUN chmod a+x /usr/local/bin/setup.sh 
#CMD ["httpd-foreground"]
CMD ["setup.sh"]

