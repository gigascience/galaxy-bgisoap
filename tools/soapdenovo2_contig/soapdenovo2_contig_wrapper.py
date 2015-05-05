"""
soapdenovo2_contig.py
A wrapper script for SOAPdenovo2 contig module
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
    ncpu = 4

    #Parse command line
    parser = optparse.OptionParser()
    #Inputs
    parser.add_option('', '--pre_graph_basic', dest='pre_graph_basic')
    parser.add_option('', '--vertex', dest='vertex')
    parser.add_option('', '--pre_arc', dest='pre_arc')
    parser.add_option('', '--edge_gz', dest='edge_gz')

    parser.add_option("", "--analysis_settings_type", dest="analysis_settings_type")
    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")
    parser.add_option("", "--multi_kmer_setting", dest="multi_kmer_setting")

    parser.add_option("-R", "--resolve_repeats", dest="resolve_repeats")
    parser.add_option("-M", "--merge_level", dest="merge_level")
    parser.add_option("-D", "--edge_cov_cutoff", dest="edge_cov_cutoff")
    parser.add_option("-m", "--max_k", dest="max_k")
    parser.add_option("-e", "--weight", dest="weight")
    parser.add_option("-s", "--reads_info_file", dest="reads_info_file")
    #Commented out to keep control
    #parser.add_option("-p", "--ncpu", dest="ncpu")
    parser.add_option("-E", "--merge_clean_bubble", dest="merge_clean_bubble")

    #Outputs
    parser.add_option("", "--contig", dest='contig')
    parser.add_option("", "--arc", dest='arc')
    parser.add_option("", "--updated_edge", dest='updated_edge')
    parser.add_option("", "--contig_index", dest='contig_index')

    opts, args = parser.parse_args()

    #Write inputs to a temporary directory
    dirpath = tempfile.mkdtemp(prefix="tmp-contig-")
    pre_graph_basic_data = open(opts.pre_graph_basic, 'r')
    pre_graph_basic_file = open(dirpath + "/out.preGraphBasic", "w")
    for line in pre_graph_basic_data:
        pre_graph_basic_file.write(line)
    pre_graph_basic_data.close()
    pre_graph_basic_file.close()

    vertex_data = open(opts.vertex, 'r')
    vertex_file = open(dirpath + "/out.vertex", "w")
    for line in vertex_data:
        vertex_file.write(line)
    vertex_data.close()
    vertex_file.close()

    pre_arc_data = open(opts.pre_arc, 'r')
    pre_arc_file = open(dirpath + "/out.preArc", "w")
    for line in pre_arc_data:
        pre_arc_file.write(line)
    pre_arc_data.close()
    pre_arc_file.close()

    edge_gz_data = open(opts.edge_gz, 'rb')
    edge_gz_file = open(dirpath + "/out.edge.gz", "wb")
    for line in edge_gz_data:
        edge_gz_file.write(line)
    edge_gz_data.close()
    edge_gz_file.close()

    #Set up command line call
    if opts.default_full_settings_type == "default":
        cmd = "SOAPdenovo-63mer_v2.0 contig -g %s" % (dirpath + "/out")
    elif opts.multi_kmer_setting == "NO" and opts.default_full_settings_type == "full":
        cmd = "SOAPdenovo-63mer_v2.0 contig -g %s -M %s -D %s -e %s" % (dirpath + "/out", opts.merge_level, opts.edge_cov_cutoff, opts.weight)
        if opts.resolve_repeats == "YES":
            cmd = cmd + " -R"
    else:
        cmd = "SOAPdenovo-63mer_v2.0 contig -g %s -M %s -D %s -e %s -m %s -s %s -p %s -E %s" % (dirpath + "/out", opts.merge_level, opts.edge_cov_cutoff, opts.weight, opts.max_k, opts.reads_info_file, ncpu, opts.merge_clean_bubble)
        if opts.resolve_repeats == "YES":
            cmd = cmd + " -R"

    #print cmd

    #Perform SOAPdenovo2_contig analysis
    buffsize = 1048576
    try:
        tmp_out_file = tempfile.NamedTemporaryFile(dir=dirpath).name
        tmp_stdout = open(tmp_out_file, 'w')
        tmp_err_file = tempfile.NamedTemporaryFile(dir=dirpath).name #Contains contig stdout
        tmp_stderr = open(tmp_err_file, 'w')

        #New additional datasets must be placed in the directory provided by $new_file_path__
        proc = subprocess.Popen(args=cmd, shell=True, cwd=dirpath, stderr=tmp_stderr.fileno())
        returncode = proc.wait()

        #Read tool stdout into galaxy stdout
        f = open(tmp_err_file)
        lines = f.readlines()
        for line in lines:
            sys.stdout.write(line)
        f.close()

        #Get stderr, allowing for case where it's very large
        tmp_stderr = open(tmp_err_file, 'r')
        stderr = ''
        try:
            while True:
                stderr += tmp_stderr.read(buffsize)
                if not stderr or len(stderr) % buffsize != 0:
                    break
        except OverflowError:
            pass
            #Close streams
        tmp_stdout.close()
        tmp_stderr.close()
        if returncode != 0:
            raise Exception, stderr
    except Exception, e:
        raise Exception, 'Problem performing contig process ' + str(e)

    #Read soap config file into its output
    contig_index_out = open(opts.contig_index, 'w')
    f = open(dirpath + "/out.ContigIndex")
    for line in f:
        contig_index_out.write(line)
    contig_index_out.close()
    f.close()

    #Read soap config file into its output
    arc_out = open(opts.arc, 'w')
    f = open(dirpath + "/out.Arc")
    for line in f:
        arc_out.write(line)
    arc_out.close()
    f.close()

    #Read soap config file into its output
    contig_out = open(opts.contig, 'w')
    f = open(dirpath + "/out.contig")
    for line in f:
        contig_out.write(line)
    contig_out.close()
    f.close()

    #Read soap config file into its output
    edge_out = open(opts.updated_edge, 'w')
    f = open(dirpath + "/out.updated.edge")
    for line in f:
        edge_out.write(line)
    edge_out.close()
    f.close()

    #Clean up temp files
    cleanup_before_exit(dirpath)
    #Check results in output file
    if os.path.getsize(opts.contig_index) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    main()
