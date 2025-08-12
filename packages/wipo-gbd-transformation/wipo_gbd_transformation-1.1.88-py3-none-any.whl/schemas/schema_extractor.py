#! /usr/bin/env python3

from xml.etree.ElementTree import fromstring, ElementTree, Element
import sys
import yaml
import os
import gzip
from pathlib import Path
from schemas.ShazamConfig import ShazamConfig
import re

YL = "  "


class CollectionPathsCounter:
    def __init__(self):
        self.paths_aggregates = {}

    paths_aggregates = {}
    #  aggregate the counts of paths over the whole collection
    # doc1 nice_path: 5
    # doc2 nice_path: 1
    # coll nice_paths: [5, 1]
    # let's see where it crashes ...


class DocCounter:
    # one level
    paths_counts = {}
    paths_values = {}

    def addEntry(self, nodePath, value):
        path = make_path(nodePath)
        # #### paths counts
        if path in self.paths_counts:
            self.paths_counts[path] += 1
        else:
            self.paths_counts[path] = 1
        # #### paths values
        if path in self.paths_values:
            self.paths_values[path].append(value)
        else:
            self.paths_values[path] = [value]

    def __str__(self):
        toReturn = []
        for path in self.paths_counts:
            toReturn.append(f"{path} : {self.paths_counts[path]}")
        return "\n".join(toReturn)


class SkellyNode:
    """ Stores the aggregate skeleton of a document type"""
    name = ""
    # ## How to store the fact that the node can have 10 Nice or Vienna child nodes?
    isMultiple = False  # is that enough?
    attributes = set()
    children = dict()
    namespace = None
    namespaceAlias = None
    parent = None
    isRoot = False

    def __init__(self, conf: ShazamConfig, parent, name, attributes):
        if name.startswith("{"):
            self.namespace = name[1:name.index("}")]
            self.name = name[name.rindex("}") + 1:]
            self.namespaceAlias = conf.nsAlias(self.namespace)
        elif name.contains(":"):
            self.namespace = name[0:name.rindex(":")]
            self.name = name[name.rindex(":") + 1:]
            self.namespaceAlias = conf.nsAlias(self.namespace)
        else:
            self.name = name
        self.parent = parent
        self.attributes = set(attributes) if attributes else set()
        self.children = dict()
        self.isMultiple = False

    def add_attribute(self, attribute):
        self.attributes.add(attribute)

    def merge_attributes(self, attributes):
        self.attributes.union(attributes)

    def merge_child(self, child):  # child should be a SkellyNode
        # print("%%%% ", self)
        if child.name in self.children.keys():
            # print(f"==> {self.name} MERGE CHILD {child.name} WITH SIBLINGS ")
            self.children[child.name].merge_with_sibling(child)
        else:
            self.children[child.name] = child

    def adopt(self, child):  # child should be a SkellyNode
        # print("%%%% ", self)
        if child.name in self.children.keys():
            print(f"==> {self.name} MERGE CHILD {child.name} WITH SIBLINGS ")
            raise ValueError("Should not adopt a child of the same name. Look at a merge function")
        self.children[child.name] = child

    def merge_with_sibling(self, node):
        self.isMultiple = True  # only merging with siblings of the same name
        # print("MULTIPLE " + self.name)
        if node.attributes:
            self.attributes.union(node.attributes)

        if node.children:
            self.children.update(node.children)

    def path(self):
        ancestry = []
        current = self
        while current is not None and current.isRoot == False:
            ancestry.insert(0, current.node_name())
            current = current.parent

        return make_path(ancestry)

    def node_name(self):
        if self.namespaceAlias:
            return self.namespaceAlias + ":" + self.name
        if self.namespace:
            return self.namespace + ":" + self.name
        return self.name

    def __str__(self):
        s = []
        s.append("{" + (self.parent.name if self.parent else "GROOT") + "}")
        s.append(f">{self.name}<")
        s.append("[" + ("MULTIPLE" if self.isMultiple else "SINGLE") + "]")

        if self.attributes:
            s.append(" _@".join(self.attributes))
        if self.children:
            s.append("\n |_" + ("\n |_".join([c.name for c in self.children.values()])))
        return " ".join(s)


def merge_trees(conf_local: ShazamConfig, sum_rec: SkellyNode, new_one: SkellyNode):
    if sum_rec is None:
        return new_one
    sum_rec.merge_attributes(new_one.attributes)
    sum_rec.isMultiple = sum_rec.isMultiple or new_one.isMultiple
    next_children = {}
    for childName in sum_rec.children.keys():
        # print(f"{childName} in sumRec: {childName in sumRec.children.keys()}")
        if childName in new_one.children.keys():
            # print(f"{childName} in sumRec: {childName in sumRec.children.keys()}")
            # print(f"{childName} in newOne : {childName in newOne.children.keys()}")
            new_child = merge_trees(conf_local, sum_rec.children[childName], new_one.children[childName])
            next_children[childName] = new_child
        else:
            next_children[childName] = sum_rec.children[childName]
    sum_rec.children = next_children
    for childName in new_one.children:
        if childName not in sum_rec.children:
            sum_rec.adopt(new_one.children[childName])
    return sum_rec


def make_path(ancestry):
    return "/".join(ancestry)


def print_skel(skel, level, out):
    root = "#  ROOT" if skel.isRoot else ""
    multi = "# Multiple" if skel.isMultiple else ""  # "# Single"
    path = skel.path()
    print(f"{level}{skel.node_name()}: {root} {multi} # {path}", file=out)
    for attr in skel.attributes:
        print(f"{level}{YL}_@{attr}: # {path}@{attr}", file=out)
    # if skel.namespace:
    #    print(f"{level}{YL}namespace: {skel.namespace}", file=out)
    for child in skel.children:
        # print(":::" , child)
        print_skel(skel.children[child], level + YL, out)


def build_skel(conf_local: ShazamConfig, parent, node: Element):
    # print("## New Skeleton Node [" + node.tag + "] parent: {" + (parent.name if parent else "None") + "}")
    localSkel = SkellyNode(conf_local, parent, node.tag, node.keys())
    if parent is None:
        localSkel.isRoot = True
    if len(node.keys()) > 0:
        localSkel.merge_attributes(node.keys())
    for child in node:
        # print ("$$$ " + child.tag)
        localSkel.merge_child(build_skel(conf_local, localSkel, child))
    return localSkel


def print_paths(accumulator, node, parents):
    if len(node) == 0:
        currentPath = []
        currentPath.extend(parents)
        currentPath.append(node.tag)

        print(make_path(currentPath), "::", node.text)
        accumulator.addEntry(currentPath, node.text)
        ## Attributes
        if len(node.keys()) == 0:
            return
        for attr in node.keys():
            accumulator.addEntry(currentPath + ["@" + attr], node.get(attr))
            # print(make_path(currentPath + ["@" + attr]), node.get(attr))
    else:
        parent_tmp = parents + [node.tag]
        for child in node:
            print_paths(accumulator, child, parent_tmp)


# def header(docType, docSource, rootName, matchIsLocalName):
#     return f"""config:
#   docType: {docType}
#   docSource: {docSource}
#   rootName: {rootName}
#   matchIsLocalName: {matchIsLocalName}
#
# """
#
def parse_file(local_conf: ShazamConfig, source: str):
    text: str = None
    if source.endswith(".xml.gz"):
        with gzip.open(source, "rb") as gz:
            text = gz.read()
    else:
        with open(source, "r") as f:
            text = f.read()
    return parse_entries(local_conf, text)


def parse_entries(local_conf: ShazamConfig, text: str):
    tree = ElementTree(fromstring(text))
    root: Element = tree.getroot()

    # < BaseXML >
    #   < U_ID >
    #       < id > 43057 < / id >
    accumulator_record = None
    records = []

    if local_conf.docNodeName is None and len(local_conf.docNodeNames) == 0:
        records = root
    elif local_conf.docNodeName:
        records = [n for n in root.iter(local_conf.docNodeName)]
    elif len(local_conf.docNodeNames):
        for doc_node_name in conf.docNodeNames:
            tmp = [n for n in root.iter(doc_node_name)]
            if len(tmp) > 0:
                print("(%s)" % doc_node_name)
                records.extend(tmp)

    for record in records:  # xml.etree.ElementTree.Element
        # print(record)
        current_record = build_skel(local_conf, None, record)
        #  printPaths(accumulator, mark, [""])
        #  print("########### 11 ############")
        #  print_skel(currentRecord, "", sys.stdout)
        accumulator_record = merge_trees(local_conf, accumulator_record, current_record)
        # sys.exit()
    # print(accumulator)
    return accumulator_record


if __name__ == "__main__":
    conf_yaml = sys.argv[1]
    name = sys.argv[2]
    source = sys.argv[3]
    destination = sys.argv[4]
    conf = None
    with open(conf_yaml, 'r') as y:
        schema_template = yaml.safe_load(y)
        conf = ShazamConfig(**schema_template.pop(name))

    # source = '/ssd/hoibian/workspace/bnd-defs/xml-schemas/kztm/gb_export_test.xml'
    # destination = "/ssd/hoibian/workspace/bnd-defs/xml-schemas/kztm/skeleton.yaml"
    print("Gonna parse", source)
    print("Saving to ", destination)

    accumulatorRecord = None

    if os.path.isfile(source):
        full_text = None
        accumulatorRecord = parse_file(source)
    elif os.path.isdir(source):
        for path in Path(source).rglob("*"+conf.extension):
            # print(path.name)
            # if conf.extension_exclusion is None or not re.match(conf.extension_exclusion, path.name):
            #     print(conf.extension_exclusion, path.name)

            if conf.extension_exclusion is None or not re.match(conf.extension_exclusion, path.name):
                print("==>", path, path.name)
                tmp = parse_file(conf, str(path))
                accumulatorRecord = merge_trees(conf, accumulatorRecord, tmp)
    print("########### 22 ############")

    with open(destination, 'w') as y:
        yaml.dump(conf, y)
        y.write("\n\n")
        print_skel(accumulatorRecord, "", y)
