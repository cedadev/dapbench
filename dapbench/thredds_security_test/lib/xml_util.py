"""
Utilities for creating and processing XML,

@author: rwilkinson
"""
def appendElement(document, parentEl, elementType, elementText):
    """Adds a text element to a specified parent.
    """
    el = document.createElement(elementType)
    textEl = document.createTextNode(elementText)
    el.appendChild(textEl)
    parentEl.appendChild(el)

def getSingleChildTextByName(rootNode, name):
    """Returns the text of a child node found by name.
    Only one such named child is expected.
    """
    try:
        nodeList = [e.firstChild.data for e in rootNode.childNodes if e.localName == name]
        if len(nodeList) > 0:
            return nodeList[0]
        else:
            return None
    except AttributeError:
        return None

def getSingleChildTextByNameNS(rootNode, ns, name):
    """Returns the text of a child node found by name and namespaceURI.
    Only one such named child is expected.
    """
    try:
        nodeList = [e.firstChild.data for e in rootNode.childNodes if e.localName == name and e.namespaceURI == ns]
        if len(nodeList) > 0:
            return nodeList[0]
        else:
            return None
    except AttributeError:
        return None

def getSingleChildByName(rootNode, name):
    """Returns a child node found by name.
    Only one such named child is expected.
    """
    nodeList = [e for e in rootNode.childNodes if e.localName == name]
    if len(nodeList) > 0:
        return nodeList[0]
    else:
        return None

def getSingleChildByNameNS(rootNode, ns, name):
    """Returns a child node found by name and namespaceURI.
    Only one such named child is expected.
    """
    nodeList = [e for e in rootNode.childNodes if e.localName == name and e.namespaceURI == ns]
    if len(nodeList) > 0:
        return nodeList[0]
    else:
        return None

def getSingleChildByPath(rootNode, path):
    """Returns a descendent node found by a list of names forming a path.
    The path is expected to define a unique node.
    """
    parentNode = rootNode
    for name in path:
        node = getSingleChildByName(parentNode, name)
        if node == None:
            return None
        else:
            parentNode = node
    return node

def getSingleChildByPathNS(rootNode, path):
    """Returns a descendent node found by a list of names and namespaceURIs forming a path.
    The path is expected to define a unique node.
    """
    parentNode = rootNode
    for (ns, name) in path:
        node = getSingleChildByNameNS(parentNode, ns, name)
        if node == None:
            return None
        else:
            parentNode = node
    return node

def getChildrenByName(rootNode, name):
    """Returns all child nodes of a specified name.
    """
    return [e for e in rootNode.childNodes if e.localName == name]

def getChildrenByNameNS(rootNode, ns, name):
    """Returns all child nodes of a specified name and namespaceURI.
    """
    return [e for e in rootNode.childNodes if e.localName == name and e.namespaceURI == ns]

def getAttributeByLocalName(element, localName):
    """Returns the value of an attribute specified by local name. The attribute's namespace is
    ignored.
    """
    attrs = element.attributes
    for idx in xrange(attrs.length):
        attr = attrs.item(idx)
        if attr.localName == localName:
            return attr.value
    return None
