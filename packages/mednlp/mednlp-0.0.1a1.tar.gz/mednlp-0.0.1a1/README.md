# MedNLP

Medical Natural Language Processing Toolkit

## Install

```bash
pip install mednlp
```

## Quick Start

```python
from mednlp import MedicalNLP

med_nlp = MedicalNLP()
text = "Patient presents with chest pain and shortness of breath."
entities = med_nlp.extract_entities(text)
```

## License

MIT License
