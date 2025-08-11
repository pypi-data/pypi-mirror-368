from langchain_core.prompts.prompt import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Literal
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser


class Subject(BaseModel):
    eventId: List[str] = Field(..., description="Celestial object name")
    instruments: List[str] = Field(..., description="Astronomical instrument names")
subject_parser = JsonOutputParser(pydantic_object=Subject)


_TASK_DESCRIPTIONS_TEMPLATE = """
You are an experienced astronomer, capable of easily recognizing knowledge entities ("celestial object names" and "astronomical instrument names") in a sentence. Specifically, your task is to perform Knowledge Entity Extraction (KEE) task from the subject line of a GCN Circular. The output should be provided in JSON format: {"eventId": ["XXX"], "instruments": ["XXX"]}.

The subject line typically starts with the name of the celestial object, followed by observation details (e.g., the instrument used, detection type, or other relevant information). A colon (:) is commonly used to separate these two components for clarity.
- eventId: Celestial object name. The naming of astronomical events typically adheres to a 'prefix + core identifier' format, where the prefix indicates the type of event or the instrument that discovered it.
- instruments: The astronomical instrument used in the observation. The instruments include different types of telescopes, satellites, observatories or collaborative networks.

1) Please ensure that all entities from the sentence have been extracted.
2) Don't create entities that's not in the given sentence. 
3) Do not overthink or repeated reason if there is ambiguity.
4) Always return a complete dictonary with empty values where information is missing.
5) Always enclose the output inside 3 backticks.

Here are some examples to help you understand the task better:
{{examples}}

Please extract the celestial object names and astronomical instrument names from the following subject: '{{ subject }}'
Use Triple Backticks to Signal **JSON Output**:
"""
TASK_DESCRIPTIONS_PROMPT = PromptTemplate.from_template(
    template=_TASK_DESCRIPTIONS_TEMPLATE, template_format="jinja2"
)


