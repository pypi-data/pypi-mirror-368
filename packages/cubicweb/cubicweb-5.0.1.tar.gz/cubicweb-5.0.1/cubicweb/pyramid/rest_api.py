# copyright 2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# copyright 2014-2016 UNLISH S.A.S. (Montpellier, FRANCE), all rights reserved.
#
# contact https://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <https://www.gnu.org/licenses/>.

"""Experimental REST API for CubicWeb using Pyramid."""

import rdflib
from logilab.mtconverter import xml_escape
from pyramid.response import Response
from pyramid.settings import aslist

from cubicweb import rdf
from cubicweb.pyramid.resources import (
    BinaryResource,
    download_context_from_eid,
    download_context_from_identifier,
    rdf_context_from_eid,
    rdf_context_from_identifier,
    RDFResource,
    HTMLResource,
)


def view_entity_as_rdf(context, request):
    graph = rdflib.ConjunctiveGraph()
    rdf.add_entity_to_graph(graph, context.entity)
    rdf_format = rdf.RDF_MIMETYPE_TO_FORMAT[context.mime_type]
    response = Response(graph.serialize(format=rdf_format))
    response.content_type = context.mime_type
    return response


def build_definition_list(e_dict, translator, is_relation):
    parts = []
    for name, value in e_dict.items():
        if not value:
            continue
        if is_relation:
            relation_parts = []
            for entity in value:
                relation_parts.append(
                    f'<li><a href="{entity.absolute_url()}">{entity.dc_title()}</a></li>'
                )
            part = "\n".join(relation_parts)
            parts.append(
                f"""
                <li><b>{translator(name)}</b>:
                    <ul>
                        {part}
                    </ul>
                </li>
                """
            )
        else:
            parts.append(f"<li><b>{translator(name)}</b>: {value}</li>")
    definitions = "\n".join(parts)
    return f"""
    <ul>
    {definitions}
    </ul>
    """


def view_download_entity(context, request):
    _ = request.cw_cnx._
    entity = context.entity
    download_entity = entity.cw_adapt_to("IDownloadable")
    if download_entity is None:
        return Response(status=404)
    response = Response(
        content_type=download_entity.download_content_type(),
        body=download_entity.download_data(),
    )
    response.content_disposition = (
        f'attachment; filename="{download_entity.download_file_name()}"'
    )
    return response


def _render_download_link(eid, entity_download):
    if entity_download is None:
        return None
    return f"<p><a href='/{eid}/download'>download</a></p>"


def view_entity_as_html(context, request):
    _ = request.cw_cnx._
    entity = context.entity
    entity_download = entity.cw_adapt_to("IDownloadable")
    result_dict = {
        "attributes": {},
        "subject_relations": {},
        "object_relations": {},
    }
    for rschema, attribute_schema in entity.e_schema.attribute_definitions():
        # skip binary data
        attribute_name = rschema.type
        if attribute_name == "eid":
            continue
        if attribute_schema.type == "Bytes":
            result_dict["attributes"][
                attribute_name
            ] = "<span style='color: grey'><i>omitted (Binary)</i></span>"
        else:
            result_dict["attributes"][attribute_name] = xml_escape(
                str(getattr(entity, attribute_name))
            )
    for rschema, _d, subject_or_object in entity.e_schema.relation_definitions():
        if rschema.final:
            continue
        relation_name = rschema.type
        if subject_or_object == "subject":
            result_dict["subject_relations"][relation_name] = getattr(
                entity, relation_name
            )
        else:
            result_dict["object_relations"][relation_name] = getattr(
                entity, f"reverse_{relation_name}"
            )
    title = entity.dc_title()
    # we don't use directly translation in f-string to allow to use i18ncubicweb
    attribute_title = _("CWAttribute_plural")
    relation_subject_title = _("Relations (subject)")
    relation_object_title = _("Relations (object)")
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
    </head>
    <body>
        <h1>{title}</h1>
        {_render_download_link(entity.eid, entity_download)}
        <h2>{attribute_title}</h2>
        {build_definition_list(result_dict["attributes"], _, is_relation=False)}
        <h2>{relation_subject_title}</h2>
        {build_definition_list(result_dict["subject_relations"], _, is_relation=True)}
        <h2>{relation_object_title}</h2>
        {build_definition_list(result_dict["object_relations"], _, is_relation=True)}
    </body>
    </html>
    """
    response = Response(html_content)
    response.content_type = "text/html"
    return response


def includeme(config):
    cubicweb_includes = aslist(config.registry.settings.get("cubicweb.includes", []))
    mimetypes_to_accept = []
    if "cubicweb.pyramid.rest_api.include_rdf" in cubicweb_includes:
        mimetypes_to_accept = list(rdf.RDF_MIMETYPE_TO_FORMAT.keys())
    if "cubicweb.pyramid.rest_api.include_html" in cubicweb_includes:
        mimetypes_to_accept.append("html/text")

    config.add_route(
        "one_entity",
        "/{etype}/{identifier}",
        factory=rdf_context_from_identifier,
        accept=mimetypes_to_accept,
        request_method="GET",
        match_is_etype_and_identifier=("etype", "identifier"),
    )
    config.add_route(
        "one_entity_eid",
        "/{eid}",
        factory=rdf_context_from_eid,
        accept=mimetypes_to_accept,
        request_method="GET",
        match_is_eid="eid",
    )


def include_rdf(config):
    config.add_view(view_entity_as_rdf, route_name="one_entity", context=RDFResource)
    config.add_view(
        view_entity_as_rdf, route_name="one_entity_eid", context=RDFResource
    )


def include_html(config):
    config.add_view(view_entity_as_html, route_name="one_entity", context=HTMLResource)
    config.add_view(
        view_entity_as_html, route_name="one_entity_eid", context=HTMLResource
    )


def include_download(config):
    config.add_route(
        "one_entity_download",
        "/{etype}/{identifier}/download",
        factory=download_context_from_identifier,
        match_is_etype_and_identifier=("etype", "identifier"),
    )
    config.add_route(
        "one_entity_eid_download",
        "/{eid}/download",
        factory=download_context_from_eid,
        match_is_eid="eid",
    )
    config.add_view(
        view_download_entity, route_name="one_entity_download", context=BinaryResource
    )
    config.add_view(
        view_download_entity,
        route_name="one_entity_eid_download",
        context=BinaryResource,
    )
