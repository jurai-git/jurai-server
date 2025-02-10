def test_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_teapot(client):
    response = client.get("/teapot")
    assert response.status_code == 418
    assert response.json["message"] == "IM_A_TEAPOT"
