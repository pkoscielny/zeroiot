import pytest
from smart_data import include
from re import compile as re_compile

re_datetime = re_compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d$")


class TestList:
    def test_empty_list(self, client):
        with client:
            res = client.get('/insolation')
            assert 200 == res.status_code
            assert b'[]' in res.data

    def test_simple_list(self, client):
        insolation_1 = {
            'type': 'insolation',
            'attributes': {
                'insolation': 111,
                'device': 'dev1_esp',
            },
        }

        insolation_2 = {
            'type': 'insolation',
            'attributes': {
                'insolation': 222,
                'device': 'dev2_esp',
            },
        }

        with client:
            client.post(
                '/insolation',
                json={'data': insolation_1},
                content_type='application/vnd.api+json',
            )

            client.post(
                '/insolation',
                json={'data': insolation_2},
                content_type='application/vnd.api+json',
            )

            res = client.get('/insolation')
            assert 200 == res.status_code

            res_json = res.get_json()
            insolation_1['id'] = '1'
            insolation_2['id'] = '2'
            insolation_1['attributes']['created'] = re_datetime
            insolation_2['attributes']['created'] = re_datetime
            assert include(res_json['data'], [insolation_1, insolation_2]) == []


class TestAdd:
    def test_required_param_insolation(self, client):
        with client:
            res = client.post(
                '/insolation',
                json={
                    'data': {
                        'type': 'insolation',
                        'attributes': {
                            'device': 'dev1_esp',
                        },
                    },
                },
                content_type='application/vnd.api+json',
            )
            assert 422 == res.status_code

            res_json = res.get_json()
            assert include(
                res_json['errors'],
                [
                    {
                        'detail': "Missing data for required field.",
                        'source': {
                            'pointer': "/data/attributes/insolation",
                        },
                    },
                ]
            ) == []

    def test_required_param_device(self, client):
        with client:
            res = client.post(
                '/insolation',
                json={
                    'data': {
                        'type': 'insolation',
                        'attributes': {
                            'insolation': '111',
                        },
                    },
                },
                content_type='application/vnd.api+json',
            )
            assert 422 == res.status_code

            res_json = res.get_json()
            assert include(
                res_json['errors'],
                [
                    {
                        'detail': "Missing data for required field.",
                        'source': {
                            'pointer': "/data/attributes/device",
                        },
                    },
                ]
            ) == []

    def test_json_structure(self, client):
        with client:
            res = client.post(
                '/insolation',
                json={},
                content_type='application/vnd.api+json',
            )
            assert 422 == res.status_code

            res_json = res.get_json()
            assert include(
                res_json['errors'],
                [
                    {
                        'detail': "Object must include `data` key.",
                        'source': {
                            'pointer': "/",
                        },
                    },
                ]
            ) == []

    def test_add_new(self, client):
        insolation_1 = {
            'type': 'insolation',
            'attributes': {
                'insolation': 42,
                'device': 'dev42_esp',
            },
        }

        with client:
            res = client.post(
                '/insolation',
                json={'data': insolation_1},
                content_type='application/vnd.api+json',
            )
            assert 201 == res.status_code

            res_json = res.get_json()
            insolation_1['id'] = '1'
            insolation_1['attributes']['created'] = re_datetime
            assert include(res_json['data'], insolation_1) == []

            res = client.get('/insolation/1')
            assert 200 == res.status_code

            res_json = res.get_json()
            assert include(res_json['data'], insolation_1) == []


@pytest.mark.usefixtures("add_insolation")
class TestDelete:
    def test_delete(self, client):
        with client:
            res = client.delete(
                '/insolation/1',
                content_type='application/vnd.api+json',
            )
            assert 200 == res.status_code

            res_json = res.get_json()
            assert res_json['meta']['message'] == "Object successfully deleted"

    def test_not_found(self, client):
        with client:
            res = client.delete(
                '/insolation/2',
                content_type='application/vnd.api+json',
            )
            assert 404 == res.status_code


@pytest.mark.usefixtures("add_insolation")
class TestUpdate:
    def test_wrong_type_insolation(self, client):
        insolation = {
            'id': "1",
            'type': "insolation",
            'attributes': {
                'insolation': 'abc',
            },
        }
        with client:
            res = client.patch(
                '/insolation/1',
                json={'data': insolation},
                content_type='application/vnd.api+json',
            )
            assert 422 == res.status_code

            res_json = res.get_json()
            assert include(
                res_json['errors'],
                [
                    {
                        'detail': "Not a valid integer.",
                        'source': {
                            'pointer': "/data/attributes/insolation",
                        },
                    },
                ]
            ) == []

    def test_wrong_type_device(self, client):
        insolation = {
            'id': "1",
            'type': "insolation",
            'attributes': {
                'insolation': '111',
                'device': 42,
            },
        }
        with client:
            res = client.patch(
                '/insolation/1',
                json={'data': insolation},
                content_type='application/vnd.api+json',
            )
            assert 422 == res.status_code

            res_json = res.get_json()
            assert include(
                res_json['errors'],
                [
                    {
                        'detail': "Not a valid string.",
                        'source': {
                            'pointer': "/data/attributes/device",
                        },
                    },
                ]
            ) == []

    def test_full_update(self, client):
        insolation = {
            'id': "1",
            'type': "insolation",
            'attributes': {
                'insolation': 123,
                'device': 'dev5_esp',
            },
        }
        with client:
            res = client.patch(
                '/insolation/1',
                json={'data': insolation},
                content_type='application/vnd.api+json',
            )
            assert 200 == res.status_code

            res_json = res.get_json()
            assert include(res_json['data'], insolation) == []
