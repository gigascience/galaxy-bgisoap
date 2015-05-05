"""
soapdenovo2_pregraph_sparse.py
A wrapper script for SOAPdenovo2 pregraph sparse module
Copyright   Peter Li - GigaScience and BGI-HK
"""

import optparse
import os
import shutil
import subprocess
import sys
import tempfile
import re
import fnmatch


def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()


def html_report_from_directory(html_out, dir):
    html_out.write('<html>\n<head>\n</head>\n<body>\n<font face="arial">\n<p>Pregraph sparse outputs</p>\n<p/>\n')
    for dirname, dirnames, filenames in os.walk(dir):
        #Link supplementary documents in HTML file
        for file in filenames:
            if fnmatch.fnmatch(file, '*pair_*'):
                continue
            else:
                html_out.write('<p><a href="%s">%s</a></p>\n' % (file, file))
    html_out.write('</font>\n</body>\n</html>\n')


def cleanup_before_exit(tmp_dir):
    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


def main():
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
    parser.add_option("-z", "--genome_size", dest="genome_size")
    parser.add_option("-d", "--kmer_freq_cutoff", dest="kmer_freq_cutoff")
    #Commented out to keep under local control
    #parser.add_option("-p", "--ncpu", dest="ncpu")

    #Optional params
    parser.add_option("-g", "--max_kmer_edge_length", dest="max_kmer_edge_length")
    parser.add_option("-e", "--kmer_edge_freq_cutoff", dest="kmer_edge_freq_cutoff")
    parser.add_option("-R", "--output_extra_info", dest="output_extra_info")
    parser.add_option("-r", "--runmode", dest="runmode")

    #HTML output
    parser.add_option("", "--html_file", dest="html_file")
    parser.add_option("", "--html_file_files_path", dest="html_file_files_path")

    #Outputs
    parser.add_option("", "--kmer_freq", dest='kmer_freq')
    parser.add_option("", "--edge", dest='edge')
    parser.add_option("", "--mark_on_edge", dest='mark_on_edge')
    parser.add_option("", "--path", dest='path')
    parser.add_option("", "--pre_arc", dest='pre_arc')
    parser.add_option("", "--vertex", dest='vertex')
    parser.add_option("", "--pregraph_basic", dest='pregraph_basic')
    parser.add_option("", "--soap_config", dest='soap_config')
    opts, args = parser.parse_args()

    #Create directory to process and store Corrector outputs
    html_file = opts.html_file
    job_work_dir = opts.html_file_files_path

    #Need a temporary directory to perform processing
    tmp_dir = tempfile.mkdtemp(prefix="tmp-pregraph-sparse-")

    #Pick up soap.config file from command line
    script_filename = sys.argv[1]

    if opts.file_source == "history":
        shutil.copyfile(opts.configuration, tmp_dir + '/soap.config')
    else:
        shutil.copyfile(os.path.basename(script_filename), tmp_dir + '/soap.config')

    #Create correct paths to html-linked files
    rex = re.compile('database/(.*)/dataset_')
    #Create replacement text using html_file
    #Split string into tokens
    tokens = html_file.split("/")
    #Get second to last token
    userId = tokens[len(tokens) - 2]
    files_dir = rex.sub("database/files/" + userId + "/dataset_", job_work_dir)
    files_dir = files_dir + "/"
    # print "New html dir: ", files_dir
    #Create directory
    if not os.path.exists(files_dir):
        try:
            os.makedirs(files_dir)
        except:
            pass

    #Set up command line call
    if int(opts.kmer_size) <= 63 and opts.default_full_settings_type == "default":
        cmd = "Pregraph_Sparse_63mer.v1.0.3 -s %s -K %s -z %s -o %s -d %s" % (tmp_dir + '/soap.config', opts.kmer_size, opts.genome_size, files_dir + "/out", opts.kmer_freq_cutoff)
    elif int(opts.kmer_size) <= 63 and opts.default_full_settings_type == "full":
        cmd = "Pregraph_Sparse_63mer.v1.0.3 -s %s -K %s -z %s -o %s -d %s -g %s -e %s -R %s -r %s -p %s" % (tmp_dir + '/soap.config', opts.kmer_size, opts.genome_size, files_dir + "/out", opts.kmer_freq_cutoff, opts.max_kmer_edge_length, opts.kmer_edge_freq_cutoff, opts.output_extra_info, opts.runmode, ncpu)
    elif int(opts.kmer_size) > 63 and opts.default_full_settings_type == "default":
        cmd = "Pregraph_Sparse_127mer.v1.0.3 -s %s -K %s -z %s -o %s -d %s" % (tmp_dir + '/soap.config', opts.kmer_size, opts.genome_size, files_dir + "/out", opts.kmer_freq_cutoff)
    elif int(opts.kmer_size) > 63 and opts.default_full_settings_type == "full":
        cmd = "Pregraph_Sparse_127mer.v1.0.3 -s %s -K %s -z %s -o %s -g %s -d %s -e %s -R %s -r %s -p %s" % (tmp_dir + '/soap.config', opts.kmer_size, opts.genome_size, files_dir + "/out", opts.max_kmer_edge_length, opts.kmer_freq_cutoff, opts.kmer_edge_freq_cutoff, opts.output_extra_info, opts.runmode, ncpu)

    # print cmd

    #Perform SOAPdenovo2_pregraph sparse analysis
    buffsize = 1048576
    try:

        tmp_out_file = tempfile.NamedTemporaryFile(dir=files_dir).name
        tmp_stdout = open(tmp_out_file, 'w')
        tmp_err_file = tempfile.NamedTemporaryFile(dir=files_dir).name #Contains pregraph's stdout
        tmp_stderr = open(tmp_err_file, 'w')

        #Call SOAPdenovo2
        #New additional datasets must be placed in the directory provided by $new_file_path__
        proc = subprocess.Popen(args=cmd, shell=True, cwd=files_dir, stdout=tmp_stdout, stderr=tmp_stderr.fileno())
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
        raise Exception, 'Problem performing pregraph sparse process ' + str(e)

    #Read files into their outputs
    kmer_freq_out = open(opts.kmer_freq, 'w')
    kmerfreq_path = os.path.join(files_dir, 'out.kmerFreq')
    for line in open(kmerfreq_path):
        kmer_freq_out.write("%s" % line)
    kmer_freq_out.close()

    edge_gz_out = open(opts.edge, 'wb')
    with open(files_dir + "/out.edge.gz", mode='rb') as f: # b is important -> binary
        fileContent = f.read()
        edge_gz_out.write(fileContent)
    edge_gz_out.close()
    f.close()

    pre_arc_out = open(opts.pre_arc, 'w')
    pre_arc_path = os.path.join(files_dir, 'out.kmerFreq')
    for line in open(pre_arc_path):
        pre_arc_out.write("%s" % line)
    pre_arc_out.close()

    vertex_out = open(opts.vertex, 'w')
    vertex_path = os.path.join(files_dir, 'out.vertex')
    for line in open(vertex_path):
        vertex_out.write("%s" % line)
    vertex_out.close()

    pregraph_basic_out = open(opts.pregraph_basic, 'w')
    pregraph_basic_path = os.path.join(files_dir, 'out.preGraphBasic')
    for line in open(pregraph_basic_path):
        pregraph_basic_out.write("%s" % line)
    pregraph_basic_out.close()

    config_out = open(opts.soap_config, 'w')
    config_path = os.path.join(tmp_dir, 'soap.config')
    for line in open(config_path):
        config_out.write("%s" % line)
    config_out.close()

    #Delete files not being linked on web page
    os.remove(files_dir + "/out.kmerFreq")
    os.remove(files_dir + "/out.edge.gz")
    os.remove(files_dir + "/out.preArc")
    os.remove(files_dir + "/out.vertex")
    os.remove(files_dir + "/out.preGraphBasic")
    files = os.listdir(files_dir)
    for f in files:
        if f.startswith("tmp"):
            os.remove(os.path.join(files_dir, f))

    #Generate html
    html_report_from_directory(open(html_file, 'w'), files_dir)

    #Clean up temp files
    cleanup_before_exit(tmp_dir)
    #Check results in output file
    if os.path.getsize(opts.pregraph_basic) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    main()
