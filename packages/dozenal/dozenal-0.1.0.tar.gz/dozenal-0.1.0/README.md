# Dozenal

A Python package for handling the Dozenal (base 12) system.

## Features
- Convert between decimal and dozenal
- Basic arithmetic in dozenal

## Usage
```python
from dozenal import decimal_to_dozenal, dozenal_to_decimal, add_dozenal, sub_dozenal

print(decimal_to_dozenal(1728))  # '1000'
print(dozenal_to_decimal('1000'))  # 1728
print(add_dozenal('10', '2'))  # '12'
print(sub_dozenal('20', '10'))  # '10'
```
