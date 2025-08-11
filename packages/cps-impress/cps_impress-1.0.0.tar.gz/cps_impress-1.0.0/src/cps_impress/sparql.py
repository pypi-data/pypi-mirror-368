#! /usr/bin/env python3
#
# Copyright (C) 2025 The Authors
# All rights reserved.
#
# This file is part of cps_impress.
#
# cps_impress is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation.
#
# cps_impress is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with cps_impress. If not, see http://www.gnu.org/licenses/
#
import argparse
import importlib.util
import jinja2
import os
import sys

from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_helpers

from dotenv import load_dotenv

def main():
    ##################################################################
    # CLASS TEST AND DEBUG
    #
    parser = argparse.ArgumentParser(description="SPARQL project", epilog="example: sparql project", add_help=True)

    parser.add_argument("-t", "--template", type=str, help="template name")
    parser.add_argument("-n", "--noescape", action="store_true", help="no HTML escapes")
    parser.add_argument("project", type=str, help="project name")

    args = parser.parse_args()

    obj = SPARQL(args.project)
    if not args.template:
        for row in obj.results:
            print(f"{row} = {obj.results[row]}")
    else:
        if args.noescape:
            print(obj.template(args.template, False))
        else:
            print(obj.template(args.template))

class SPARQL:
    # akamaitechnologies hangs unless it recognises the User-Agent
    _USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134."

    _project_dir = None # Project directory

    results = None # Query results

    def __init__(self, project_name):
        load_dotenv(os.getcwd() + os.sep + ".env")

        ##################################################################
        # SPARQL query service
        #
        wbi_config["DEFAULT_LANGUAGE"] = "en"
        wbi_config["USER_AGENT"] = self._USER_AGENT
        if os.getenv("SPARQL_URL"):
            wbi_config['SPARQL_ENDPOINT_URL'] = os.getenv("SPARQL_URL")

        ##################################################################
        # Project files
        #
        self._project_dir = os.getenv("PROJECT_DIR")
        if not self._project_dir:
            raise Exception("PROJECT_DIR is missing")

        self._project_dir = self._project_dir + "/" + project_name + "/"
        if not os.path.isdir(self._project_dir):
            raise Exception(f"no SPARQL project [{self._project_dir}]")

        sparql_query = self._project_dir + "query.txt"
        if not os.path.isfile(sparql_query):
            raise Exception(f"no SPARQL query [{sparql_query}]")

        ##################################################################
        # SPARQL query
        #
        query = ""
        with open(sparql_query, "r", encoding="utf-8") as f:
            for line in f:
                query += line

        res = wbi_helpers.execute_sparql_query(query, prefix=os.getenv("SPARQL_PREFIX"))
        try:
            bindings = res["results"]["bindings"]
        except:
            raise Exception("no result bindings")

        ##################################################################
        # Get results
        #
        result_list = []
        for binding in bindings:
            result_dict = {}
            for key in binding:
                result_dict[key] = binding[key]['value']
            result_list.append(result_dict)

        self.results = {"bindings": result_list}

        ##################################################################
        # Process results
        #
        project_py = self._project_dir + "project.py"
        if os.path.isfile(project_py):
            spec = importlib.util.spec_from_file_location("project", project_py)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.results = module.process(self.results)

    def template(self, name, escape=True):
        filename = f"{name}.j2"
        if not os.path.isfile(self._project_dir + filename):
            raise Exception(f"no Jinja2 template [{self._project_dir + filename}]")

        template_loader = jinja2.FileSystemLoader(searchpath=self._project_dir)
        template_env = jinja2.Environment(loader=template_loader,
            autoescape=escape, trim_blocks=True, lstrip_blocks=True)
        template = template_env.get_template(filename)

        return template.render(rs=self.results)

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
