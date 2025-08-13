import pytest
from pathlib import Path
from aas_http_client.client import create_client_by_config, AasHttpClient
from basyx.aas.model import AssetAdministrationShell, Submodel, MultiLanguageTextType
import aas_http_client.utilities.model_builder as model_builder
import json
import basyx.aas.adapter.json

@pytest.fixture(scope="module")
def client() -> AasHttpClient:
    try:
        file = Path("./tests/server_configs/test_java_server_config.json").resolve()
        
        if not file.exists():
            raise FileNotFoundError(f"Configuration file {file} does not exist.")
        
        client = create_client_by_config(file, password="")
    except Exception as e:
        raise RuntimeError("Unable to connect to server.")

    shells = client.get_shells()
    if shells is None:
        raise RuntimeError("No shells found on server. Please check the server configuration.")

    for shell in shells.get("result", []):
        id = shell.get("id", "")
        client.delete_shells_by_id(id)
        
    submodels = client.get_submodels()
    if submodels is None:
        raise RuntimeError("No submodels found on server. Please check the server configuration.")

    for submodel in submodels.get("result", []):
        id = submodel.get("id", "")
        client.delete_submodels_by_id(id)        

    return client

@pytest.fixture(scope="module")
def shared_sm() -> Submodel:
    # create a Submodel
    return model_builder.create_base_submodel("sm_http_client_unit_tests", "")

@pytest.fixture(scope="module")
def shared_aas(client: AasHttpClient, shared_sm: Submodel) -> AssetAdministrationShell:
    # create an AAS
    aas = model_builder.create_base_ass(id_short="aas_http_client_unit_tests", namespace="")

    # add Submodel to AAS
    model_builder.add_submodel_to_aas(aas, shared_sm)
    
    return aas
 
def test_001_connect(client: AasHttpClient):
    assert client is not None
    
def test_002_get_shells(client: AasHttpClient):
    result = client.get_shells()
    assert result is not None
    shells = result.get("result", [])
    assert len(shells) == 0

def test_003_post_shells(client: AasHttpClient, shared_aas: AssetAdministrationShell):
    aas_data_string = json.dumps(shared_aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_data = json.loads(aas_data_string)
    result = client.post_shells(aas_data)
    
    assert result is not None
    result_id_short = result.get("idShort", "")
    assert result_id_short == shared_aas.id_short
    
    get_result = client.get_shells()
    assert get_result is not None
    shells = get_result.get("result", [])
    assert len(shells) == 1
    assert shells[0].get("idShort", "") == shared_aas.id_short

def test_004a_get_shell_by_id(client: AasHttpClient, shared_aas: AssetAdministrationShell):
    result = client.get_shells_by_id(shared_aas.id)
    
    assert result is not None
    assert result.get("idShort", "") == shared_aas.id_short

def test_004b_get_shell_by_id_not_found(client: AasHttpClient):
    result = client.get_shells_by_id("non_existent_id")
    
    assert result is None
    
def test_005a_put_shells(client: AasHttpClient, shared_aas: AssetAdministrationShell):
    aas = AssetAdministrationShell(id_=shared_aas.asset_information.global_asset_id, asset_information=shared_aas.asset_information)
    aas.id_short = shared_aas.id_short

    description_text = "Put description for unit tests"
    aas.description = MultiLanguageTextType({"en": description_text})
    aas.submodel = shared_aas.submodel  # Keep existing submodels
    
    aas_data_string = json.dumps(aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_data = json.loads(aas_data_string)
    
    result = client.put_shells(shared_aas.id, aas_data)
    
    assert result
    
    get_result = client.get_shells_by_id(shared_aas.id)
    
    assert get_result is not None
    assert get_result.get("idShort", "") == shared_aas.id_short
    assert get_result.get("id", "") == shared_aas.id
    # description must have changed
    assert get_result.get("description", {})[0].get("text", "") == description_text
    assert get_result.get("description", {})[0].get("text", "") != shared_aas.description.get("en", "")
    # submodels must be retained
    assert len(get_result.get("submodels", [])) == len(shared_aas.submodel)
    # The display name must be empty 
    assert len(get_result.get("displayName", {})) == 0

def test_005b_put_shells_with_id(client: AasHttpClient, shared_aas: AssetAdministrationShell):
    # put with other ID
    id_short = "put_short_id"
    asset_info = model_builder.create_base_asset_information(id_short)
    aas = AssetAdministrationShell(id_=asset_info.global_asset_id, asset_information=asset_info)
    aas.id_short = id_short

    description_text = {"en": "Updated description for unit tests"}
    aas.description = MultiLanguageTextType(description_text)
    
    aas_data_string = json.dumps(shared_aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_data = json.loads(aas_data_string)
    
    aas_data["id"] = "updated_id"  # Ensure the id is included in the update
    
    result = client.put_shells(shared_aas.id, aas_data)
    
    assert not result

def test_006_get_shells_reference_by_id(client: AasHttpClient, shared_aas: AssetAdministrationShell):
    result = client.get_shells_reference_by_id(shared_aas.id)
    
    # Basyx java server do not provide this endpoint
    assert not result
        
def test_007_get_shells_submodels_by_id_not_posted(client: AasHttpClient, shared_aas: AssetAdministrationShell, shared_sm: Submodel):
    result = client.get_shells_submodels_by_id(shared_aas.id, shared_sm.id)

    assert result is None
    
def test_008_get_submodels(client: AasHttpClient):
    result = client.get_submodels()
    
    assert result
    submodels = result.get("result", [])
    assert len(submodels) == 0
    
def test_009_post_submodels(client: AasHttpClient, shared_sm: Submodel):
    sm_data_string = json.dumps(shared_sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)
    
    result = client.post_submodels(sm_data)

    assert result is not None
    result_id_short = result.get("idShort", "")
    assert result_id_short == shared_sm.id_short
    
    get_result = client.get_submodels()
    assert get_result is not None
    submodels = get_result.get("result", [])
    assert len(submodels) == 1
    assert submodels[0].get("idShort", "") == shared_sm.id_short

def test_010_get_shells_submodels_by_id(client: AasHttpClient, shared_aas: AssetAdministrationShell, shared_sm: Submodel):
    result = client.get_shells_submodels_by_id(shared_aas.id, shared_sm.id)

    # Basyx java server do not provide this endpoint
    assert result is None
    
def test_011a_get_submodels_by_id(client: AasHttpClient, shared_sm: Submodel):
    result = client.get_submodels_by_id(shared_sm.id)

    assert result is not None
    result_id_short = result.get("idShort", "")
    assert result_id_short == shared_sm.id_short
    
def test_011b_get_submodels_by_id_not_found(client: AasHttpClient):
    result = client.get_submodels_by_id("non_existent_id")

    assert result is None
 
def test_012_patch_submodel_by_id(client: AasHttpClient, shared_sm: Submodel):
    sm = Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Patched description for unit tests"
    sm.description = MultiLanguageTextType({"en": description_text})

    sm_data_string = json.dumps(sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    result = client.patch_submodel_by_id(shared_sm.id, sm_data)

    # Basyx java server do not provide this endpoint
    assert not result

def test_013_put_shells_submodels_by_id(client: AasHttpClient, shared_aas: AssetAdministrationShell, shared_sm: Submodel):
    sm = Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Put via shell description for unit tests"
    sm.description = MultiLanguageTextType({"en": description_text})

    sm_data_string = json.dumps(sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    result = client.put_shells_submodels_by_id(shared_aas.id, shared_sm.id, sm_data)
    
    assert not result
            
def test_014_put_submodels_by_id(client: AasHttpClient, shared_sm: Submodel):
    sm = Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Put description for unit tests"
    sm.description = MultiLanguageTextType({"en": description_text})

    sm_data_string = json.dumps(sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    result = client.put_submodels_by_id(shared_sm.id, sm_data)
    
    assert result
    
    get_result = client.get_submodels_by_id(shared_sm.id)
    assert get_result is not None
    assert get_result.get("idShort", "") == shared_sm.id_short
    assert get_result.get("id", "") == shared_sm.id
    # description must have changed
    assert get_result.get("description", {})[0].get("text", "") == description_text
    assert get_result.get("description", {})[0].get("text", "") != shared_sm.description.get("en", "")
    assert len(get_result.get("displayName", {})) == 0
    
    # restore to its original state
    sm_data_string = json.dumps(shared_sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)
    client.put_submodels_by_id(shared_sm.id, sm_data)  # Restore original submodel            
            
def test_098_delete_shells_by_id(client: AasHttpClient, shared_aas: AssetAdministrationShell):
    result = client.delete_shells_by_id(shared_aas.id)
    
    assert result
    
    get_result = client.get_shells()
    assert get_result is not None
    shells = get_result.get("result", [])
    assert len(shells) == 0
        
def test_099_delete_submodel_by_id(client: AasHttpClient, shared_sm: Submodel):
    result = client.delete_submodels_by_id(shared_sm.id)
    
    assert result
    
    get_result = client.get_submodels()
    assert get_result is not None
    submodels = get_result.get("result", [])
    assert len(submodels) == 0