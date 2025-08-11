"""
## Aiology

Aiology is a package which pressents you four modules :

## 📄 PDF module

This module uses to extract data from pdf files ,or uses pdf data to ask question from ai 
(This module can extract Persian texts too !!)

## 🤖 AI module

You can commiunicate with ai by this module ,by using this module you can ask question from ai in different ways
,and about different topics

## 🤖 AI speech recognizer models
### Whisper
Whisper is a local audio recognizer ,which is used to translate/transcribe voice/audio files

### Google
Google cloud speech recognizer is an online recognizer ,which is used for transcribe voice/audio files

## 🔊 Audio

you pass this class as a parameter to ai models for translating ,or transcribing

## 🗃️ Tools modules

By this tools you can make chunks of text ,or document content , and store them in a vector database

You can use database information to ask ai about them

## Author

✍️ Seyed Moied Seyedi

😁 I will be glad to see your tricks 
"""
from .main import PDF , AI , Audio , Whisper , Google
from .chunk_tool import Chunk
from .vector_database import DataBase