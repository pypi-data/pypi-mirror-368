# masterai-pptx2md

```python
from masterai_pptx2md.parser import Parse
from masterai_pptx2md.models import Config
from masterai_pptx2md.outputter import MarkDownOutPutter

c = Config()
md_outputter = MarkDownOutPutter()
p = Parse(c, md_outputter)
with open("pptx.pptx", "rb") as pptx:
    with open("pptx.md", "w") as md:
        md.write(p.parse(pptx.read()))
```