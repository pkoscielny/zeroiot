import pytest
from smart_data import include
from re import compile as re_compile

re_datetime = re_compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d$")


class TestList:
    def test_empty_list(self, client):
        with client:
            res = client.get('/air_state')
            assert 200 == res.status_code
            assert b'[]' in res.data

    def test_simple_list(self, client):
        air_state_1 = {
            'type': 'air_state',
            'attributes': {
                'temperature': '21.1',
                'humidity': '51.1',
                'location': 'kitchen',
                'device': 'dev1_esp',
            },
        }

        air_state_2 = {
            'type': 'air_state',
            'attributes': {
                'temperature': '22.2',
                'humidity': '52.2',
                'location': 'bathroom',
                'device': 'dev2_esp',
            },
        }

        with client:
            client.post(
                '/air_state',
                json={'data': air_state_1},
                content_type='application/vnd.api+json',
            )

            client.post(
                '/air_state',
                json={'data': air_state_2},
                content_type='application/vnd.api+json',
            )

            res = client.get('/air_state')
            assert 200 == res.status_code

            res_json = res.get_json()
            air_state_1['id'] = '1'
            air_state_2['id'] = '2'
            air_state_1['attributes']['created'] = re_datetime
            air_state_2['attributes']['created'] = re_datetime
            assert include(res_json['data'], [air_state_1, air_state_2]) == []


class TestAdd:
    def test_required_param_temperature(self, client):
        with client:
            res = client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'humidity': 51.2,
                            'location': 'kitchen',
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
                            'pointer': "/data/attributes/temperature",
                        },
                    },
                ]
            ) == []

    def test_required_param_humidity(self, client):
        with client:
            res = client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': 20.1,
                            'location': 'kitchen',
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
                            'pointer': "/data/attributes/humidity",
                        },
                    },
                ]
            ) == []

    def test_required_param_location(self, client):
        with client:
            res = client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': 20.1,
                            'humidity': 51.2,
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
                            'pointer': "/data/attributes/location",
                        },
                    },
                ]
            ) == []

    def test_required_param_device(self, client):
        with client:
            res = client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': '20.1',
                            'humidity': '51.2',
                            'location': 'kitchen',
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

    def test_wrong_param_temperature(self, client):
        with client:
            res = client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': 'abc',
                            'humidity': 55.5,
                            'location': 'kitchen',
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
                        'detail': "Not a valid number.",
                        'source': {
                            'pointer': "/data/attributes/temperature",
                        },
                    },
                ]
            ) == []

    def test_wrong_param_humidity(self, client):
        with client:
            res = client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': '30.2',
                            'humidity': 'abc',
                            'location': 'kitchen',
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
                        'detail': "Not a valid number.",
                        'source': {
                            'pointer': "/data/attributes/humidity",
                        },
                    },
                ]
            ) == []

    def test_wrong_param_location(self, client):
        with client:
            res = client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': '30.2',
                            'humidity': '50.4',
                            'location': 123,
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
                        'detail': "Not a valid string.",
                        'source': {
                            'pointer': "/data/attributes/location",
                        },
                    },
                ]
            ) == []

    def test_wrong_param_device(self, client):
        with client:
            res = client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': '30.2',
                            'humidity': '50.5',
                            'location': 'kitchen',
                            'device': 123,
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
                        'detail': "Not a valid string.",
                        'source': {
                            'pointer': "/data/attributes/device",
                        },
                    },
                ]
            ) == []

    def test_json_structure(self, client):
        with client:
            res = client.post(
                '/air_state',
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
        air_state_1 = {
            'type': 'air_state',
            'attributes': {
                'temperature': '20.1',
                'humidity': '51.2',
                'location': 'kitchen',
                'device': 'dev1_esp',
            },
        }

        with client:
            res = client.post(
                '/air_state',
                json={'data': air_state_1},
                content_type='application/vnd.api+json',
            )
            assert 201 == res.status_code

            res_json = res.get_json()
            air_state_1['id'] = '1'
            air_state_1['attributes']['created'] = re_datetime
            assert include(res_json['data'], air_state_1) == []

            res = client.get('/air_state/1')
            assert 200 == res.status_code

            res_json = res.get_json()
            assert include(res_json['data'], air_state_1) == []


@pytest.mark.usefixtures("add_air_state")
class TestDelete:
    def test_delete(self, client):
        with client:
            res = client.delete(
                '/air_state/1',
                content_type='application/vnd.api+json',
            )
            assert 200 == res.status_code

            res_json = res.get_json()
            assert res_json['meta']['message'] == "Object successfully deleted"

    def test_not_found(self, client):
        with client:
            res = client.delete(
                '/air_state/2',
                content_type='application/vnd.api+json',
            )
            assert 404 == res.status_code


@pytest.mark.usefixtures("add_air_state")
class TestUpdate:
    def test_wrong_type_temperature(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'temperature': "abc",
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
                content_type='application/vnd.api+json',
            )
            assert 422 == res.status_code

            res_json = res.get_json()
            assert include(
                res_json['errors'],
                [
                    {
                        'detail': "Not a valid number.",
                        'source': {
                            'pointer': "/data/attributes/temperature",
                        },
                    },
                ]
            ) == []

    def test_wrong_type_humidity(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'humidity': "abc",
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
                content_type='application/vnd.api+json',
            )
            assert 422 == res.status_code

            res_json = res.get_json()
            assert include(
                res_json['errors'],
                [
                    {
                        'detail': "Not a valid number.",
                        'source': {
                            'pointer': "/data/attributes/humidity",
                        },
                    },
                ]
            ) == []

    def test_wrong_type_location(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'location': 42,
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
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
                            'pointer': "/data/attributes/location",
                        },
                    },
                ]
            ) == []

    def test_wrong_type_device(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'device': 42,
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
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

    def test_wrong_temperature(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'temperature': 'abc',
                'humidity': '67.8',
                'location': 'bathroom_2',
                'device': 'dev5_esp',
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
                content_type='application/vnd.api+json',
            )
            assert 422 == res.status_code

            res_json = res.get_json()
            assert include(
                res_json['errors'],
                [
                    {
                        'detail': "Not a valid number.",
                        'source': {
                            'pointer': "/data/attributes/temperature",
                        },
                    },
                ]
            ) == []

    def test_wrong_humidity(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'temperature': 20.5,
                'humidity': 'abc',
                'location': 'bathroom_2',
                'device': 'dev5_esp',
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
                content_type='application/vnd.api+json',
            )
            assert 422 == res.status_code

            res_json = res.get_json()
            assert include(
                res_json['errors'],
                [
                    {
                        'detail': "Not a valid number.",
                        'source': {
                            'pointer': "/data/attributes/humidity",
                        },
                    },
                ]
            ) == []

    def test_wrong_location(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'temperature': 20.5,
                'humidity': 62.3,
                'location': 123,
                'device': 'dev5_esp',
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
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
                            'pointer': "/data/attributes/location",
                        },
                    },
                ]
            ) == []

    def test_wrong_device(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'temperature': 20.5,
                'humidity': 62.3,
                'location': 'kitchen',
                'device': 123,
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
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

    def test_update_temperature_and_humidity(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'temperature': "23.3",
                'humidity': "33.3",
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
                content_type='application/vnd.api+json',
            )
            assert 200 == res.status_code

            res_json = res.get_json()
            air_state['id'] = '1'
            air_state['attributes']['created'] = re_datetime
            assert include(res_json['data'], air_state) == []

            res = client.get('/air_state/1')
            assert 200 == res.status_code

            res_json = res.get_json()
            assert include(res_json['data'], air_state) == []

    def test_full_update(self, client):
        air_state = {
            'id': "1",
            'type': "air_state",
            'attributes': {
                'temperature': "10.2",
                'humidity': "67.8",
                'location': 'bathroom_2',
                'device': 'dev5_esp',
            },
        }
        with client:
            res = client.patch(
                '/air_state/1',
                json={'data': air_state},
                content_type='application/vnd.api+json',
            )
            assert 200 == res.status_code

            res_json = res.get_json()
            air_state['id'] = '1'
            air_state['attributes']['created'] = re_datetime
            assert include(res_json['data'], air_state) == []

            res = client.get('/air_state/1')
            assert 200 == res.status_code

            res_json = res.get_json()
            assert include(res_json['data'], air_state) == []
