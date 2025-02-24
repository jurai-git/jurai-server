import pytest

from app import RequerenteService, AdvogadoService
from app.main.model.advogado import Advogado
from app.test.controller.test_advogado_controller import advogado_create_data, alt_advogado_data
from app.main.model.requerente import Requerente

requerente_data = {
    'cpf_cnpj': '83827894808',
    'nome': 'requerente',
    'nome_social': 'requerente_social',
    'genero': 'M',
    'idoso': False,
    'rg': '217179745',
    'orgao_emissor': 'SSP',
    'estado_civil': 'casado',
    'nacionalidade': "brasileiro(a)",
    "profissao": "encanador",
    "cep": "13106108",
    "logradouro": "Rua Cotil",
    "email": "requerente.encanador@proton.me",
    "num_imovel": "123",
    "complemento": "casa",
    "estado": "São Paulo",
    "cidade": "limeira",
    "bairro": "Jd. Nova Itália",
}

@pytest.fixture(scope='function')
def advogado(client, app):
    response = client.post('/advogado/new', json=advogado_create_data)
    assert response.status_code == 201

    advogado_service: AdvogadoService = app.extensions['advogado_service']
    advogados = advogado_service.get_all()
    assert len(advogados) == 1
    advogado: Advogado = advogado_service.get_all()[0]
    return advogado

@pytest.fixture(scope='function')
def requerente(client, app, advogado):
    response = client.post('/requerente/new', json=requerente_data,
                           headers={"Authorization": f"Bearer {advogado.access_token}"})
    assert response.status_code // 100 == 2

    # Get the created requerente and assert it was correctly related to the advogado
    requerente_service: RequerenteService = app.extensions['requerente_service']
    requerentes = requerente_service.get_requerentes_unserialized(advogado)
    assert len(requerentes) == 1
    adv_requerentes = advogado.requerentes
    assert len(adv_requerentes) == 1
    assert requerentes[0] == adv_requerentes[0]
    return requerentes[0]

def test_create_requerente(client, app, advogado: Advogado, requerente: Requerente):
    for key, value in requerente_data.items():
        assert getattr(requerente, key) == value

def test_create_requerente_with_conflicting_username(client, app, advogado: Advogado, requerente: Requerente):
    response = client.post('requerente/new', json=requerente_data, headers={"Authorization": f"Bearer {advogado.access_token}"})
    assert response.status_code == 409

    newdata = requerente_data
    newdata['cpf_cnpj'] = '1029381203982' # test for just the RG field being equal

    response = client.post('requerente/new', json=requerente_data, headers={"Authorization": f"Bearer {advogado.access_token}"})
    assert response.status_code == 409

    newdata = requerente_data
    newdata['rg'] = '0193812132' # test for just the CPF field being equal

    response = client.post('requerente/new', json=requerente_data, headers={"Authorization": f"Bearer {advogado.access_token}"})
    assert response.status_code == 409

def test_create_requerente_without_fields(client, app, advogado):
    response = client.post('requerente/new', json={}, headers={"Authorization": f"Bearer {advogado.access_token}"})
    assert response.status_code == 400

def test_create_requerente_with_empty_fields(client, app, advogado):
    old_nome = requerente_data['nome']
    requerente_data['nome'] = ''
    response = client.post('requerente/new', json=requerente_data, headers={"Authorization": f"Bearer {advogado.access_token}"})
    requerente_data['nome'] = old_nome
    assert response.status_code == 400
    requerente_service: RequerenteService = app.extensions['requerente_service']
    requerentes = requerente_service.get_requerentes_unserialized(advogado)
    assert len(requerentes) == 0


def test_create_requerente_without_token(client, app, advogado):
    response = client.post('requerente/new', json=requerente_data)
    assert response.status_code == 401

    requerente_service: RequerenteService = app.extensions['requerente_service']
    requerentes = requerente_service.get_requerentes_unserialized(advogado)
    assert len(requerentes) == 0

def test_create_requerente_with_invalid_token(client, app, advogado):
    response = client.post('requerente/new', json=requerente_data, headers={"Authorization": f"Bearer abc"})
    assert response.status_code == 401

    requerente_service: RequerenteService = app.extensions['requerente_service']
    requerentes = requerente_service.get_requerentes_unserialized(advogado)
    assert len(requerentes) == 0


def test_delete_requerente(client, app, advogado, requerente):
    response = client.delete('requerente/remove', json={"requerente_id": requerente.id_requerente}, headers={"Authorization": f"Bearer {advogado.access_token}"})
    assert response.status_code // 100 == 2

    requerente_service: RequerenteService = app.extensions['requerente_service']
    requerentes = requerente_service.get_requerentes_unserialized(advogado)
    assert len(requerentes) == 0

def test_delete_requerente_with_invalid_auth(client, app, advogado, requerente):
    response = client.delete('requerente/remove', json={"requerente_id": requerente.id_requerente}, headers={"Authorization": f"Bearer abc"})
    assert response.status_code == 401

    requerente_service: RequerenteService = app.extensions['requerente_service']
    requerentes = requerente_service.get_requerentes_unserialized(advogado)
    assert len(requerentes) == 1

def test_delete_requerente_with_other_advogado_token(client, app, advogado, requerente):
    response = client.post('/advogado/new', json=alt_advogado_data)
    assert response.status_code // 100 == 2

    advogado_service: AdvogadoService = app.extensions['advogado_service']
    advogados = advogado_service.get_all()
    assert len(advogados) == 1
    advogado: Advogado = advogado_service.get_all()[0]

    response = requerente.delete('requerente/remove', json={'requerente_id': requerente.id_requerente}, headers={"Authorization": f"Bearer {advogado.access_token}"})
    assert response.status_code == 401

    requerente_service: RequerenteService = app.extensions['requerente_service']
    requerentes = requerente_service.get_requerentes_unserialized(advogado)
    assert len(requerentes) == 1