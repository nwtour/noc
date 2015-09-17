# -*- coding: utf-8 -*-
__author__ = 'FeNikS'
# Python modules
import re
from xml.dom.minidom import parseString
# NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetConfig

re_html = re.compile(r"""<html>.+</html>""",
                     re.VERBOSE | re.MULTILINE | re.DOTALL)
re_xml = re.compile(r"""<?xml.+><settings.+></settings>""",
                    re.VERBOSE | re.MULTILINE | re.DOTALL)

class Script(noc.sa.script.Script):
    name = "Tangram.GT21.get_config"
    implements = [IGetConfig]

    def execute(self):        
        config = self.http.get("/um/backup.binc")
        match_xml = re.search(re_xml, config)
        if match_xml:
            if config.find("&lt;") != -1:
                config = config.replace("&lt;", "<")
            if config.find("&gt;") != -1:
                config = config.replace("&gt;", ">")
            parsing = parseString(config)
            return parsing.toprettyxml()

        return self.cleaned_config(config)     