from langchain_core.documents import Document
from langchain_core.utils import get_from_dict_or_env
# from langchain_neo4j.chains.graph_qa.cypher_utils import CypherQueryCorrector
# from neo4j_graphrag.retrievers.text2cypher import extract_cypher
from neo4j_graphrag.schema import (
    get_structured_schema, 
    format_schema,
    _value_sanitize,
)

from typing import Any, Dict, List, Optional, Type
import neo4j
import logging
from tqdm import tqdm

class GCNGraphDB:
    """
    A class to handle the connection to the Neo4j database and perform operations.
    """
    def __init__(
            self, 
            url: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            database: Optional[str] = None,
            driver_config: Optional[Dict] = None,
        ):
        """
        Create a new Neo4j graph wrapper instance.

        Args:
            url (Optional[str]): The URL of the Neo4j database server.
            username (Optional[str]): The username for database authentication.
            password (Optional[str]): The password for database authentication.
            database (str): The name of the database to connect to. Default is 'neo4j'.
            driver_config (Dict): Configuration passed to Neo4j Driver.
        """
        url = get_from_dict_or_env({"url": url}, "url", "NEO4J_URI")
        # if username and password are "", assume Neo4j auth is disabled
        if username == "" and password == "":
            auth = None
        else:
            username = get_from_dict_or_env(
                {"username": username},
                "username",
                "NEO4J_USERNAME",
            )
            password = get_from_dict_or_env(
                {"password": password},
                "password",
                "NEO4J_PASSWORD",
            )
            auth = (username, password)
        database = get_from_dict_or_env(
            {"database": database}, "database", "NEO4J_DATABASE", "neo4j"
        )
        
        self._driver = neo4j.GraphDatabase.driver(
            url, auth=auth, **(driver_config or {})
        )
        self._database = database

        # Verify connection
        try:
            self._driver.verify_connectivity()
            logging.info("Connected to Neo4j.")
        except neo4j.exceptions.ServiceUnavailable:
            raise ValueError(
                "Could not connect to Neo4j. "
                "Please ensure that the url is correct"
            )
        except neo4j.exceptions.AuthError:
            raise ValueError(
                "Could not connect to Neo4j. "
                "Please ensure that the username and password are correct"
            )

        # Initialize schema
        self.schema: str = ""
        self.structured_schema: Dict[str, Any] = {}

    def refresh_schema(self) -> None:
        """
        Refreshes the Neo4j graph schema information.

        Raises:
            RuntimeError: If the connection has been closed.
        """
        self._check_driver_state()
        self._schema = get_structured_schema(
            driver=self._driver,
            database=self._database
        )
        self.schema = format_schema(schema=self._schema, is_enhanced=False)

    def run(
            self, 
            query: str, 
            params: dict = {},
            session_params: dict = {},
        ) -> None:
        """
        This method is used for executing queries that do not return any results.

        Args:
            query (str): The Cypher query to execute.
            params (dict): The parameters to pass to the query.
            database (str): The name of the database to connect to. Default is 'neo4j'.
            session_params (dict): Parameters to pass to the session used for executing the query.
        """
        self._check_driver_state()
        if not session_params:
            session_params.setdefault("database", self._database)
        with self._driver.session(**session_params) as session:
            session.run(query, params)
            
    def query(
            self, 
            query: str, 
            params: dict = {},
            session_params: dict = {},
            sanitize: bool = True,
        ) -> List[Dict[str, Any]]:
        """
        This method is used for executing queries that return results.

        Args:
            query (str): The Cypher query to execute.
            params (dict): The parameters to pass to the query.
            database (str): The name of the database to connect to. Default is 'neo4j'.
            session_params (dict): Parameters to pass to the session used for executing the query.
            sanitize (bool): Sanitizes the input by removing embedding-like values. Default is True.
            
        Returns:
            List[Dict[str, Any]]: The list of dictionaries containing the query results.
        """
        self._check_driver_state()
        if not session_params:
            session_params.setdefault("database", self._database)
        with self._driver.session(**session_params) as session:
            result = session.run(query, params)
            json_data = result.data()
            if sanitize:
                json_data = [_value_sanitize(el) for el in json_data]
            return json_data

    def retrieve(self):
        """
        Retrieve documents from the database.
        """
        pass


    def add_gcn_circular_node(
            self, 
            documents: List[Document], 
            session_params: dict = {},
        ) -> None:
        """
        This method constructs nodes in the graph based on the provided gcn documents.

        Args:
            documents (list[Document]): A list of gcn documents to be added to the graph.
            session_params (dict): Parameters to pass to the session used for executing the query.
        """
        _query = (
            "MERGE (d:Circular {circularId: $metadata.circularId}) "
            "SET d.content = $page_content "
            "SET d += $metadata "
        )
        
        logging.info("Adding documents to the database...")
        for doc in tqdm(documents):
            self.run(
                _query,
                params={"metadata": doc.metadata, "page_content": doc.page_content},
                session_params=session_params,
            )

    def add_subject_relationship(
            self,
            subject_relations: List[Dict[str, Any]],
            session_params: dict = {},
        ) -> None:
        """
        Add the relationship between the event and the telescope from the subject.
        """
        _ce_query = (
            "MATCH (c:Circular {circularId: $circularId}) "
            "MERGE (e:Event {name: $eventId}) "
            "MERGE (c) -[r:REPORT {createdOn: $createdOn}]-> (e) "
        )
        _ct_query = (
            "MATCH (c:Circular {circularId: $circularId}) "
            "UNWIND $telescopes AS telescope "
            "MERGE (t:Telescope {name: telescope}) "
            "MERGE (c) -[u:USE {createdOn: $createdOn}]-> (t) "
        )
        _te_query = (
            "MATCH (e:Event {name: $eventId}) "
            "UNWIND $telescopes AS telescope "
            "MATCH (t:Telescope {name: telescope}) "
            "MERGE (e) -[:OBSERVED {circularId: $circularId}]-> (t) "
        )
        logging.info("Adding subject relationships to the database...")
        for relation in tqdm(subject_relations):
            circularId = relation.get("circularId")
            createdOn = relation.get("createdOn")
            eventId = relation.get("eventId")
            telescopes = relation.get("telescopes")
            if eventId:
                print(f"Add eventId: {eventId}")
                self.run(
                    _ce_query,
                    params={
                        "circularId": relation.get("circularId"),
                        "eventId": eventId,
                        "createdOn": createdOn
                    },
                    session_params=session_params,
                )
            if telescopes:
                print(f"Add telescopes: {telescopes}")
                self.run(
                    _ct_query,
                    params={
                        "circularId": relation.get("circularId"),
                        "telescopes": telescopes,
                        "createdOn": createdOn
                    },
                    session_params=session_params,
                )
            if eventId and telescopes:
                print(f"Add both")
                self.run(
                    _te_query,
                    params={
                        "circularId": relation.get("circularId"),
                        "eventId": eventId,
                        "telescopes": telescopes
                    },
                    session_params=session_params,
                )


    def add_telescope_node(filepath: str) -> None:
        # pd.read_csv(filepath)
        pass

    def find_circular(
            self,
            circularId: str,
            session_params: dict = {},
        ) -> List[Dict[str, Any]]:
        """
        Find a circular in the database by its ID.
        """
        query = (
            "MATCH (d:Circular) "
            "WHERE d.circularId = $circularId "
            "RETURN d.content "
        )
        params={"circularId": circularId}
        return self.query(query, params=params, session_params=session_params)

    def find_event(
            self, 
            event_id: str
        ) -> List[Dict[str, Any]]:
        """
        Find a transient event in the database by its ID.
        """
        query = (
            "MATCH (e:Event) "
            "WHERE e.name = $event_id "
            "RETURN e "
        )
        return self.query(query, event_id=event_id)

    # def QAChain(
    #         self, 
    #         query: str, 
    #         input_key: str = "query", 
    #         output_key: str = "result", 
    #         top_k: int = 10
    #     ) -> list[Document]:
    #     """
    #     Chain for question-answering against a graph by generating Cypher statements.
    #     """
    #     # 1. Generate Cypher statement
    #     generated_cypher = cypher_generation_chain(query, input_key, output_key, top_k)
    #     cypher = extract_cypher(generated_cypher)
    #     logging.info(f"Generated Cypher: {cypher}")

    #     # 2. Use Cypher statement to look up in db
    #     result = self.query(cypher, database)
    #     # 3. Answer question
    #     answer = qa_chain(result, query, database, input_key, output_key)
    #     return answer
    
    def delate_all(self) -> None:
        """
        Delete all nodes and relationships in the database. Please use with caution.

        Note: APOC are used to delete schema constraints and indexes.
        """
        with self._driver.session(database=self._database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            logging.info("All nodes and relationships deleted from the database.")
            try:
                session.run("CALL apoc.schema.assert({}, {})")
                logging.info("Schema constraints and indexes have been deleted.")
            except Exception as e:
                raise RuntimeError(
                    "Failed to delete schema constraints and indexes. "
                    "Please ensure APOC procedures are installed."
                )

    def _check_driver_state(self) -> None:
        """
        Check if the driver is available and ready for operations.

        Raises:
            RuntimeError: If the driver has been closed or is not initialized.
        """
        if not hasattr(self, "_driver"):
            raise RuntimeError(
                "Cannot perform operations - Neo4j connection has been closed"
            )

    def close(self) -> None:
        """
        Don't forget to close the driver connection when you are finished with it.
        """
        if hasattr(self, "_driver"):
            self._driver.close()
            delattr(self, "_driver")
            logging.info("Explicitly close the Neo4j driver connection.")

    def __enter__(self) -> "GCNGraphDB":
        """
        Enables use of the graph connection with the 'with' statement.

        Returns:
            GCNGraphDB: The current graph connection instance

        Example:
            with Neo4jGraph(...) as graph:
                graph.query(...)  # Connection automatically managed
        """
        return self
    
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """
        This method is automatically called when exiting a 'with' statement.

        Args:
            exc_type: The type of exception that caused the context to exit
                      (None if no exception occurred)
            exc_val: The exception instance that caused the context to exit
                     (None if no exception occurred)
            exc_tb: The traceback for the exception (None if no exception occurred)

        Note:
            Any exception is re-raised after the connection is closed.
        """
        self.close()