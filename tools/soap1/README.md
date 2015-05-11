# Galaxy wrapper for SOAP1

This tool provides Galaxy with access to
[SOAP1](http://soap.genomics.org.cn/soap1/) for performing reference-based
genome assembly.

## Citation

If you use this tool, you should cite the SOAP1 tool:

[SOAP: short oligonucleotide alignment program. Li et. al.  Bioinformatics 2008, 24: 713-714(http://bioinformatics.oxfordjournals.org/content/24/5/713.long).
DOI: 10.1093/bioinformatics/btn025.

## Automated installation

Galaxy should be able to automatically install the SOAP1 Galaxy tool and its
binary dependency when directed to it on the
[GigaToolShed](http://gigatoolshed.net).

## Manual installation

To install the SOAP1 tool manually, you need to put the XML and Python files in
the `tools/bgisoap/soap1/` folder and add the XML file to your tool_conf.xml as normal. For example, use:

<label id="bgisoap" text="BGISOAP" />
<section name="Reference assembly" id="reference_assembly">
  <tool file="bgisoap/soap1.xml" />
</section>

You must install the SOAP1 binary somewhere on the system path.

## History

| Version        | Changes                         |
| -------------- |:-------------------------------:|
| v0.1           | First release on GigaToolShed   |
