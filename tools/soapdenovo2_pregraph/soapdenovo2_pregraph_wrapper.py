"""
soapdenovo2_pregraph.py
A wrapper script for SOAPdenovo2 pregraph module
Copyright   Peter Li - GigaScience and BGI-HK
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
    #Thread number
    ncpu = 4

    #Parse command line
    parser = optparse.OptionParser()
    parser.add_option("", "--max_read_length", dest="max_read_length")
    parser.add_option('', '--file_source', dest='file_source')
    parser.add_option("", "--configuration", dest="configuration")

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")

    #Mandatory params
    parser.add_option("-K", "--kmer_size", dest="kmer_size")
    #Commented out to keep control of thread number
    #parser.add_option("-p", "--ncpu", dest="ncpu")
    parser.add_option("-d", "--kmer_freq_cutoff", dest="kmer_freq_cutoff")

    #Custom params
    parser.add_option("-a", "--init_memory_assumption", dest="init_memory_assumption")
    parser.add_option("-R", "--output_extra_info", dest="output_extra_info")

    parser.add_option("", "--avg_ins", action="append", type="string", dest="avg_insert_list")
    parser.add_option("", "--reverse_seq", action="append", type="string", dest="reverse_seq_list")
    parser.add_option("", "--asm_flags", action="append", type="string", dest="asm_flags_list")
    parser.add_option("", "--rd_len_cutoff", action="append", type="string", dest="rd_len_cutoff_list")
    parser.add_option("", "--rank", action="append", type="string", dest="rank_list")
    parser.add_option("", "--pair_num_cutoff", action="append", type="string", dest="pair_num_cutoff_list")
    parser.add_option("", "--map_len", action="append", type="string", dest="map_len_list")

    #Outputs
    parser.add_option("", "--pregraph_basic", dest='pregraph_basic')
    parser.add_option("", "--vertex", dest='vertex')
    parser.add_option("", "--preArc", dest='preArc')
    parser.add_option("", "--edge", dest='edge')
    parser.add_option("", "--kmer_freq", dest='kmer_freq')
    parser.add_option("", "--soapconfig", dest='soapconfig')
    opts, args = parser.parse_args()

    #Create temp directory for performing analysis
    tmp_dir = tempfile.mkdtemp(prefix="tmp-pregraph-")
    print tmp_dir

    #Pick up soap.config file from command line
    script_filename = sys.argv[1]

    if opts.file_source == "history":
        shutil.copyfile(opts.configuration, tmp_dir + '/soap.config')
    else:
        shutil.copyfile(os.path.basename(script_filename), tmp_dir + '/soap.config')

    #Set up command line call
    if int(opts.kmer_size) <= 63 and opts.default_full_settings_type == "default":
        cmd = "SOAPdenovo-63mer_v2.0 pregraph -s %s -o %s -K %s -p %s -d %s" % (tmp_dir + '/soap.config', tmp_dir + "/out", opts.kmer_size, ncpu, opts.kmer_freq_cutoff)
    elif int(opts.kmer_size) <= 63 and opts.default_full_settings_type == "full":
        cmd = "SOAPdenovo-63mer_v2.0 pregraph -s %s -o %s -K %s -p %s -d %s -a %s -R %s" % (tmp_dir + '/soap.config', tmp_dir + "/out", opts.kmer_size, ncpu, opts.kmer_freq_cutoff, opts.init_mem_assumption, opts.output_extra_info)
    elif int(opts.kmer_size) > 63 and opts.default_full_settings_type == "default":
        cmd = "SOAPdenovo-127mer_v2.0 pregraph -s %s -o %s -K %s -p %s -d %s" % (tmp_dir + '/soap.config', tmp_dir + "/out", opts.kmer_size, ncpu, opts.kmer_freq_cutoff)
    elif int(opts.kmer_size) > 63 and opts.default_full_settings_type == "full":
        cmd = "SOAPdenovo-127mer_v2.0 pregraph -s %s -o %s -K %s -p %s -d %s -a %s -R %s" % (tmp_dir + '/soap.config', tmp_dir + "/out", opts.kmer_size, ncpu, opts.kmer_freq_cutoff, opts.init_mem_assumption, opts.output_extra_info)

    #Perform SOAPdenovo2_pregraph analysis
    buffsize = 1048576
    try:
    #To hold standard output from process
        stdout_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        #To hold standard error output from process
        stderr_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        #Open streams to files
        stderr_hd = open(stderr_file, 'w')
        stdout_hd = open(stdout_file, 'w')

        #Call SOAPdenovo2
        proc = subprocess.Popen(args=cmd, shell=True, cwd=tmp_dir, stdout=stdout_hd, stderr=stderr_hd.fileno())
        returncode = proc.wait()

        stderr_hd.close()
        stdout_hd.close()

        #Get stderr, allowing for case where it's very large
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

        #Read tool stdout into galaxy stdout
        f = open(stderr_file)
        lines = f.readlines()
        for line in lines:
            sys.stdout.write(line)
        f.close()

        if returncode != 0:
            raise Exception, stderr
    except Exception, e:
        raise Exception, 'Problem performing SOAPdenovo2 pregraph process ' + str(e)

    #Read SOAPdenovo2 results into outputs
    kmer_freq_out = open(opts.kmer_freq, 'w')
    f = open(tmp_dir + "/out.kmerFreq")
    for line in f:
        kmer_freq_out.write(line)
    kmer_freq_out.close()
    f.close()

    edge_gz_out = open(opts.edge, 'wb')
    with open(tmp_dir + "/out.edge.gz", mode='rb') as f: # b is important -> binary
        fileContent = f.read()
        edge_gz_out.write(fileContent)
    edge_gz_out.close()
    f.close()

    pre_arc_out = open(opts.preArc, 'w')
    f1 = open(tmp_dir + "/out.preArc")
    for line in f1:
        pre_arc_out.write(line)
    pre_arc_out.close()
    f1.close()

    vertex_out = open(opts.vertex, 'w')
    f = open(tmp_dir + "/out.vertex")
    for line in f:
        vertex_out.write(line)
    vertex_out.close()
    f.close()

    pregraph_basic_out = open(opts.pregraph_basic, 'w')
    f = open(tmp_dir + "/out.preGraphBasic")
    for line in f:
        pregraph_basic_out.write(line)
    pregraph_basic_out.close()
    f.close()

    config_out = open(opts.soapconfig, 'w')
    f = open(tmp_dir + '/soap.config')
    for line in f:
        config_out.write(line)
    config_out.close()
    f.close()

    #Clean up temp files
    cleanup_before_exit(tmp_dir)
    #Check results in output file
    if os.path.getsize(opts.pregraph_basic) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    main()
