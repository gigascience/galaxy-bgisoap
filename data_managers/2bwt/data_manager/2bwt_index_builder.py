"""
2bwt_index_builder.py
For generating indexes using 2bwt-builder in Galaxy

This code is based on data_manager_bwa_index_builder by Dan Blankenberg.
"""

import sys
import os
import tempfile
import optparse
import subprocess

from galaxy.util.json import from_json_string, to_json_string


CHUNK_SIZE = 2**20
ONE_GB = 2**30

DEFAULT_DATA_TABLE_NAME = "2bwt_indexes"


def copy_from_directory( data_manager_dict, params, target_directory, sequence_name ):
    input_filename = params['param_dict']['reference_source']['fasta_filename']
    create_symlink = params['param_dict']['reference_source']['create_symlink'] == 'create_symlink'
    if create_symlink:
        data_table_entry = _create_symlink( input_filename, target_directory, sequence_name )
    else:
        if isinstance( input_filename, list ):
            fasta_reader = [ open( filename, 'rb' ) for filename in input_filename ]
        else:
            fasta_reader = open( input_filename )
        data_table_entry = _stream_fasta_to_file( fasta_reader, target_directory, sequence_name )
    _add_data_table_entry( data_manager_dict, "2bwt_indexes", data_table_entry )


def _create_symlink( input_filename, target_directory, dbkey, sequence_id, sequence_name ):
    fasta_base_filename = "%s.fa" % sequence_id
    fasta_filename = os.path.join( target_directory, fasta_base_filename )
    os.symlink( input_filename, fasta_filename )
    return dict( name=sequence_name, path=fasta_base_filename )


def _stream_fasta_to_file( fasta_stream, target_directory,  sequence_name, close_stream=True ):
    fasta_base_filename = "%s.fa" % sequence_name
    fasta_filename = os.path.join( target_directory, fasta_base_filename )
    fasta_writer = open( fasta_filename, 'wb+' )

    if isinstance( fasta_stream, list ) and len( fasta_stream ) == 1:
        fasta_stream = fasta_stream[0]

    if isinstance( fasta_stream, list ):
        last_char = None
        for fh in fasta_stream:
            if last_char not in [ None, '\n', '\r' ]:
                fasta_writer.write( '\n' )
            while True:
                data = fh.read( CHUNK_SIZE )
                if data:
                    fasta_writer.write( data )
                    last_char = data[-1]
                else:
                    break
            if close_stream:
                fh.close()
    else:
        while True:
            data = fasta_stream.read( CHUNK_SIZE )
            if data:
                fasta_writer.write( data )
            else:
                break
        if close_stream:
            fasta_stream.close()

    fasta_writer.close()

    return dict( name=sequence_name, path=fasta_base_filename )


def build_2bwt_index( data_manager_dict, fasta_filename, params, target_directory, sequence_name, data_table_name=DEFAULT_DATA_TABLE_NAME):
    fasta_base_name = os.path.split( fasta_filename )[-1]
    sym_linked_fasta_filename = os.path.join( target_directory, fasta_base_name )
    os.symlink( fasta_filename, sym_linked_fasta_filename )

    args = ['2bwt-builder']
    args.append(sym_linked_fasta_filename)
    tmp_stderr = tempfile.NamedTemporaryFile(prefix="tmp-data-manager-2bwt-index-builder-stderr")

    proc = subprocess.Popen(args=args, shell=False, cwd=target_directory, stderr=tmp_stderr.fileno())
    return_code = proc.wait()
    if return_code:
        tmp_stderr.flush()
        tmp_stderr.seek(0)
        print >> sys.stderr, "Error building index:"
        while True:
            chunk = tmp_stderr.read( CHUNK_SIZE )
            if not chunk:
                break
            sys.stderr.write( chunk )
        sys.exit( return_code )
    tmp_stderr.close()
    data_table_entry = dict(value=sequence_name, name=sequence_name, path=fasta_base_name)
    _add_data_table_entry(data_manager_dict, data_table_name, data_table_entry)


def _add_data_table_entry( data_manager_dict, data_table_name, data_table_entry ):
    data_manager_dict['data_tables'] = data_manager_dict.get( 'data_tables', {} )
    data_manager_dict['data_tables'][ data_table_name ] = data_manager_dict['data_tables'].get( data_table_name, [] )
    data_manager_dict['data_tables'][ data_table_name ].append( data_table_entry )
    return data_manager_dict


def main():
    # Parse command line
    parser = optparse.OptionParser()
    parser.add_option('-o', '--outfile', dest='outfile', action='store', type="string", default=None, help='outfile')
    parser.add_option('-f', '--fasta_filename', dest='fasta_filename', action='store', type="string", default=None, help='fasta_filename')
    parser.add_option('-s', '--sequence_name', dest='sequence_name', action='store', type="string", default=None, help='sequence_name')
    parser.add_option('-n', '--data_table_name', dest='data_table_name', action='store', type="string", default=None, help='data_table_name')
    (options, args) = parser.parse_args()

    outfile = options.outfile

    params = from_json_string(open(outfile).read())
    target_directory = params[ 'output_data' ][0]['extra_files_path']
    os.mkdir(target_directory)
    data_manager_dict = {}

    # Build index files
    build_2bwt_index(data_manager_dict, options.fasta_filename, params, target_directory, options.sequence_name, data_table_name=options.data_table_name or DEFAULT_DATA_TABLE_NAME)

    # Save info to json file
    open(outfile, 'wb').write(to_json_string(data_manager_dict))

if __name__ == "__main__":
    main()