#!/usr/bin/perl
##################################################
#
#	Author: shizhongbin
#
##################################################
use strict;
use warnings;
use FindBin qw($Bin $Script);

die "Usage: <fileName> <tooldir> \n" if(@ARGV < 2);


my ($fileName, $tooldir) = @ARGV;
my $pairFile1;
my $pairFile2;
my $outputFile;

#my $i=0;
print "Tool directory: '$tooldir'\n";
open (IN, $fileName) || die "fail open $fileName\n";
while (<IN>) {

	$pairFile1 = $_;
	$pairFile2 = <IN>;
	chomp $pairFile1;
	chomp $pairFile2;
	
	#$pairFile1 .= ".corr";
	#$pairFile2 .= ".corr";

	$pairFile1 =~ /(.*)_1\.\w+/;
	#$outputFile = $1."\.corr";
	$outputFile = "output.corr";	

	print "merging $outputFile\n";
#	system "perl $Bin/merge_pair.pl $pairFile1 $pairFile2 $outputFile";
#   system "perl ./merge_pair.pl $pairFile1 $pairFile2 $outputFile";
	system "perl '$tooldir'/merge_pair.pl $pairFile1 $pairFile2 $outputFile";
	
#	$i++;
#	if ($i%25==0) {
#		wait;
#	}
}
close IN;
