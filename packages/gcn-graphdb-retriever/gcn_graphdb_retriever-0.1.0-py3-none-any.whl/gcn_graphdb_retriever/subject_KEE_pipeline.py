#!/usr/bin/env python
"""
This pipeline is used to extract subject knowledge entities from GCN Circular files.
"""
from langchain_ollama.llms import OllamaLLM

from gcn_graphdb_retriever.utils import tarfile_loader
from gcn_graphdb_retriever.chains_old import SubjectKEEPrompt, subject_parser

from tqdm.asyncio import tqdm
import asyncio
import aiofiles
import argparse
import logging
import json


def subject_pipeline(in_filepath, out_filepath, examples_filepath, model = "qwen3:14b", silent_errors = False, examples_num = 1):
    # 1. Load the GCN Circular file
    filepath = in_filepath
    if filepath.endswith(".tar.gz"):
        docs = tarfile_loader(filepath, silent_errors=silent_errors, show_progress=True)
    else:
        raise ValueError("Unsupported file format.")

    # 2. Construct the extraction chain
    logging.info(f"LLM model: {model}")
    llm = OllamaLLM(model=model, temperature=0.7)
    # if args.llm_fallback:
    #     logging.info(f"The order of fallback LLMs: {args.llm_fallback}")
    #     llm_fallback = [OllamaLLM(model=model) for model in args.llm_fallback]
    #     llm = llm.with_fallbacks(llm_fallback)
    KEE_chain = SubjectKEEPrompt(examples_filepath, k=examples_num) | llm | subject_parser

    # 3. subject queries
    queries = [{"circularId": doc.metadata["circularId"], "createdOn": doc.metadata["createdOn"], "subject": doc.metadata["subject"]} for doc in docs]

    # 4. Define KEE task
    async def kee_task(output_file):
        async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
            async for query in tqdm(queries, desc="Writing"):
                try:
                    response = await KEE_chain.ainvoke(query)
                    # query.update({"output": str(response)})
                    query.update(response)
                except Exception as e:
                    if silent_errors:
                        logging.error(f"Error processing query {query}")
                        continue
                    else:
                        raise e
                await f.write(json.dumps(query, ensure_ascii=False) + '\n')

    # 5. async run
    logging.info(f"Results will be saved to {out_filepath}")
    asyncio.run(kee_task(out_filepath))

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Subject KEE pipeline")
    parser.add_argument("-i", "--input", required=True, type=str, help="GCN Circular file path")
    parser.add_argument("-o", "--output", required=True, type=str, help="Write file")
    parser.add_argument("--llm", type=str, default="qwen3:14b", help="Large Language Model")
    # parser.add_argument("--llm-fallback", type=str, nargs="+", help="Fallback LLM")
    parser.add_argument("--examples", type=str, help="Example file used for few shot")
    parser.add_argument("--examples-num", type=int, default=1, help="Number of examples used for few shot")
    parser.add_argument("-v", "--verbose", action="store_true", help="Use logging output")
    parser.add_argument("-e", "--error", type=str, default="error.log", help="Error log file")
    parser.add_argument("--silent_errors", action="store_true", help="Ignore errors")
    args = parser.parse_args()

    if args.error:
        logging.basicConfig(
            filename=args.error,
            filemode="w",
            level=logging.ERROR, 
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logging.getLogger("httpx").setLevel(logging.ERROR)
    elif args.verbose:
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        logging.getLogger("httpx").setLevel(logging.ERROR)

    filepath = args.input

    subject_pipeline(filepath, args.output, args.examples, args.llm, args.silent_errors, args.examples_num)


if __name__ == "__main__":
    main()