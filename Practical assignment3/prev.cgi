#!"C:\xampp\perl\bin\perl.exe"
# Software, Server protocol, CGI Revision etc.
use CGI':standard';
use strict;
use warnings;
open my $file, '<', 'fibonacci.txt' or die "Cannot open file: $!";
my @fibonacci_numbers = split(',', <$file>);
close $file;

# Calculate the previous Fibonacci numbers
my ($x, $y, $z) = @fibonacci_numbers;
my $previous_x = $y - $x;
my $previous_y = $x;
my $previous_z = $y;

# Update the file with the new Fibonacci numbers
open $file, '>', 'fibonacci.txt' or die "Cannot open file: $!";
print $file "$previous_x,$previous_y,$previous_z";
close $file;

# Output HTML
print "Content-type: text/html\n\n";
print "<!DOCTYPE HTML>\n";
print "<html><head><title>Fibonacci Previous</title></head><body>\n";
print "<p><h1>Fibonacci Sequence:</h1> $previous_x, $previous_y, $previous_z</p>\n";
if ($previous_x != 0) {
    print "<a href=\"prev.cgi\">Previous</a>\n";
}
print "<a href=\"next.cgi\">Next</a>\n";

print "</body></html>\n";