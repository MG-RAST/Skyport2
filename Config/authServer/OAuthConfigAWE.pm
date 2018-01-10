package OAuthConfigAWE;

require Exporter;

use constant SESSION_COOKIE_NAME => 'AuthWebSession';
use constant SESSION_TIMEOUT => "+2d";

use constant ADMIN_EMAIL => "admin@some.where.loc";

use constant BASE_URL => 'http://localhost:8001/auth';
use constant IMAGE_DIR => '/auth/images/';
use constant JS_DIR => '/auth/js/';
use constant CSS_DIR => '/auth/css/';

use constant ALLOW_REGISTER_APPLICATION => 1;
use constant ALLOW_REGISTER_USER => 1;
use constant TRUSTED => "Demo AWE Application";

use constant APPLICATION_NAME => "Demo AWE Application";
use constant APPLICATION_URL => "http://localhost:8001/awe/index.html";

use constant SHOCK_URL => "http://shock/node/";
use constant SHOCK_AUTH => "";
use constant APP_SECRET => "abXYffLyDabuyxXN8vstbsaMdNwpMKfk";

use constant AUTH_KEYWORD => 0;
use constant AUTH_PREFIX => 0;

# mysql connection
use constant DB_NAME     => '' || $ENV{'MYSQL_DATABASE' } ;
use constant DB_HOST     => '' || $ENV{'MYSQL_HOST' } ;
use constant DBI_USER    => "" || $ENV{'MYSQL_USER' } ; # "authService"
use constant DBI_PASS    => "authServicePassword" ||  $ENV{'MYSQL_PASSWORD'};
use constant DBI_CONNECT => "dbi:mysql:database=".DB_NAME.";host=".DB_HOST;

use constant SMTP => "smtp.server.local";

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



@ISA = qw(Exporter);
@EXPORT = qw(DBI_USER DBI_PASS SESSION_COOKIE_NAME USER_DB SESSION_TIMEOUT ADMIN_EMAIL BASE_URL IMAGE_DIR JS_DIR CSS_DIR ALLOW_REGISTER_APPLICATION ALLOW_REGISTER_USER APPLICATION_NAME TRUSTED APPLICATION_URL SMTP SHOCK_URL SHOCK_AUTH DBI_CONNECT APP_SECRET EMAIL_REG_SUFFIX EMAIL_SHARE_UNKNOWN_SUFFIX EMAIL_SHARE_SUBJECT EMAIL_SHARE_KNOWN SHOCK_PREAUTH_URL EMAIL_IS_LOGIN EMAIL_REG_SUBJECT EMAIL_REG_PREFIX EMAIL_SHARE_UNKNOWN_PREFIX AUTH_KEYWORD AUTH_PREFIX);

1;
