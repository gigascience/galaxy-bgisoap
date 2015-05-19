"""
gapcloser_1_12_wrapper.py
A wrapper script for GapCloser version 1.12
Peter Li - GigaScience/BGI-HK
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
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    thread_num = 4

    # Parse command line
    parser = optparse.OptionParser()
    parser.add_option("-a", "--scaff_in", dest="scaff_in")

    parser.add_option("", "--max_read_length_soapconfig", dest="max_read_length_soapconfig")
    parser.add_option("", "--file_source", dest="file_source")
    parser.add_option("", "--configuration", dest="configuration")

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")

    # Custom params
    parser.add_option("-p", "--overlap_param", dest="overlap_param")
    parser.add_option("-t", "--thread_num", dest="thread_num")
    parser.add_option("-l", "--max_read_length", dest="max_read_length")

    # Outputs
    parser.add_option("", "--scaff", dest='scaff')
    parser.add_option("", "--fill_info", dest='fill_info')
    opts, args = parser.parse_args()

    # Create temp directory for performing analysis
    tmp_dir = tempfile.mkdtemp(prefix="tmp-gapcloser-")
    print tmp_dir

    # Pick up soap.config file from command line
    script_filename = sys.argv[1]

    if opts.file_source == "history":
        shutil.copyfile(opts.configuration, tmp_dir + '/soap.config')
    else:
        shutil.copyfile(os.path.basename(script_filename), tmp_dir + '/soap.config')

    # Set up command line call - assumes path to executable has been defined in user's environment
    if opts.default_full_settings_type == "default":
        cmd = "GapCloser_v1.12 -a %s -b %s -o %s" % (opts.scaff_in, tmp_dir + '/soap.config', tmp_dir + "/gapclo.out")
    elif opts.default_full_settings_type == "full":
        cmd = "GapCloser_v1.12 -a %s -b %s -o %s -p %s -t %s -l %s" % (opts.scaff_in, tmp_dir + '/soap.config', tmp_dir + "/gapclo.out", opts.overlap_param, thread_num, opts.max_read_length)

    print cmd

    # Perform GapCloser analysis
    buffsize = 1048576
    try:
        tmp_out_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stdout = open(tmp_out_file, 'w')
        # Stdout is outputted to here
        tmp_err_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stderr = open(tmp_err_file, 'w')

        # Call SOAPdenovo2
        proc = subprocess.Popen(args=cmd, shell=True, cwd=tmp_dir, stderr=tmp_stderr.fileno())
        returncode = proc.wait()

        # Get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp_err_file, 'r')
        stderr = ''
        try:
            while True:
                stderr += tmp_stderr.read(buffsize)
                if not stderr or len(stderr) % buffsize != 0:
                    break
        except OverflowError:
            pass
        tmp_stderr.close()

        # A return code of 1 is given but result is ok - wierd
        print "Returncode: ", returncode
        if returncode > 1:
        #  if returncode != 0:
            raise Exception, stderr

    except Exception, e:
        raise Exception, 'Problem executing GapCloser ' + str(e)

    # Read results into outputs
    scaff_out = open(opts.scaff, 'wb')
    f = open(tmp_dir + '/gapclo.out')
    for line in f:
        scaff_out.write(line)
    scaff_out.close()
    f.close()

    fill_info_out = open(opts.fill_info, 'wb')
    f = open(tmp_dir + '/gapclo.out.fill')
    for line in f:
        fill_info_out.write(line)
    fill_info_out.close()
    f.close()

    # Clean up temp files
    cleanup_before_exit(tmp_dir)
    # Check results in output file
    if os.path.getsize(opts.scaff) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("Problem with GapCloser process")

if __name__ == "__main__":
    main()
