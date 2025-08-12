import pytest
import json
from decimal import Decimal

from transpara.internal.output_tstore import DecimalEncoder







@pytest.fixture
def sample_data():
    return {
        "metric": "test_metric",
        "value": Decimal("12.34"),
        "timestamp": "2025-08-05T12:00:00Z",
        "labels": "tag=label"
    }

def test_decimal_value_conversion(sample_data):
    json_str = json.dumps(sample_data, cls=DecimalEncoder)
    result = json.loads(json_str)

    assert result["metric"] == sample_data["metric"]
    assert isinstance(result["value"], float)
    assert result["value"] == float(sample_data["value"])
    assert result["timestamp"] == sample_data["timestamp"]
    assert result["labels"] == sample_data["labels"]


@pytest.mark.asyncio
async def test_write_data_endpoint(client, auth_token):
    client.headers["Authorization"] = f"Bearer {auth_token}"



    batch = {
        "testmetric|tag=test": [
            {"v": Decimal(99.99), "ts": "2025-08-05T12:00:00-06:00"},
            {"v": 120, "ts": "2025-08-05T13:00:00-06:00"},
            {"v": "140", "ts": "2025-08-05T13:00:00-06:00"},

        ]
    }
    json_str = json.dumps(batch, cls=DecimalEncoder)


    response = await client.post("/write/write-data?overwrite_data=false&write_mode=both", content=json_str)

    assert response.status_code == 200, (
        f"Expected 200 OK, got {response.status_code} – {response.text}"
    )


@pytest.mark.asyncio
async def test_write_data_endpoint_integration_without_DecimalEncoder(client, auth_token):
    client.headers["Authorization"] = f"Bearer {auth_token}"



    batch = {
        "testmetric|tag=test": [
            {"v": Decimal(99.99), "ts": "2025-08-05T12:00:00-06:00"},
            {"v": 120, "ts": "2025-08-05T13:00:00-06:00"},
            {"v": "140", "ts": "2025-08-05T13:00:00-06:00"},

        ]
    }
    with pytest.raises(TypeError) as e:
        json.dumps(batch)
    
    assert str(e.value) == "Object of type Decimal is not JSON serializable"