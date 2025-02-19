#!/usr/bin/perl
use strict;
use warnings;
use IO::Socket::INET;

# Create a TCP socket
my $server = IO::Socket::INET->new(
    LocalAddr => 'localhost',
    LocalPort => 55555,
    Type      => SOCK_STREAM,
    Reuse     => 1,
    Listen    => 10
) || die "Cannot create socket: $!";

print "Server running at http://localhost:55555/\n";

# Accept and handle incoming connections
while (my $client = $server->accept()) {
    # Read the request
    my $request = '';
    while (my $line = <$client>) {
        $request .= $line;
        last if $line =~ /^\r\n$/; # End of HTTP request
    }

    # Handle the request
    my $response = handle_request($request);

    # Send the response
    print $client $response;

    # Close the client connection
    close($client);
}

# Function to handle HTTP requests
# Function to handle HTTP requests
sub handle_request {
    my ($request) = @_;

    if ($request =~ m!GET /prev\.cgi HTTP/1\.[01]\r\n!) {
        my $output = `perl ./prev.cgi`; # Adjusted file path
        return "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n$output";
    } elsif ($request =~ m!GET /next\.cgi HTTP/1\.[01]\r\n!) {
        my $output = `perl ./next.cgi`; # Adjusted file path
        return "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n$output";
    } else {
        # Redirect to next.cgi by default
        return "HTTP/1.0 302 Found\r\nLocation: /next.cgi\r\n\r\n";
    }
}


