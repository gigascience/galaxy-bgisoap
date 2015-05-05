"""
soapdenovo2_wrapper.py
A wrapper script for SOAPdenovo2
Peter Li - GigaScience and BGI-HK
Huayan Gao - CUHK
"""

import optparse
import os
import shutil
import subprocess
import sys
import tempfile
import os.path


def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()


def cleanup_before_exit(tmp_dir):
    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


def main():
    # Thread number
    ncpu = 4

    # Parse command line
    parser = optparse.OptionParser()
    # parser.add_option("", "--max_read_length", dest="max_read_length")
    parser.add_option("", "--file_source", dest="file_source")
    parser.add_option("", "--configuration", dest="configuration")

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")

    # Mandatory params
    parser.add_option("-K", "--kmer_size", dest="kmer_size")
    # Commented out to keep control of thread number
    # parser.add_option("-p", "--ncpu", dest="ncpu")
    parser.add_option("-d", "--kmer_freq_cutoff", dest="kmer_freq_cutoff")
    parser.add_option("-R", "--resolve_repeats", dest="resolve_repeats")
    parser.add_option("-F", "--fill_gaps", dest="fill_gaps")

    # Custom params
    parser.add_option("-a", "--init_memory_assumption", dest="init_memory_assumption")
    parser.add_option("-D", "--edge_cov_cutoff", dest="edge_cov_cutoff")
    parser.add_option("-M", "--merge_level", dest="merge_level")
    parser.add_option("-m", "--max_k", dest="max_k")
    parser.add_option("-E", "--merge_clean_bubble", dest="merge_clean_bubble")
    parser.add_option("-e", "--weight", dest="weight")
    # parser.add_option("-r", "--keep_avail_read", dest="keep_avail_read")
    # parser.add_option("-f", "--output_gap_related_reads", dest="output_gap_related_reads")
    parser.add_option("-k", "--kmer_r2c", dest="kmer_r2c")
    parser.add_option("-u", "--unmask_contigs", dest="unmask_contigs")
    parser.add_option("-w", "--keep_contigs_connected", dest="keep_contigs_connected")
    parser.add_option("-G", "--gap_len_diff", dest="gap_len_diff")
    parser.add_option("-L", "--min_contig_len", dest="min_contig_len")
    parser.add_option("-c", "--min_contig_cvg", dest="min_contig_cvg")
    parser.add_option("-C", "--max_contig_cvg", dest="max_contig_cvg")
    parser.add_option("-b", "--insert_size_upper_bound", dest="insert_size_upper_bound")
    parser.add_option("-B", "--bubble_coverage", dest="bubble_coverage")
    parser.add_option("-N", "--genome_size", dest="genome_size")
    parser.add_option("-V", "--ass_visual", dest="ass_visual")

    # Outputs
    parser.add_option("", "--contig", dest="contig")
    parser.add_option("", "--scafseq", dest="scafseq")
    parser.add_option("", "--config", dest="config")
    opts, args = parser.parse_args()

    # Create temp directory for performing analysis
    tmp_dir = tempfile.mkdtemp(prefix="tmp-soapdenovo2-all-")
    print tmp_dir

    # Pick up soap.config file from command line
    script_filename = sys.argv[1]

    if opts.file_source == "history":
        shutil.copyfile(opts.configuration, tmp_dir + '/soap.config')
    else:
        shutil.copyfile(os.path.basename(script_filename), tmp_dir + '/soap.config')

    # Check if library files are gzipped
    # If so copy them into a file with a name that has a *.gz ending
    f = open(tmp_dir + '/soap.config')
    for line in f:
        if line.startswith("q"):
            if "gz" in line:
                # Strip line from = to .fq.gz
                begin_index = line.find("=")
                end_index = line.find(".fq.gz")
                filepath = line[begin_index + 1:end_index]
                # Check file exists
                try:
                    os.path.exists(filepath)
                    # Copy file
                    shutil.copyfile(filepath, filepath + '.fq.gz')
                except IOError:
                    print 'Cannot find ' + filepath + ' in soap.config'
                    raise
        elif line.startswith("f"):
            if "gz" in line:
                # Strip line from = to .fa.gz
                begin_index = line.find("=")
                end_index = line.find(".fa.gz")
                filepath = line[begin_index + 1:end_index]
                # Check file exists
                try:
                    os.path.exists(filepath)
                    # Copy file
                    shutil.copyfile(filepath, filepath + '.fa.gz')
                except IOError:
                    print 'Cannot find ' + filepath + ' in soap.config'
                    raise
    f.close()

    if opts.default_full_settings_type == "default":
        if int(opts.kmer_size) <= 63:
            # Hardcoded param p to set thread number
            cmd = "SOAPdenovo-63mer_v2.0 all -s %s -o %s -K %s -p %s -d %s" % (tmp_dir + '/soap.config', tmp_dir + "/result", opts.kmer_size, ncpu, opts.kmer_freq_cutoff)
            if opts.resolve_repeats == "YES":
                cmd += " -R"
            if opts.fill_gaps == "YES":
                cmd += " -F"
        elif int(opts.kmer_size) > 63:
            cmd = "SOAPdenovo-127mer_v2.0 all -s %s -o %s -K %s -p %s -d %s" % (tmp_dir + '/soap.config', tmp_dir + "/result", opts.kmer_size, ncpu, opts.kmer_freq_cutoff)
            if opts.resolve_repeats == "YES":
                cmd += " -R"
            if opts.fill_gaps == "YES":
                cmd += " -F"
    elif opts.default_full_settings_type == "full":
        # Check important params
        # Commented out for testing contig saureus step
        if int(opts.max_k) <= int(opts.kmer_size):
            sys.stderr.write("Problem: The value for the maximum kmer parameter has to be an odd value and higher than the kmer size.\n\n")
        if int(opts.kmer_r2c) < int(opts.kmer_size):
            sys.stderr.write("Problem: The kmer size used for mapping reads to contigs should be at least equal to the kmer size or higher.\n\n")
        if int(opts.kmer_size) <= 63:
            cmd = "SOAPdenovo-63mer_v2.0 all -s %s -o %s -K %s -p %s -a %s -d %s -D %s -M %s -m %s -e %s -E %s -k %s -u %s -w %s -G %s -L %s -c %s -C %s -b %s -B %s -N %s -V %s" % (tmp_dir + "/soap.config", tmp_dir + "/result", opts.kmer_size, ncpu, opts.init_memory_assumption, opts.kmer_freq_cutoff, opts.edge_cov_cutoff, opts.merge_level, opts.max_k, opts.weight, opts.merge_clean_bubble, opts.kmer_r2c, opts.unmask_contigs, opts.keep_contigs_connected, opts.gap_len_diff, opts.min_contig_len, opts.min_contig_cvg, opts.max_contig_cvg, opts.insert_size_upper_bound, opts.bubble_coverage, opts.genome_size, opts.ass_visual)
            if opts.resolve_repeats == "YES":
                cmd += " -R"
            if opts.fill_gaps == "YES":
                cmd += " -F"
        elif int(opts.kmer_size) > 63:
            cmd = "SOAPdenovo-127mer_v2.0 all -s %s -o %s -K %s -p %s -a %s -d %s -D %s -M %s -m %s -e %s -E %s -k %s -u %s -w %s -G %s -L %s -c %s -C %s -b %s -B %s -N %s -V %s" % (tmp_dir + "/soap.config", tmp_dir + "/result", opts.kmer_size, ncpu, opts.init_memory_assumption, opts.kmer_freq_cutoff, opts.edge_cov_cutoff, opts.merge_level, opts.max_k, opts.weight, opts.merge_clean_bubble, opts.kmer_r2c, opts.unmask_contigs, opts.keep_contigs_connected, opts.gap_len_diff, opts.min_contig_len, opts.min_contig_cvg, opts.max_contig_cvg, opts.insert_size_upper_bound, opts.bubble_coverage, opts.genome_size, opts.ass_visual)
            if opts.resolve_repeats == "YES":
                cmd += " -R"
            if opts.fill_gaps == "YES":
                cmd += " -F"

    # Perform SOAPdenovo2 analysis
    buffsize = 1048576
    try:
        # To hold standard output from process
        stdout_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        # To hold standard error output from process
        stderr_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        # Open streams to files
        stderr_hd = open(stderr_file, 'w')
        stdout_hd = open(stdout_file, 'w')

        # Call SOAPdenovo2
        proc = subprocess.Popen(args=cmd, shell=True, cwd=tmp_dir, stdout=stdout_hd, stderr=stderr_hd.fileno())
        returncode = proc.wait()

        stderr_hd.close()
        stdout_hd.close()

        # Get stderr, allowing for case where it's very large
        stderr_hd = open(stderr_file, 'r')
        stderr = ''
        try:
            while True:
                stderr += stderr_hd.read(buffsize)
                if not stderr or len(stderr) % buffsize != 0:
                    break
        except OverflowError:
            pass
        stderr_hd.close()

        # Read tool stdout into galaxy stdout
        f = open(stderr_file)
        lines = f.readlines()
        for line in lines:
            sys.stdout.write(line)
        f.close()

        if returncode != 0:
            raise Exception, stderr
    except Exception, e:
        raise Exception, 'Problem performing SOAPdenovo2 process ' + str(e)

    # Read SOAPdenovo2 results into outputs
    contig_out = open(opts.contig, 'w')
    f = open(tmp_dir + '/result.contig')
    for line in f:
        contig_out.write(line)
    contig_out.close()

    scafseq_out = open(opts.scafseq, 'w')
    f = open(tmp_dir + '/result.scafSeq')
    for line in f:
        scafseq_out.write(line)
    scafseq_out.close()

    config_out = open(opts.config, 'w')
    f = open(tmp_dir + '/soap.config')
    for line in f:
        config_out.write(line)
    config_out.close()
    f.close()

    # Clean up temp files
    cleanup_before_exit(tmp_dir)

    # Check results in output file
    if os.path.getsize(opts.contig) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("Problem with SOAPdenovo2 process")

if __name__ == "__main__":
    main()
