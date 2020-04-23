"""
Validate a KGTK file, producing a clean KGTK file (no comments, whitespace lines, etc.) as output.
"""

from pathlib import Path
import sys
import typing

from kgtk.join.enumnameaction import EnumNameAction
from kgtk.join.kgtkformat import KgtkFormat
from kgtk.join.kgtkreader import KgtkReader, KgtkReaderErrorAction
from kgtk.join.kgtkwriter import KgtkWriter

def parser():
    return {
        'help': 'Validate a KGTK file and output a clean copy: no comments, whitespace lines, invalid lines, etc. '
    }


def add_arguments(parser):
    """
    Parse arguments
    Args:
        parser (argparse.ArgumentParser)
    """
    parser.add_argument(      "input_file", nargs="?", help="The KGTK file to read", type=Path, nargs='?')
    
    parser.add_argument(      "output_file", nargs="?", help="The KGTK file to write", type=Path, nargs='?')
    
    parser.add_argument(      "--allow-comment-lines", dest="ignore_comment_lines",
                              help="When specified, do not ignore comment lines.", action='store_false')

    parser.add_argument(      "--allow-empty-lines", dest="ignore_empty_lines",
                              help="When specified, do not ignore empty lines.", action='store_false')

    parser.add_argument(      "--allow-long-lines", dest="ignore_long_lines",
                              help="When specified, do not ignore lines with extra columns.", action='store_false')

    parser.add_argument(      "--allow-short-lines", dest="ignore_short_lines",
                              help="When specified, do not ignore lines with missing columns.", action='store_false')
    
    parser.add_argument(      "--allow-whitespace-lines", dest="ignore_whitespace_lines",
                              help="When specified, do not ignore whitespace lines.", action='store_false')

    parser.add_argument(      "--column-separator", dest="column_separator",
                              help="Column separator.", type=str, default=KgtkReader.COLUMN_SEPARATOR)

    parser.add_argument(      "--input-compression", dest="input_compression_type", help="Specify the input file compression type, otherwise use the extension.")
    
    parser.add_argument(      "--error-action", dest="error_action",
                              help="The action to take for error input lines",
                              type=KgtkReaderErrorAction, action=EnumNameAction, default=KgtkReaderErrorAction.STDERR)
    
    parser.add_argument(      "--error-limit", dest="error_limit",
                              help="The maximum number of errors to report before failing", type=int, default=KgtkReader.ERROR_LIMIT_DEFAULT)

    parser.add_argument(      "--fill-short-lines", dest="fill_short_lines",
                              help="Fill missing trailing columns in short lines with empty values.", action='store_true')

    parser.add_argument(      "--force-column-names", dest="force_column_names", help="Force the input file column names.", nargs='+')
    
    parser.add_argument(      "--gzip-in-parallel", dest="gzip_in_parallel", help="Execute gzip in parallel.", action='store_true')
        
    parser.add_argument(      "--gzip-queue-size", dest="gzip_queue_size",
                              help="Queue size for parallel gzip.", type=int, default=KgtkReader.GZIP_QUEUE_SIZE_DEFAULT)
    
    parser.add_argument(      "--mode", dest="mode",
                              help="Determine the KGTK input file mode.", type=KgtkReader.Mode, action=EnumNameAction, default=KgtkReader.Mode.AUTO)

    # Not yet implemented:
    # parser.add_argument(      "--output-compression", dest="input_compression_type", help="Specify the input file compression type, otherwise use the extension.")
    
    parser.add_argument(      "--skip-first-record", dest="skip_first_record", help="Skip the first input data record when forcing column names.",
                              action='store_true')

    parser.add_argument(      "--truncate-long-lines", dest="truncate_long_lines",
                              help="Remove excess trailing columns in long lines.", action='store_true')

    parser.add_argument("-v", "--verbose", dest="verbose", help="Print additional progress messages.", action='store_true')

    parser.add_argument(      "--very-verbose", dest="very_verbose", help="Print additional progress messages.", action='store_true')

def run(input_file: typing.Optional[Path],
        output_file: typing.Optional[Path],
        force_column_names: typing.Optional[typing.List[str]] = None,
        skip_first_record: bool = False,
        fill_short_lines: bool = False,
        truncate_long_lines: bool = False,
        error_action: KgtkReaderErrorAction = KgtkReaderErrorAction.STDERR,
        error_limit: int = KgtkReader.ERROR_LIMIT_DEFAULT,
        ignore_empty_lines: bool = True,
        ignore_comment_lines: bool = True,
        ignore_whitespace_lines: bool = True,
        ignore_blank_node1_lines: bool = True,
        ignore_blank_node2_lines: bool = True,
        ignore_blank_id_lines: bool = True,
        ignore_short_lines: bool = True,
        ignore_long_lines: bool = True,
        input_compression_type: typing.Optional[str] = None,
        # output_compression_type: typing.Optional[str] = None, # Not yet implemented
        gzip_in_parallel: bool = False,
        gzip_queue_size: int = KgtkReader.GZIP_QUEUE_SIZE_DEFAULT,
        column_separator: str = KgtkFormat.COLUMN_SEPARATOR,
        input_mode: KgtkReader.Mode = KgtkReader.Mode.AUTO,
        output_mode: KgtkWriter.Mode = KgtkWriter.Mode.AUTO,
        verbose: bool = False,
        very_verbose: bool = False,
)->int:
    # import modules locally
    from kgtk.exceptions import KGTKException

    try:
        if verbose:
            if input_file is not None:
                print("Cleaning data from '%s'" % str(input_file), file=sys.stderr)
            else:
                print ("Cleaning data from stdin", file=sys.stderr)
            if output_file is not None:
                print("Writing data to '%s'" % str(output_file), file=sys.stderr)
            else:
                print ("Writing data to stdin", file=sys.stderr)
                
        kr: KgtkReader = KgtkReader.open(input_file,
                                         force_column_names=force_column_names,
                                         skip_first_record=skip_first_record,
                                         fill_short_lines=fill_short_lines,
                                         truncate_long_lines=truncate_long_lines,
                                         error_action=error_action,
                                         error_limit=error_limit,
                                         ignore_comment_lines=ignore_comment_lines,
                                         ignore_whitespace_lines=ignore_whitespace_lines,
                                         ignore_blank_node1_lines=ignore_blank_node1_lines,
                                         ignore_blank_node2_lines=ignore_blank_node2_lines,
                                         ignore_blank_id_lines=ignore_blank_id_lines,
                                         ignore_short_lines=ignore_short_lines,
                                         ignore_long_lines=ignore_long_lines,
                                         compression_type=input_compression_type,
                                         gzip_in_parallel=gzip_in_parallel,
                                         gzip_queue_size=gzip_queue_size,
                                         column_separator=column_separator,
                                         mode=input_mode,
                                         verbose=verbose, very_verbose=very_verbose)

        kw: KgtkWriter = KgtkWriter.open(kr.column_names,
                                         output_file,
                                         gzip_in_parallel=gzip_in_parallel,
                                         gzip_queue_size=gzip_queue_size,
                                         column_separator=column_separator,
                                         mode=output_mode,
                                         verbose=verbose, very_verbose=very_verbose)
        
        line_count: int = 0
        line: typing.List[str]
        for line in kr:
            kw.write(line)
            line_count += 1

        kw.close()
        if verbose:
            print("Copied %d clean data lines" % line_count, file=sys.stderr)
        return 0

    except Exception as e:
        raise KGTKException(e)

