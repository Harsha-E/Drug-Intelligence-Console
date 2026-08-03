import hashlib
import os

def compute_directory_hash(directory):
    if not os.path.exists(directory):
        return ""
    hasher = hashlib.sha256()
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if file.endswith('.json') or file.endswith('.yaml') or file.endswith('.yml'):
                path = os.path.join(root, file)
                with open(path, 'rb') as f:
                    hasher.update(f.read())
    return hasher.hexdigest()

def generate_build_hash(knowledge_dir, evidence_dir, vocab_dir, claims_dir, maps_dir, schema_version):
    hasher = hashlib.sha256()
    hasher.update(schema_version.encode('utf-8'))
    hasher.update(compute_directory_hash(knowledge_dir).encode('utf-8'))
    hasher.update(compute_directory_hash(evidence_dir).encode('utf-8'))
    hasher.update(compute_directory_hash(vocab_dir).encode('utf-8'))
    hasher.update(compute_directory_hash(claims_dir).encode('utf-8'))
    hasher.update(compute_directory_hash(maps_dir).encode('utf-8'))
    return hasher.hexdigest()
