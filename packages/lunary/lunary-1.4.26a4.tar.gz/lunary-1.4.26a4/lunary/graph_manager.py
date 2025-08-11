from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
  from langchain_core.runnables.graph import Graph as LangChainGraph
else:
  LangChainGraph = Any 

GraphID = str

## TODO: subgraphs (xray=True)

class GraphManager:
  def __init__(self):
    self.graphs: Dict[GraphID, LangChainGraph] = {}
    
  def add_graph(self, id: GraphID, graph: LangChainGraph):
    self.graphs[id] = graph
    
  def get_graph(self, id: GraphID) -> LangChainGraph | None:
    return self.graphs.get(id)
  
  