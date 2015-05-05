"""
A Galaxy wrapper script for merge_pair.pl
Peter Li - GigaScience and BGI-HK
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
    # Parse command line
    parser = optparse.OptionParser()
    # List of mandatory inputs and params
    parser.add_option("-i", "--corr_filelist", dest="corr_filelist")

    # Outputs for reads
    parser.add_option("", "--pair", dest="pair")
    parser.add_option("", "--single", dest="single")
    parser.add_option("", "--readsum", dest="readsum")
    opts, args = parser.parse_args()

    # Temp directory for data processing
    tmp_dir = tempfile.mkdtemp(prefix="tmp-mergepair-")
    print tmp_dir

    # Set up command line call
    cmd = "perl ./merge_pair_list.pl %s" % opts.corr_filelist 
    print cmd

    # Execute merge pair
    try:
        tmp_out_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stdout = open(tmp_out_file, 'w') # Contains merge pair stdout log
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
        if returncode != 0:
            raise Exception, stderr

    except Exception, e:
        raise Exception, 'Problem performing merge pair process: ' + str(e)

    # Read corrected forward and reverse files into outputs
    pair_in = open(opts.pair, 'w')
    output_corr_pair_out = open(tmp_dir + "/output.corr.pair", 'r')
    data = output_corr_pair_out.read()
    pair_in.write(data)
    pair_in.close()
    output_corr_pair_out.close()

    single_in = open(opts.single, 'w')
    output_corr_single_out = open(tmp_dir + "/output.corr.single", 'r')
    data = output_corr_single_out.read()
    single_in.write(data)
    single_in.close()
    output_corr_single_out.close()

    readsum_in = open(opts.readsum, 'w')
    output_corr_readsum_out = open(tmp_dir + "/output.corr.readsum", 'r')
    data = output_corr_readsum_out.read()
    readsum_in.write(data)
    readsum_in.close()
    output_corr_readsum_out.close()

    # Clean up temp files
    cleanup_before_exit(tmp_dir)
    # Check results in output file
    if os.path.getsize(opts.pair) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    main()

