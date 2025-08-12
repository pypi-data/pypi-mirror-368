from cubicweb.server.sources import datafeed
from cubicweb.entities import AnyEntity
from cubicweb.entity import EntityAdapter
from cubicweb.predicates import is_instance


class SourceParserSuccess(datafeed.DataFeedParser):
    __regid__ = "test_source_parser_success"

    def process(self, url, raise_on_error=False):
        entity = self._cw.create_entity("Card", title="success")
        self.notify_updated(entity)


class SourceParserFail(SourceParserSuccess):
    __regid__ = "test_source_parser_fail"

    def process(self, url, raise_on_error=False):
        entity = self._cw.create_entity("Card", title="fail")
        self.notify_updated(entity)
        raise RuntimeError("fail")


class Affaire(AnyEntity):
    __regid__ = "Affaire"

    def ref_sujet(self):
        return f"{self.ref} -- {self.sujet}"


class AffaireRQLInterfaceAdapter(EntityAdapter):
    __regid__ = "IRQLInterface"
    __select__ = is_instance("Affaire")

    @property
    def sujet(self):
        return self.entity.sujet

    def ref_sujet_interface(self):
        return self.entity.ref_sujet()
