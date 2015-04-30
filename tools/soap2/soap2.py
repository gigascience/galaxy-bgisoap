"""
soap2.py
A wrapper script for SOAP2
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
    parser.add_option("", "--ref", dest="ref")

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")

    #Single-end params
    parser.add_option("-a", "--forward_set", dest="forward_set", help="Forward set of reads")
    #Paired-end params
    parser.add_option("-b", "--reverse_set", dest="reverse_set")
    parser.add_option("-m", "--min_insert_size", dest="min_insert_size")
    parser.add_option("-x", "--max_insert_size", dest="max_insert_size")
    #Custom params
    parser.add_option("-n", "--filter", dest="filter")
    parser.add_option("-t", "--read_id", dest="read_id")
    parser.add_option("-r", "--report_repeats", dest="report_repeats")
    parser.add_option("-R", "--long_insert_align", dest="long_insert_align")
    parser.add_option("-l", "--high_error_rate", dest="high_error_rate")
    parser.add_option("-v", "--allow_all_mismatches", dest="allow_all_mismatches")
    parser.add_option("-M", "--match_mode", dest="match_mode")
    parser.add_option("-p", "--num_threads", dest="num_threads")

    #Outputs
    parser.add_option("-o", "--alignment_out", dest="alignment_out")
    parser.add_option("-2", "--unpaired_alignment_out", dest="unpaired_alignment_out")
    opts, args = parser.parse_args()

    #Create temp directory
    tmp_dir = tempfile.mkdtemp(prefix="tmp-soap2-")

    #Get reference index directory
    ref_index_filename = opts.ref
    print ref_index_filename

    #Set up command line call
    if opts.analysis_settings_type == "single" and opts.default_full_settings_type == "default":
        cmd = "soap -a %s -D " % opts.forward_set + ref_index_filename + " -o %s" % (opts.alignment_out)
    elif opts.analysis_settings_type == "paired" and opts.default_full_settings_type == "default":
        cmd = "soap -a %s -b %s -D " % (opts.forward_set, opts.reverse_set) + ref_index_filename + " -o %s -2 %s -m %s -x %s" % (opts.alignment_out, opts.unpaired_alignment_out, opts.min_insert_size, opts.max_insert_size)
    elif opts.analysis_settings_type == "single" and opts.default_full_settings_type == "full":
        cmd = "soap -a %s -D " % opts.forward_set + ref_index_filename + " -o %s -n %s -t %s -r %s -v %s -M %s -p %s" % (opts.alignment_out, opts.filter, opts.read_id, opts.report_repeats, opts.allow_all_mismatches, opts.match_mode, opts.num_threads)
    elif opts.analysis_settings_type == "paired" and opts.default_full_settings_type == "full":
        cmd = "soap -a %s -b %s -D " % (opts.forward_set, opts.reverse_set) + ref_index_filename + " -o %s -2 %s -m %s -x %s -n %s -t %s -r %s -v %s -M %s -p %s" % (opts.alignment_out, opts.unpaired_alignment_out, opts.min_insert_size, opts.max_insert_size, opts.filter, opts.read_id, opts.report_repeats, opts.allow_all_mismatches, opts.match_mode, opts.num_threads)

    #print cmd

    #Run
    try:
        #Stdout from SOAP2 is being written into this file!
        tmp_err_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stderr = open(tmp_err_file, 'w')

        #Perform SOAP2 call
        proc = subprocess.Popen(args=cmd, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno())
        returncode = proc.wait()

        # get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp_err_file, 'r')
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

        #Read tool stderr into galaxy stdout
        f = open(tmp_err_file)
        lines = f.readlines()
        for line in lines:
            sys.stdout.write(line)
        f.close()

    except Exception, e:
        stop_err('Error in running soap2 from (%s), %s' % (opts.alignment_out, str(e)))

    #Clean up temp files
    cleanup_before_exit(tmp_dir)
    #Check results in output file
    if os.path.getsize(opts.alignment_out) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    __main__()
