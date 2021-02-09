#TODO: add more tests for list

def test_no_air_states(client):
    res = client.get('/air_state')
    assert 200 == res.status_code
    assert b'[]' in res.data


def test_required_params_add_air_state(client):
    res = client.post(
        '/air_state',
        json = {'humidity': 51.2, 'location': 'kitchen', 'device': 'dev1_esp'}
    )
    assert 400 == res.status_code
    res_json = res.get_json()
    assert res_json['message']['temperature'] == 'temperature is required parameter!'

    res = client.post(
        '/air_state',
        json = {'temperature': 20.1, 'location': 'kitchen', 'device': 'dev1_esp'}
    )
    assert 400 == res.status_code
    #TODO: check json.

    res = client.post(
        '/air_state',
        json = {'temperature': 20.1, 'humidity': 51.2, 'device': 'dev1_esp'}
    )
    assert 400 == res.status_code
    #TODO: check json.

    res = client.post(
        '/air_state',
        json = {'temperature': 20.1, 'humidity': 51.2, 'location': 'kitchen'}
    )
    assert 400 == res.status_code
    #TODO: check json.


def test_add_new_air_state(client):
    res = client.post(
        '/air_state',
        json = {'temperature': 20.1, 'humidity': 51.2, 'location': 'kitchen', 'device': 'dev1_esp'}
    )
    assert 201 == res.status_code
    res_json = res.get_json()
    assert res_json['id'] == 1
    assert res_json['temperature'] == 20.1
    assert res_json['humidity'] == 51.2
    assert res_json['location'] == 'kitchen'
    assert res_json['device'] == 'dev1_esp'
    assert 'created' in res_json.keys()

    res = client.get('/air_state')
    assert 200 == res.status_code
    res_json = res.get_json()
    assert res_json[0]['id'] == 1
    assert res_json[0]['temperature'] == 20.1
    assert res_json[0]['humidity'] == 51.2
    assert res_json[0]['location'] == 'kitchen'
    assert res_json[0]['device'] == 'dev1_esp'
    assert 'created' in res_json[0].keys()
    assert len(res_json) == 1


def test_not_accessible_routing_air_state(client):
    res = client.post(
        '/air_state',
        json={'temperature': 22.1, 'humidity': 40.2, 'location': 'bathroom', 'device': 'dev2_esp'}
    )
    assert 201 == res.status_code
    res_json = res.get_json()
    assert res_json['id'] == 1

    res = client.get('/air_state/1')
    assert 404 == res.status_code

    res = client.put('/air_state/1')
    assert 404 == res.status_code

    res = client.delete('/air_state/1')
    assert 404 == res.status_code

