"""
A registry for logic_tree_branches (sources and GMMs) that are uniquely identified by a shake_256 hash.

Data is stored in the resources folder in CSV form. New branched may be added by developers to support
new source or logic tree components.
"""

import csv
import io
import pathlib
import hashlib
from dataclasses import dataclass, asdict
from nzshm_model import logic_tree

HEADERS = ['hash_digest','identity','extra']
GMM_REGISTRY_CSV = pathlib.Path(__file__).parent.parent /  'resources' / 'gmm_branches.csv'
SOURCE_REGISTRY_CSV = pathlib.Path(__file__).parent.parent / 'resources' / 'source_branches.csv'


def identity_digest(identity:str) -> str:
    return hashlib.shake_256(identity.encode()).hexdigest(6)


class Registry():
    gmms:'BranchRegistry' = None
    sources:'BranchRegistry' = None

    @property
    def gmm_registry(self):
        if not self.gmms:
            self.gmms = BranchRegistry().load(open(GMM_REGISTRY_CSV, 'r'))
        return self.gmms

    @property
    def source_registry(self):
        if not self.sources:
            self.sources = BranchRegistry().load(open(SOURCE_REGISTRY_CSV, 'r'))
        return self.sources


@dataclass
class BranchRegistryEntry():
    identity: str
    hash_digest: str = ""
    extra: str = ""

    def __post_init__(self):
        """Set default, or validate the user hash"""
        if self.hash_digest:
            if not self.hash_digest == identity_digest(self.identity):
                raise ValueError(f'Incorrect hash_digest "{self.hash_digest}"" for "{self.identity}"')
        else:
            self.hash_digest = identity_digest(self.identity)


class BranchRegistry():

    def __init__(self):
        self._branches_by_hash = dict()
        self._branches_by_identity = dict() 
    
    def _load_row(self, row):
        entry = BranchRegistryEntry(**row) 
        assert entry.hash_digest not in self._branches_by_hash
        assert entry.identity not in self._branches_by_identity
    
        self._branches_by_hash[entry.hash_digest] = entry
        self._branches_by_identity[entry.identity] = entry 

    def load(self, registry_file: io.FileIO) -> 'BranchRegistry':
        registry_file.seek(0)
        reader = csv.DictReader(registry_file, fieldnames=HEADERS)
        headers = list(next(reader).values())
        assert HEADERS == headers
        for row in reader:
            self._load_row(row)
        return self

    def save(self, registry_file: io.FileIO) -> None:
        csv_writer = csv.DictWriter(registry_file, fieldnames=HEADERS)
        csv_writer.writeheader()
        for row in self._branches_by_hash.values():
            csv_writer.writerow(asdict(row))

    def add(self, entry: BranchRegistryEntry) -> None:
        if entry.hash_digest in self._branches_by_hash:
            assert entry.identity in self._branches_by_identity
        else:
            assert entry.identity not in self._branches_by_identity            

        self._branches_by_hash[entry.hash_digest] = entry
        self._branches_by_identity[entry.identity] = entry     

    def get_by_hash(self, hash_digest: str)  -> BranchRegistryEntry:
        return self._branches_by_hash[hash_digest]

    def get_by_identity(self, identity:str) -> BranchRegistryEntry:
        return self._branches_by_identity[identity]

    def __len__(self):
        return len(self._branches_by_hash.keys())


