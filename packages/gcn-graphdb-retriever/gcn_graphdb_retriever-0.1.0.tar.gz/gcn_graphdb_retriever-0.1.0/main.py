from gcn_graphdb_retriever import subject_KEE_pipeline
from gcn_graphdb_retriever import gcn_graph_builder

def main():
    in_filepath = "tests/archive.txt.tar.gz"
    out_filepath = "tests/model_test.txt"
    examples_filepath = "tests/subject_parser_examples.json"
    model = "qwen3:14b"
    silent_errors = False
    examples_num = 1
    subject_KEE_pipeline.subject_pipeline(in_filepath, out_filepath, examples_filepath, model, silent_errors, examples_num)

    in_filepath = "tests/model_test.txt"
    silent_errors = False
    gcn_graph_builder(in_filepath, silent_errors)

if __name__ == "__main__":
    main()