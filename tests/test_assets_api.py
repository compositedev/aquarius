#
# Copyright 2021 Ocean Protocol Foundation
# SPDX-License-Identifier: Apache-2.0
#
import json
import lzma

from web3 import Web3

from aquarius.constants import BaseURLs
from aquarius.events.constants import EVENT_METADATA_CREATED
from tests.ddo_samples_invalid import json_dict_no_valid_metadata
from tests.ddos.ddo_sample1 import json_dict
from tests.ddos.ddo_sample_updates import json_before
from tests.helpers import (
    get_event,
    get_web3,
    new_ddo,
    send_create_update_tx,
    test_account1,
    run_request,
    run_request_get_data,
)


def get_ddo(client, base_ddo_url, did):
    rv = client.get(base_ddo_url + f"/{did}", content_type="application/json")
    fetched_ddo = json.loads(rv.data.decode("utf-8"))
    return fetched_ddo


def add_assets(_events_object, name, total=5):
    block = get_web3().eth.block_number
    assets = []
    txs = []
    for i in range(total):
        ddo = new_ddo(test_account1, get_web3(), f"{name}.{i+block}", json_dict)
        assets.append(ddo)

        txs.append(
            send_create_update_tx(
                "create",
                ddo.id,
                bytes([1]),
                lzma.compress(Web3.toBytes(text=json.dumps(dict(ddo.items())))),
                test_account1,
            )
        )

    block = txs[0].blockNumber
    _events_object.store_last_processed_block(block)
    for ddo in assets:
        _ = get_event(EVENT_METADATA_CREATED, block, ddo.id)
        _events_object.process_current_blocks()

    return assets


def test_post_with_no_valid_ddo(client, base_ddo_url, events_object):
    block = get_web3().eth.block_number
    ddo = new_ddo(test_account1, get_web3(), f"dt.{block}", json_dict_no_valid_metadata)
    ddo_string = json.dumps(dict(ddo.items()))
    _ = send_create_update_tx(
        "create",
        ddo.id,
        bytes([1]),
        lzma.compress(Web3.toBytes(text=ddo_string)),
        test_account1,
    )
    get_event(EVENT_METADATA_CREATED, block, ddo.id)
    events_object.process_current_blocks()
    try:
        published_ddo = get_ddo(client, base_ddo_url, ddo.id)
        assert not published_ddo, (
            "publish should fail, Aquarius validation "
            "should have failed and skipped the "
            f"{EVENT_METADATA_CREATED} event."
        )
    except Exception:
        pass


def test_resolveByDtAddress(client_with_no_data, query_url, events_object):
    client = client_with_no_data
    block = get_web3().eth.block_number
    _ddo = json_before.copy()
    ddo = new_ddo(test_account1, get_web3(), f"dt.{block}", _ddo)
    send_create_update_tx(
        "create",
        ddo["id"],
        bytes([1]),
        lzma.compress(Web3.toBytes(text=json.dumps(dict(ddo)))),
        test_account1,
    )
    get_event(EVENT_METADATA_CREATED, block, ddo["id"])
    events_object.process_current_blocks()
    result = run_request_get_data(
        client.post,
        query_url,
        {
            "query": {
                "query_string": {
                    "query": _ddo["dataToken"],
                    "default_field": "dataToken",
                }
            }
        },
    )
    assert len(result["hits"]["hits"]) > 0


def test_get_assets_names(client, events_object):
    base_url = BaseURLs.BASE_AQUARIUS_URL + "/assets"

    response = run_request(client.post, base_url + "/names", {"notTheDidList": ["a"]})

    assert response.status == "400 BAD REQUEST"

    response = run_request(client.post, base_url + "/names", {"didList": []})

    assert response.status == "400 BAD REQUEST"

    response = run_request(client.post, base_url + "/names", {"didList": "notadict"})

    assert response.status == "400 BAD REQUEST"

    response = run_request(client.post, base_url + "/names", "notadict")

    assert response.status == "400 BAD REQUEST"

    assets = add_assets(events_object, "dt_name", 3)
    dids = [ddo["id"] for ddo in assets]
    did_to_name = run_request_get_data(
        client.post, base_url + "/names", {"didList": dids}
    )
    for did in dids:
        assert did in did_to_name, "did not found in response."
        assert did_to_name[did], "did name not found."


def test_asset_metadata_not_found(client):
    result = run_request(client.get, "api/v1/aquarius/assets/metadata/missing")
    assert result.status == "404 NOT FOUND"
