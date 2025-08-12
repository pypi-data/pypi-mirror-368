
class ShazamConfig(object):
    namespaceAliases = {}
    matchIsLocalName = False
    extension: str
    extension_exclusion: str = None
    docType: str
    docSource: str
    docNodeName: str = None
    docNodeNames = []

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def matchPath(self, name):
        return f"*[local-name() = '{name}'" if self.matchIsLocalName else name

    def element(self, nName, eName):
        return f"<xsl:element name='{eName}'><xsl:value-of select=\"{self.matchPath(nName)}\"/></xsl:element>"

    def makeComplexLeaf(self, nName, parts):
        if parts[1] == "for-each":
            eName = parts[0]
            e = self.element('.', eName)
            return f"\t<xsl:for-each select=\"{self.matchPath(nName)}\">{e}</xsl:for-each>"
        else:
            return "\n\t".join([self.element(nName, eName) for eName in parts])

    def nsAlias(self, namespace):
        # print("asking for alias for " + namespace)
        for alias in self.namespaceAliases.keys():
            if self.namespaceAliases[alias] == namespace:
                # print(namespace," -> ", alias)
                return alias
        return None
