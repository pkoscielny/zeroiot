#TODO: add checking parameters.
#TODO: write helper for recursively json checking or find relevant module in internet.
#TODO: add more tests for list

def test_no_insolations(client):
    res = client.get('/insolation')
    assert 200 == res.status_code
    assert b'[]' in res.data


def test_add_new_insolation(client):
    res = client.post(
        '/insolation',
        json = {'insolation': 42, 'device': 'dev2_esp'}
    )
    assert 201 == res.status_code
    res_json = res.get_json()
    assert res_json['id'] == 1

    res = client.get('/insolation')
    assert 200 == res.status_code
    res_json = res.get_json()
    assert res_json[0]['id'] == 1
    assert res_json[0]['insolation'] == 42
    assert res_json[0]['device'] == 'dev2_esp'
    assert len(res_json) == 1

    # This routing is not accessible. Only 'list' and 'add' actions work.
    res = client.get('/insolation/1')
    assert 404 == res.status_code


def test_not_accessible_routing_insolation(client):
    res = client.post(
        '/insolation',
        json = {'insolation': 42, 'device': 'dev2_esp'}
    )
    assert 201 == res.status_code
    res_json = res.get_json()
    assert res_json['id'] == 1

    res = client.get('/insolation/1')
    assert 404 == res.status_code

    res = client.put('/insolation/1')
    assert 404 == res.status_code

    res = client.delete('/insolation/1')
    assert 404 == res.status_code

