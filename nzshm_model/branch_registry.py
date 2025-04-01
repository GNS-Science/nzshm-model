"""
A registry for logic_tree_branches (sources and GMMs) that are uniquely identified by a shake_256 hash.

Data is stored in the resources folder in CSV form. New branched may be added by developers to support
new source or logic tree components.

Examples:
    >>> from nzshm_model import branch_registry
    >>> registry = branch_registry.Registry()
    >>> entry = registry.source_registry.get_by_hash("af9ec2b004d7")
    ... BranchRegistryEntry(... )

Functions:
    identity_digest: get a standard hash_digest from an identity string
"""

import csv
import hashlib
import importlib.resources as resources
from dataclasses import asdict, dataclass
from typing import IO, Any, Optional, Union

HEADERS = ['hash_digest', 'identity', 'extra']
RESOURCES_DIR = resources.files('nzshm_model.resources')
GMM_REGISTRY_CSV = RESOURCES_DIR / 'gmm_branches.csv'
SOURCE_REGISTRY_CSV = RESOURCES_DIR / 'source_branches.csv'


def identity_digest(identity: str) -> str:
    """get a standard hash_digest from an identity string

    Arguments:
        identity: a unique identity string

    Returns:
        a shake_256 hash digest
    """
    return hashlib.shake_256(identity.encode()).hexdigest(6)


class Registry:
    """A container for the published registries.

    Attributes:
        gmm_registry: the model sources registry.
        source_registry: the model gmms registry.
    """

    _gmms: Optional['BranchRegistry'] = None
    _sources: Optional['BranchRegistry'] = None

    @property
    def gmm_registry(self) -> 'BranchRegistry':
        if not self._gmms:
            self._gmms = BranchRegistry().load(GMM_REGISTRY_CSV.open('r'))
        return self._gmms

    @property
    def source_registry(self) -> 'BranchRegistry':
        if not self._sources:
            self._sources = BranchRegistry().load(SOURCE_REGISTRY_CSV.open('r'))
        return self._sources


@dataclass
class BranchRegistryEntry:
    """A standard registry entry

    Attributes:
        identity: the unique identity string (see Branch.registry_identity)
        hash_digest: the shake_256 hexdigest of the identity.
        extra: more information about the entry.
    """

    identity: str
    hash_digest: Optional[str] = None
    extra: Optional[str] = None

    def __post_init__(self):
        if self.hash_digest:
            if not self.hash_digest == identity_digest(self.identity):
                raise ValueError(f'Incorrect hash_digest "{self.hash_digest}"" for "{self.identity}"')
        else:
            self.hash_digest = identity_digest(self.identity)


class BranchRegistry:
    """Storage Manager for BranchRegistryEntry objects"""

    def __init__(self):
        self._branches_by_hash = dict()
        self._branches_by_identity = dict()
        self._branches_by_extra = dict()

    def _load_row(self, row):
        entry = BranchRegistryEntry(**row)
        assert entry.hash_digest not in self._branches_by_hash
        assert entry.identity not in self._branches_by_identity

        self._branches_by_hash[entry.hash_digest] = entry
        self._branches_by_identity[entry.identity] = entry
        if entry.extra:
            self._branches_by_extra[entry.extra] = entry

    def load(self, registry_file: IO[Any]) -> 'BranchRegistry':
        """Load the entries contained in a CSV file.

        Arguments:
            registry_file: file-like object with expected CSV header file

        Returns:
            the populated BranchRegistry
        """
        registry_file.seek(0)
        reader = csv.DictReader(registry_file, fieldnames=HEADERS)
        headers = list(next(reader).values())
        assert HEADERS == headers
        for row in reader:
            self._load_row(row)
        return self

    def save(self, registry_file: IO[Any]) -> None:
        """Save the registry entries in CSV format.

        Arguments:
            registry_file: file-like object to write
        """
        csv_writer = csv.DictWriter(registry_file, fieldnames=HEADERS)
        csv_writer.writeheader()
        for row in self._branches_by_hash.values():
            csv_writer.writerow(asdict(row))

    def add(self, entry: BranchRegistryEntry) -> None:
        """add a new registry entry.

        Arguments:
            entry: a BranchRegistryEntry object.
        """
        if entry.hash_digest in self._branches_by_hash:
            assert entry.identity in self._branches_by_identity
        else:
            assert entry.identity not in self._branches_by_identity

        self._branches_by_hash[entry.hash_digest] = entry
        self._branches_by_identity[entry.identity] = entry

    def get_by_hash(self, hash_digest: str) -> BranchRegistryEntry:
        """Get a registry entry by hash_digest.

        Arguments:
            hash_digest: the hash digest string.
        """
        return self._branches_by_hash[hash_digest]

    def get_by_identity(self, identity: str) -> BranchRegistryEntry:
        """Get a registry entry by identity string.

        Arguments:
            identity: the identity string.
        """
        return self._branches_by_identity[identity]

    def get_by_extra(self, extra: str) -> Union[BranchRegistryEntry, None]:
        """Get a registry entry by the extra string.

        Notes:
         - this may return None.
         - only used a workaroound becuase some post NSHM hazard jobs used the extra value
           instead of the identity string in the HDF% ( e.g. `T3BlbnF1YWtlSGF6YXJkVGFzazo2OTMxODkz` )

        Arguments:
            extra: the extra string.
        """
        return self._branches_by_extra.get(extra)

    def __len__(self):
        return len(self._branches_by_hash.keys())
