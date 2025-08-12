# thtml-escape

Dependency of `thtml` for (un)escaping HTML.

```python
from thtml_escape import encode, decode

print(encode('" onmouseover="alert(1)'))
# &quot; onmouseover=&quot;alert(1)

print(decode('&quot; onmouseover=&quot;alert(1)'))
```
