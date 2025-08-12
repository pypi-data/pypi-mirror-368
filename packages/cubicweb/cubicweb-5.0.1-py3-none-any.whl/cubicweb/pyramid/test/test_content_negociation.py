from rdflib import Graph

from cubicweb.devtools import BASE_URL
from cubicweb.pyramid.test import PyramidCWTest

_MIMETYPES = [
    "application/rdf+xml",
    "text/turtle",
    "text/n3",
    "application/n-quads",
    "application/n-triples",
    "application/trig",
    "application/ld+json",
]


class ContentNegociationTC(PyramidCWTest):
    settings = {
        "cubicweb.includes": [
            "cubicweb.pyramid.rest_api.include_html",
            "cubicweb.pyramid.rest_api.include_rdf",
        ]
    }

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.blog = cnx.create_entity(
                "Blog",
                title="CubicWeb Blog",
            )
            self.blog_entry = cnx.create_entity(
                "PublicBlogEntry",
                title="une news !",
                content="cubicweb c'est beau",
                unique_id=42,
                entry_of=self.blog,
            )
            cnx.commit()

    def _check_alternate_links(self, res):
        links = res.headers.getall("Link")
        html_links = [str(x) for x in res.html.find_all("link")]
        rest_path = self.blog_entry.rest_path()
        for mimetype in _MIMETYPES:
            assert f"<{BASE_URL}{rest_path}>;rel=alternate;type={mimetype}" in links
            assert (
                f'<link href="{BASE_URL}{rest_path}" rel="alternate"'
                f' title="{mimetype}" type="{mimetype}"/>' in html_links
            )

    def test_content_negociation_link_alternate_etype_eid(self):
        # the resource does not exist since a "rest_attr" is defined for PublicBlogEntry
        res = self.webapp.get(
            f"{BASE_URL}PublicBlogEntry/{self.blog_entry.eid}", status=404
        )
        assert "The resource could not be found." in res.body.decode("utf-8")

    def test_content_negociation_alternate_eid(self):
        res = self.webapp.get(
            f"{BASE_URL}{self.blog_entry.eid}", headers={"Accept": "text/n3"}
        )

        g = Graph()
        g.parse(data=res.body.decode("utf-8"), format="text/n3")
        ask_res = g.query(
            f"""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            ASK {{
                <{BASE_URL}{self.blog_entry.eid}> ^owl:sameAs ?x.
                ?x
                    a <http://ns.cubicweb.org/cubicweb/0.0/PublicBlogEntry>;
                    <http://ns.cubicweb.org/cubicweb/0.0/title> "{self.blog_entry.title}";
                    <http://ns.cubicweb.org/cubicweb/0.0/content> "{self.blog_entry.content}".
            }}"""
        )
        assert ask_res.askAnswer

    def test_content_negociation_no_accept(self):
        response = self.webapp.get(f"{BASE_URL}{self.blog_entry.eid}")
        # check if result is HTML content
        assert response.html

    def test_content_negociation_404_with_eid(self):
        """The /etype/eid route is disabled if rest_attr if defined"""
        res = self.webapp.get(
            f"{BASE_URL}PublicBlogEntry/{self.blog_entry.eid}",
            headers={"Accept": "text/n3"},
            status=404,
        )
        # check if result is HTML content
        assert "The resource could not be found." in res.body.decode("utf-8")

    def test_content_negociation_wrong_accept(self):
        # The mime-type isn't a RDF valid type, so we return a 404
        self.webapp.get(
            f"{BASE_URL}{self.blog_entry.eid}",
            headers={"Accept": "text/n4"},
            status=404,
        )

    def test_content_negociation_rest_attr(self):
        res = self.webapp.get(
            f"{BASE_URL}PublicBlogEntry/{self.blog_entry.unique_id}",
            headers={"Accept": "text/n3"},
        )
        g = Graph()
        g.parse(data=res.body.decode("utf-8"), format="text/n3")
        ask_res = g.query(
            f"""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            ASK {{
                <{BASE_URL}{self.blog_entry.eid}> ^owl:sameAs ?x.
                ?x
                    a <http://ns.cubicweb.org/cubicweb/0.0/PublicBlogEntry>;
                    <http://ns.cubicweb.org/cubicweb/0.0/title> "{self.blog_entry.title}";
                    <http://ns.cubicweb.org/cubicweb/0.0/content> "{self.blog_entry.content}".
            }}"""
        )
        assert ask_res.askAnswer

    def test_content_negociation_etype_eid(self):
        res = self.webapp.get(
            f"{BASE_URL}Blog/{self.blog.eid}", headers={"Accept": "text/n3"}
        )
        g = Graph()
        g.parse(data=res.body.decode("utf-8"), format="text/n3")
        ask_res = g.query(
            f"""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            ASK {{
                <{BASE_URL}{self.blog.eid}> ^owl:sameAs ?x.
                ?x
                    a <http://ns.cubicweb.org/cubicweb/0.0/Blog>;
                    <http://ns.cubicweb.org/cubicweb/0.0/title> "{self.blog.title}".
            }}"""
        )
        assert ask_res.askAnswer, res.body.decode("Utf-8")

    def test_content_negociation_cwuri_sameas(self):
        res = self.webapp.get(
            f"{BASE_URL}Blog/{self.blog.eid}", headers={"Accept": "text/n3"}
        )
        g = Graph()
        g.parse(data=res.body.decode("utf-8"), format="text/n3")
        ask_res = g.query(
            f"""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            ASK {{
            <{self.blog.absolute_url()}>
                owl:sameAs <{BASE_URL}{self.blog.eid}>.
            }}"""
        )
        assert ask_res.askAnswer, res.body.decode("Utf-8")

    def test_content_negociation_jsonld_triples_content(self):
        res = self.webapp.get(
            f"{BASE_URL}PublicBlogEntry/{self.blog_entry.unique_id}",
            headers={"Accept": "application/ld+json"},
        )
        g = Graph()
        g.parse(data=res.body.decode("utf-8"), format="json-ld")
        ask_res = g.query(
            f"""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            ASK {{
                <{BASE_URL}{self.blog_entry.eid}> ^owl:sameAs ?x.
                ?x
                    a <http://ns.cubicweb.org/cubicweb/0.0/PublicBlogEntry>;
                    <http://ns.cubicweb.org/cubicweb/0.0/title> "{self.blog_entry.title}";
                    <http://ns.cubicweb.org/cubicweb/0.0/content> "{self.blog_entry.content}".
            }}"""
        )
        assert ask_res.askAnswer, res.body.decode("Utf-8")
