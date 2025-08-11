from langchain.output_parsers.enum import EnumOutputParser
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum
import json
import logging


# Pydantic model used for output parsing
class Subject(BaseModel):
    eventId: str = Field(..., description="Celestial object name")
    instruments: List[str] = Field(..., description="astronomical instrument names")
subject_parser = JsonOutputParser(pydantic_object=Subject)

class Binary(Enum):
    YES = "yes"
    NO = "no"
yn_parser = EnumOutputParser(enum=Binary)


# Template used for prompting
TASK_DESCRIPTIONS_TEMPLATE = """
You are an experienced astronomer, capable of easily recognizing knowledge entities ("transient event" and "astronomical instrument names") in a sentence. Specifically, your task is to perform Knowledge Entity Extraction (KEE) task from the subject line of an astronomical alert (e.g., a GCN Circular). The output should be provided in JSON format: {"eventId": "XXX", "instruments": ["XXX"]}.
"""

ENTITY_DEFINITIONS_TEMPLATE = """
The subject line typically starts with the name or unique identifier of the transient event, followed by observation details (e.g., the instrument used, detection type, or other relevant information). A colon (:) is commonly used to separate these two components for clarity.
- eventId: The celestial object or transient event identifier. 
    1) Usually structured as follows: Prefix indicates the event type or discovery instrument (e.g., GRB for gamma-ray bursts, LIGO/Virgo/KAGRA for gravitational wave events, IceCube for neutrino events). Date encoding in "YYMMDD" format. Suffix (Optional) used to distinguish multiple events on the same day (e.g., A, B, C). For GRB, always include a space between the prefix and the date-suffix (e.g., GRB 221009A is correct; GRB221009A is incorrect).
    2) Non-Standard Designations: Retain their original format, such as Fermi trigger numbers, Soft gamma repeaters, Zwicky Transient Facility (e.g., Fermi trigger No 737476171, SGR 1935+2154, ZTF22aaajecp, AT2022cmc, 1ES 1959+650).
- instruments: The astronomical instrument used in the observation.
    1) May include different types of telescopes (e.g., SAO RAS, pt5m), satellite (e.g., Swift, Fermi), instrument abbreviations (e.g., BAT, XRT, UVOT), observatories (e.g., RBO) or collaborative networks (e.g., IPN, MASTER-Net).
    2) The instrument on the telescope uses a slash / as a separator (e.g., Swift/BAT is correct; Swift BAT or Swift-BAT are incorrect).
    3) The sentence may contain some telescope names represented by their aperture length and address information. 
"""

TASK_EMPHASIS_TEMPLATE = """
1) Ensure that "eventId" and "instruments" follow standard naming conventions.
2) Don't create entities that's not in the given sentence. 
3) Always return a complete dictonary with empty values where information is missing.
4) Verify entities before returning them.
5) Please ensure that all entities from the sentence have been extracted.
6) Always enclose the output inside 3 backticks.
"""

# Prompt used for task descriptions
TASK_DESCRIPTIONS_PROMPT = PromptTemplate.from_template(
    template=TASK_DESCRIPTIONS_TEMPLATE, template_format="jinja2"
)

ENTITY_DEFINITIONS_PROMPT = PromptTemplate.from_template(
    template=ENTITY_DEFINITIONS_TEMPLATE, template_format="jinja2"
)

TASK_EMPHASIS_PROMPT = PromptTemplate.from_template(
    template=TASK_EMPHASIS_TEMPLATE, template_format="jinja2"
)

# Chain used for specific tasks
def SubjectKEEPrompt(file_path, k=3):
    """
    The prompt consists of four key components: Task Descriptions, Entity Definitions, Task Emphasis, and Task Examples. These elements work together to guide the model in extracting specific entities from text (arXiv:2310.17892).
    """
    logging.info(f"Number of examples used for few shot: {k}")

    # Prompt template
    prefix = TASK_DESCRIPTIONS_TEMPLATE + ENTITY_DEFINITIONS_TEMPLATE + TASK_EMPHASIS_TEMPLATE + "\n" + """{{ format_instructions }}\n\nHere are some examples to help you understand the task better:\n------"""
    suffix = "------\n\nPlease extract the celestial object names and astronomical instrument names from the following subject: '{{ subject }}'\nUse Triple Backticks to Signal **JSON Output**:" 

    # examples
    with open(file_path, 'r', encoding='utf-8') as file:
        examples = json.load(file)
    example_prompt = PromptTemplate.from_template("subject: '{{ subject }}' -> output: {{ output }}", template_format="jinja2")
    # VectorStore
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OllamaEmbeddings(model="nomic-embed-text"),
        Chroma,
        k=k,
    )
    # Few-shot examples
    return FewShotPromptTemplate(
        example_prompt=example_prompt,
        example_selector=example_selector,
        example_separator='\n',
        prefix=prefix,
        suffix=suffix,
        input_variables=["subject"],
        template_format="jinja2",
        partial_variables={"format_instructions": subject_parser.get_format_instructions()},
    )

def cypher_generation_chain():
    """Generate Cypher statement, use it to look up in db and answer question."""
    pass

def qa_chain():
    """Chain for question-answering against a graph by generating Cypher statements."""
    pass
