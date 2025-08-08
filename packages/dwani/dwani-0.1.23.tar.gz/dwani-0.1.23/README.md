# dwani.ai - python library

- dwani.ai is self-hosted GenAI platform for multimodal AI inference.

- Image, Speech, Docs, Text supported today !!

- dwani.ai - is now compatible with OpenAI Spec

### Install the library
```bash
pip install --upgrade dwani
```

### Model Supported
- Text
  - gpt-oss , gemma3
- Vision
  - gemma3

### Languages supported
- Indian
  - Assamese, Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi Odia, Punjabi, Tamil, Telugu
- European
  - English, German

### Setup the credentials
```python
import dwani
import os

dwani.api_key = os.getenv("DWANI_API_KEY")

dwani.api_base = os.getenv("DWANI_API_BASE_URL")
```


---

- Source Code : [https://github.com/dwani-ai/dwani-python-sdk](https://github.com/dwani-ai/dwani-python-sdk)
- Check examples folder for detailed use cases 

  - [examples/chat.py](examples/chat.py)
  - [examples/vision.py](examples/vision.py)
  - [examples/docs.py](examples/docs.py)
  - [examples/speech.py](examples/speech.py)
  - [examples/asr.py](examples/asr.py)

#### Document - OCR
```python
result = dwani.Documents.run_ocr_page(file_path="dwani-workshop.pdf", page_number=1, model="gemma3")
print(result)
```
```json
{'page_content': "Here's the plain text extracted from the image:\n\ndwani's Goals\n\nTo integrate and enhance the following models and services for Kannada:\n\n*   **Automatic Speech Recognition (ASR):**"}
```


#### Document - Summary

```python
result = dwani.Documents.summarize_all(
            file_path="dwani-workshop.pdf", model="gemma3" , tgt_lang="english"  
    )

print("Document Query Response: gemma3- ", result["summary"])
```


### Text Query 
---
- gemma3 (default)

  ```python
  resp = dwani.Chat.create(prompt="Hello!", src_lang="english", tgt_lang="kannada", model="gemma3")
  print(resp)
  ```
  ```json
  {'response': 'ನಮಸ್ತೆ! ಭಾರತ ಮತ್ತು ಕರ್ನಾಟಕವನ್ನು ಗಮನದಲ್ಲಿಟ್ಟುಕೊಂಡು ಇಂದು ನಿಮ್ಮ ಪ್ರಶ್ನೆಗಳಿಗೆ ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?'}
  ```

---
### Vision Query
---
- gemma3 (default)
    ```python
    result = dwani.Vision.caption(
        file_path="image.png",
        query="Describe this logo",
        src_lang="english",
        tgt_lang="kannada",
        model="gemma3"
    )
    print(result)
    ```
    ```json
    {'answer': 'ಒಂದು ವಾಕ್ಯದಲ್ಲಿ ಚಿತ್ರದ ಸಾರಾಂಶವನ್ನು ಇಲ್ಲಿ ನೀಡಲಾಗಿದೆಃ ಪ್ರಕಟಣೆಯ ಅವಲೋಕನವು ಪ್ರಸ್ತುತ ಅರವತ್ತನಾಲ್ಕು ದೇಶಗಳು/ಪ್ರದೇಶಗಳನ್ನು ಸೇರಿಸಲಾಗಿದೆ ಮತ್ತು ಇನ್ನೂ ಹದಿನಾರು ಪ್ರದೇಶಗಳನ್ನು ಸೇರಿಸಬೇಕಾಗಿದೆ. ಒದಗಿಸಲಾದ ಚಿತ್ರದಲ್ಲಿ ಲಾಂಛನವು ಕಾಣಿಸುವುದಿಲ್ಲ.'}
    ```

---
### Speech to Text -  Automatic Speech Recognition (ASR)
---
```python
result = dwani.ASR.transcribe(file_path="kannada_sample.wav", language="kannada")
print(result)
```
```json
{'text': 'ಕರ್ನಾಟಕ ದ ರಾಜಧಾನಿ ಯಾವುದು'}
```
---
### Translate
---
```python
resp = dwani.Translate.run_translate(sentences="hi, i am gaganyatri", src_lang="english", tgt_lang="kannada")
print(resp)
```
```json
{'translations': ['ಹಾಯ್, ನಾನು ಗಗನಯಾತ್ರಿ']}
```
---
### Text to Speech -  Speech Synthesis
---
```python
response = dwani.Audio.speech(input="ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ ಯಾವುದು", response_format="wav", language="kannada")
with open("output.wav", "wb") as f:
    f.write(response)
```

#### Document - Extract Text
```python
result = dwani.Documents.run_extract(file_path = "dwani-workshop.pdf", page_number=1, src_lang="english",tgt_lang="kannada" )
print(result)
```
```json
{'pages': [{'processed_page': 1, 'page_content': ' a plain text representation of the document', 'translated_content': 'ಡಾಕ್ಯುಮೆಂಟ್ನ ಸರಳ ಪಠ್ಯ ಪ್ರಾತಿನಿಧ್ಯವನ್ನು ಇಲ್ಲಿ ನೀಡಲಾಗಿದೆ, ಅದನ್ನು ಸ್ವಾಭಾವಿಕವಾಗಿ ಓದುವಂತೆಃ'}]}
```

- Website -> [dwani.ai](https://dwani.ai)


<!-- 
## local development
pip install -e .


pip install twine build
rm -rf dist/
python -m build

python -m twine upload dist/*

-->

<!--
Without Batch  
2025-07-14 13:39:50,330 - dwani_api - INFO - Request to /indic-summarize-pdf-all took 245.381 seconds
INFO:dwani_api:Request to /indic-summarize-pdf-all took 245.381 seconds

With Batch

vllm serve google/gemma-3-4b-it --served-model-name gemma3 --host 0.0.0.0 --port 9000 --gpu-memory-utilization 0.8 --tensor-parallel-size 1 --max-model-len 65536     --dtype bfloat16 


-->