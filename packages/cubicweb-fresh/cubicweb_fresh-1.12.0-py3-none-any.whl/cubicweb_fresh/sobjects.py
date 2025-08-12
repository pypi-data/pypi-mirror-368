from six import text_type
import cwclientlib
from cubicweb.server.sources import datafeed
from cubicweb.dataimport import stores, importer


# XXX class copied in crm/fresh, should be kepts sync
class CWClientLibDataFeedParser(datafeed.DataFeedParser):
    """Base class for parsers that search for distant entities using cwclientlib."""

    def process_urls(self, *args, **kwargs):
        """IDataFeedParser main entry point."""
        self._source_uris = {}
        error = super(CWClientLibDataFeedParser, self).process_urls(*args, **kwargs)
        if not error:
            self.handle_deletion()
        return error

    def process(self, url, raise_on_error=False):
        """Called once by process_urls (several URL are not expected with this parser)."""
        # ensure url ends with a single slash for proper extid generation
        url = url.rstrip("/") + "/"
        eeimporter = self.build_importer(raise_on_error)
        entities = self.extentities_generator(url)
        set_cwuri = importer.use_extid_as_cwuri(eeimporter.extid2eid)
        eeimporter.import_entities(set_cwuri(entities))
        self.stats["created"] = eeimporter.created
        self.stats["updated"] = eeimporter.updated

    def build_importer(self, raise_on_error):
        """Instantiate and configure an importer"""
        etypes, extid2eid = self.init_extid2eid()
        existing_relations = self.init_existing_relations()
        store = stores.NoHookRQLObjectStore(
            self._cw, metagen=stores.MetadataGenerator(self._cw, source=self.source)
        )
        return importer.ExtEntitiesImporter(
            self._cw.vreg.schema,
            store,
            extid2eid=extid2eid,
            existing_relations=existing_relations,
            etypes_order_hint=etypes,
            import_log=self.import_log,
            raise_on_error=raise_on_error,
        )

    def handle_deletion(self, *args, **kwargs):
        for extid, (eid, etype) in self._source_uris.items():
            self._cw.entity_from_eid(eid, etype).cw_delete()

    def existing_entities(self, etype):
        rset = self._cw.execute(
            "Any XURI, X WHERE X cwuri XURI, X is {0},"
            " X cw_source S, S eid %(s)s".format(etype),
            {"s": self.source.eid},
        )
        for extid, eid in rset:
            self._source_uris[extid] = (eid, etype)
            yield extid, eid

    def states_map(self, etype):
        return dict(
            self._cw.execute(
                "Any SN,S WHERE S name SN, S state_of WF, "
                "ET default_workflow WF, ET name %(etype)s",
                {"etype": etype},
            )
        )

    def ext_entity(self, url, etype, eid, values):
        extid = url + text_type(eid)
        self._source_uris.pop(extid, None)
        return importer.ExtEntity(etype, extid, values)


class DataFeedFreshActivity(CWClientLibDataFeedParser):
    """Parser to import workcases from crm."""

    __regid__ = "fresh.workcases"

    def init_extid2eid(self):
        # put state eids in extid2eid as we'll want to link to them
        extid2eid = dict(self._cw.execute("Any X,X WHERE X is State"))
        # map existing orders and workorders from our souce
        etypes = ("Workcase",)
        for etype in etypes:
            for extid, eid in self.existing_entities(etype):
                extid2eid[extid] = eid
        return etypes, extid2eid

    def init_existing_relations(self):
        existing_relations = {}
        rset = self._cw.execute(
            "Any O,OS WHERE O in_state OS, O is Workcase, O cw_source S, S eid %(s)s",
            {"s": self.source.eid},
        )
        existing_relations["in_state"] = set(tuple(x) for x in rset)
        return existing_relations

    def extentities_generator(self, url):
        # connect to the instance using cwclientlib
        proxy = cwclientlib.cwproxy_for(url)
        # XXX check modification_date > last_update
        # information necessary to relate order to a state
        states_map = self.states_map("Workcase")

        for args in proxy.execute(
            "Any W,SN,WR,WS WHERE W is_instance_of Workcase, "
            "W ref WR, W subject WS, W in_state S, S name SN"
        ):
            eid = args.pop(0)
            state = args.pop(0)
            values = values_dict(args, ["ref", "subject"])
            values["in_state"] = set([states_map[state]])
            yield self.ext_entity(url, "Workcase", eid, values)


def values_dict(values_list, attributes):
    values = {}
    for k, v in zip(attributes, values_list):
        if v is not None:
            values[k] = set([v])
    return values
