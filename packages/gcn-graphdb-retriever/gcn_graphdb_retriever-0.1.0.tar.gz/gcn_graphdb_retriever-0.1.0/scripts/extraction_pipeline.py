from gcn_graphdb_retriever.chains import GCNSubjectParserChain
from gcn_graphdb_retriever.utils import tarfile_loader

from langchain_ollama import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM

from tqdm.asyncio import tqdm
import argparse
import logging
import json
import time

# Parse arguments
parser = argparse.ArgumentParser(description="GCN Subject Parser Pipeline")
parser.add_argument("--gcn-filepath", required=True, type=str, help="GCN Circular file path")
parser.add_argument("--example-filepath", required=True, type=str, help="Example file used for few shot")
parser.add_argument("-o", "--output", required=True, type=str, help="Write results to file")
parser.add_argument("-e", "--error", required=True, type=str, default="error.log", help="Error log file")
parser.add_argument("--example-num", type=int, default=4, help="Number of examples used for few shot")
parser.add_argument("--llm", type=str, default="deepseek-r1:32b", help="Ollama Large Language Model")
parser.add_argument("--temperature", type=int, default=0.7, help="The temperature of the model")
parser.add_argument("--max-tokens", type=int, default=1000, help="Maximum number of tokens to predict when generating text.")
parser.add_argument("--embeddings", type=str, default="nomic-embed-text", help="Ollama embedding model")
args = parser.parse_args()


logging.basicConfig(
    filename=args.error,
    filemode="w",
    level=logging.ERROR, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# logging.getLogger("httpx").setLevel(logging.ERROR)

# 1. Load the GCN Circular file
filepath = args.gcn_filepath
if filepath.endswith(".tar.gz"):
    docs = tarfile_loader(filepath, silent_errors=True, show_progress=True)
else:
    raise ValueError("Unsupported file format.")

# 2. Load few shot examples file
file_path = args.example_filepath
with open(file_path, 'r', encoding='utf-8') as file:
    examples = json.load(file)

# 3. Construct the extraction chain
logging.info(f"LLM model: {args.llm}")
logging.info(f"Maximum number of tokens: {args.max_tokens}")
logging.info(f"Embedding model: {args.embeddings}")
llm = OllamaLLM(model=args.llm, temperature=args.temperature, num_predict=args.max_tokens)
chain = GCNSubjectParserChain.from_llm(
    llm=llm,
    embeddings=OllamaEmbeddings(model=args.embeddings),
    examples=examples,
    k=args.example_num
) 

# 4. subject queries
queries = [{"circularId": doc.metadata["circularId"], "createdOn": doc.metadata["createdOn"], "subject": doc.metadata["subject"]} for doc in docs]

# 5. run
logging.info(f"Results will be saved to {args.output}")
with open(args.output, "w", encoding="utf-8") as f:
    for query in tqdm(queries, desc="Writing"):
        try:
            response = chain.invoke(query)
            query.update(response)
        except KeyboardInterrupt:
            exit(130)
        except:
            logging.error(f"Error processing query {query}")
            continue

        f.write(json.dumps(query, ensure_ascii=False) + '\n')
        time.sleep(1) # Avoid request too frequency
