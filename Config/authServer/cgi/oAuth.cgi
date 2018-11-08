#!/usr/bin/perl

# authServer main script
# This is an authentication server complying to the oAuth2 protocol. It supports user
# and application registration as well as rights management. Use OAuthConfig.pm for
# configuration and more information.

use strict;
use warnings;
no warnings 'once';


use CGI;
use CGI::Cookie;
$CGI::LIST_CONTEXT_WARN = 0;
$CGI::Application::LIST_CONTEXT_WARN = 0;

use DBI;
use Digest::MD5 qw(md5_hex);
use Net::SMTP;
use POSIX qw(strftime);
use MIME::Base64;
use HTML::Strip;
use Scalar::Util qw(looks_like_number);

use OAuthConfig;

my $dbh = dbh();
my $cgi = new CGI();

#my @params = $cgi->param;
#foreach my $param (@params) {
#  $cgi->param($param, quote($cgi->param($param)));
#}

my $cookie = $cgi->cookie(SESSION_COOKIE_NAME);
my $user = "";
my $uhash = "";
if ($cookie) {
  my $secret;
  ($uhash, $secret) = split(/;/, $cookie);
  
  my $res = $dbh->selectrow_arrayref("SELECT login FROM user WHERE cookie='".$secret."';");
  if ($dbh->err()) {
    warning_message($DBI::errstr);
    exit 0;
  }
  if ($res) {
    if (md5_hex($res->[0]) eq $uhash) {
      $user = $res->[0];
    } else {
      $uhash = "";
    }
  } else {
    $uhash = "";
  }
}

if ($cgi->param('logout')) {
  $cookie = CGI::Cookie->new( -name    => SESSION_COOKIE_NAME,
			      -value   => '',
			      -expires => "-1d" );
  
  $dbh->disconnect();
  if ($cgi->param('redirect')) {
    print $cgi->header( -redirect => $cgi->param('redirect'), -cookie => $cookie );
  } else { 
    print $cgi->header( -cookie => $cookie );
    print base_template();
    print success_message("You have been logged out.");
    print close_template();
    exit 0;
  }
}

if ($cgi->param('login') && $cgi->param('pass')) {
  my $res = $dbh->selectrow_arrayref("SELECT login FROM user WHERE login='".$cgi->param("login")."' AND password='".md5_hex(scalar $cgi->param("pass"))."' AND confirmed='yes';");
  if ($dbh->err()) {
    warning_message($DBI::errstr);
    exit 0;
  }

  if ($res) {
    my $secret = secret();
    $uhash = md5_hex(scalar $cgi->param("login"));
    $user = $cgi->param("login");
    $dbh->do("UPDATE user SET cookie='".$secret."' WHERE login='$user';");
    $dbh->commit();
    if ($dbh->err()) {
      warning_message($DBI::errstr);
      exit 0;
    }
    $cookie = CGI::Cookie->new( -name    => SESSION_COOKIE_NAME,
				-value   => $uhash.";".$secret,
				-expires => SESSION_TIMEOUT );
  } else {
    login_screen({ "invalid" => 1 });
    exit 0;
  }
}

unless ($cgi->param('action')) {
  $dbh->disconnect();
  print $cgi->header();
  print base_template();
  print ALLOW_REGISTER_APPLICATION ? qq~
<div>
  <h3>Register Application</h3>
  <form>
    <input type="hidden" name="action" value="register_application">
    <label>application name</label>
    <input type="text" class="span6" placeholder="enter application name" name="application">
    <span class="help-block">Create a unique identifier for your application. Use alphanumerical characters only.</span>
    <label>application url</label>
    <input type="text" class="span6" placeholder="enter URL" name="url">
    <span class="help-block">Enter the full path to your application script that will handle the authentication.</span>
    <button type="submit" class="btn">register</button>
  </form>
</div>~ : '';
  if (ALLOW_REGISTER_USER) {
    print qq~
<div>
  <h3>Register User</h3>
  <form class="form-horizontal">
    <input type="hidden" name="action" value="register_user">
    <fieldset>
      <div class="control-group">
        <label class="control-label" for="user">Full User Name</label>
        <div class="controls">
          <input type="text" class="span3" placeholder="enter full name" name="username" id="user">
          <p class="help-block">Enter your full name as you would like it to be displayed.</p>
        </div>
      </div>
~;
    if (! EMAIL_IS_LOGIN) {
      print qq~
      <div class="control-group">
        <label class="control-label" for="login">Login</label>
        <div class="controls">
          <input type="text" class="span3" placeholder="enter login" name="login" id="login">
          <p class="help-block">Enter your desired login. Use alphanumerical characters only</p>
        </div>
      </div>
~;
    }
    print qq~
      <div class="control-group">
        <label class="control-label" for="email">eMail</label>
        <div class="controls">
          <input type="text" class="span3" placeholder="enter email" name="email" id="email">
          <p class="help-block">Enter a valid email address.</p>
        </div>
      </div>

      <div class="control-group">
        <label class="control-label" for="password">Password</label>
        <div class="controls">
          <input type="password" class="span3" placeholder="enter password" name="password" id="password">
          <p class="help-block">Enter your desired password.</p>
        </div>
      </div>

      <div class="control-group">
        <label class="control-label" for="password_two">Password Validation</label>
        <div class="controls">
          <input type="password" class="span3" placeholder="re-enter password" name="password_two" id="password_two">
          <p class="help-block">Enter your password again for validation</p>
        </div>
      </div>
    </fieldset>
    <button type="submit" class="btn">register</button>
  </form>
</div>~;
  }
  print close_template();
} else {
  if ($cgi->param("action") eq "register_application") {
    if ($cgi->param("application") && $cgi->param("url")) {
      my $res = $dbh->selectrow_arrayref("SELECT application FROM apps WHERE application ='".$cgi->param("application")."';");
      if ($dbh->err()) {
	warning_message($DBI::errstr);
	exit 0;
      }
      if ($res) {
	warning_message("This application is already registered.");
      } else {
	my $secret = secret();
	$dbh->do("INSERT INTO apps (application, url, secret) VALUES ('".$cgi->param("application")."', '".$cgi->param("url")."', '".$secret."');");
	$dbh->commit();
	if ($dbh->err()) {
	  warning_message($DBI::errstr);
	  exit 0;
	}
	success_message("Successfully registered application:<br><table style='text-align: left;'><tr><th style='padding-right: 10px;'>application name</th><td>".$cgi->param("application")."</td></tr><tr><th>application url</th><td>".$cgi->param("url")."</td></tr><tr><th>application secret</th><td>".$secret."</td></tr></table>");
	exit 0;
      }
    } else {
      warning_message("You must supply both an application name and a URL");
      exit 0;
    }
    
  } elsif ($cgi->param("action") eq "user_details") {
    if ($user) {
      my $res = $dbh->selectrow_arrayref("SELECT login, cookie, name, email FROM user WHERE login='".$user."';");
      if ($dbh->err()) {
	warning_message($DBI::errstr);
	exit 0;
      }
      if (! $res) {
	warning_message('User not found');
      }
      my $html = '<h3>Current User</h3><table><tr><td style="font-weight: bold; text-align: right;">full name</td><td style="text-align: left; padding-left: 15px;">'.$res->[2].'</td></tr><tr><td style="font-weight: bold; text-align: right;">login</td><td style="text-align: left; padding-left: 15px;">'.$res->[0].'</td></tr><tr><td style="font-weight: bold; text-align: right;">email</td><td style="text-align: left; padding-left: 15px;">'.$res->[3].'</td></tr><tr><td style="font-weight: bold; text-align: right;">token</td><td style="text-align: left; padding-left: 15px;">'.$res->[1].'</td></tr></table>';
      information_page($html);
    } else {
      warning_message('There is currently no user logged in');
    }
  } elsif ($cgi->param("action") eq "register_user") {
    my $claimuser;
    if ($cgi->param("token")) {
      my $res2 = $dbh->selectrow_arrayref("SELECT name FROM scope WHERE user='".$cgi->param("token")."';");
      if ($dbh->err()) {
	warning_message($DBI::errstr);
	exit 0;
      }
      $claimuser = $res2->[0];
      if ($cgi->param("email")) {
	# check if this email is registered, if so attach the token and say goodbye
	my $res = $dbh->selectrow_arrayref("SELECT login FROM user WHERE email='".$cgi->param("email")."';");
	if ($dbh->err()) {
	  warning_message($DBI::errstr);
	  exit 0;
	}
	if ($res) {
	  my $login = $res->[0];
	  $res = $res2;
	  if ($res) {
	    my $email = $res->[0];
	    $dbh->do("DELETE FROM scope WHERE user='".$cgi->param("token")."'");
	    $dbh->do("UPDATE rights SET scope='$login' WHERE scope='".$email."'");
	    $dbh->commit();
	    if ($dbh->err()) {
	      warning_message($DBI::errstr);
	      exit 0;
	    }
	  } else {
	    warning_message("token not found");
	    exit 0;
	  }
	  success_message("token claimed successfully");
	  exit 0;
	}
      }
    }
    if ($cgi->param("username") && (EMAIL_IS_LOGIN || $cgi->param("login")) && $cgi->param("password") && $cgi->param("password_two") && $cgi->param("email")) {
      if ($cgi->param("password") eq $cgi->param("password_two")) {
	if (! EMAIL_IS_LOGIN) {
	  my $res = $dbh->selectrow_arrayref("SELECT login FROM user WHERE login='".$cgi->param("login")."';");
	  if ($dbh->err()) {
	    warning_message($DBI::errstr);
	    exit 0;
	  }
	  if ($res) {
	    warning_message("This login is already taken.");
	    exit 0;
	  }
	}
	my $res = $dbh->selectrow_arrayref("SELECT email FROM user WHERE email='".$cgi->param("email")."';");
	if ($dbh->err()) {
	  warning_message($DBI::errstr);
	  exit 0;
	}
	if ($res) {
	  warning_message("This email is already taken.");
	  exit 0;
	}
	  
	my $secret = secret();
	my $pass = md5_hex(scalar $cgi->param("password"));
	$dbh->do("INSERT INTO user (login, name, password, email, confirmed) VALUES ('".(EMAIL_IS_LOGIN ? $cgi->param('email') : $cgi->param("login"))."', '".$cgi->param("username")."', '".$pass."', '".$cgi->param("email")."', '".$secret."');");

	if ($claimuser) {
	  $dbh->do("DELETE FROM scope WHERE user='".$cgi->param("token")."'");
	  $dbh->do("UPDATE rights SET scope='".(EMAIL_IS_LOGIN ? $cgi->param('email') : $cgi->param("login"))."' WHERE scope='".$claimuser."'");
	}
	
	$dbh->do("INSERT INTO scope (name, user) VALUES ('".(EMAIL_IS_LOGIN ? $cgi->param('email') : $cgi->param("login"))."', '".(EMAIL_IS_LOGIN ? $cgi->param('email') : $cgi->param("login"))."');");
	$dbh->commit();
	if ($dbh->err()) {
	  warning_message($DBI::errstr);
	  exit 0;
	}
		
	my $email = $cgi->param("email");
	if (sendmail({ from    => ADMIN_EMAIL,
		       to      => $email,
		       subject => EMAIL_REG_SUBJECT,
		       body => "Dear ".$cgi->param("username").",\n".EMAIL_REG_PREFIX.BASE_URL."/cgi-bin/oAuth.cgi?action=verify&login=".(EMAIL_IS_LOGIN ? $cgi->param('email') : $cgi->param("login"))."&id=$secret".EMAIL_REG_SUFFIX})) {
	  success_message("Your account is registered. You will receive a confirmation message to the entered email address. Your account will be inactive until you click the verification link in that email.");
	} else {
	  warning_message("Could not send out verification email: $@");
	  exit 0;
	}
	
      } else {
	warning_message("Password and password verification do not match.");
	exit 0;
      }
    } else {
      warning_message("You must fill out all fields to register");
      exit 0;
    }
  } elsif ($cgi->param("action") eq "verify") {
    $cgi->param("login");
    $cgi->param("id");
    my $res = $dbh->selectrow_arrayref("SELECT login FROM user WHERE login='".$cgi->param("login")."' AND confirmed='".$cgi->param('id')."';");
    if ($dbh->err()) {
      warning_message($DBI::errstr);
      exit 0;
    }
    if ($res) {
      $dbh->do("UPDATE user SET confirmed='yes' WHERE login='".$cgi->param('login')."'");
      $dbh->commit();
      if ($dbh->err()) {
	warning_message($DBI::errstr);
	exit 0;
      }
      success_message("Your account is verified.");
    } else {
      warning_message("Invalid id for this login.");
    }
  } elsif ($cgi->param("action") eq "dialog") {
      if ($cgi->param("client_id") && $cgi->param("redirect_url")) {
	my $res = $dbh->selectrow_arrayref("SELECT application FROM apps WHERE application='".$cgi->param("client_id")."' AND url='".$cgi->param('redirect_url')."';");
	if ($dbh->err()) {
	  warning_message($DBI::errstr);
	  exit 0;
	}
	if ($res) {
	  if ($user) {
	    $res = $dbh->selectrow_arrayref("SELECT token FROM accepts WHERE application='".$cgi->param("client_id")."' AND login='".$user."';");
	    my $secret = secret();
	    if ($res) {
	      $secret = $res->[0];
	    } else {
	      if (TRUSTED && $cgi->param("client_id") eq TRUSTED) {
		$cgi->param("accept", "1");
	      }
	      if (defined($cgi->param("accept"))) {
		if ($cgi->param('accept') eq '1') {
		  $res = $dbh->do("INSERT INTO accepts (login, application, token) VALUES ('".$user."','".$cgi->param('client_id')."','".$secret."');");
		  $dbh->commit();
		  if ($dbh->err()) {
		    warning_message($DBI::errstr);
		    exit 0;
		  }
		} else {
		  warning_message("You denied the application ".$cgi->param('client_id')." to access your data.");
		  exit 0;
		}
	      } else {
		auth_client_screen();
		exit 0;
	      }
	    }

	    my $url = $cgi->param("redirect_url");
	    if ($url =~ /\?/) {
	      $url .= "&";
	    } else {
	      $url .= "?";
	    }
	    print $cgi->redirect( -uri => $url."code=".$secret );
	    exit 0;				

	  } else {
	    login_screen();
	    exit 0;
	  }
	} else {
	  respond('{ "ERROR": "redirect_url '. $cgi->param('redirect_url') . ' does not match client id '.$cgi->param("client_id").'" }', 400);
	}
      }
    } elsif ($cgi->param("action") eq "token") {
      if ($cgi->param("client_id") && $cgi->param("client_secret") && $cgi->param("code")) {
	my $res = $dbh->selectrow_arrayref("SELECT accepts.login FROM apps, accepts WHERE apps.application='".$cgi->param("client_id")."' AND apps.secret='".$cgi->param('client_secret')."' AND apps.application=accepts.application and accepts.token='".$cgi->param('code')."';");
	if ($dbh->err()) {
	  respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	}
	if ($res) {
	  $user = $res->[0];
	  $uhash = md5_hex($user);
	} else {
	  respond('{ "ERROR": "Invalid code" }', 400);
	}
	$dbh->do('DELETE FROM tokens WHERE login="'.$user.'"');
	$dbh->commit();
	if ($dbh->err()) {
	  respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	}
	my $secret = secret();
	$res = $dbh->selectrow_arrayref("SELECT token FROM tokens WHERE token='$secret';");
	if ($dbh->err()) {
	  respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	}
	while ($res) {
	  $secret = secret();
	  $res = $dbh->selectrow_arrayref("SELECT token FROM tokens WHERE token='$secret';");
	  if ($dbh->err()) {
	    respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	  }
	}
	$dbh->do("INSERT INTO tokens (token, login, created) values ('$secret', '$user', ".time.");");
	$dbh->commit();
	if ($dbh->err()) {
	  respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	}
	respond('{ "token": "'.$secret.'" }');
      } else {
	respond('{ "ERROR": "missing parameter" }', 400);
      }
    } elsif ($cgi->param("action") eq "data") {
      if ($cgi->http('HTTP_AUTH') && ! $cgi->param("access_token")) {
	$cgi->param("access_token", $cgi->http('HTTP_AUTH'));
      }
      if ($cgi->param("access_token")) {
	my $res = $dbh->selectrow_arrayref("SELECT user.login, user.name, user.email, user.admin, tokens.token FROM user, tokens WHERE tokens.token='".$cgi->param('access_token')."' AND user.login=tokens.login;");
	if ($dbh->err()) {
	  respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	}
	if ($res) {
	  if ($cgi->param('refresh')) {
	    my $secret = secret();
	    my $res2 = $dbh->selectrow_arrayref("SELECT token FROM tokens WHERE token='$secret';");
	    if ($dbh->err()) {
	      respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	    }
	    while ($res2) {
	      $secret = secret();
	      $res2 = $dbh->selectrow_arrayref("SELECT token FROM tokens WHERE token='$secret';");
	      if ($dbh->err()) {
		respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	      }
	    }
	    $dbh->do("UPDATE tokens SET token='$secret' WHERE token='".$res->[3]."';");
	    $res->[3] = $secret;
	    $dbh->do("UPDATE tokens SET created=".time." WHERE token='$secret';");
	    $dbh->commit();
	    if ($dbh->err()) {
	      respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	    }
	  }
	  $dbh->disconnect();
	  respond('{ "login": "'.$res->[0].'", "name": "'.$res->[1].'", "email": "'.$res->[2].'", "admin": '.($res->[3] ? "true" : "false").', "token": "'.$res->[4].'" }');
	  exit 0;
	} else {
	  respond('{ "ERROR": "invalid access token" }', 401);
	}
      } else {
	respond('{ "ERROR": "missing access token" }', 400);
      }
    } elsif ($cgi->param('action') eq 'users') {
      unless ($cgi->http('HTTP_AUTH')) {
	respond('{ "ERROR": "missing authentication" }', 400);
      }
      my $login = $dbh->selectrow_arrayref("SELECT login FROM tokens WHERE token='".$cgi->http('HTTP_AUTH')."'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      if ($login) {
	$login = $login->[0];
      } else {
	respond('{ "ERROR": "invalid access token" }', 401);
      }

      my $admin = 0;
      my $res = $dbh->selectrow_arrayref("SELECT admin FROM user WHERE login='$login'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      } else {
	if ($res->[0]) {
	  $admin = 1;
	}
      }

      unless ($admin) {
	respond('{ "ERROR": "insufficient permissions" }', 401);
      }

      $res = $dbh->selectall_arrayref("SELECT user.login, user.name, user.email, user.admin, user.confirmed, user.date FROM user;");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      if ($res) {
	my $retval = '{"ERROR": false, "columns": ["login","name","email","admin","confirmed","date"], "data": [';
	my $rows = [];
	foreach my $row (@$res) {
	  $row->[3] = $row->[3] || 0;
	  push(@$rows, '["'.join('","', @$row).'"]');
	}
	$retval .= join(',', @$rows);
	$retval .= '] }';
	respond($retval)
      } else {
	respond('{ "ERROR": "could not get user list" }', 500);
      }
      
    } elsif ($cgi->param('action') eq 'impersonate') {

      unless ($cgi->http('HTTP_AUTH')) {
	respond('{ "ERROR": "missing authentication" }', 400);
      }
      my $login = $dbh->selectrow_arrayref("SELECT login FROM tokens WHERE token='".$cgi->http('HTTP_AUTH')."'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      if ($login) {
	$login = $login->[0];
      } else {
	respond('{ "ERROR": "invalid access token" }', 401);
      }

      my $admin = 0;
      my $res = $dbh->selectrow_arrayref("SELECT admin FROM user WHERE login='$login'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      } else {
	if ($res->[0]) {
	  $admin = 1;
	}
      }

      unless ($admin) {
	respond('{ "ERROR": "insufficient permissions" }', 401);
      }

      unless ($cgi->param('login')) {
	respond('{ "ERROR": "missing login" }', 400);
      }

      my $token = $dbh->selectrow_arrayref("SELECT token FROM tokens WHERE login='".$cgi->param('login')."'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      my $user = $dbh->selectrow_arrayref("SELECT login, name, email, admin FROM user WHERE login='".$cgi->param('login')."'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      if ($token && $user) {
	$token = $token->[0];
	respond('{ "ERROR": false, "data": { "login": "'.$user->[0].'", "name": "'.$user->[1].'", "email": "'.$user->[2].'", "admin": '.($user->[3] ? "1" : "0").', "token": "'.$token.'" } }');
      } else {
	respond('{ "ERROR": "invalid login" }', 401);
      }
      
    } elsif ($cgi->param('action') eq 'reconfirm') {
      
      unless ($cgi->http('HTTP_AUTH')) {
	respond('{ "ERROR": "missing authentication" }', 400);
      }
      my $login = $dbh->selectrow_arrayref("SELECT login FROM tokens WHERE token='".$cgi->http('HTTP_AUTH')."'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      if ($login) {
	$login = $login->[0];
      } else {
	respond('{ "ERROR": "invalid access token" }', 401);
      }
      
      my $admin = 0;
      my $res = $dbh->selectrow_arrayref("SELECT admin FROM user WHERE login='$login'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      } else {
	if ($res->[0]) {
	  $admin = 1;
	}
      }
      
      unless ($admin) {
	respond('{ "ERROR": "insufficient permissions" }', 401);
      }
      
      unless ($cgi->param('login')) {
	respond('{ "ERROR": "missing login" }', 400);
      }
      
      my $user = $dbh->selectrow_arrayref("SELECT login, name, email, confirmed FROM user WHERE login='".$cgi->param('login')."'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }

      if (! $user) {
	respond('{ "ERROR": "user not found" }', 404);
      }

      if ($user->[3] eq 'yes') {
	respond('{ "ERROR": "user is already confirmed" }', 400);
      }
      
      if (sendmail({ from    => ADMIN_EMAIL,
		     to      => $user->[2],
		     subject => EMAIL_REG_SUBJECT,
		     body => "Dear ".$user->[1].",\n".EMAIL_REG_PREFIX.BASE_URL."/cgi-bin/oAuth.cgi?action=verify&login=".(EMAIL_IS_LOGIN ? $user->[2] : $user->[0])."&id=".$user->[3].EMAIL_REG_SUFFIX})) {
	respond('{ "ERROR": null, "message": "confirmation message resent to '.$user->[1].' ('.(EMAIL_IS_LOGIN ? $user->[2] : $user->[0]).')" }', 200);
      } else {
	respond('{ "ERROR": "could not resend confirmation message" }', 500);
      }
      
    } elsif ($cgi->param('action') eq 'rights') {
      unless ($cgi->http('HTTP_AUTH')) {
	respond('{ "ERROR": "missing authentication" }', 400);
      }
      my $login = $dbh->selectrow_arrayref("SELECT login FROM tokens WHERE token='".$cgi->http('HTTP_AUTH')."'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      if ($login) {
	$login = $login->[0];
      } else {
	respond('{ "ERROR": "invalid access token" }', 401);
      }

      my $admin = 0;
      my $res = $dbh->selectrow_arrayref("SELECT admin FROM user WHERE login='$login'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      } else {
	if ($res->[0]) {
	  $admin = 1;
	}
      }
      
      my $scopes = $dbh->selectall_arrayref("SELECT name FROM scope WHERE user='".$login."'");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      unless (ref $scopes && scalar(@$scopes)) {
	respond('{ "ERROR": "user has no rights" }', 404);
      }
      my $rights = $dbh->selectall_arrayref("SELECT type, item, edit, view, owner, scope FROM rights WHERE ".($admin ? "1" : "scope IN ('".join("','", map { $_->[0] } @$scopes)."')").($cgi->param('type') ? " AND type='".$cgi->param('type')."'" : "").($cgi->param('item') ? " AND item='".$cgi->param('item')."'" : ""));
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      my $rightscopes = {};
      foreach my $r (@$rights) {
	$rightscopes->{$r->[5]} = 1;
      }
      my $scopeusers = $dbh->selectall_arrayref("SELECT user.name, user.email, scope.name FROM scope JOIN user ON scope.user=user.login WHERE scope.name IN ('".join("','", keys(%$rightscopes))."')");
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      my $scopeuserhash = {};
      foreach my $scopeuser (@$scopeusers) {
	unless (exists $scopeuserhash->{$scopeuser->[2]}) {
	  $scopeuserhash->{$scopeuser->[2]} = [];
	}
	push(@{$scopeuserhash->{$scopeuser->[2]}}, '[ "'.$scopeuser->[0].'", "'.$scopeuser->[1].'" ]');
      }
      foreach my $k (keys(%$scopeuserhash)) {
	$scopeuserhash->{$k} = '[ '.join(',', @{$scopeuserhash->{$k}}).' ]';
      }
      
      my $response = '{ "ERROR": false, "columns": [ "type", "item", "edit", "view", "owner", "users" ], "data": [';
      my $rs = [];
      foreach my $row (@$rights) {
	push(@$rs, '[ "'.$row->[0].'", "'.$row->[1].'", '.($row->[2] ? 'true' : 'false').', '.($row->[3] ? 'true' : 'false').', '.($row->[4] ? 'true' : 'false').', '.$scopeuserhash->{$row->[5]}.']');
      }
      $response .= join(",", @$rs).' ] }';
      respond($response);
      
    } elsif ($cgi->param('action') eq 'modrights') {
      unless ($cgi->http('HTTP_AUTH')) {
	respond('{ "ERROR": "missing authentication" }', 400);
      }
      my $login = $dbh->selectrow_arrayref("SELECT login, token FROM tokens WHERE token='".$cgi->http('HTTP_AUTH')."'");
      my $admin = 0;
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      if ($login) {
	$login = $login->[0];
	$admin = $dbh->selectrow_arrayref("SELECT admin FROM user WHERE login='".$login."'")->[0];
      } else {
	respond('{ "ERROR": "invalid access token" }', 401);
      }
      my $existing_user = 0;
      if ($cgi->param('scope')) {
	my $response = $dbh->selectrow_arrayref("SELECT email FROM user, scope WHERE scope='".$cgi->param('scope')."' AND user.login=scope.user");
	if ($dbh->err()) {
	  respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	}
	if (ref ($response) && scalar(@$response)) {
	  $cgi->param('email', $response->[0]);
	  $existing_user = 1;
	} else {
	  respond('{ "ERROR": "target scope not found" }', 401);
	}
      } elsif ($cgi->param('email')) {
	my $response = $dbh->selectrow_arrayref("SELECT login FROM user WHERE email='".$cgi->param('email')."'");
	if ($dbh->err()) {
	  respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	}
	if (ref $response && scalar(@$response)) {
	  $cgi->param('scope', $response->[0]);
	  $existing_user = 1;
	} else {
	  my $token = secret();
	  $dbh->do("INSERT INTO scope (name, user) VALUES ('".$cgi->param('email')."', '$token')");
	  $dbh->commit();
	  if ($dbh->err()) {
	    respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	  }
	  my $body = EMAIL_SHARE_UNKNOWN_SUFFIX;
	  my $dynamic = $cgi->param('dynamic') || '';
	  $body =~ s/DYNAMIC/$dynamic/;
	  sendmail({ from    => ADMIN_EMAIL,
		     to      => $cgi->param("email"),
		     subject => EMAIL_SHARE_SUBJECT,
		     body    => EMAIL_SHARE_UNKNOWN_PREFIX.BASE_URL."/cgi-bin/oAuth.cgi?action=claim&token=".$token.$body
		   });
	  $cgi->param('scope', $cgi->param('email'));
	}
      } else {
	respond('{ "ERROR": "missing target identification" }', 400);
      }
      if ($cgi->param('type') && $cgi->param('item') && ($cgi->param('add') || $cgi->param('del'))) {
	if (! $admin) {
	  my $scopes = $dbh->selectall_arrayref("SELECT name FROM scope WHERE user='".$login."'");
	  if ($dbh->err()) {
	    respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	  }
	  unless (ref $scopes && scalar(@$scopes)) {
	    respond('{ "ERROR": false, "data": [] }', 404);
	  }
	  foreach my $item ($cgi->param('item')) {
	    my $response = $dbh->selectrow_arrayref("SELECT item FROM rights WHERE type='".$cgi->param('type')."' AND item='".$item."' AND owner=1 AND scope IN ('".join("','", map { $_->[0] } @$scopes)."')");
	    if ($dbh->err()) {
	      respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	    }
	    unless (ref $response) {
	      respond('{ "ERROR": "insufficient permissions" }', 401);
	    }
	  }
	}
	foreach my $item ($cgi->param('item')) {
	  $dbh->do("DELETE FROM rights WHERE type='".$cgi->param('type')."' AND item='".$item."' AND scope='".$cgi->param('scope')."'");
	  $dbh->commit();
	  if ($dbh->err()) {
	    respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	  }
	  if ($cgi->param('add')) {
	    $dbh->do("INSERT INTO rights (type, item, edit, view, scope, owner) VALUES ('".$cgi->param('type')."', '".$item."', ".($cgi->param('edit') || 0).", ".($cgi->param('view') || 0).", '".$cgi->param('scope')."', ".($cgi->param('owner') || 0)." )");
	    $dbh->commit();
	    if ($dbh->err()) {
	      respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	    }
	  }
	}
	if ($cgi->param('add')) {
	  if ($existing_user) {
	    my $body = EMAIL_SHARE_KNOWN;
	    my $dynamic = $cgi->param('dynamic') || '';
	    $body =~ s/DYNAMIC/$dynamic/;
	    sendmail({ from    => ADMIN_EMAIL,
		       to      => scalar $cgi->param('email'),
		       subject => EMAIL_SHARE_SUBJECT,
		       body    => $body
		     });
	  }
	  respond('{ "ERROR": false, "data": "permission added" }');
	} else {
	  respond('{ "ERROR": false, "data": "permission removed" }');
	}
      } else {
	respond('{ "ERROR": "missing parameter" }', 400);
      }
    } elsif ($cgi->param('action') eq 'modscope') {
      unless ($cgi->http('HTTP_AUTH')) {
	respond('{ "ERROR": "missing authentication" }', 400);
      }
      my $login = $dbh->selectrow_arrayref("SELECT login FROM tokens WHERE token='".$cgi->http('HTTP_AUTH')."'");
      my $admin = 0;
      if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
      }
      if ($login) {
	$login = $login->[0];
	$admin = $dbh->selectrow_arrayref("SELECT admin FROM user WHERE login='".$login."'")->[0];
      } else {
	respond('{ "ERROR": "invalid access token" }', 401);
      }
      unless ($cgi->param('name') && $cgi->param('user')) {
	respond('{ "ERROR": "missing parameter" }', 400);
      }
      if ($cgi->param('del')) {
	unless ($admin || ($cgi->param('user') eq $login)) {
	  respond('{ "ERROR": "insufficient permissions" }', 401);
	}
	if ($cgi->param('name') eq $cgi->param('user')) {
	  respond('{ "ERROR": "cannot remove personal user scope" }', 400);
	}
	$dbh->do("DELETE FROM scope WHERE name='".$cgi->param('name')."' AND user='".$cgi->param('user')."'");
	$dbh->commit();
	if ($dbh->err()) {
	  respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	} else {
	  respond('{ "ERROR": false, "data": "scope removed" }');
	}
      } else {
	my $res = $dbh->selectrow_arrayref("SELECT name FROM scope WHERE name='".$cgi->param('name')."' AND user='".$cgi->param('user')."'");
	if ($dbh->err()) {
	  respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	}
	if ($res) {
	  respond('{ "ERROR": "scope already exists" }', 400);
	} else {
	  $dbh->do("INSERT INTO scope (name, user) VALUES ('".$cgi->param('name')."', '".$cgi->param('user')."')");
	  $dbh->commit();
	  if ($dbh->err()) {
	    respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
	  } else {
	    respond('{ "ERROR": false, "data": "scope added" }');
	  }
	}
      }
    } elsif ($cgi->param('action') eq 'claim') {
      my $token = $cgi->param('token');
      unless ($token) {
	warning_message("No token was detected in a claim token request");
	exit 0;
      }
      
      claim_token_screen($token);
      exit 0;
    } else {
      respond('{ "ERROR": "Authentication page called with an invalid action parameter - '.$cgi->param('action').'" }', 400);
    }
}

sub base_template {
    return qq~<!DOCTYPE html>
<html>

  <head>

    <title>Authentication</title>

    <script type="text/javascript" src="~ . JS_DIR . qq~jquery.min.js"></script>
    <script type="text/javascript" src="~ . JS_DIR . qq~bootstrap.min.js"></script>

    <link rel="icon" href="~. IMAGE_DIR .qq~logo.ico" type="image/x-icon">

    <link rel="stylesheet" type="text/css" href="~ . CSS_DIR . qq~bootstrap.min.css">
    <link rel="stylesheet" type="text/css" href="~ . CSS_DIR . qq~bootstrap-responsive.min.css">
    <link rel="stylesheet" type="text/css" href="~ . CSS_DIR . qq~application.css">

  </head>

  <body>
    
    <div class="header">

      <div style="width: 235px; float: left; margin-right: 25px;">
        <img src="~. IMAGE_DIR .qq~logo.png" style="float: left; height: 59px; margin-top: 3px; cursor: pointer;">
      </div>

      <div style="float: left; color: white; font-weight: lighter; position: relative; top: 15px; font-size: 40px;" id="pageTitle">~. APPLICATION_NAME .qq~</div>
	  
    </div>

    <div style="height: 80px;" class="visible-desktop"></div>
    <div style="height: 120px;" class="hidden-desktop"></div>
    
    <div class="row-fluid">
      
      <!-- main content -->
      <div id="content" class="span10 offset1">
~;
}

sub close_template {
    return qq~
      </div>

    </div>
    
    <div style="height: 100px;"></div>

  </body>
</html>~;
}

sub information_page {
  my ($page) = @_;

  $dbh->disconnect();
    print $cgi->header();
    print base_template();
    print $page;
    print close_template(); 
}

sub warning_message {
    my ($message) = @_;

    $dbh->disconnect();
    print $cgi->header();
    print base_template();
    print qq~<div class="alert alert-error">
<button class="close" data-dismiss="alert" type="button">x</button>~;
    print $message;
    print qq~<br><a href="oAuth.cgi">return to registration</a><a href="~.APPLICATION_URL.qq~" style="float: right;">return to application</a></div>~;
    print close_template();    
}

sub success_message {
    my ($message) = @_;

    $dbh->disconnect();
    print $cgi->header();
    print base_template();
    print qq~<div class="alert alert-success">
<button class="close" data-dismiss="alert" type="button">x</button>~;
    print $message;
    print qq~<br><a href="oAuth.cgi">return to registration</a><a href="~.APPLICATION_URL.qq~" style="margin-left: 50px;">return to application</a></div>~;
    print close_template();
}

sub login_screen {
  my ($params) = @_;
  
  my $message = "";
  if ($params->{invalid}) {
    $message = qq~<div class="alert alert-error">
<button class="close" data-dismiss="alert" type="button">x</button>Your login failed.</div>~;
  }
  
  my @pa = $cgi->param;
  my $hidden = "";
  foreach my $p (@pa) {
    next if ($p eq "login");
    next if ($p eq "pass");
    $hidden .= "<input type='hidden' name='".$p."' value='".$cgi->param($p)."'>";
  }
  
  print $cgi->header();
  print base_template();
  print qq~
<div>
  <h3>Login</h3>
  <form method=post>
    $hidden$message
    <label>~.(EMAIL_IS_LOGIN ? 'email' : 'login').qq~</label>
    <input type="text" placeholder="enter ~.(EMAIL_IS_LOGIN ? 'email' : 'login').qq~" name="login">
    <label>password</label>
    <div class="input-append"><input type="password" placeholder="enter password" name="pass">
    <button type="submit" class="btn">login</button></div>
  </form>
</div>~;
  print close_template();
  
  $dbh->disconnect();
}

sub auth_client_screen {
  my @pa = $cgi->param;
  my $hidden = "<input type='hidden' name='accept' id='accept_app'>";
  foreach my $p (@pa) {
    next if ($p eq "login");
    next if ($p eq "pass");
    $hidden .= "<input type='hidden' name='".$p."' value='".$cgi->param($p)."'>";
  }
  
  my $application = $cgi->param("client_id");
  print $cgi->header(-cookie=>$cookie);
  print base_template();
  print qq~
  <div>
    <h3>application authorization</h3>
    <p>The $application is requesting to verify your login, name and email address. Is that OK?</p>
    <form>
      $hidden
      <input type="button" value="deny" class="btn" onclick="document.getElementById('accept_app').value='0';document.forms[0].submit();"><input type="button" class="btn" value="accept" onclick="document.getElementById('accept_app').value='1';document.forms[0].submit();">
    </form>
  </div>~;
  print close_template();

  $dbh->disconnect();
}

sub claim_token_screen {
  my ($token) = @_;
  
  print $cgi->header(-cookie=>$cookie);
  print base_template();
  print qq~
  <div>
    <h3>claim token</h3>
    <p>A user of ~.APPLICATION_NAME.qq~ wants to share data with you. Please enter registration information into the form below to create an account and claim the data. If you already have an account, you only need to put in the email address associated with it.</p>
    <div>
      <h3>Register User</h3>
      <form class="form-horizontal">
        <input type="hidden" name="action" value="register_user">
        <input type="hidden" name="token" value="~.$token.qq~">
        <fieldset>
          <div class="control-group">
            <label class="control-label" for="user">Full User Name</label>
            <div class="controls">
              <input type="text" class="span3" placeholder="enter full name" name="username" id="user">
              <p class="help-block">Enter your full name as you would like it to be displayed.</p>
            </div>
          </div>
~.(EMAIL_IS_LOGIN ? '' : qq~
          <div class="control-group">
            <label class="control-label" for="login">Login</label>
            <div class="controls">
              <input type="text" class="span3" placeholder="enter login" name="login" id="login">
              <p class="help-block">Enter your desired login. Use alphanumerical characters only</p>
            </div>
          </div>
~).qq~
          <div class="control-group">
            <label class="control-label" for="email">eMail</label>
            <div class="controls">
              <input type="text" class="span3" placeholder="enter email" name="email" id="email">
              <p class="help-block">Enter a valid email address.</p>
            </div>
          </div>

          <div class="control-group">
            <label class="control-label" for="password">Password</label>
            <div class="controls">
              <input type="password" class="span3" placeholder="enter password" name="password" id="password">
              <p class="help-block">Enter your desired password.</p>
            </div>
          </div>

          <div class="control-group">
            <label class="control-label" for="password_two">Password Validation</label>
            <div class="controls">
              <input type="password" class="span3" placeholder="re-enter password" name="password_two" id="password_two">
              <p class="help-block">Enter your password again for validation</p>
            </div>
          </div>
        </fieldset>
        <button type="submit" class="btn">register</button>
      </form>
    </div>
  </div>~;
  print close_template();

  $dbh->disconnect();
}

sub secret {
    my $generated = "";
    my $possible = 'abcdefghijkmnpqrstuvwxyz123456789ABCDEFGHJKLMNPQRSTUVWXYZ';
    while (length($generated) < 32) {
	$generated .= substr($possible, (int(rand(length($possible)))), 1);
    }
    return $generated;
  }

sub dbh {
  my $connection = DBI->connect(DBI_CONNECT, DBI_USER, DBI_PASS, {AutoCommit => 0, PrintError => 1});
  unless ($connection) {
    die "could not open database: $@";
  }
  return $connection;
}

sub quote {
  my ($text) = @_;
  
  my $clean_text = $text;
  if(defined $text && !looks_like_number($text)) {
    my $hs = HTML::Strip->new();
    my $clean_text = $hs->parse($text);
    $clean_text =~ s/\n//g;
    $hs->eof;
  }

  return $dbh->quote($clean_text);
}

sub respond {
  my ($data, $code) = @_;

  $code = $code || 200;
  
  $dbh->disconnect();
  print $cgi->header(-type => 'application/json',
		     -status => $code,
		     -charset => 'UTF-8',
		     -Content_Length => length $data,
		     -Access_Control_Allow_Origin => '*' );
  print $data;
  exit 0;
}

sub sendmail {
  my ($params) = @_;

  my $smtp_host = SMTP;
  
  my $from = $params->{'from'};
  my $to = $params->{'to'};
  
  my $subject = $params->{'subject'};
  my $body = $params->{'body'};
    
  my $smtp = Net::SMTP->new($smtp_host, Hello => $smtp_host);
    
  unless (defined $smtp) {
    respond('{ "ERROR": "could not connect to SMTP host" }', 500);
  }
  
  my @data = (
	      "To: $to\n",
	      "From: $from\n",
	      "Date: ".strftime("%a, %d %b %Y %H:%M:%S %z", localtime)."\n",
	      "Subject: $subject\n",
	      "Content-Type: text/html\n\n",
	      $body
	     );
  
  $smtp->mail('mg-rast');
  if ($smtp->to($to)) {
    $smtp->data(@data);
  } 
  $smtp->quit;

  return 1;
}
