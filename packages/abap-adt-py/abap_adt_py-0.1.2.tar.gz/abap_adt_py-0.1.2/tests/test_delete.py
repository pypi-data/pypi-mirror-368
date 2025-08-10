import pytest
from abap_adt_py.adt_client import AdtClient

import pytest

TEST_DELETE_ORDER = 10


@pytest.mark.order(TEST_DELETE_ORDER)
def test_delete_report(client: AdtClient, test_report: str):
    uri = f"/sap/bc/adt/programs/programs/{test_report}"
    lock_handle = client.lock(uri)
    client.delete(uri, lock_handle)


@pytest.mark.order(TEST_DELETE_ORDER)
def test_delete_class(client: AdtClient, test_class: str):
    uri = f"/sap/bc/adt/oo/classes/{test_class}"
    lock_handle = client.lock(uri)
    client.delete(uri, lock_handle)
    client.unlock(uri, lock_handle)


# @pytest.mark.order(TEST_DELETE_ORDER)
# def test_delete_table(client: AdtClient, test_table: str):
#     uri = f"/sap/bc/adt/ddic/tables/{test_table}"
#     lock_handle = client.lock(uri)
#     client.delete(uri, lock_handle)


# @pytest.mark.order(TEST_DELETE_ORDER)
# def test_delete_function_module(client: AdtClient, test_func_mod: str):
#     uri = f"/sap/bc/adt/functions/groups/{test_func_mod}"  # Usually FMs are subnodes of FUGRs
#     lock_handle = client.lock(uri)
#     client.delete(uri, lock_handle)


# @pytest.mark.order(TEST_DELETE_ORDER)
# def test_delete_function_group(client: AdtClient, test_fugr: str):
#     uri = f"/sap/bc/adt/functions/groups/{test_fugr}"
#     lock_handle = client.lock(uri)
#     client.delete(uri, lock_handle)


# @pytest.mark.order(TEST_DELETE_ORDER)
# def test_delete_message_class(client: AdtClient, test_msag: str):
#     uri = f"/sap/bc/adt/messages/{test_msag}"
#     lock_handle = client.lock(uri)
#     client.delete(uri, lock_handle)


# @pytest.mark.order(TEST_DELETE_ORDER)
# def test_delete_dcl_source(client: AdtClient, test_dcls: str):
#     uri = f"/sap/bc/adt/authorization/dcls/{test_dcls}"
#     lock_handle = client.lock(uri)
#     client.delete(uri, lock_handle)


# @pytest.mark.order(TEST_DELETE_ORDER)
# def test_delete_ddls_view(client: AdtClient, test_ddls: str):
#     uri = f"/sap/bc/adt/cds/ddls/{test_ddls}"
#     lock_handle = client.lock(uri)
#     client.delete(uri, lock_handle)


# @pytest.mark.order(TEST_DELETE_ORDER)
# def test_delete_ddlx_extension(client: AdtClient, test_ddlx: str):
#     uri = f"/sap/bc/adt/cds/ddlextensions/{test_ddlx}"
#     lock_handle = client.lock(uri)
#     client.delete(uri, lock_handle)


# @pytest.mark.order(TEST_DELETE_ORDER)
# def test_delete_data_element(client: AdtClient, test_dtel: str):
#     uri = f"/sap/bc/adt/ddic/dataelements/{test_dtel}"
#     lock_handle = client.lock(uri)
#     client.delete(uri, lock_handle)
