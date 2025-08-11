# SplitterMR

<img src="https://raw.githubusercontent.com/andreshere00/Splitter_MR/refs/heads/main/docs/assets/splitter_mr_logo.svg#gh-light-mode-only" alt="SplitterMR logo" width=100%/>
<img src="https://raw.githubusercontent.com/andreshere00/Splitter_MR/refs/heads/main/docs/assets/splitter_mr_logo_white.svg#gh-dark-mode-only" alt="SplitterMR logo" width=100%/>

## Description

**SplitterMR** is a library for chunking data into convenient text blocks compatible with your LLM applications.

!!! important
    **New version v0.4.0**
     
    Add support for reading files and splitting them by pages using `PageSplitter`. Add support to read more files with `VanillaReader`.
      
    ➡️ See [**documentation**](https://andreshere00.github.io/Splitter_MR/examples/text/paged_splitter/).


## Features

### Different input formats

SplitterMR can read data from multiples sources and files. To read the files, it uses the Reader components, which inherits from a Base abstract class, `BaseReader`. This object allows you to read the files as a properly formatted string, or convert the files into another format (such as `markdown` or `json`). 

Currently, there are supported three readers: `VanillaReader`, and `MarkItDownReader` and `DoclingReader`. These are the differences between each Reader component:

| **Reader**             | **Unstructured files & PDFs** | **MS Office suite files** | **Tabular data** | **Files with hierarchical schema** | **Image files** | **Markdown conversion** |
|------------------------|-------------------------------|---------------------------|------------------|------------------------------------|-----------------|-------------------------|
| **`VanillaReader`**    | `txt`, `md`, `pdf` | `xlsx`, `docx`, `pptx` | `csv`, `tsv`, `parquet` | `json`, `yaml`, `html`, `xml` | `jpg`, `png`, `webp`, `gif` | Partial                 |
| **`MarkItDownReader`** | `txt`, `md`, `pdf` | `docx`, `xlsx`, `pptx` | `csv`, `tsv` | `json`, `html`, `xml`                    | `jpg`, `png`, `pneg`        | Yes                     |
| **`DoclingReader`**    | `txt`, `md`, `pdf` | `docx`, `xlsx`, `pptx` | –            | `html`, `xhtml`                 | `png`, `jpeg`, `tiff`, `bmp`, `webp` | Yes                     |

### Several splitting methods

SplitterMR allows you to split files in many different ways depending on your needs. The available splitting methods are described in the following table:

| Splitting Technique | Description |
| ------------------------- | -----------------------------|
| **Character Splitter**    | Splits text into chunks based on a specified number of characters. Supports overlapping by character count or percentage. <br> **Parameters:** `chunk_size` (max chars per chunk), `chunk_overlap` (overlapping chars: int or %). <br> **Compatible with:** Text. |
| **Word Splitter**         | Splits text into chunks based on a specified number of words. Supports overlapping by word count or percentage. <br> **Parameters:** `chunk_size` (max words per chunk), `chunk_overlap` (overlapping words: int or %). <br> **Compatible with:** Text. |
| **Sentence Splitter**     | Splits text into chunks by a specified number of sentences. Allows overlap defined by a number or percentage of words from the end of the previous chunk. Customizable sentence separators (e.g., `.`, `!`, `?`). <br> **Parameters:** `chunk_size` (max sentences per chunk), `chunk_overlap` (overlapping words: int or %), `sentence_separators` (list of characters). <br> **Compatible with:** Text. |
| **Paragraph Splitter**    | Splits text into chunks based on a specified number of paragraphs. Allows overlapping by word count or percentage, and customizable line breaks. <br> **Parameters:** `chunk_size` (max paragraphs per chunk), `chunk_overlap` (overlapping words: int or %), `line_break` (delimiter(s) for paragraphs). <br> **Compatible with:** Text. |
| **Recursive Splitter**    | Recursively splits text based on a hierarchy of separators (e.g., paragraph, sentence, word, character) until chunks reach a target size. Tries to preserve semantic units as long as possible. <br> **Parameters:** `chunk_size` (max chars per chunk), `chunk_overlap` (overlapping chars), `separators` (list of characters to split on, e.g., `["\n\n", "\n", " ", ""]`). <br> **Compatible with:** Text.                                                                                   |
| **Token Splitter**        | Splits text into chunks based on the number of tokens, using various tokenization models (e.g., tiktoken, spaCy, NLTK). Useful for ensuring chunks are compatible with LLM context limits. <br> **Parameters:** `chunk_size` (max tokens per chunk), `model_name` (tokenizer/model, e.g., `"tiktoken/cl100k_base"`, `"spacy/en_core_web_sm"`, `"nltk/punkt"`), `language` (for NLTK). <br> **Compatible with:** Text. |
| **Paged Splitter**        | **WORK IN PROGRESS**. Splits text by pages for documents that have page structure. Each chunk contains a specified number of pages, with optional word overlap. <br> **Parameters:** `num_pages` (pages per chunk), `chunk_overlap` (overlapping words). <br> **Compatible with:** Word, PDF, Excel, PowerPoint. |
| **Row/Column Splitter**   | For tabular formats, splits data by a set number of rows or columns per chunk, with possible overlap. Row-based and column-based splitting are mutually exclusive. <br> **Parameters:** `num_rows`, `num_cols` (rows/columns per chunk), `overlap` (overlapping rows or columns). <br> **Compatible with:** Tabular formats (csv, tsv, parquet, flat json). |
| **JSON Splitter**         | Recursively splits JSON documents into smaller sub-structures that preserve the original JSON schema. <br> **Parameters:** `max_chunk_size` (max chars per chunk), `min_chunk_size` (min chars per chunk). <br> **Compatible with:** JSON. |
| **Semantic Splitter**     | **WORK IN PROGRESS**. Splits text into chunks based on semantic similarity, using an embedding model and a max tokens parameter. Useful for meaningful semantic groupings. <br> **Parameters:** `embedding_model` (model for embeddings), `max_tokens` (max tokens per chunk). <br> **Compatible with:** Text. |
| **HTML Tag Splitter**       | Splits HTML content based on a specified tag, or automatically detects the most frequent and shallowest tag if not specified. Each chunk is a complete HTML fragment for that tag. <br> **Parameters:** `chunk_size` (max chars per chunk), `tag` (HTML tag to split on, optional). <br> **Compatible with:** HTML. |
| **Header Splitter**        | Splits Markdown or HTML documents into chunks using header levels (e.g., `#`, `##`, or `<h1>`, `<h2>`). Uses configurable headers for chunking. <br> **Parameters:** `headers_to_split_on` (list of headers and semantic names), `chunk_size` (unused, for compatibility). <br> **Compatible with:** Markdown, HTML. |
| **Code Splitter**         | Splits source code files into programmatically meaningful chunks (functions, classes, methods, etc.), aware of the syntax of the specified programming language (e.g., Python, Java, Kotlin). Uses language-aware logic to avoid splitting inside code blocks. <br> **Parameters:** `chunk_size` (max chars per chunk), `language` (programming language as string, e.g., `"python"`, `"java"`). <br> **Compatible with:** Source code files (Python, Java, Kotlin, C++, JavaScript, Go, etc.). |

!!! warning
    **Semantic Splitter** is **not fully implemented yet**. 
    Stay aware to updates!


## Architecture

![SplitterMR architecture diagram](https://raw.githubusercontent.com/andreshere00/Splitter_MR/refs/heads/main/docs/assets/splitter_mr_architecture_diagram.svg#gh-light-mode-only)
![SplitterMR architecture diagram](https://raw.githubusercontent.com/andreshere00/Splitter_MR/refs/heads/main/docs/assets/splitter_mr_architecture_diagram_white.svg#gh-dark-mode-only)

**SplitterMR** is designed around a modular pipeline that processes files from raw data all the way to chunked, LLM-ready text. There are three main components: Readers, Models and Splitters.

- **Readers**
    - The **`BaseReader`** components read a file and optionally converts to other formats to subsequently conduct a splitting strategy.
    - Supported readers (e.g., **`VanillaReader`**, **`MarkItDownReader`**, **`DoclingReader`**) produce a `ReaderOutput` dictionary containing:
        - **Text** content (in `markdown`, `text`, `json` or another format).
        - Document **metadata**.
        - **Conversion** method.
- **Models:**
    - The **`BaseModel`** component is used to read non-text content using a Visual Language Model (VLM).
    - Supported models are `AzureOpenAI` and `OpenAI`, but more models will be available soon.
    - All the models have a `extract_text` method which returns the LLM response based on a prompt, the client and the model parameters.
- **Splitters**
    - The **`BaseSplitter`** components take the **`ReaderOutput`** text content and divide that text into meaningful chunks for LLM or other downstream use.
    - Splitter classes (e.g., **`CharacterSplitter`**, **`SentenceSplitter`**, **`RecursiveSplitter`**, etc.) allow flexible chunking strategies with optional overlap and rich configuration.

## How to install

Package is published on [PyPi](https://pypi.org/project/splitter-mr/). To install it, you can use the official Python package manager:

```python
pip install splitter-mr
```

Alternatively, you can install it using other Python package management tools such as [`uv`](https://docs.astral.sh/uv/), [Conda](https://anaconda.org/anaconda/conda) or [Poetry](https://python-poetry.org/):

```python
uv add splitter-mr
```

!!! note
    **Python 3.11 or greater** is required to use this library.


## How to use

### Read files

Firstly, you need to instantiate an object from a BaseReader class, for example, `VanillaReader`.

```python
from splitter_mr.reader import VanillaReader

reader = VanillaReader()
```

To read any file, provide the file path within the `read()` method. If you use `DoclingReader` or `MarkItDownReader`, your files will be automatically parsed to markdown text format. The result of this reader will be a `ReaderOutput` object, a dictionary with the following shape:

```python 
reader_output = reader.read('https://raw.githubusercontent.com/andreshere00/Splitter_MR/refs/heads/main/data/lorem_ipsum.txt')
print(reader_output)
```
```python
ReaderOutput(
    text='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum sit amet ultricies orci. Nullam et tellus dui.', 
    document_name='lorem_ipsum.txt',
    document_path='https://raw.githubusercontent.com/andreshere00/Splitter_MR/refs/heads/main/data/lorem_ipsum.txt', 
    document_id='732b9530-3e41-4a1a-a4ea-1d9d6fe815d3', 
    conversion_method='txt', 
    reader_method='vanilla', 
    ocr_method=None, 
    page_placeholder=None,
    metadata={}
    )
```

!!! note
    Note that you can read from an URL, a variable and from a `file_path`. See [Developer guide](https://andreshere00.github.io/Splitter_MR/api_reference/reader/).


### Split text

To split the text, first import the class that implements your desired splitting strategy (e.g., by characters, recursively, by headers, etc.). Then, create an instance of this class and call its `split` method, which is defined in the `BaseSplitter` class.

For example, we will split by characters with a maximum chunk size of 50, with an overlap between chunks:

```python
from splitter_mr.splitter import CharacterSplitter

char_splitter = CharacterSplitter(chunk_size=50, chunk_overlap = 10)
splitter_output = char_splitter.split(reader_output)
print(splitter_output)
```
```python
SplitterOutput(
    chunks=['Lorem ipsum dolor sit amet, consectetur adipiscing', 'adipiscing elit. Vestibulum sit amet ultricies orc', 'ricies orci. Nullam et tellus dui.'], 
    chunk_id=['db454a9b-32aa-4fdc-9aab-8770cae99882', 'e67b427c-4bb0-4f28-96c2-7785f070d1c1', '6206a89d-efd1-4586-8889-95590a14645b'], 
    document_name='lorem_ipsum.txt', 
    document_path='https://raw.githubusercontent.com/andreshere00/Splitter_MR/refs/heads/main/data/lorem_ipsum.txt', 
    document_id='732b9530-3e41-4a1a-a4ea-1d9d6fe815d3', 
    conversion_method='txt', 
    reader_method='vanilla', 
    ocr_method=None, 
    split_method='character_splitter', 
    split_params={'chunk_size': 50, 'chunk_overlap': 10}, 
    metadata={}
    )
```

The returned object is a `SplitterOutput` dataclass, which provides all the information you need to further process your data. You can easily add custom metadata, and you have access to details such as the document name, path, and type. Each chunk is uniquely identified by an UUID, allowing for easy traceability throughout your LLM workflow.

### Compatibility with vision tools for image processing and annotations

Pass a VLM model to any Reader via the `model` parameter:

```python
from splitter_mr.reader import VanillaReader
from splitter_mr.model.models import AzureOpenAIVisionModel

model = AzureOpenAIVisionModel()
reader = VanillaReader(model=model)
output = reader.read(file_path="data/lorem_ipsum.pdf")
print(output.text)
```

These VLMs can be used for captioning, annotation or text extraction. In fact, you can use these models to process the files as you want using the `prompt` parameter in the `read` method for every class which inherits from `BaseReader`. 

!!! note
    To see more details, consult documentation [here](https://andreshere00.github.io/Splitter_MR/api_reference/model/).


## Next features

- [ ] Implement a method to split by embedding similarity: `SemanticSplitter`.
    - [ ] Add HuggingFace embeddings model support.
    - [ ] Add OpenAI embeddings model support.
    - [ ] Add Gemini embeddings model support.
    - [ ] Add Claude Anthropic embeddings model support.
- [ ] Modularize library into several sub-libraries.
- [ ] Add support to read formulas.
- [ ] Add classic **OCR** models: `easyocr` and `pytesseract`.
- [ ] Add new models:
    - [ ] Add HuggingFace VLMs model support.
    - [ ] Add Gemini VLMs model support.
    - [ ] Add Claude Anthropic VLMs model support.
    - [ ] Add Grok VLMs model support.
    - [ ] Add support to generate output in Markdown format.
- [X] Add new supported formats to be analyzed with OpenAI and AzureOpenAI models.
- [X] Add support to read images using `VanillaReader`. 
- [X] Add support to read `xlsx`, `docx` and `pptx` files using `VanillaReader`. 
- [X] Add support to read images using `VanillaReader`.
- [X] Implement a method to split a document by pages (`PagedSplitter`).
- [X] Add support to read PDF as scanned pages.
- [X] Add support to change image placeholders.
- [X] Add support to change page placeholders.
- [X] Add Pydantic models.

## Contact

If you want to collaborate, please contact me through the following media: 

- [My mail](mailto:andresherencia2000@gmail.com).
- [My LinkedIn](https://linkedin.com/in/andres-herencia)
- [PyPI package](https://pypi.org/project/splitter-mr/)