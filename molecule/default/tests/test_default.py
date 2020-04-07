import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_temporary_files_deleted(host):
    f = host.file('/tmp/acme.sh')
    assert not f.exists


# def test_cert_created(host):
#     f = host.file('/tmp/acme_test/test_role.justereseau.com.pem')
#     assert f.exists


# def test_key_created(host):
#     f = host.file('/tmp/acme_test/test_role.justereseau.com.key')
#     assert f.exists
