"""
soap1.py
A wrapper script for SOAP1
Copyright Peter Li peter@gigasciencejournal.com
"""

import sys, optparse, os, tempfile, shutil, subprocess

def stop_err(msg):
    sys.stderr.write('%s\n' % msg)
    sys.exit()

def cleanup_before_exit(tmp_dir):
    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

def __main__():
    #Parse command line
    parser = optparse.OptionParser()
    #Generic input params
    parser.add_option("-d", "--ref_seq", dest="ref_seq")
    parser.add_option("", "--analysis_settings_type")
    parser.add_option("", "--default_full_settings_type")
    #Single-end params
    parser.add_option("-a", "--forward_set", dest="forward_set")
    #Paired-end params
    parser.add_option("-b", "--reverse_set", dest="reverse_set")
    parser.add_option("-m", "--min_insert_size", dest="min_insert_size")
    parser.add_option("-x", "--max_insert_size", dest="max_insert_size")
    #Custom params
    parser.add_option("-s", "--seed_size", dest="seed_size")
    parser.add_option("-v", "--max_mismatches", dest="max_mismatches")
    parser.add_option("-g", "--max_gap_size", dest="max_gap_size")
    parser.add_option("-w", "--max_best_hits", dest="max_best_hits")
    parser.add_option("-e", "--gap_exist", dest="gap_exist")
    #Setting initial_quality generates a binary output so commented out
    #parser.add_option("-z", "--initial_quality", dest="initial_quality")
    parser.add_option("-c", "--trim", dest="trim")
    parser.add_option("-f", "--filter", dest="filter")
    parser.add_option("-r", "--report_repeats", dest="report_repeats",)
    #Setting read_id stops SOAP1 process from completing so param commented out
    #parser.add_option("-t", "--read_id", dest="read_id")
    parser.add_option("-n", "--ref_chain_align", dest="ref_chain_align")
    parser.add_option("-p", "--num_processors", dest="num_processors")
    #Outputs
    parser.add_option("-o", "--alignment_out", dest="alignment_out")
    parser.add_option("-2", "--unpaired_alignment_out", dest="unpaired_alignment_out")
    opts, args = parser.parse_args()

    #Create temp directory
    tmp_dir = tempfile.mkdtemp(prefix="tmp-soap1-")
    #To hold standard output from SOAP1 process
    tmp_out = tempfile.NamedTemporaryFile(dir=tmp_dir).name

    #Set up command line call
    if opts.analysis_settings_type == "single" and opts.default_full_settings_type == "default":
        cmd = "soap1 -d %s -a %s -o %s > %s" % (opts.ref_seq, opts.forward_set, opts.alignment_out, tmp_out)
    elif  opts.analysis_settings_type == "paired" and opts.default_full_settings_type == "default":
        cmd = "soap1 -d %s -a %s -b %s -o %s -2 %s -m %s -x %s > %s" % (opts.ref_seq, opts.forward_set, opts.reverse_set, opts.alignment_out, opts.unpaired_alignment_out, opts.min_insert_size, opts.max_insert_size, tmp_out)
    elif opts.analysis_settings_type == "single" and opts.default_full_settings_type == "full":
        cmd = "soap1 -d %s -a %s -o %s -s %s -v %s -g %s -w %s -e %s -c %s -f %s -r %s -n %s -p %s > %s" % (opts.ref_seq, opts.forward_set, opts.alignment_out, opts.seed_size, opts.max_mismatches, opts.max_gap_size, opts.max_best_hits, opts.gap_exist, opts.trim, opts.filter, opts.report_repeats, opts.ref_chain_align, opts.num_processors, tmp_out)
    elif opts.analysis_settings_type == "paired" and opts.default_full_settings_type == "full":
        cmd = "soap1 -d %s -a %s -b %s -o %s -2 %s -m %s -x %s -s %s -v %s -g %s -w %s -e %s -c %s -f %s -r %s -n %s -p %s > %s" % (opts.ref_seq, opts.forward_set, opts.reverse_set, opts.alignment_out, opts.unpaired_alignment_out, opts.min_insert_size, opts.max_insert_size, opts.seed_size, opts.max_mismatches, opts.max_gap_size, opts.max_best_hits, opts.gap_exist, opts.trim, opts.filter, opts.report_repeats, opts.ref_chain_align, opts.num_processors, tmp_out)

    #print cmd

    #Run
    try:
        tmp_err = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stderr = open(tmp_err, 'wb')

        proc = subprocess.Popen(args=cmd, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno())
        returncode = proc.wait()

        # get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp_err, 'rb')
        stderr = ''
        buffsize = 1048576
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

        #Read tool stdout into galaxy stdout
        f = open(tmp_out)
        lines = f.readlines()
        for line in lines:
            sys.stdout.write(line)
        f.close()

    except Exception, e:
        #Clean up temp files
        cleanup_before_exit(tmp_dir)
        stop_err('Error in running soap1 from (%s), %s' % (opts.alignment_out, str(e)))

    #Clean up temp files
    cleanup_before_exit(tmp_dir)
    #Check results in output file
    if os.path.getsize(opts.alignment_out) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    __main__()
