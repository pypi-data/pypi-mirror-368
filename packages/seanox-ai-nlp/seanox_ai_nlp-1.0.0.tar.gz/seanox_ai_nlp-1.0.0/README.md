<p>
  <a href="https://github.com/seanox/seanox-ai-nlp/pulls"
      title="Development"
    ><img src="https://img.shields.io/badge/development-active-green?style=for-the-badge"
  ></a>  
  <a href="https://github.com/seanox/seanox-ai-nlp/issues"
    ><img src="https://img.shields.io/badge/maintenance-active-green?style=for-the-badge"
  ></a>
  <a href="https://seanox.com/contact"
    ><img src="https://img.shields.io/badge/support-active-green?style=for-the-badge"
  ></a>
</p>

# Description

This package addresses challenges in semantic processing of domain-specific
content within NLP pipelines. It aims to improve the connection between semantic
user queries and structured, technically rich data—especially where traditional
embedding models and similarity metrics reach their limits.

The approach combines:

- __Token-sensitive preprocessing__ for better contextual understanding
- __Rule-based enhancements__ to detect technical terms and units
- __Modular components__ that integrate easily into existing retrieval systems

The package attempts to support existing NLP workflows through lightweight
components designed to better handle domain-specific terminology, structured
data, and semantic matching.

Further modules are planned to extend the package's capabilities, including:

- __Sentence Generator__: For creating synthetic, recombinable training data to
  support model fine-tuning
- __Logic Query Composer__: For transforming natural-language queries into
  structured formats (e.g. SQL, JSON, YAML, etc.)

# Licence Agreement

LIZENZBEDINGUNGEN - Seanox Software Solutions ist ein Open-Source-Projekt, im
Folgenden Seanox Software Solutions oder kurz Seanox genannt.

Diese Software unterliegt der Version 2 der Apache License.

Copyright (C) 2025 Seanox Software Solutions

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

# System Requirement

- Python 3.9 or higher

# Installation & Setup

```
pip install seanox-ai-nlp
```

# Packages & Modules

## [units](seanox_ai_nlp/units/README.md)

The units module uses __rule-based__, __deterministic pattern recognition__ to
identify numerical expressions and units in text. It does not rely on __large
language models (LLMs)__ and is suitable for integration into __lightweight NLP
pipelines__. Its language-agnostic design and adaptable formatting support a
wide range of applications, including general, semi-technical, and semi-academic
content. The module can be integrated with tools like spaCy’s __EntityRuler__,
supporting __annotation__, __filtering__, and __token alignment__ workflows with
structured output for downstream semantic analysis -- without performing it
itself.

### Features

- __Pattern-based extraction__  
  Identifies constructs like _5 km_, _-20 &ordm;C_, or _1000 hPa_ using regular
  expressions and token patterns -- no training required.
  
- __Language-independent architecture__  
  Operates at token and character level, making it effective across multilingual
  content.
  
- __Support for compound expressions__  
  Recognizes both unit combinations (_km/h, kWh/m&sup2;, g/cm&sup3;_) and
  numerical constructs using signs and operators: _&plusmn;, &times;, &middot;,
  :, /, ^, –_ and more.
  
- __Integration-ready output__  
  Returns structured results compatible with tools like spaCy’s EntityRuler for
  use in pipelines.
  
- __Transparent design__  
  Fully interpretable and deterministic -- avoids black-box ML, supporting
  reliable and auditable processing.

### Quickstart

- [Usage](seanox_ai_nlp/units/README.md#usage)
- [Integration in NLP Workflows](
  seanox_ai_nlp/units/README.md#integration-in-nlp-workflows)
- [Downstream Processing with pandas](
  seanox_ai_nlp/units/README.md#downstream-processing-with-pandas)

# Changes

TODO:

# Contact

[Issues](https://github.com/seanox/seanox-ai-nlp/issues)  
[Requests](https://github.com/seanox/seanox-ai-nlp/pulls)  
[Mail](https://seanox.com/contact)
