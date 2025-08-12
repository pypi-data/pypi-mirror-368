from cubicweb.entities import AnyEntity, fetch_config


class BlogEntry(AnyEntity):
    __regid__ = "BlogEntry"
    fetch_attrs, cw_fetch_order = fetch_config(["creation_date", "title"], order="DESC")
    rest_attr = "unique_id"


class PublicBlogEntry(AnyEntity):
    __regid__ = "PublicBlogEntry"
    fetch_attrs, cw_fetch_order = fetch_config(["creation_date", "title"], order="DESC")
    rest_attr = "unique_id"
