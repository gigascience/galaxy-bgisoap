"""
soapdenovo1.py
A wrapper script for SOAPdenovo-1.0
Copyright   Peter Li - GigaScience and BGI-HK
            Huayan Gao - CUHK
"""

import optparse
import os
import shutil
import subprocess
import sys
import tempfile


def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()


def cleanup_before_exit(tmp_dir):
    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


def parse(tmp_dir, filename):
    myfile = open(tmp_dir + "/new_soap.config", "w")
    f = open(tmp_dir + "/" + filename, 'r')
    for line in f:
        line = line.rstrip()
        if "p=/home" in line:
            # if os.path.lexists(line[2:] + ".corr.pair") == -1:
            if (not os.path.isfile(line[2:] + ".corr.pair")):
                os.symlink(line[2:], line[2:] + ".corr.pair")
            newline = line + ".corr.pair"
            myfile.write(newline + "\n")
        elif "f=/home" in line:
            # if os.path.lexists(line[2:] + ".corr.single") == -1:
            if (not os.path.isfile(line[2:] + ".corr.single")):
                os.symlink(line[2:], line[2:] + ".corr.single")
            newline = line + ".corr.single"
            myfile.write(newline + "\n")
        elif "q1=/home" in line:
            # if os.path.lexists(line[3:] + ".fq.clean") == -1:
            if (not os.path.isfile(line[3:] + ".fq.clean")):
                os.symlink(line[3:], line[3:] + ".fq.clean")
            newline = line + ".fq.clean"
            myfile.write(newline + "\n")
        elif "q2=/home" in line:
            # if os.path.lexists(line[3:] + ".fq.clean") == -1:
            if (not os.path.isfile(line[3:] + ".fq.clean")):
                os.symlink(line[3:], line[3:] + ".fq.clean")
            newline = line + ".fq.clean"
            myfile.write(newline + "\n")
        else:
            myfile.write(line + "\n")
            
    myfile.close()


def main():
    # Parse command line
    parser = optparse.OptionParser()
    parser.add_option("", "--file_source", dest="file_source")
    parser.add_option("", "--configuration", dest="configuration")

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")
    # Custom params
    parser.add_option("", "--kmer_size", dest="kmer_size")
    parser.add_option("", "--ncpu", dest="ncpu")
    parser.add_option("", "--delete_kmers_freq_one", dest="delete_kmers_freq_one")
    parser.add_option("", "--delete_edges_coverage_one", dest="delete_edges_coverage_one")
    parser.add_option("", "--unsolve_repeats", dest="unsolve_repeats")
    parser.add_option("", "--fill_gaps_scaffold", dest="fill_gaps_scaffold")

    # Outputs
    parser.add_option("", "--contig", dest='contig', help="Contig sequence file")
    parser.add_option("", "--scafseq", dest='scafseq', help="Scaffold sequence file")
    parser.add_option("", "--config", dest="config")
    opts, args = parser.parse_args()

    # Create temp directory for performing analysis
    tmp_dir = tempfile.mkdtemp(prefix="tmp-soapdenovo1-")
    print tmp_dir
    # Pick up soap.config file from command line
    script_filename = sys.argv[1]

    print opts.configuration

    if opts.file_source == "history":
        shutil.copyfile(opts.configuration, tmp_dir + '/new_soap.config')
    else:
        shutil.copyfile(os.path.basename(script_filename), tmp_dir + '/soap.config')
        #Need to create soft links to dataset files and change the soap.config file
        #to refer to the soft links
        parse(tmp_dir, "soap.config")

    if opts.default_full_settings_type == "default":
        cmd = "SOAPdenovo_v1.0 all -s %s -o %s" % (tmp_dir + '/new_soap.config', tmp_dir + "/result")
    elif opts.default_full_settings_type == "full":
        cmd = "SOAPdenovo_v1.0 all -s %s -o %s -K %s -p %s" % (tmp_dir + '/new_soap.config', tmp_dir + "/result", opts.kmer_size, opts.ncpu)
        if opts.delete_edges_coverage_one == "yes":
            cmd += " -D"
        if opts.delete_kmers_freq_one == "yes":
            cmd += " -d 1"
        if opts.unsolve_repeats == "yes":
            cmd += " -R"
        if opts.fill_gaps_scaffold == "yes":
            cmd += " -F"
    #print cmd

    #Perform SOAPdenovo-1.0 analysis
    buffsize = 1048576
    try:
        #Create file in temporary directory
        tmp = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        #Open a stream to file
        tmp_stderr = open(tmp, 'wb')
        #Call SOAPdenovo
        proc = subprocess.Popen(args=cmd, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno())
        returncode = proc.wait()
        #Close stream
        tmp_stderr.close()
        #Get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp, 'rb')
        stderr = ''
        try:
            while True:
                stderr += tmp_stderr.read(buffsize)
                if not stderr or len(stderr) % buffsize != 0:
                    break
        except OverflowError:
            pass
        tmp_stderr.close()
        if returncode != 0:
            raise Exception, stderr
    except Exception, e:
        raise Exception, 'Problem performing SOAPdenovo 1 ' + str(e)

    #Read SOAPdenovo 1 results into outputs
    contig_out = open(opts.contig, 'wb')
    file = open(tmp_dir + '/result.contig')
    for line in file:
        #print line
        contig_out.write(line)
    contig_out.close()
    file.close()

    scafseq_out = open(opts.scafseq, 'wb')
    file = open(tmp_dir + '/result.scafSeq')
    for line in file:
        #print line
        scafseq_out.write(line)
    scafseq_out.close()
    file.close()

    config_out = open(opts.config, 'w')
    f = open(tmp_dir + '/new_soap.config')
    for line in f:
        config_out.write(line)
    config_out.close()
    f.close()

    #Clean up temp files
    #cleanup_before_exit(tmp_dir)
    #Check results in output file
    if os.path.getsize(opts.contig) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    main()

