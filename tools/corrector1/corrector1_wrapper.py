"""
A Galaxy wrapper script for corrector-1.0
Peter Li - GigaScience and BGI-HK
"""

import optparse
import os
import shutil
import subprocess
import sys
import tempfile
import fnmatch


def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()


def cleanup_before_exit(tmp_dir):
    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


def html_report_from_directory(html_out, dir):
    html_out.write('<html>\n<head>\n</head>\n<body>\n<font face="arial">\n<p>Corrector outputs</p>\n<p/>\n')
    for dirname, dirnames, filenames in os.walk(dir):
        # Link supplementary documents in HTML file
        for file in filenames:
            if fnmatch.fnmatch(file, '*pair_*'):
                continue
            else:
                html_out.write('<p><a href="%s">%s</a></p>\n' % (file, file))
    html_out.write('</font>\n</body>\n</html>\n')


def main():
    thread_num = 4

    # Parse command line
    parser = optparse.OptionParser()
    # List of mandatory inputs and params
    parser.add_option("-i", "--filelist", dest="filelist")
    parser.add_option("-r", "--freq", dest="freq")

    parser.add_option("-n", "--kmer_index", dest="kmer_index")
    parser.add_option("-k", "--start_cutoff", dest="start_cutoff")
    parser.add_option("-e", "--end_cutoff", dest="end_cutoff")
    parser.add_option("-d", "--delta", dest="delta")
    parser.add_option("-s", "--seed_length", dest="seed_length")
    # Removed from galaxy interface to keep under own control
    # parser.add_option("-t", "--thread_num", dest="thread_num")
    parser.add_option("", "--file_format", dest="file_format")

    # Outputs for reads
    parser.add_option("", "--corrected_forward", dest="corrected_forward")
    parser.add_option("", "--corrected_reverse", dest="corrected_reverse")
    parser.add_option("", "--corr_filelist", dest="corr_filelist")
    opts, args = parser.parse_args()

    # Temp directory for data processing
    tmp_dir = tempfile.mkdtemp(prefix="tmp-corrector-")
    print tmp_dir

    # Set up command line call
    cmd = "Corrector_v1.0 -i %s -r %s -n %s -k %s -e %s -d %s -s %s -t %s -f %s -l 1 -g 0" % (opts.filelist, opts.freq, opts.kmer_index, opts.start_cutoff, opts.end_cutoff, opts.delta, opts.seed_length, thread_num, opts.file_format)
    print "Command: ", cmd

    # Execute Corrector
    try:
        tmp_out_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stdout = open(tmp_out_file, 'w') # Contains Corrector stdout log
        tmp_err_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stderr = open(tmp_err_file, 'w')

        # Perform Corrector call
        proc = subprocess.Popen(args=cmd, shell=True, cwd=tmp_dir, stdout=tmp_stdout, stderr=tmp_stderr)
        returncode = proc.wait()

        # Read tool stdout into galaxy stdout
        f = open(tmp_out_file)
        lines = f.readlines()
        for line in lines:
            sys.stdout.write(line)
        f.close()

        #  get stderr, allowing for case where it's very large
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
        tmp_stdout.close()
        tmp_stderr.close()
        # if returncode != 0:
        #     raise Exception, stderr

    except Exception, e:
        raise Exception, 'Problem performing Corrector process: ' + str(e)

    # Need to move and rename files for galaxy for display multiple files
    filelist = open(opts.filelist)

    #  # Read file paths in read.lst
    pair_index = 1
    for path in filelist:
        # Read corrected forward and reverse files into outputs
        source = path.rstrip() + ".corr"
        if pair_index == 1:
            corrected_forward_in = open(opts.corrected_forward, 'w')
            file_out = open(source, 'r')
            data = file_out.read()
            corrected_forward_in.write(data)
            corrected_forward_in.close()
            file_out.close()

        if pair_index == 2:
            corrected_reverse_in = open(opts.corrected_reverse, 'w')
            file_out = open(source, 'r')
            data = file_out.read()
            corrected_reverse_in.write(data)
            corrected_reverse_in.close()
            file_out.close()

        pair_index += 1
        if pair_index == 3:
            pair_index = 1
    filelist.close()
    
    # Create corrected file list
    corrected_files_in = open(opts.corr_filelist, 'w')
    corrected_files_in.write(opts.corrected_forward + "\n")
    corrected_files_in.write(opts.corrected_reverse + "\n")
    corrected_files_in.close()

    # Clean up temp files
    cleanup_before_exit(tmp_dir)
    # Check results in output file
    if os.path.getsize(opts.corrected_forward) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    main()

