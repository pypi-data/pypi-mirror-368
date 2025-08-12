from yams import ValidationError
from cubicweb.pyramid.test import PyramidCWTest


def put_in_uncommitable_state(request):
    try:
        request.cw_cnx.execute('SET U login NULL WHERE U login "anon"')
    except ValidationError:
        pass
    request.response.body = b"OK"
    return request.response


class CoreTest(PyramidCWTest):
    anonymous_allowed = True

    def includeme(self, config):
        config.add_route("uncommitable", "/uncommitable")
        config.add_view(put_in_uncommitable_state, route_name="uncommitable")

    def test_uncommitable_cnx(self):
        res = self.webapp.get("/uncommitable")
        self.assertEqual(res.text, "OK")
        self.assertEqual(res.status_int, 200)


if __name__ == "__main__":
    from unittest import main

    main()
