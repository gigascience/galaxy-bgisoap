#!/usr/bin/perl -w
use strict;

if (@ARGV < 1) {
	print "stat.pl: used to make statistic of evaluation result of GAGE.\n";
	print "Usage:\n  perl $0 getCorrectnessStats.log >evaStat.txt\n";
	exit;
}

my ($ctgNum, $rawCtgN50, $corCtgN50, $ctgErrNum, $scafNum, $rawScafN50, $corScafN50, $scafErrNum) = (0, 0, 0, 0, 0, 0, 0, 0);
my ($rawCtgFlag, $corCtgFlag, $rawScafFlag, $corScafFlag) = (0, 0, 0, 0);
my $statFile = shift;
open IN, $statFile or die "Can't open file: $statFile\n";
while (<IN>) {
	if (/^Contig Stats/) {
		while (<IN>) {
			if (/^Total units: (\d+)/) {
				$ctgNum = $1;
			} elsif (/^N50: (\d+)/) {
				$rawCtgN50 = $1;
			} elsif (/^Indels >= 5: (\d+)/ || /^Inversions: (\d+)/ || /^Relocation: (\d+)/ || /^Translocation: (\d+)/) {
				$ctgErrNum += $1;
			} elsif (/^Corrected Contig Stats/) {
				last;
			}
		}

		while (<IN>) {
			if (/^N50: (\d+)/) {
				$corCtgN50 = $1;
			} elsif (/^Scaffold Stats/) {
				last;
			}
		}

		while (<IN>) {
			if (/^Total units: (\d+)/) {
				$scafNum = $1;
			} elsif (/^N50: (\d+)/) {
				$rawScafN50 = $1;
			} elsif (/^Corrected Scaffold Stats/) {
				last;
			}
		}

		while (<IN>) {
			if (/^(\d+),(\d+),(\d+),(\d+),\d+,[^,]+,\d+,(\d+),/) {
				$scafErrNum += ($1 + $2 + $3 + $4);
				$corScafN50 = $5;
			}
		}
	} else {
		print "Format error of input file: $statFile\n";
		last;
	}
}
close IN;

#$rawCtgN50 = ($rawCtgN50+50)/1000;
$rawCtgN50 /= 1000;
#$corCtgN50 = ($corCtgN50+50)/1000;
$corCtgN50 /= 1000;
$rawScafN50 = ($rawScafN50 + 500)/1000;
$corScafN50 = ($corScafN50 + 500)/1000;
printf ("No. contigs\tN50 (kb)\tErrors\tCorrected N50 (kb)\tNo. scaffolds\tN50 (kb)\tErrors\tCorrected N50 (kb)\n");
printf ("%d\t%.1f\t%d\t%.1f\t%d\t%d\t%d\t%d\n", $ctgNum, $rawCtgN50, $ctgErrNum, $corCtgN50, $scafNum, $rawScafN50, $scafErrNum, $corScafN50);
