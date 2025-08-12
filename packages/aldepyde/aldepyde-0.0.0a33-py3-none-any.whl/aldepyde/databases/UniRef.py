import zlib

from aldepyde.databases.RemoteFileHandler import RemoteFileHandler
from aldepyde.databases._database import _database
from aldepyde.utils import ProgressBar
import os
import gzip

class uniref_parser(_database):
    def __init__(self):
        super().__init__()

    # TODO single entry parsing
    # TODO store metadata upon request

    @staticmethod
    def stream_uniref_gz(filepath, chunk_size=8192, use_progress_bar=False):
        raw_stream, size = _database.open_stream(filepath)
        pbar = ProgressBar(size//chunk_size) if use_progress_bar else None
        decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
        try:
            while True:
                comp_chunk = raw_stream.read(chunk_size)
                if not comp_chunk:
                    break
                if pbar is not None:
                    pbar.update()
                decomp_chunk = decompressor.decompress(comp_chunk)
                if decomp_chunk:
                    yield decomp_chunk
            final = decompressor.flush()
            if final:
                yield final
        finally:
            raw_stream.close()

    @staticmethod
    def download_file(url, destination, chunk_size=8192, use_progress_bar=False):
        raw_stream, size = _database.open_stream(url)
        pbar = ProgressBar(size // chunk_size) if use_progress_bar else None
        with open(destination, 'wb') as fp:
            while True:
                chunk = raw_stream.read(chunk_size)
                if not chunk:
                    break
                if pbar is not None:
                    pbar.update()
                fp.write(chunk)




    @staticmethod
    def stitch_streamed_sequences(stream, as_str=True):
        buffer = b''
        for chunk in stream:
            buffer += chunk
            while buffer.count(b'>') >= 2:
                sequences = [b">" + seq for seq in buffer.split(b">") if seq != b""]
                buffer = buffer[buffer.rfind(b">"):]
                ret_l = [b"".join(sequence.split(b'\n')[1:]).replace(b"\n", b"") for sequence in sequences[:-1]]
                for s in ret_l:
                    yield s if not as_str else s.decode()
        yield uniref_parser._final_sequence(buffer) if not as_str else uniref_parser._final_sequence(buffer).decode()

    @staticmethod
    def _final_sequence(buffer):
        lines = buffer.split(b'\n')
        return b"".join(lines[1:])

    @staticmethod
    def stream_uniref50(chunk_size=8192, use_progress_bar=False, stitch=False):
        if not stitch:
            yield from uniref_parser.stream_uniref_gz('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref50/uniref50.fasta.gz',
                                                  chunk_size=chunk_size, use_progress_bar=use_progress_bar)
        else:
            yield from uniref_parser.stitch_streamed_sequences(uniref_parser.stream_uniref_gz(
                'https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref50/uniref50.fasta.gz',
                                                  chunk_size=chunk_size, use_progress_bar=use_progress_bar))

    @staticmethod
    def stream_uniref90(chunk_size=8192, use_progress_bar=False, stitch=False):
        if not stitch:
            yield from uniref_parser.stream_uniref_gz('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz',
                                                  chunk_size=chunk_size, use_progress_bar=use_progress_bar)
        else:
            yield from uniref_parser.stitch_streamed_sequences(uniref_parser.stream_uniref_gz(
                'https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz',
                chunk_size=chunk_size, use_progress_bar=use_progress_bar))

    @staticmethod
    def stream_uniref100(chunk_size=8192, use_progress_bar=False, stitch=False):
        if not stitch:
            yield from uniref_parser.stream_uniref_gz('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.fasta.gz',
                                                  chunk_size=chunk_size, use_progress_bar=use_progress_bar)
        else:
            yield from uniref_parser.stitch_streamed_sequences(uniref_parser.stream_uniref_gz(
                'https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.fasta.gz',
                chunk_size=chunk_size, use_progress_bar=use_progress_bar))

    @staticmethod
    def download_uniref50(destination='uniref50.fasta.gz', chunk_size=8192, use_progress_bar=False):
        uniref_parser.download_file('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref50/uniref50.fasta.gz', destination=destination,
                                    chunk_size=chunk_size, use_progress_bar=use_progress_bar)

    @staticmethod
    def download_uniref90(destination='uniref90.fasta.gz', chunk_size=8192, use_progress_bar=False):
        uniref_parser.download_file('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz', destination=destination,
                                    chunk_size=chunk_size, use_progress_bar=use_progress_bar)
    @staticmethod
    def download_uniref100(destination='uniref100.fasta.gz', chunk_size=8192, use_progress_bar=False):
        uniref_parser.download_file('https://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref100/uniref100.fasta.gz', destination=destination,
                                    chunk_size=chunk_size, use_progress_bar=use_progress_bar)