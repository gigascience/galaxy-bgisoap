"""
A Galaxy wrapper script for Corrector_AR_v2.0
Peter Li - GigaScience and BGI-HK
"""

import optparse
import os
import shutil
import subprocess
import sys
import tempfile
import fnmatch
import re


def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()


def cleanup_before_exit(tmp_dir):
    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)


def html_report_from_directory(html_out, dir):
    html_out.write('<html>\n<head>\n</head>\n<body>\n<font face="arial">\n<p>Corrector AR outputs</p>\n<p/>\n')
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
    parser.add_option("", "--space_consecutive_settings_type", dest="space_consecutive_settings_type")
    parser.add_option("", "--filelist", dest="filelist")
    parser.add_option("", "--freq_cz", dest="freq_cz")
    parser.add_option("", "--freq_cz_len", dest="freq_cz_len")

    parser.add_option("-k", "--kmer_size", dest="kmer_size")
    parser.add_option("-l", "--consec_low_freq_cutoff", dest="consec_low_freq_cutoff")
    parser.add_option("-Q", "--ascii_shift_quality_value", dest="ascii_shift_quality_value")
    # Removed from galaxy interface to keep under own control
    # parser.add_option("-t", "--thread_num", dest="thread_num")
    parser.add_option("", "--space_freq_cz", dest="space_freq_cz")
    parser.add_option("", "--space_freq_cz_len", dest="space_freq_cz_len")
    parser.add_option("-K", "--space_kmer", dest="space_kmer")
    parser.add_option("-s", "--space_seed", dest="space_seed")
    parser.add_option("-L", "--space_low_freq_cutoff", dest="space_low_freq_cutoff")

    parser.add_option("", "--default_full_settings_type", dest="default_full_settings_type")
    # Custom params
    parser.add_option("-c", "--max_read_change", dest="max_read_change")
    parser.add_option("-n", "--max_node_num", dest="max_node_num")
    parser.add_option("-a", "--remove_suspicious_data", dest="remove_suspicious_data")
    parser.add_option("-e", "--trim_suspicious_end_regions_Q", dest="trim_suspicious_end_regions_Q")
    parser.add_option("-w", "--trim_error_bases_Q", dest="trim_error_bases_Q")
    parser.add_option("-q", "--qual_threshold_error_bases", dest="qual_threshold_error_bases")
    parser.add_option("-x", "--length_trim_low_qual_ends", dest="length_trim_low_qual_ends")
    parser.add_option("-m", "--min_length_high_freq_region", dest="min_length_high_freq_region")
    parser.add_option("-j", "--convert_reads_into_paired_end_file", dest="convert_reads_into_paired_end_file")
    parser.add_option("-o", "--output_format", dest="output_format")

    parser.add_option("-r", "--min_length_trimmed_read", dest="min_length_trimmed_read")

    # HTML output
    parser.add_option("", "--html_file", dest="html_file")
    parser.add_option("", "--html_file_files_path", dest="html_file_files_path")
    # Outputs for reads
    parser.add_option("", "--corrected_forward", dest="corrected_forward")
    parser.add_option("", "--corrected_reverse", dest="corrected_reverse")
    parser.add_option("", "--corrected_single", dest="corrected_single")
    opts, args = parser.parse_args()

    # Create directory to process and store Corrector outputs
    html_file = opts.html_file
    job_work_dir = opts.html_file_files_path

    # Temp directory for data processing
    tmp_dir = tempfile.mkdtemp(prefix="tmp-corrector-")

    # Run Corrector
    rex = re.compile('database/(.*)/dataset_')
    # Create replacement text using html_file
    # Split string into tokens
    tokens = html_file.split("/")
    # Get second to last token
    userId = tokens[len(tokens) - 2]
    files_dir = rex.sub("database/files/" + userId + "/dataset_", job_work_dir)
    files_dir += "/"
    # print "New html dir: ", files_dir
    # Create directory
    if not os.path.exists(files_dir):
        # print "HTML directory does not exist"
        try:
            os.makedirs(files_dir)
        except:
            pass

    # Set up command line call
    if opts.space_consecutive_settings_type == "consecutive" and opts.default_full_settings_type == "default":
        cmd = "Corrector_AR_v2.0 -k %s -l %s -Q %s -t %s %s %s %s" % (opts.kmer_size, opts.consec_low_freq_cutoff, opts.ascii_shift_quality_value, thread_num, opts.freq_cz, opts.freq_cz_len, opts.filelist)
    if opts.space_consecutive_settings_type == "consecutive" and opts.default_full_settings_type == "full":
        cmd = "Corrector_AR_v2.0 -k %s -l %s -Q %s -t %s -c %s -n %s -a %s -e %s -w %s -q %s -m %s -j %s -o %s %s %s %s" % (opts.kmer_size, opts.consec_low_freq_cutoff, opts.ascii_shift_quality_value, thread_num, opts.max_read_change, opts.max_node_num, opts.remove_suspicious_data, opts.trim_suspicious_end_regions_Q, opts.trim_error_bases_Q, opts.qual_threshold_error_bases, opts.min_length_high_freq_region, opts.convert_reads_into_paired_end_file, opts.output_format, opts.freq_cz, opts.freq_cz_len, opts.filelist)
        if opts.length_trim_low_qual_ends != "":
            cmd += " -x %s" % opts.length_trim_low_qual_ends
    if opts.space_consecutive_settings_type == "space" and opts.default_full_settings_type == "default":
        cmd = "Corrector_AR_v2.0 -k %s -l %s -K %s -s %s -L %s -Q %s -t %s %s %s %s %s %s" % (opts.kmer_size, opts.consec_low_freq_cutoff, opts.space_kmer, opts.space_seed, opts.space_low_freq_cutoff, opts.ascii_shift_quality_value, thread_num, opts.freq_cz, opts.freq_cz_len, opts.space_freq_cz, opts.freq_cz_len, opts.filelist)
    if opts.space_consecutive_settings_type == "space" and opts.default_full_settings_type == "full":
        cmd = "Corrector_AR_v2.0 -k %s -l %s -K %s -s %s -L %s -Q %s -t %s -c %s -n %s -a %s -e %s -w %s -q %s -m %s -j %s -o %s %s %s %s %s %s" % (opts.kmer_size, opts.consec_low_freq_cutoff, opts.space_kmer, opts.space_seed, opts.space_low_freq_cutoff, opts.ascii_shift_quality_value, thread_num, opts.max_read_change, opts.max_node_num, opts.remove_suspicious_data, opts.trim_suspicious_end_regions_Q, opts.trim_error_bases_Q, opts.qual_threshold_error_bases, opts.min_length_high_freq_region, opts.convert_reads_into_paired_end_file, opts.output_format, opts.freq_cz, opts.freq_cz_len, opts.space_freq_cz, opts.freq_cz_len, opts.filelist)
        if opts.length_trim_low_qual_ends != "":
            cmd += " -x %s" % opts.length_trim_low_qual_ends

    # print "Command executed: ", cmd

    # Execute Corrector
    try:
        tmp_out_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stdout = open(tmp_out_file, 'w') # Contains Corrector stdout log
        tmp_err_file = tempfile.NamedTemporaryFile(dir=tmp_dir).name
        tmp_stderr = open(tmp_err_file, 'w')

        # Perform Corrector_AR call
        proc = subprocess.Popen(args=cmd, shell=True, cwd=files_dir, stdout=tmp_stdout, stderr=tmp_stderr)
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
        raise Exception, 'Problem performing Corrector AR process: ' + str(e)

    # Copy Excel file into HTML file dir
    xlspath = opts.filelist + ".QC.xls"
    shutil.move(xlspath, files_dir)

    # Need to move and rename files for galaxy for display multiple files
    filelist = open(opts.filelist)

    # Check file format
    fileformat = ""
    if opts.default_full_settings_type == "default":
        fileformat = ".fq.gz"
    elif opts.default_full_settings_type == "full":
        if opts.output_format == "0":
            fileformat = ".fa.gz"
        elif opts.output_format == "1":
            fileformat = ".fq.gz"
        elif opts.output_format == "2":
            fileformat = ".fa"
        elif opts.output_format == "3":
            fileformat = ".fq"

    # Read file paths in read.lst
    pair_index = 1
    done_single = False
    for path in filelist:
        # Read corrected forward and reverse files into outputs
        print "File format: ", fileformat

        if done_single == False:
            # Deal with single.gz file
            try:
                # Check file exists
                if os.path.exists(path.rstrip() + ".cor.single" + fileformat):
                    source_single = path.rstrip() + ".cor.single" + fileformat

                else:
                    if fileformat == ".fq.gz":
                        source_single = path.rstrip() + ".cor.single.fq"
                    elif fileformat == ".fa.gz":
                        source_single = path.rstrip() + ".cor.single.fa"

                print source_single

                os.path.exists(source_single)
                if fnmatch.fnmatch(source_single, '*single*'):
                    corrected_single_in = open(opts.corrected_single, 'w')
                file_out2 = open(source_single, 'r')
                data = file_out2.read()
                corrected_single_in.write(data)
                corrected_single_in.close()
                file_out2.close()
                done_single = True
            except IOError:
                print 'Cannot find ' + source_single
                raise

        source = path.rstrip() + ".cor.pair_" + str(pair_index) + fileformat
        if fnmatch.fnmatch(source, '*pair_1*'):
            corrected_forward_in = open(opts.corrected_forward, 'w')
            file_out = open(source, 'r')
            data = file_out.read()
            corrected_forward_in.write(data)
            corrected_forward_in.close()
            file_out.close()

            #  # Deal with single.gz file
            #  try:
            #      # Check file exists
            #      if os.path.exists(path.rstrip() + ".cor.single" + fileformat):
            #          source_single = path.rstrip() + ".cor.single" + fileformat
            # 
            #      else:
            #          if fileformat == ".fq.gz":
            #              source_single = path.rstrip() + ".cor.single.fq"
            #          elif fileformat == ".fa.gz":
            #              source_single = path.rstrip() + ".cor.single.fa"
            # 
            #      print source_single
            # 
            #      os.path.exists(source_single)
            #      if fnmatch.fnmatch(source_single, '*single*'):
            #          corrected_single_in = open(opts.corrected_single, 'w')
            #      file_out2 = open(source_single, 'r')
            #      data = file_out2.read()
            #      corrected_single_in.write(data)
            #      corrected_single_in.close()
            #      file_out2.close()
            #  except IOError:
            #      print 'Cannot find ' + source_single
            #      raise


        elif fnmatch.fnmatch(source, '*pair_2*'):
            corrected_reverse_in = open(opts.corrected_reverse, 'w')
            file_out = open(source, 'r')
            data = file_out.read()
            corrected_reverse_in.write(data)
            corrected_reverse_in.close()
            file_out.close()

        # Move cor.stat files to html dir
        source = path.rstrip() + ".cor.stat"
        shutil.move(source, files_dir)

        # Move cor pair single stat files to html dir if present
        source = path.rstrip() + ".cor.pair.single.stat"
        # Check file is present
        if os.path.isfile(source):
            shutil.move(source, files_dir)

        pair_index += 1
        if pair_index == 3:
            pair_index = 1
    filelist.close()

    # Generate html
    html_report_from_directory(open(html_file, 'w'), files_dir)

    # Clean up temp files
    cleanup_before_exit(tmp_dir)
    # Check results in output file
    if os.path.getsize(opts.html_file) > 0:
        sys.stdout.write('Status complete')
    else:
        stop_err("The output is empty")

if __name__ == "__main__":
    main()
