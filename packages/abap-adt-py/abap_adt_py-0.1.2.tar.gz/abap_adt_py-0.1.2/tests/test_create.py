import datetime

import pytest
from abap_adt_py.adt_client import AdtClient

TEST_CREATE_ORDER = 1
TEST_CREATE_CLASS_INTERFACE_ORDER = 2


@pytest.mark.order(TEST_CREATE_ORDER)
def test_create_report(client: AdtClient, test_report: str):
    file_created = client.create(
        object_type="PROG/P",
        name=test_report,
        description="Test Program",
        parent="$TMP",
    )
    assert file_created


@pytest.mark.order(TEST_CREATE_ORDER)
def test_create_class(client: AdtClient, test_class: str):
    file_created = client.create(
        object_type="CLAS/OC",
        name=test_class,
        description="Test Class",
        parent="$TMP",
    )
    assert file_created


@pytest.mark.order(TEST_CREATE_CLASS_INTERFACE_ORDER)
def test_create_abap_testclass_include(client: AdtClient, test_class: str):
    uri = f"/sap/bc/adt/oo/classes/{test_class}"
    lock_handle = client.lock(uri)
    file_created = client.create_test_class_include(test_class, lock_handle)
    client.unlock(uri, lock_handle)
    assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_table(client: AdtClient, test_table: str):
#     file_created = client.create(
#         object_type="TABL/DT",
#         name=test_table,
#         description="Test Table",
#         parent="$TMP",
#     )
#     assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_interface(client: AdtClient, test_interface: str):
#     file_created = client.create(
#         object_type="INTF/OI",
#         name=test_interface,
#         description="Test Interface",
#         parent="$TMP",
#     )
#     assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_executable_program(client: AdtClient, test_executable: str):
#     file_created = client.create(
#         object_type="PROG/I",
#         name=test_executable,
#         description="Test Executable Program",
#         parent="$TMP",
#     )
#     assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_function_group(client: AdtClient, test_fugr: str):
#     file_created = client.create(
#         object_type="FUGR/F",
#         name=test_fugr,
#         description="Test Function Group",
#         parent="$TMP",
#     )
#     assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_function_module(client: AdtClient, test_func_mod: str):
#     file_created = client.create(
#         object_type="FUGR/FF",
#         name=test_func_mod,
#         description="Test Function Module",
#         parent="$TMP",
#     )
#     assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_message_class(client: AdtClient, test_msag: str):
#     file_created = client.create(
#         object_type="MSAG/N",
#         name=test_msag,
#         description="Test Message Class",
#         parent="$TMP",
#     )
#     assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_dcl_source(client: AdtClient, test_dcls: str):
#     file_created = client.create(
#         object_type="DCLS/DL",
#         name=test_dcls,
#         description="Test DCL Source",
#         parent="$TMP",
#     )
#     assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_ddls_view(client: AdtClient, test_ddls: str):
#     file_created = client.create(
#         object_type="DDLS/DF",
#         name=test_ddls,
#         description="Test CDS View",
#         parent="$TMP",
#     )
#     assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_ddlx_extension(client: AdtClient, test_ddlx: str):
#     file_created = client.create(
#         object_type="DDLX/EX",
#         name=test_ddlx,
#         description="Test CDS View Extension",
#         parent="$TMP",
#     )
#     assert file_created


# @pytest.mark.order(TEST_CREATE_ORDER)
# def test_create_data_element(client: AdtClient, test_dtel: str):
#     file_created = client.create(
#         object_type="DTEL/DE",
#         name=test_dtel,
#         description="Test Data Element",
#         parent="$TMP",
#     )
#     assert file_created
