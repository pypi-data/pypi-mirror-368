#!/usr/bin/env python
"""
Citation file format (.cff) functions.

https://citation-file-format.github.io/
https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md
"""


import json

import yaml

from .file import update_content
from .id.hal import get_hal_id_from_url, get_hal_url_by_origin
from .id.swh import get_swh_url_by_origin, get_swhid_by_origin

TEMPLATE = """\
cff-version: 1.2.0
message: If you use this software, please cite it using these metadata.
title: My Research Software
abstract: This is my awesome research software. It does many things.
authors:
  - family-names: Rye
    given-names: Jan-Michael
    email: jan-michael.rye@inria.fr
    orcid: "https://orcid.org/0009-0005-0109-6598"
version: 0.11.2
# date-released: "yyyy-mm-dd"
identifiers:
  - description: Collection of archived snapshots of My Research Software
    type: doi
    value: "10.5281/zenodo.123456"
  - description: Archived snapshot of version 0.11.2 of My Research Software
    type: doi
    value: "10.5281/zenodo.123457"
license: MIT
repository-code: "https://github.com/citation-file-format/my-research-software"
"""


class Citation:
    """
    Citation data manager.
    """

    def __init__(self, project):
        """
        Args:
            project:
                A Project instance.
        """
        self.project = project

    @staticmethod
    def get_template():
        """
        Get the cff file template as an object.
        """
        return yaml.safe_load(TEMPLATE)

    @staticmethod
    def _transform_codemeta_authors(authors):
        """
        Transform the CodeMeta authors list to citation file format.
        """
        for author in authors:
            data = {}
            for cff_key, cm_key in (
                ("family-names", "familyName"),
                ("given-names", "givenName"),
                ("email", "email"),
            ):
                data[cff_key] = author[cm_key]
            author_id = author.get("@id")
            if author_id and "//orcid.org/" in author_id:
                data["orcid"] = author_id
            yield data

    def update(self):
        """
        Update the citation file with data from codemeta.json and other sources.

        Returns:
            The citation file object.
        """
        path = self.project.citation_cff_path
        if not path.exists() and not self.project.config.get(
            "citations_cff", default=False
        ):
            return
        cff_data = self.get_template()
        with self.project.codemeta_json_path.open("rb") as handle:
            cm_data = json.load(handle)
        for cff_key, cm_key in (
            ("title", "name"),
            ("abstract", "description"),
            ("version", "version"),
            ("repository-code", "codeRepository"),
        ):
            try:
                cff_data[cff_key] = cm_data[cm_key]
            except KeyError:
                del cff_data[cff_key]

        try:
            cff_data["license"] = cm_data["license"].rsplit("/", 1)[1]
        except KeyError:
            del cff_data["license"]
        cff_data["authors"] = list(self._transform_codemeta_authors(cm_data["author"]))

        identifiers = cff_data["identifiers"]
        identifiers.clear()
        git_url = self.project.git_repo.public_git_url
        swh_id = get_swhid_by_origin(git_url)
        if swh_id:
            # TODO
            # Uncomment once cff convert supports this.
            #  identifiers.append({
            #      'type': 'swh',
            #      'value': swh_id,
            #      'description': 'The Software Heritage identifier.'
            #  })
            identifiers.append(
                {
                    "type": "url",
                    "value": get_swh_url_by_origin(git_url),
                    "description": "The Software Heritage URL.",
                }
            )
            hal_url = get_hal_url_by_origin(git_url)
            if hal_url:
                identifiers.append(
                    {
                        "type": "url",
                        "value": hal_url,
                        "description": "HAL open science URL.",
                    }
                )
                identifiers.append(
                    {
                        "type": "other",
                        "value": get_hal_id_from_url(hal_url),
                        "description": "HAL open science identifier.",
                    }
                )

        content = yaml.dump(cff_data)
        update_content(content, path)
