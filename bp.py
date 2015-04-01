#
# LLDB Python script for drawing a call graph of breakpoint hits.
#
# To use run the following lldb commands:
#
# (lldb) command script import bp.py
# (lldb) break set ...
# (lldb) break command add -F bp.bpStack 1
# (lldb) run
#     .........
# (lldb) script bp.draw() 
# Open BPCallStack.png


import pydot # Use pydot from drawing call graph

# Node in call graph
class Node:
   def __init__(self,name):
       self.name = name # Function name, or module with offset
       self.count = 1   # Reference count
       self.pydotNode = pydot.Node(name) # pydot node object
       self.children =[] # Callees, a list of Node objects

   def addChild(self,data): # Add Callee
       self.children.append(data)

   def incCount(self): # Increment reference 
       self.count += 1;
    
class CallGraph:
  def __init__(self):
      self.nodes = {} # Dictionary of function names to Node objects
      self.graph = pydot.Dot(graph_type = 'digraph',nodesep=.05,bgcolor="transparent") # Init pydot graph
      self.graph.set_edge_defaults(weight="1") # Short pydot edge lengths
      self.root = None # Root node for call graph

  @property
  def nodes(self): # reference nodes directly
      return self.nodes

  # Update call graph with caller
  def update(self,name,parent,frameIndex): 
       if(self.contains(name)):                       # Node already exists
          return self.incRefCount(name,parent) 
       else:                                          # Node doesn't exist, add to call Graph
          return self.addNode(name,frameIndex==0,parent)

  def addNode(self,name,breakFunc,parent=None):
     node = Node(name)
     self[name] = node

     if breakFunc: # Highlight nodes in red where the breakpoint exists
         node.pydotNode.set_color("red")
         node.pydotNode.set_style("filled")

     if parent is None:
        self.root = node
     else:
        self.graph.add_node(node.pydotNode)
        self[parent.name].addChild(name)
        self.addEdge(parent,node)

     return node

  def addEdge(self,src,dest): # Adds edge to pydot graph
      if src is not self.root:
          edge = pydot.Edge(src.pydotNode,dest.pydotNode)
          self.graph.add_edge(edge)

  def contains(self,name):
      return name in self.nodes

  # Increment the reference count of the node
  def incRefCount(self,name,parent):
      self[name].incCount()
      if name not in parent.children:  
          self.addEdge(parent,self[name])
          parent.addChild(name)

      pdNode = self[name].pydotNode
      label = name + "\nCalled "+ str(self[name].count) + " times"
      pdNode.set_label(label)

      return self[name]
 
  def __setitem__(self,key,item):
      self.nodes[key] = item
  
  def __getitem__(self,key):
      return self.nodes[key]

# Init call Graph and root node
callGraph = CallGraph(); 
root = callGraph.addNode("Root",-1);

# Function called when breakpoint is hit
def bpStack (frame, bp_loc, internal_dict):

    thread = frame.GetThread() 
    numFrames = thread.GetNumFrames() 
 
    lastnode = root # Caller node
    for f in reversed(range(0, numFrames)): # Walk the stack
       name = thread.GetFrameAtIndex(f).GetFunctionName() 

       # If we can't get the function name use the module name, with
       # offset to the call site.
       if name == "???" or name == None: 
           frame = thread.GetFrameAtIndex(f)
           pc_addr = frame.GetPCAddress()
           file_addr = pc_addr.GetFileAddress()
           start_addr = frame.GetSymbol().GetStartAddress().GetFileAddress()

           modname = frame.GetModule().GetFileSpec().GetFilename()
           offset_addr = file_addr - start_addr 
           offset_str = "0x%X" % offset_addr
           name = modname + " + "+offset_str


       # Update call Graph
       node = callGraph.update(name,lastnode,f)
       lastnode = node

    return False

def draw(): # Print graph to png image
    callGraph.graph.write_png('BPCallStack.png')

