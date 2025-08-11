# capslovess

مكتبة Python بسيطة للتعامل مع API الخاص بـ Capslovess.

## التثبيت


## الاستخدام

```python
from capslovess.client import CapslovessClient

client = CapslovessClient()
result = client.solve(did="your_did", iid="your_iid")
print(result)
