import pytest


from gcn_graphdb_retriever.utils import header_regex_match, tarfile_loader


def test_tarfile_loader():
    docs = tarfile_loader(file_path="./tests/archive.txt.tar.gz")
    assert len(docs) > 0

def test_header_regex_match():
    pass