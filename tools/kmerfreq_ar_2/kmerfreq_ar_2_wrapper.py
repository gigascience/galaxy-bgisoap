"""
kmerfreq_ar_2_wrapper.py
A wrapper script for KmerFreq_AR_v2.0
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

    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")
    parser.add_option("", "--space_consecutive_settings_type", dest="space_consecutive_settings_type")

    # Custom params
    parser.add_option("-k", "--kmer_size", dest="kmer_size")
    parser.add_option("-s", "--kmer_space_seed_size", dest="kmer_space_seed_size")
    parser.add_option("-c", "--min_precision_kmer_rate", dest="min_precision_kmer_rate")
    #  parser.add_option("-t", "--thread_num", dest="thread_num") # Keep under local control

    parser.add_option("-q", "--ascii_shift", dest="ascii_shift")
    parser.add_option("-m", "--output_depth", dest="output_depth")
    parser.add_option("-b", "--use_num_bases", dest="use_num_bases")

    # Outputs
    parser.add_option("", "--stat", dest='stat', help="Statistical information")
    parser.add_option("", "--cz_len", dest='cz_len', help="Length information")
    parser.add_option("", "--cz", dest='cz', help="Zipped frequency information")
    parser.add_option("", "--filelist", dest='filelist', help="List of files processed by KmerFreq")
    parser.add_option("", "--genome_estimate", dest='genome_estimate', help="Genome estimate")
    opts, args = parser.parse_args()

    # Create temp directory for performing analysis
    tmp_dir = tempfile.mkdtemp(prefix="tmp-kmerfreq-ar-")

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

    cmd = ""

    # Set up command line call - need to remove hard coded path
    if opts.space_consecutive_settings_type == "consecutive":
        cmd = "KmerFreq_AR_v2.0 %s -k %s -c %s -t %s -q %s -m %s" % (config_file, opts.kmer_size, opts.min_precision_kmer_rate, thread_num, opts.ascii_shift, opts.output_depth)
        if opts.use_num_bases != "":
            cmd += " -b %s" % opts.use_num_bases
        cmd += " >%s 2>%s" % (tmp_out_file, tmp_err_file)

    elif opts.space_consecutive_settings_type == "space":
        cmd = "KmerFreq_AR_v2.0 %s -k %s -s %s -c %s -t %s -q %s -m %s" % (config_file, opts.kmer_size, opts.kmer_space_seed_size, opts.min_precision_kmer_rate, thread_num, opts.ascii_shift, opts.output_depth)
        if opts.use_num_bases != "":
            cmd += " -b %s" % opts.use_num_bases
        cmd += " >%s 2>%s" % (tmp_out_file, tmp_err_file)

    print "Command executed: ", cmd

    try:
        # Call Kmerfreq_AR
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
        f = open(tmp_out_file)
        lines = f.readlines()
        for line in lines:
            sys.stdout.write(line)
        f.close()

        # Close streams
        tmp_stdout.close()
        tmp_stderr.close()
        if returncode != 0:
            raise Exception, stderr

    except Exception, e:
        raise Exception, 'Problem performing KmerFreq AR process ' + str(e)

    # Read KmerFreq results into outputs
    stat_out = open(opts.stat, 'w')
    if opts.space_consecutive_settings_type == "consecutive":
        f = open(tmp_dir + '/output.freq.stat')
    elif opts.space_consecutive_settings_type == "space":
        f = open(tmp_dir + '/output.space.freq.stat')
    for line in f:
        stat_out.write(line)
    stat_out.close()
    f.close()

    cz_len_out = open(opts.cz_len, 'w')
    if opts.space_consecutive_settings_type == "consecutive":
        f = open(tmp_dir + '/output.freq.cz.len')
    elif opts.space_consecutive_settings_type == "space":
        f = open(tmp_dir + '/output.space.freq.cz.len')
    for line in f:
        cz_len_out.write(line)
    cz_len_out.close()
    f.close()

    if opts.space_consecutive_settings_type == "consecutive":
        freq_out = open(opts.cz, 'wb')
        with open(tmp_dir + "/output.freq.cz", mode='rb') as f:  #  b is important -> binary
            fileContent = f.read()
            freq_out.write(fileContent)
    elif opts.space_consecutive_settings_type == "space":
        freq_out = open(opts.cz, 'wb')
        with open(tmp_dir + "/output.space.freq.cz", mode='rb') as f:  #  b is important -> binary
            fileContent = f.read()
            freq_out.write(fileContent)
    freq_out.close()
    f.close()

    filelist_out = open(opts.filelist, 'w')
    read_list_handle = open(config_file, 'r')
    paths = read_list_handle.read()
    filelist_out.write(paths)
    filelist_out.close()
    read_list_handle.close()

    if opts.space_consecutive_settings_type == "consecutive":
        genome_estimate_out = open(opts.genome_estimate, 'w')
        with open(tmp_dir + "/output.genome_estimate", mode='r') as f:
            fileContent = f.read()
            genome_estimate_out.write(fileContent)
    elif opts.space_consecutive_settings_type == "space":
        genome_estimate_out = open(opts.genome_estimate, 'w')
        with open(tmp_dir + "/output.space.genome_estimate", mode='r') as f:
            fileContent = f.read()
            genome_estimate_out.write(fileContent)
    genome_estimate_out.close()
    f.close()

    # Clean up temp files
    cleanup_before_exit(tmp_dir)
    # Check results in output file
    if os.path.getsize(opts.stat) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    main()
