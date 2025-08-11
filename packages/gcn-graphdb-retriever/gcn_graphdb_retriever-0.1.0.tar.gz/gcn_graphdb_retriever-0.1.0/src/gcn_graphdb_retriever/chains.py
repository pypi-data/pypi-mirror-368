from gcn_graphdb_retriever.prompts import TASK_DESCRIPTIONS_PROMPT, subject_parser

from langchain.chains.base import Chain
from langchain_core.runnables import Runnable
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import BasePromptTemplate
from langchain_core.callbacks.manager import CallbackManagerForChainRun
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.embeddings import Embeddings
from langchain_core.example_selectors.base import BaseExampleSelector
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_chroma import Chroma

from typing import Any, Dict, List, Optional


class GCNSubjectParserChain(Chain):
    """
    Chain for NASA's GCN Circular subject parser.
    """
    
    extraction_chain: Runnable
    """The chain used to extract the """
    example_selector: BaseExampleSelector
    """The selector used to select similar example"""
    input_key: str = "subject"
    output_key: str = "output"

    @property
    def input_keys(self) -> List[str]:
        """
        Input keys
        """
        return [self.input_key]
    
    @property
    def output_keys(self) -> List[str]:
        """
        Output keys
        """
        return [self.output_key]
    
    @property
    def _chain_type(self) -> str:
        """Return the chain type."""
        return "gcn_subject_parser_chain"

    def _call(
            self, 
            inputs: Dict[str, Any], 
            run_manager: Optional[CallbackManagerForChainRun] = None,
        ) -> Dict[str, str]:
        """
        Extract entities
        """
        # Callback
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        callbacks = _run_manager.get_child()

        # Input
        question = inputs[self.input_key]
        _run_manager.on_text("Input:", end="\n", verbose=self.verbose)
        _run_manager.on_text(question, color="green", end="\n", verbose=self.verbose)

        # Select example
        examples = self.example_selector.select_examples(inputs)
        example_template = "\n".join(["subject: '{}' -> output: {}".format(example["subject"], example["output"]) for example in examples])
        _run_manager.on_text("Selected Examples:", end="\n", verbose=self.verbose)
        _run_manager.on_text(example_template, color="green", end="\n", verbose=self.verbose)

        # Extract Entities
        output = self.extraction_chain.invoke({"subject": question, "examples": example_template}, config={"callbacks": callbacks})
        _run_manager.on_text("Entities Extracted:", end="\n", verbose=self.verbose)
        _run_manager.on_text(output, color="green", end="\n", verbose=self.verbose)
        return {self.output_key: output}

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        embeddings: Embeddings,
        examples: list[dict] = [{"subject": "GRB 151031A: Swift detection of a burst", "output": "{'eventId': ['GRB 151031A'], 'instruments': ['Swift']}"}],
        extraction_prompt: BasePromptTemplate = TASK_DESCRIPTIONS_PROMPT,
        parser: BaseOutputParser = subject_parser,
        k: int = 1,
        **kwargs: Any
    ):
        """
        Initialize from LLM.
        """
        example_selector = SemanticSimilarityExampleSelector.from_examples(
            examples=examples,
            embeddings=embeddings,
            vectorstore_cls=Chroma,
            k=k
        )
        extraction_chain = extraction_prompt | llm | parser

        return cls(
            extraction_chain=extraction_chain,
            example_selector=example_selector,
            **kwargs,
        )

