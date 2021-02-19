
#TODO: add more tests for list
#TODO: implement function to compare structures deeply like eq_or_diff in Perl.
#TODO: add tests for GET/PUT/DELETE.

class TestList:
    def test_empty_list(self, client):
        with client:
            res = client.get('/air_state')
            assert 200 == res.status_code
            assert b'[]' in res.data

    def test_simple_list(self, client):
        with client:
            client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': 21.1,
                            'humidity': 51.1,
                            'location': 'kitchen',
                            'device': 'dev1_esp',
                        },
                    },
                },
                content_type='application/vnd.api+json',
            )

            client.post(
                '/air_state',
                json={
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': 22.2,
                            'humidity': 52.2,
                            'location': 'bathroom',
                            'device': 'dev2_esp',
                        },
                    },
                },
                content_type = 'application/vnd.api+json',
            )

            res = client.get('/air_state')
            assert 200 == res.status_code
            res_json = res.get_json()
            assert res_json['data'][0]['id'] == '1'
            assert res_json['data'][1]['id'] == '2'
            assert res_json['data'][0]['attributes']['temperature'] == '21.1'
            assert res_json['data'][1]['attributes']['temperature'] == '22.2'


class TestAdd:
    def test_required_param_temperature(self, client):
        with client:
            res = client.post(
                '/air_state',
                json = {
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'humidity': 51.2,
                            'location': 'kitchen',
                            'device': 'dev1_esp',
                        },
                    },
                },
                content_type = 'application/vnd.api+json',
            )
            assert 422 == res.status_code
            res_json = res.get_json()
            assert res_json['errors'][0]['detail'] == 'Missing data for required field.'
            assert res_json['errors'][0]['source']['pointer'] == '/data/attributes/temperature'

    def test_required_param_humidity(self, client):
        with client:
            res = client.post(
                '/air_state',
                json = {
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': 20.1,
                            'location': 'kitchen',
                            'device': 'dev1_esp',
                        },
                    },
                },
                content_type = 'application/vnd.api+json',
            )
            assert 422 == res.status_code
            res_json = res.get_json()
            assert res_json['errors'][0]['detail'] == 'Missing data for required field.'
            assert res_json['errors'][0]['source']['pointer'] == '/data/attributes/humidity'

    def test_required_param_location(self, client):
        with client:
            res = client.post(
                '/air_state',
                json = {
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': 20.1,
                            'humidity': 51.2,
                            'device': 'dev1_esp',
                        },
                    },
                },
                content_type = 'application/vnd.api+json',
            )
            assert 422 == res.status_code
            res_json = res.get_json()
            assert res_json['errors'][0]['detail'] == 'Missing data for required field.'
            assert res_json['errors'][0]['source']['pointer'] == '/data/attributes/location'

    def test_required_param_device(self, client):
        with client:
            res = client.post(
                '/air_state',
                json = {
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': '20.1',
                            'humidity': '51.2',
                            'location': 'kitchen',
                        },
                    },
                },
                content_type = 'application/vnd.api+json',
            )
            assert 422 == res.status_code
            res_json = res.get_json()
            assert res_json['errors'][0]['detail'] == 'Missing data for required field.'
            assert res_json['errors'][0]['source']['pointer'] == '/data/attributes/device'

    def test_json_structure(self, client):
        with client:
            res = client.post(
                '/air_state',
                json = {},
                content_type = 'application/vnd.api+json',
            )
            assert 422 == res.status_code

    def test_add_new(self, client):
        with client:
            res = client.post(
                '/air_state',
                json = {
                    'data': {
                        'type': 'air_state',
                        'attributes': {
                            'temperature': 20.1,
                            'humidity': 51.2,
                            'location': 'kitchen',
                            'device': 'dev1_esp',
                        },
                    },
                },
                content_type = 'application/vnd.api+json',
            )
            assert 201 == res.status_code
            res_json = res.get_json()
            assert res_json['data']['type'] == 'air_state'
            assert res_json['data']['id'] == '1'
            assert res_json['data']['attributes']['temperature'] == '20.1'
            assert res_json['data']['attributes']['humidity'] == '51.2'
            assert res_json['data']['attributes']['location'] == 'kitchen'
            assert res_json['data']['attributes']['device'] == 'dev1_esp'
            assert 'created' in res_json['data']['attributes'].keys()

            res = client.get('/air_state')
            assert 200 == res.status_code
            res_json = res.get_json()
            assert res_json['data'][0]['id'] == '1'
            assert res_json['data'][0]['attributes']['temperature'] == '20.1'
            assert res_json['data'][0]['attributes']['humidity'] == '51.2'
            assert res_json['data'][0]['attributes']['location'] == 'kitchen'
            assert res_json['data'][0]['attributes']['device'] == 'dev1_esp'
            assert 'created' in res_json['data'][0]['attributes'].keys()
            assert len(res_json['data']) == 1
