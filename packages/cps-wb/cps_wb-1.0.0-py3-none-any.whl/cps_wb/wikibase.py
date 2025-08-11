#! /usr/bin/env python3
#
# Copyright (C) 2025 The Authors
# All rights reserved.
#
# This file is part of cps_wb.
#
# cps_wb is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation.
#
# cps_wb is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with cps_wb. If not, see http://www.gnu.org/licenses/
#
import argparse
import inspect
import logging

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.datatypes import Item, URL
from wikibaseintegrator import wbi_login
from wikibaseintegrator import wbi_helpers

from cps_wb.wikilabel import WikiLabel

def main():
    ##################################################################
    # CLASS TEST AND DEBUG
    #
    logging.basicConfig(level="INFO", format="%(asctime)s %(name)s %(message)s")

    parser = argparse.ArgumentParser(description="Get wikibase entity", epilog="example: wikibase Q1", add_help=True)

    parser.add_argument("entity", type=str, help="Pn|Qn")

    args = parser.parse_args()

    wb = WB()

    e = args.entity.upper()
    if e.startswith("P"):
        e = wb.Pproperty(e)
    elif e.startswith("Q"):
        e = wb.Qitem(e)
    else:
        raise Exception("Entity must start with P or Q")
    if e:
        results = wb.Edict(e)
        for row in results:
            print(f"{row} = {results[row]}")
    else:
        raise Exception("Entity not found")

class WB:
    # WikibaseIntegrator object
    wbi = None

    # Logging
    logger = None

    ##################################################################
    # Basic properties
    #
    # https://www.wikidata.org/wiki/Help:Basic_membership_properties
    #
    PInstanceOf = "P31"  # wikidata P31 instance of
    PInstances  = None   # wikidata UNKNOWN
    PPartOf     = "P361" # wikidata P361 part of
    PParts      = "P527" # wikidata P527 has part(s)
    PTypeOf     = "P279" # wikidata P279 subclass of
    PTypes      = None   # wikidata UNKNOWN

    def __init__(self, username=None, password=None):
        self.logger = logging.getLogger(__name__)
        if username and password:
            ##################################################################
            # CPS Wikibase Login
            #
            # NB preconfigure wikibaseintegrator.wbi_config
            #
            self.wbi = WikibaseIntegrator(login=wbi_login.Login(user=username, password=password))

            ##################################################################
            # CPS Wikibase objects
            #
            self.PInstanceOf = self.property([WikiLabel("Instance of", "Instance of an item", "en")], "wikibase-item")
            self.PInstances = self.property([WikiLabel("Instances", "Instances of an item", "en")], "wikibase-item")
            self.PPartOf = self.property([WikiLabel("Part of", "Part of an item", "en")], "wikibase-item")
            self.PParts = self.property([WikiLabel("Parts", "Parts of an item", "en")], "wikibase-item")
        else:
            ##################################################################
            # Default Wikidata Login
            #
            from wikibaseintegrator.wbi_config import config as wbi_config

            wbi_config["USER_AGENT"] = "CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)"
            self.wbi = WikibaseIntegrator()

    def __del__(self):
        pass

    def Qitem(self, q):
        #######################################################################
        # Get Item, return Entity
        #
        try:
            e = self.wbi.item.get(q)
            self.logger.info(f"{inspect.stack()[0].function}() {e.id}")
        except:
            return None
        return e

    def Pproperty(self, p):
        #######################################################################
        # Get Property, return Entity
        #
        try:
            e = self.wbi.property.get(p)
            self.logger.info(f"{inspect.stack()[0].function}() {e.id}")
        except:
            return None
        return e

    def Edict(self, e, language="de"):
        #######################################################################
        # Simplified dictionary of an item or property
        #
        if not e:
            raise Exception("Entity not found")
        d = {"title": e.title, "pageid": e.pageid, "lastrevid": e.lastrevid, "type": e.type, "id": e.id}
        try:
            d["label"] = e.labels.values[language].value
        except:
            pass
        try:
            d["description"] = e.descriptions.values[language].value
        except:
            pass
        try:
            d["datatype"] = e.datatype.value
        except:
            pass
        try:
            l = []
            for a in e.aliases.aliases[language]:
                l.append(a.value)
            d["aliases"] = l
        except:
            pass
        l = []
        for c in e.claims:
            if c.mainsnak.datavalue:
                match c.mainsnak.datatype:
                    case "wikibase-item":
                        v = c.mainsnak.datavalue['value']['id']
                    case _:
                        v = c.mainsnak.datavalue['value']
                l.append((f"{c.mainsnak.datatype}:{c.mainsnak.property_number}", v))
        d["claims"] = l
        return d

    def item(self, wikilabels, claims=[], wait=False):
        #######################################################################
        # Get or Create Item, return Entity ID 
        #
        entity = self.finditem(wikilabels[0].label, wikilabels[0].description, wikilabels[0].language)
        if entity:
            if claims:
                for claim in claims:
                    entity.add_claims(claim)
                entity.write()

            self.logger.info(f"{inspect.stack()[0].function}() '{wikilabels[0].label}' '{wikilabels[0].description}' '{wikilabels[0].language}' {entity.id}")
            return entity.id

        entity = self.wbi.item.new()
        for wikilabel in wikilabels:
            entity.labels.set(value=wikilabel.label, language=wikilabel.language)
            entity.descriptions.set(value=wikilabel.description, language=wikilabel.language)
        for claim in claims:
            entity.add_claims(claim)
        try:
            entity.write()
        except:
            raise Exception(f"Permission denied.")

        while wait:
            entity = self.finditem(wikilabels[0].label, wikilabels[0].description, wikilabels[0].language)
            if entity:
                break
            else:
                sleep(0.5)

        self.logger.info(f"{inspect.stack()[0].function}() '{wikilabels[0].label}' '{wikilabels[0].description}' '{wikilabels[0].language}' {entity.id}")
        return entity.id

    def finditem(self, label, description, language="en"):
        #######################################################################
        # Find Item, return Entity
        #
        ids = wbi_helpers.search_entities(search_string=label, language=language, strict_language=True, search_type="item")
        for id in ids:
            entity = self.wbi.item.get(id)
            if label == entity.labels.get(language=language) and description == entity.descriptions.get(language=language):
                return entity

        return None

    def property(self, wikilabels, datatype):
        #######################################################################
        # Get or Create Property, return Entity ID 
        #
        entity = self.findproperty(wikilabels[0].label, wikilabels[0].description, wikilabels[0].language)
        if entity:
            self.logger.info(f"{inspect.stack()[0].function}() '{wikilabels[0].label}' '{wikilabels[0].description}' '{wikilabels[0].language}' {entity.id}")
            return entity.id

        entity = self.wbi.property.new(datatype=datatype)
        for wikilabel in wikilabels:
            entity.labels.set(value=wikilabel.label, language=wikilabel.language)
            entity.descriptions.set(value=wikilabel.description, language=wikilabel.language)
        try:
            entity.write()
        except:
            raise Exception(f"Permission denied.")

        while True:
            entity = self.findproperty(wikilabels[0].label, wikilabels[0].description, wikilabels[0].language)
            if entity:
                break
            else:
                sleep(0.5)

        self.logger.info(f"{inspect.stack()[0].function}() '{wikilabels[0].label}' '{wikilabels[0].description}' '{wikilabels[0].language}' {entity.id}")
        return entity.id

    def findproperty(self, label, description, language="en"):
        #######################################################################
        # Find Property, return Entity
        #
        ids = wbi_helpers.search_entities(search_string=label, language=language, strict_language=True, search_type="property")
        for id in ids:
            entity = self.wbi.property.get(id)
            if label == entity.labels.get(language=language) and description == entity.descriptions.get(language=language):
                return entity

        return None

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
