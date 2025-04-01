import io

import pytest

from nzshm_model import branch_registry


@pytest.fixture(scope='module')
def gmm_csv_fixture():
    csv = """
hash_digest,identity,extra
380a95154af2,"Atkinson2022SInter(epistemic=Central, modified_sigma=true)",
957eb00fd580,"Atkinson2022SInter(epistemic=Lower, modified_sigma=true)",
772d4ab2272f,"NZNSHM2022_AbrahamsonGulerce2020SInter(region=GLO, sigma_mu_epsilon=1.28155)",
"""
    yield io.StringIO(csv)


@pytest.fixture(scope='module')
def sources_csv_fixture():
    csv = """
hash_digest,identity,extra
ef55f8757069,RmlsZToxMzA3MDc=|SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MDE=,"[dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s0.66]"
"""  # noqa
    yield io.StringIO(csv)


class TestBranchRegistry:
    def test_init_sources_registry(self, sources_csv_fixture):
        # registry_file = open(sources_csv_fixture, 'r')
        sources_registry = branch_registry.BranchRegistry().load(sources_csv_fixture)
        assert len(sources_registry) == 1

    def test_init_gmm_registry(self, gmm_csv_fixture):
        gmm_registry = branch_registry.BranchRegistry().load(gmm_csv_fixture)
        assert len(gmm_registry) == 3

    def test_add_to_registry(self, gmm_csv_fixture):
        gmm_registry = branch_registry.BranchRegistry().load(gmm_csv_fixture)
        new_entry = branch_registry.BranchRegistryEntry(identity="SomeGMM")
        gmm_registry.add(new_entry)

        assert len(gmm_registry) == 4
        assert gmm_registry.get_by_hash(new_entry.hash_digest) == new_entry
        assert gmm_registry.get_by_identity(new_entry.identity) == new_entry

    def test_save_registry(self, gmm_csv_fixture):
        registry = branch_registry.BranchRegistry().load(gmm_csv_fixture)
        output_file = io.StringIO()
        registry.save(output_file)
        assert output_file.read() == gmm_csv_fixture.read()


class TestBranchRegistryEntry:
    def test_auto_digest(self):
        new_entry = branch_registry.BranchRegistryEntry("SomeGMM")
        assert new_entry.hash_digest == branch_registry.identity_digest("SomeGMM")
        assert new_entry.identity == "SomeGMM"

    def test_validate_user_digest_bad(self):
        with pytest.raises(ValueError):
            new_entry = branch_registry.BranchRegistryEntry("SomeGMM", hash_digest="ABC")
            assert new_entry

    def test_validate_user_digest_good(self):
        new_entry = branch_registry.BranchRegistryEntry(
            "SomeGMM", hash_digest=branch_registry.identity_digest("SomeGMM")
        )
        assert new_entry.hash_digest == branch_registry.identity_digest("SomeGMM")
        assert new_entry.identity == "SomeGMM"


class TestRegistryClass:
    def test_source_registry(self):
        registry = branch_registry.Registry()
        assert len(registry.source_registry) == 49
        entry = registry.source_registry.get_by_identity("RmlsZToxMzA3NTM=|SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE2NTc=")
        assert entry.hash_digest == "af9ec2b004d7"

    def test_source_registry_by_extra(self):
        """
        ef55f8757069,RmlsZToxMzA3MDc=|SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MDE=,
        "[dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s0.66]"
        """
        registry = branch_registry.Registry()
        assert len(registry.source_registry) == 49
        entry = registry.source_registry.get_by_extra("[dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s0.66]")
        assert entry.hash_digest == "ef55f8757069"
        assert entry.identity == "RmlsZToxMzA3MDc=|SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MDE="
