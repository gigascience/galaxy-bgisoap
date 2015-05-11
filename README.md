# galaxy-bgisoap

This repository houses the Galaxy wrappers for the
[SOAP](http://soap.genomics.org.cn) tools developed by
[BGI](http://www.genomics.cn/en/index).

## Galaxy wrappers for BGI's SOAP tools

The Galaxy tools contained within this repository wrap up BGI's SOAP
command-line tools for working with NGS data. The
[GigaToolShed](http://gigatoolshed.net) is used to host these Galaxy tools.

Each Galaxy SOAP tool is dependent on an associated Tool shed package which
provides access to a particular SOAP binary.

## Folder structure

There is one directory for each SOAP tool which has been wrapped for use in
Galaxy and these are contained within the tools *folder*.  The *dependencies*
folder contains the packages for the SOAP Galaxy Tool dependency definitions.

The *data_managers* folder contains a single Galaxy Data Manager for setting up
index files for use with [SOAP2](http://soap.genomics.org.cn/soapaligner.html).
In *tool-data*, you will find configuration files which are used by Galaxy to
access SOAP2's index files.

The *test-data* directory contains data files which are used for functional
tests by the Galaxy wrappers.

## Installation

The Galaxy SOAP tools are to be  used from within a Galaxy server. They can be
automatically installed via the
[GigaScience Tool Shed](http://gigatoolshed.net) which handles their required
dependencies. All tools can be manually installed too. Documentation for
automatically and manually installing each Galaxy SOAP tool can be found within
the tools' README file.

## Testing

Functional tests for most of the tools can be found in the tool's XML
configuration file.