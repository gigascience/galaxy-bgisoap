"""
kmerfreq1_wrapper.py
A wrapper script for kmerfreq
Peter Li - GigaScience, BGI-HK
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


def main():
    thread_num = 4

    # Parse command line
    parser = optparse.OptionParser()
    # Make list of params
    parser.add_option("", "--format_of_data", action="append", type="string", dest="format_of_data", help="Format of data")
    # Data inputs
    parser.add_option("", "--paired_fastq_input1", action="append", type="string", dest="paired_fastq_input1_list")
    parser.add_option("", "--paired_fastq_input2", action="append", type="string", dest="paired_fastq_input2_list")
    parser.add_option("", "--paired_fasta_input1", action="append", type="string", dest="paired_fasta_input1_list")
    parser.add_option("", "--paired_fasta_input2", action="append", type="string", dest="paired_fasta_input2_list")

    # Custom params
    parser.add_option("-s", "--seed_length", dest="seed_length")
    parser.add_option("-Q", "--ascii_shift", dest="ascii_shift")
    parser.add_option("-q", "--cutoff", dest="cutoff")
    parser.add_option("-n", "--output_kmer_index", dest="output_kmer_index")

    # Outputs
    parser.add_option("", "--stat", dest='stat', help="Statistical information")
    parser.add_option("", "--freq", dest='freq', help="Length information")
    parser.add_option("", "--filelist", dest='filelist', help="List of files processed by KmerFreq")
    opts, args = parser.parse_args()

    # Create temp directory for performing analysis
    tmp_dir = tempfile.mkdtemp(prefix="tmp-kmerfreq-1.0-")
    print tmp_dir

    # Create temp file for configuration
    config_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
    try:
        fout = open(config_file, 'w')
        if opts.format_of_data[0] == "fastq":
            for index in range(len(opts.paired_fastq_input1_list)):
                path = opts.paired_fastq_input1_list[index]
                fout.write(path)
                fout.write("\n")
                path = opts.paired_fastq_input2_list[index]
                fout.write(path)
                fout.write("\n")
            fout.close()
        elif opts.format_of_data[0] == "fasta":
            for index in range(len(opts.paired_fasta_input1_list)):
                path = opts.paired_fasta_input1_list[index]
                fout.write(path)
                fout.write("\n")
                path = opts.paired_fasta_input2_list[index]
                fout.write(path)
                fout.write("\n")
            fout.close()
    except Exception, e:
        stop_err("Output config file cannot be opened for writing. " + str(e))

    tmp_out_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
    tmp_stdout = open(tmp_out_file, 'w')
    tmp_err_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
    tmp_stderr = open(tmp_err_file, 'w')

    # Set up command line call - need to remove hard coded path
    cmd = "KmerFreq_v1.0 -o " + tmp_dir + "/output"
    cmd = cmd + " -i %s -s %s -q %s -Q %s -f 1 -l 1 -g 0 -n %s" % (config_file, opts.seed_length, opts.cutoff, opts.ascii_shift, opts.output_kmer_index)
    print "Command executed: ", cmd

    try:
        # Call Kmerfreq
        proc = subprocess.Popen(args=cmd, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno())
        returncode = proc.wait()

        # Get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp_err_file, 'r')
        stderr = ''
        try:
            buffsize = 1048576
            while True:
                stderr += tmp_stderr.read(buffsize)
                if not stderr or len(stderr) % buffsize != 0:
                    break
        except OverflowError:
            pass

        # Read tool stdout into galaxy stdout
        # f = open(tmp_out_file)
        # lines = f.readlines()
        # for line in lines:
        #     sys.stdout.write(line)
        # f.close()

        # Close streams
        # tmp_stdout.close()
        tmp_stderr.close()
	if returncode != 0:
            # raise Exception, stderr
	    print "Return code does not equal 0"

    except Exception, e:
        raise Exception, 'Problem performing KmerFreq process ' + str(e)

    # Read KmerFreq results into outputs
    stat_out = open(opts.stat, 'w')
    f = open(tmp_dir + '/output.stat')
    for line in f:
        stat_out.write(line)
    stat_out.close()
    f.close()

    freq_out = open(opts.freq, 'w')
    f = open(tmp_dir + '/output.freq')
    for line in f:
        freq_out.write(line)
    freq_out.close()
    f.close()

    filelist_out = open(opts.filelist, 'w')
    read_list_handle = open(config_file, 'r')
    paths = read_list_handle.read()
    filelist_out.write(paths)
    filelist_out.close()
    read_list_handle.close()

    # Clean up temp files
    #  cleanup_before_exit(tmp_dir)
    # Check results in output file
    if os.path.getsize(opts.stat) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    main()
