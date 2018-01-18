package OAuthConfig;

# This is the configuration file for authServer

require Exporter;

# name and timeout of the cookie used by the authServer
use constant SESSION_COOKIE_NAME => 'AuthWebSession';
use constant SESSION_TIMEOUT => "+2d";

# user / permission database
# You can use either an sqlite3 or mySQL database. Adjust the connect string accordingly.
# use constant USER_DB => '/db/user.db';
# use constant MYSQL_USER_NAME => "";
# use constant MYSQL_USER_PASSWORD => "";
# use constant DBI_CONNECT => "dbi:SQLite:dbname=".USER_DB;


# mysql connection
use constant DB_NAME     => '' || $ENV{'MYSQL_DATABASE' } ;
use constant DB_HOST     => '' || $ENV{'MYSQL_HOST' } ;
use constant DBI_USER    => "" || $ENV{'MYSQL_USER' } ; # "authService"
use constant DBI_PASS    => "authServicePassword" ||  $ENV{'MYSQL_PASSWORD'};
use constant DBI_CONNECT => "dbi:mysql:database=".DB_NAME.";host=".DB_HOST;



# Name of the authServer. If you use the authServer for a single application, you can use
# the name of that application and its URL here. In this case you should also set TRUSTED
# to the same value.
# The TRUSTED application does not require the user to confirm they want to share their
# information with the app. Set this to 0 if you do not want to use any trusted application.
use constant APPLICATION_NAME => "Authentication Server";
use constant TRUSTED => 0 ;
use constant APPLICATION_URL => "http://localhost:8001/auth/";

# Setting this to true will enable the registration of applications / users (if oAuth.cgi is
# called without any parameters)
use constant ALLOW_REGISTER_APPLICATION => 0;
use constant ALLOW_REGISTER_USER => 0 ;

# Added

use constant EMAIL_IS_LOGIN => "" ;
use constant EMAIL_REG_SUFFIX => "" ;
use constant EMAIL_REG_PREFIX => "" ;
use constant EMAIL_REG_SUBJECT => "" ;
use constant EMAIL_SHARE_UNKNOWN_SUFFIX => "";
use constant EMAIL_SHARE_UNKNOWN_PREFIX => "";
use constant EMAIL_SHARE_SUBJECT => "" ;
use constant EMAIL_SHARE_KNOWN => "" ;
use constant SHOCK_PREAUTH_URL => "" ;


# base and relative urls for the authServer and its images, javascript and stylesheets
use constant BASE_URL => 'http://localhost:8001/auth/';
use constant IMAGE_DIR => 'http://localhost:8001/auth/images/';
use constant JS_DIR => 'http://localhost:8001/auth/js/';
use constant CSS_DIR => 'http://localhost:8001/auth/css/';


# response email and SMTP server used in registration and sharing emails
use constant ADMIN_EMAIL => 'admin@some.where';
use constant SMTP => "smtp.server.local";

@ISA = qw(Exporter);
@EXPORT = qw(SESSION_COOKIE_NAME SESSION_TIMEOUT DBI_CONNECT APPLICATION_NAME TRUSTED
APPLICATION_URL ALLOW_REGISTER_APPLICATION ALLOW_REGISTER_USER BASE_URL
IMAGE_DIR JS_DIR CSS_DIR ADMIN_EMAIL SMTP DBI_USER DBI_PASS
EMAIL_IS_LOGIN EMAIL_REG_SUFFIX EMAIL_REG_PREFIX EMAIL_REG_SUBJECT EMAIL_SHARE_UNKNOWN_SUFFIX
EMAIL_SHARE_UNKNOWN_PREFIX EMAIL_SHARE_SUBJECT EMAIL_SHARE_KNOWN SHOCK_PREAUTH_URL
);

1;
