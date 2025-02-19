#!"C:\xampp\perl\bin\perl.exe"
# Software, Server protocol, CGI Revision etc.
use CGI':standard';
use strict;
use warnings;

# Read Fibonacci numbers from file
open my $file, '<', 'fibonacci.txt' or die "Cannot open file: $!";
my @fibonacci_numbers = split(',', <$file>);
close $file;

# Calculate the next Fibonacci number
my $next_number = $fibonacci_numbers[-1] + $fibonacci_numbers[-2];
push @fibonacci_numbers, $next_number;

# Update the file with the new Fibonacci numbers
open $file, '>', 'fibonacci.txt' or die "Cannot open file: $!";
print $file join(',', @fibonacci_numbers[-3..-1]);
close $file;

# Output HTML
print "Content-type: text/html\n\n";
print "<!DOCTYPE HTML>\n";
print "<html><head><title>Fibonacci Next</title></head><body>\n";
print "<p><h1>Fibonacci Sequence:</h1> @fibonacci_numbers[-3..-1]</p>\n";
print "<a href=\"prev.cgi\">Previous</a>\n";
print "<a href=\"next.cgi\">Next</a>\n";
print "</body></html>\n";




