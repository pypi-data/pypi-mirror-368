# Django EOSE

**Django Encrypted Object Search Engine**  
Efficient parallel search for encrypted or derived fields in Django querysets, with smart batching and caching.

## Features

- Parallel search using processes, threads, or sync mode.
- Batch size adapts to available memory.
- Supports searching across related fields (e.g., `order__client`).
- Caches search results for fast repeated queries.
- Optimized for large datasets and encrypted fields.

## Installation

```sh
pip install django-eose
```

Or add to your requirements.txt:
```sh
django-eose
```
## Requirements

- Python 3.10+
- Django 5.2.5
- sqlparse==0.5.3
- asgiref==3.9.1
- psutil==7.0.0

## Model configuration

Example of model configuration with fields encrypted with Fernet:
```python
class Client(models.Model):
    _encrypted_name = model.BinaryField()
    _encrypted_email = model.BinaryField()

    def _decrypt_field(self, encrypted_value):
        return Fernet(AES_KEY).decrypt(encrypted_value).decode()

    def _encrypt_field(self, value):
        return Fernet(AES_KEY).encrypt(value.encode())
    
    @staticmethod
    def _property(field_name):
        # Getter decrypts the field value before returning it.
        def getter(self):
            return self._decrypt_field(getattr(self, field_name))
        
        # Setter encrypts the value before setting it to the field.
        def setter(self, value):
            setattr(self, field_name, self._encrypt_field(value))

        return property(getter, setter)
    
    name = _property('_encrypted_name')
    email = _property('_encrypted_email')
```

## Usage

Import and use search_queryset:

```python
from django_eose import search_queryset

# Example: search for "john" in related client fields
results = search_queryset(
    search="john",
    queryset=OrderItem.objects.all(),
    related_field="order__client",
    fields=("name", "email"),
    only_fields=("_encrypted_name", "_encrypted_email")
    executor="processes"
)
```

## Parameters

- search: Search term (case-insensitive).
- queryset: Django queryset to search.
- related_field: Dotted path to related object (e.g., "order__client").
- fields: Tuple of fields to inspect on the related object.
- only_fields: Fields to load with .only(...) for optimization (optional).
- executor: "processes", "threads", or "sync" (default: "processes").
- cache_timeout: Cache duration in seconds (default: 600).
- imap_chunksize: Chunk size per worker (default: 10240).
- memory_fraction: Fraction of available memory for batching (default: 0.60).
- avg_obj_size_bytes: Estimated average object size in bytes (optional).
- max_workers: Number of parallel workers (optional).

See search_queryset for full details.

## Settings

Default settings are defined in django_eose/settings.py:

- MEMORY_FRACTION
- IMAP_CHUNKSIZE
- EXECUTOR
- CACHE_TIMEOUT
- AVG_OBJ_SIZE_FALLBACK
- MIN_BATCH_SIZE
- MAX_BATCH_SIZE

License
MIT © 2025 Paulo Otávio Castoldi

## Links

[Source](https://github.com/paulootaviodev/django-eose)
