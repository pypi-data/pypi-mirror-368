from gcn_graphdb_retriever import GCNGraphDB
from gcn_graphdb_retriever.utils import tarfile_loader

import logging
import argparse

def gcn_graph_builder(in_filepath, silent_errors = False):

    # 1. Load documents
    filepath = in_filepath
    if filepath.endswith(".tar.gz"):
        docs = tarfile_loader(filepath, silent_errors=silent_errors, show_progress=True)
    else:
        raise ValueError("Unsupported file format.")

    # 2. Connect to Neo4j database
    url = "bolt://localhost:7687"
    username = "neo4j"
    password = "20230049" # Replace with your password
    database = "neo4j"    # Replace with your database name
    with GCNGraphDB(url, username, password) as graph:
        # 3. clean the database. If you want to keep the database, comment this line
        graph.delate_all()

        # 4. Add gcn documents to the database
        graph.run("CREATE CONSTRAINT circularId_unique FOR (c:Circular) REQUIRE c.circularId IS UNIQUE")
        graph.add_gcn_documents(docs)

        # 5. Add subject relationship to the database
        # graph.add_subject_relationship()

        # 6. Add telescope node to the database
        # graph.add_telescope_node()

        graph.refresh_schema()
        print(graph.schema)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Quick view")
    parser.add_argument("-i", "--input", required=True, type=str, help="GCN Circular file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Use logging output")
    parser.add_argument("--silent-errors", action="store_true", help="Ignore errors")
    args = parser.parse_args()

    # Logging configuration
    if args.verbose:
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    gcn_graph_builder(args.input, args.silent_errors)

if __name__ == "__main__":
    main()