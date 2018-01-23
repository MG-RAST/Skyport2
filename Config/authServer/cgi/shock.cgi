#!/usr/bin/perl
use strict;
use warnings;

use Data::Dumper;

use DBI;
use CGI;
use JSON;
use LWP::UserAgent;

use OAuthConfig;

my $cgi = new CGI;
$CGI::LIST_CONTEXT_WARN = 0;

# get request method
$ENV{'REQUEST_METHOD'} =~ tr/a-z/A-Z/;
my $request_method = $ENV{'REQUEST_METHOD'};

if (lc($request_method) eq 'options') {
  print $cgi->header(-Access_Control_Allow_Origin => '*',
		     -status => 200,
		     -type => 'text/plain',
		     -charset => 'UTF-8',
		     -Access_Control_Allow_Methods => 'POST, GET, OPTIONS, PUT, DELETE',
		     -Access_Control_Allow_Headers => 'AUTH, AUTHORIZATION, CONTENT-TYPE'
		    );
  print "";
  exit 0;
}

my $agent = LWP::UserAgent->new;
$agent->timeout(600);
my $json = JSON->new();
$json->max_size(0);
my $dbh = dbh();
my @args = (('Authorization', SHOCK_AUTH));
my $url = SHOCK_URL;

my ($su, $perm) = auth();
unless ($su) {
  $cgi->param('type', 'run-folder-archive-fastq');
  my $project_id = $cgi->param('project_id') || "";
  my $group = $cgi->param('group') || "";
  my $project = $cgi->param('project') || "";
  my $filename = $cgi->param('name') || "";
  my $u = $cgi->url(-query=>1);
  if ($u =~ /download/) {
    if ($request_method eq 'GET') {
      my $nodeid = $cgi->url(-relative=>1);
      eval {
	my $response = $json->decode($agent->get($url.$nodeid, @args)->content);
	$project_id = $response->{data}->{attributes}->{project_id};
	$group = $response->{data}->{attributes}->{group};
	$project = $response->{data}->{attributes}->{project};
	$filename = $response->{data}->{attributes}->{name};
      };
      if ($@) {
	respond('{ "ERROR": "unable to retrieve node from server ('.$@.')" }', 404);
      }
    } elsif ($request_method eq 'POST') {
      my $params = {};
      my $sharelist = [];
      foreach my $p ($cgi->param) {
	if ($p eq 'sharenames') {
	  foreach my $sharename ($cgi->param('sharenames')) {
	    push(@$sharelist, $sharename);
	  }
	} else {
	  $params->{$p} = $cgi->param($p);
	}
      }
      foreach my $fn (@$sharelist) {
	my $hasPermission = 0;
	my ($pid, $project, $group, $file) = split /\|/, $fn;
	foreach my $right (@$perm) {
	  if (($right->{item} eq "$pid|$file" && $right->{type} eq 'file') || ($right->{item} eq "$pid|$project" && $right->{type} eq 'project') || ($right->{item} eq "$pid|$group" && $right->{type} eq 'group')) {
	    $hasPermission = 1;
	    last;
	  }
	}
	if (! $hasPermission) {
	  respond('{ "ERROR": "insufficient permissions" }', 401);
	}
      }
      push(@args, ('Content-Type', "multipart/form-data"));
      respond($agent->post($url, @args, Content => $params)->content);
    }
  } elsif (! $cgi->param('project_id')) {
    respond('{ "ERROR": "missing run folder" }', 400);
  }
  
  my $can = 0;
  foreach my $r (@$perm) {
    if ($r->{type} eq 'project') {
      my ($project_idR, $projectR) = split /\|/, $r->{item};
      if ($project_idR eq $project_id && $projectR eq $project) {
	$can = 1;
	last;
      }
    } elsif ($r->{type} eq 'group') {
      my ($project_idR, $groupR) = split /\|/, $r->{item};
      if ($project_idR eq $project_id && $groupR eq $group) {
	$can = 1;
	last;
      }
    } else {
      my ($project_idR, $filenameR) = split /\|/, $r->{item};
      if ($project_idR eq $project_id && $filenameR eq $filename) {
	$can = 1;
	last;
      }
    }
  }
  
  unless ($can) {
    respond('{ "ERROR": "insufficient permissions" }', 401);
  }
}

my $response;
if ($request_method eq 'GET') {
  $url .= $cgi->url(-relative=>1, -query=>1);
  $url =~ s/;/&/g;
  $response = $agent->get($url, @args)->content;
} elsif ($request_method eq 'POST') {
  my $params = {};
  foreach my $p ($cgi->param) {
    $params->{$p} = $cgi->param($p);
  }
  push(@args, ('Content-Type', "multipart/form-data"));
  $response = $agent->post($url, @args, Content => $params)->content;
} elsif ($request_method eq 'DELETE') {
  $response = $agent->delete($url, @args)->content;
}

respond($response);

sub dbh {
  my $connection = DBI->connect(DBI_CONNECT, DBI_USER, DBI_PASS, {AutoCommit => 0, PrintError => 1});
  unless ($connection) {
    die "could not open database: $@";
  }
  return $connection;
}

sub auth {
    unless ($cgi->http('HTTP_AUTH')) {
	respond('{ "ERROR": "missing authentication" }', 400);
    }
    
    my $login = $dbh->selectrow_arrayref("SELECT login FROM tokens WHERE token='".$cgi->http('HTTP_AUTH')."'");
    if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
    } else {
	if (scalar(@$login)) {
	    $login = $login->[0];
	} else {
	    respond('{ "ERROR": "invalid token" }', 401);
	}
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
    if (ref $scopes && scalar(@$scopes)) {
	@$scopes = map { $_->[0] } @$scopes;
    } else {
	respond('{ "ERROR": "user has no rights" }', 404);
    }
    
    my $rights;
    @$rights = map { { "type" => $_->[0], "item" => $_->[1], "edit" => $_->[2], "view" => $_->[3], "owner" => $_->[4] } } @{$dbh->selectall_arrayref("SELECT type, item, edit, view, owner FROM rights WHERE scope IN ('".join("','", @$scopes)."')")};
    if ($dbh->err()) {
	respond('{ "ERROR": "'.$DBI::errstr.'" }', 500);
    }
    
    return ($admin, $rights);
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
