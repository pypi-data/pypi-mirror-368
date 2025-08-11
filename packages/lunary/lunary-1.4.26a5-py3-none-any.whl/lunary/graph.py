from typing import TYPE_CHECKING, Dict, Any
import logging

if TYPE_CHECKING:
  from langchain_core.runnables.graph import Graph as LangChainGraph
else:
  LangChainGraph = Any 


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GraphID = str

## TODO: subgraphs (xray=True)

class GraphManager:
  def __init__(self):
    self.graphs: Dict[GraphID, LangChainGraph] = {}
    
  def add_graph(self, id: GraphID, graph: LangChainGraph):
    self.graphs[id] = graph
    
  def get_serialized_graph(self, id: GraphID):
    if self.graphs.get(id) is None:
      logger.warning("Lunary couldn't reconciliate your LangGraph Graph execution with a full static graph. Please use `lunary.monitor(graph)`.") # TODO: link to docs, take next.js errors as model for phrasing 
      return

    return self.graphs[id].to_json(with_schemas=True)
