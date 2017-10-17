#!/usr/bin/perl

use strict;
use warnings;

use Data::Dumper;

use CGI;
use CGI::Cookie;
use JSON;
use LWP::UserAgent;
use URI::Escape;

# Should have own config
use OAuthConfig;

my $json = new JSON;
my $cgi = new CGI();

my $settings = { app_id => APPLICATION_NAME,
		 app_secret => APP_SECRET,
		 dialog_url => BASE_URL.'/cgi-bin/oAuth.cgi?action=dialog',
		 token_url => 'http://localhost/cgi-bin/oAuth.cgi?action=token',
		 data_url => 'http://localhost/cgi-bin/oAuth.cgi?action=data' };

my $app_id = $settings->{app_id};
my $app_secret = $settings->{app_secret};
my $dialog_url = $settings->{dialog_url};
my $token_url = $settings->{token_url};
my $data_url = $settings->{data_url};


print STDERR "CLIENT CGI\n"; 

my $my_url = BASE_URL."/cgi-bin/client.cgi";

my $code = $cgi->param('code');

unless (defined($code)) {
    my $call_url = $dialog_url."&client_id=" . $app_id . "&redirect_url=" . uri_escape($my_url);
    print $cgi->redirect( -uri => $call_url );
    exit 0;
}

my $call_url = $token_url . "&client_id=" . $app_id . "&client_secret=" . $app_secret . "&code=" . $code;
my $ua = LWP::UserAgent->new;
my $response = $json->decode($ua->get($call_url)->content);
my $access_token = $response->{token};
$call_url = $data_url . "&access_token=" . $access_token;
$response = $ua->get($call_url)->content;
my $cookie = CGI::Cookie->new( -name    => 'AuthWebSession',
			       -value   => $response,
			       -expires => '+2d' );

print $cgi->redirect(-uri => APPLICATION_URL, -cookie => $cookie);

exit 0;
