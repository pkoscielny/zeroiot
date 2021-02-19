#TODO: add checking parameters.
#TODO: write helper for recursively json checking or find relevant module in internet.
#TODO: add more tests for list
#TODO: add tests for GET/PUT/DELETE.

def test_no_insolations(client):
    with client:
        res = client.get('/insolation')

    assert 200 == res.status_code
    assert b'[]' in res.data


def test_add_new_insolation(client):
    with client:
        res = client.post(
            '/insolation',
            json={
                'data': {
                    'type': 'insolation',
                    'attributes': {
                        'insolation': 42,
                        'device': 'dev2_esp',
                    },
                },
            },
            content_type='application/vnd.api+json',
        )
        assert 201 == res.status_code
        res_json = res.get_json()
        assert res_json['data']['type'] == 'insolation'
        assert res_json['data']['id'] == '1'
        assert res_json['data']['attributes']['insolation'] == 42
        assert res_json['data']['attributes']['device'] == 'dev2_esp'
        assert 'created' in res_json['data']['attributes'].keys()

        res = client.get('/insolation')
        assert 200 == res.status_code
        res_json = res.get_json()
        assert res_json['data'][0]['id'] == '1'
        assert res_json['data'][0]['attributes']['insolation'] == 42
        assert res_json['data'][0]['attributes']['device'] == 'dev2_esp'
        assert 'created' in res_json['data'][0]['attributes'].keys()
        assert len(res_json['data']) == 1
