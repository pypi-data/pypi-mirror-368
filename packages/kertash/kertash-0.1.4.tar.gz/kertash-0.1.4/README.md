# kertash

[![PyPI version](https://img.shields.io/pypi/v/kertash.svg)](https://pypi.org/project/kertash/)
[![Python version](https://img.shields.io/pypi/pyversions/kertash.svg)](https://pypi.org/project/kertash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**kertash** adalah modul Python sederhana untuk menganalisis dan melakukan cracking hash menggunakan wordlist indonesian dan juga rockyou.txt.
Mendukung crack single hash, file hash, serta analisis tipe hash.

## Instalasi

```bash
pip install kertash
```

## Fitur

- Crack satu hash dengan mode tertentu
- Crack semua hash dari file (`all` mode untuk mencoba semua algoritma)
- Analisis tipe hash tunggal atau dari file

## Contoh Penggunaan

```python
from kertash import crack, crack_file, analyze, analyze_file

# Crack single hash
status, result = crack("md5", "5d41402abc4b2a76b9719d911017c592")
print(status, result)  # True hello (mode: MD5 (0))

# Crack hash dari file dengan semua algoritma
for hash_value, status, result in crack_file("hashes.txt", "all"):
    print(hash_value, status, result)

# Analisis single hash 
candidates = analyze("5d41402abc4b2a76b9719d911017c592")
print(candidates)

# Analisis hash dari file
for hash_value, candidates in analyze_file("hashes.txt"):
    print(hash_value, candidates)
```



## Lisensi

MIT License Â© 2025 - Hades