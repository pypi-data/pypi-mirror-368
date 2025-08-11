from requests import post
import pypdf as pdf
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from os.path import exists
from .vector_database import DataBase
from .chunk_tool import Chunk
from colorama import init , Fore , Style 
from base64 import b64encode
import faster_whisper as whisper
import speech_recognition as speechrec
from io import BytesIO

init(True)



class Audio:
    """
# 🔊 Audio

This class is used to prepare voice/audio information for Whisper/Google models

## Microphone/Voice/Audio file

If you wanna use microphone to get user input ,you can set `use_microphone` parameter True ,otherwise if you wanna pass an audio file

you should pass `use_microphone` parameter False ,then set `audio_file` parameter to show your audio file location
    """
    def __init__(self,use_microphone : bool,audio_file : str = "",microphone_timeout : float | None = None):
        self.recognizer = speechrec.Recognizer()
        self.use_microphone = use_microphone
        self.audio_file = audio_file
        self.microphone_timeout = microphone_timeout

    def microphone(self,timeout : float | None = None):
        """
## Microphone

This function gets input from microphone ,then return its wav file data

`microphone(self,timeout : float | None = None) -> wav file data` 
        """
        try:
            with speechrec.Microphone() as mic:
                self.recognizer.adjust_for_ambient_noise(mic)
                audio_data = self.recognizer.listen(mic,timeout=timeout)
        except:
            raise Exception("There is a problem with your microphone ,check your microphone access")
        
        return audio_data

    def prepare_for_whisper(self):
        """
## Prepare for Whisper model

This function prepare all audio data which stored in this class for Whisper model usage

`prepare_for_whisper() -> audio data for Whisper model` 
        """
        if self.use_microphone == False:
            return self.audio_file
        
        audio_data = self.microphone(timeout=self.microphone_timeout)
        return BytesIO(audio_data.get_wav_data())
        
    def prepare_for_google(self,language_code : str = "en-US"):
        """
## Prepare for Google model

This function prepare all audio data which stored in this class for Google model usage

`prepare_for_google(language_code : str = "en-US") -> audio data for Whisper model` 
        """
        if self.use_microphone:
            audio_data = self.microphone(timeout=self.microphone_timeout)
        else:
            try:
                with speechrec.AudioFile(self.audio_file) as source:
                    self.recognizer.adjust_for_ambient_noise(source=source)
                    audio_data = self.recognizer.record(source=source)
            except:
                raise Exception("Invalid audio file format for google recognizer !!")

        try:
            return self.recognizer.recognize_google(audio_data,language=language_code)
        except:
            raise Exception("SpeechRecognizer error occured !! ,check your internet connection ,or recognizer couldn't detect your words")



class Google:
    """
# 🤖 Google online model

This class is used to transcribe your audios ,and use google online trained model to do this things

### transcribe function

This function is used to transcribe information from your audios ,then return data as text
    """
    def __init__(self,audio_language_detection : str = "en-US"):
        self.audio_language_detection = audio_language_detection
    
    def transcribe(self,audio_data : Audio):
        """
## Transcribe

This function transcribes all data which stored in Audio object

`transcribe(self,audio_data : Audio) -> transcribed text` 
        """
        return audio_data.prepare_for_google(language_code=self.audio_language_detection)
        


class Whisper:
    """
# 🤖 Whisper model

This class is used to translate/transcribe your audios ,and use whisper ai model to do this things

when you use this module for the first time ,it should takes some minutes to download whisper model on your local machine

The most important parameter you should care about is `whisper_model` ,this parameter shows local folder of whisper model which downloaded

### transcribe function

This function is used to translate/transcribe information from your audios ,then return two data

`segment_data` -> Show translate/transcribe information

`audio_info` -> Show audio information ,and others information about your audio
    """
    def __init__(self,whisper_model : str,device : str = "cpu",audio_language_detection : str = "en",device_index : int | list = 0,compute_type : str ="int8",cpu_threads : int = 5,num_workers : int = 1,download_root : str = "",use_local_files : bool = True):
        self.whisper = whisper.WhisperModel(whisper_model,
                                            device=device,
                                            device_index=device_index,
                                            compute_type=compute_type,
                                            cpu_threads=cpu_threads,
                                            num_workers=num_workers,
                                            local_files_only=use_local_files,
                                            download_root=download_root)
        self.audio_language_detection = audio_language_detection
        
    def transcribe(self,audio_data : Audio,use_language : bool = True,temperature : int = 0,task : str = "transcribe",hotwords : str | None = None,silence_filter : bool = True,use_timestamps : bool = False):
        """
## Transcribe

This function transcribes all data which stored in Audio object

`transcribe(self,audio_data : Audio,use_language : bool = True,temperature : int = 0,task : str = "transcribe",hotwords : str | None = None,silence_filter : bool = True,use_timestamps : bool = False) -> transcribed text` 
        """
        if not 0 <= temperature <= 1:
            raise Exception("Temperature parameter value should be between 0 ,and 1")
        
        if not self.audio_language_detection in self.whisper.supported_languages:
            raise Exception(f"Whisper doesn't support this language type !! ,please choose a language from list below :\n{self.whisper.supported_languages}")

        segment_data , audio_info = self.whisper.transcribe(audio=audio_data.prepare_for_whisper(),
                                language= self.audio_language_detection if use_language else None,
                                vad_filter=silence_filter,
                                task=task,
                                temperature=temperature,
                                without_timestamps=True if use_timestamps == False else False,
                                hotwords=hotwords)
        return segment_data , audio_info



class PDF:
    """
# 📄 PDF

easily extract ,and use your pdf content by this class

## Quick start

PDF class needs four parameters 

`pdf_path -> The path of your pdf file as string`

`use_for_telegram -> Set this option True if you use this for a telegram bot (False as default)`

### ⚠️ If you use this pdf to asking ai relative questions , you need to pass collection_name and collection_directory

`collection_name -> Set this for vector database`

`collection_directory -> Set this for vector database folder`

## ----------------------------------------------------

## Get pdf content example :

```
#import from our module
from Aiology import PDF

#variables
pdf_path = "YOUR_PDF_FILE_PATH"

#define your pdf
pdf = PDF(pdf_path)

#read pdf content
result = pdf.get_pdf_content()

#print result
print(result)
```

## Ask pdf question from ai :

⚠️ WARNING : before asking questions from ai , you need to run *prepare_for_ai* function 

```
#import from our module
from Aiology import PDF , AI

#variables
pdf_path = "YOUR_PDF_FILE_PATH"
gemini_api_key = "YOUR_GEMINI_API_KEY"

#define your pdf
pdf = PDF(pdf_path) # <----- (You can pass collection_name ,and collection_directory parameters now)
pdf.prepare_for_ai(1000) # <----- (Convert your pdf content to small pieces and save them in database collection)

#AI
ai = AI(gemini_api_key)

#ask your question
result = ai.ask_pdf_question("YOUR_QUESTION_TEXT",pdf)

#print result
print(result)
```
    """
    def __init__(self,pdf_path : str,use_for_telegram : bool = False,collection_name : str = "Documents",collection_directory : str = "Database"):
        if not exists(pdf_path):
            raise Exception(f"There is no pdf file in {pdf_path} address !!")
        
        self.telegram_usage = use_for_telegram
        self.collection_name = collection_name
        self.collection_folder = collection_directory
        self.reader = pdf.PdfReader(pdf_path)
        self.pdf_pages_num = self.reader.get_num_pages()
        self.content = ""

        for i in range(self.pdf_pages_num):
            if self.telegram_usage:
                self.content += self.reader.get_page(i).extract_text()
            else:
                self.content += get_display(reshape(self.reader.get_page(i).extract_text()))

    def get_pdf_content(self):
        """
## Get pdf content

This function gets your pdf content and return them back

`get_pdf_content() -> pdf content` 
        """
        return self.content
    
    def get_pdf_page_content(self,page_num : int):
        """
## Get pdf page content

This function gets your pdf content by its page number and return them back

`get_pdf_page_content(page_number : int) -> pdf content of that page` 
        """
        if page_num > self.pdf_pages_num:
            raise Exception(f"This pdf has {self.pdf_pages_num} page(s) , you can't have page {page_num} content !!")
        elif page_num > 0:
            if self.telegram_usage:
                return self.reader.get_page(page_num-1).extract_text()
            else:
                return get_display(reshape(self.reader.get_page(page_num-1).extract_text()))
        else:
            raise Exception(f"{page_num} is an invalid page number !!")
        
    def chunk_pdf_content(self,chunk_size : int = 1000,page_num : int = None):
        """
## make pdf content chunks

This function is used to make chunks of your pdf content

`chunk_pdf_content(chunk_size : int = 1000,page_num : int = None) -> chunks of the pdf (page) content` 
        """
        if page_num != None:
            chunk_content = self.get_pdf_page_content(page_num=page_num)
        else:
            chunk_content = self.content
        
        chunker = Chunk(content=chunk_content , chunk_size=chunk_size)
        return chunker.make_chunk()
    
    def prepare_for_ai(self,chunk_size : int = 1000,chunks_ids : list[str] = None,page_num : int = None):
        """
## Prepare this pdf information for ai

This function is used to prepare this pdf information for ai in database

💡 TIP : Use this function when you wanna ask question about this pdf from ai 

`prepare_for_ai() -> None` 
        """
        chunks = self.chunk_pdf_content(chunk_size=chunk_size , page_num=page_num)
        database = DataBase(collection_name=self.collection_name,database_path=self.collection_folder)
        database.add_collection(chunked_content=chunks,ids=chunks_ids)
    


class AI:
    """
## 🤖 AI

You can easily exteract your pdf files data , then ask the ai everything
about your pdf content by using AI , and it will answer your question immediately

## Quick start

AI class needs two parameters 

`api_key -> The ai api_key , this module only supports Gemini api_keys !!`

`use_for_telegram -> Set this option True if you use this for a telegram bot (False as default)

## ------------------------------------------------------------------------------
```
#import from our module
from Aiology import PDF , AI

#variables
pdf_path = "YOUR_PDF_FILE_PATH"
gemini_api_key = "YOUR_GEMINI_API_KEY"

#define your pdf
pdf = PDF(pdf_path) # <----- (You can pass collection_name ,and collection_directory parameters now)
pdf.prepare_for_ai(1000) # <----- (Convert your pdf content to small pieces and save them in database collection)

#AI
ai = AI(gemini_api_key)

#ask your question
result = ai.ask_pdf_question("YOUR_QUESTION_TEXT",[pdf])

#print result
print(result)
```
    """
    def __init__(self,api_key : str,use_for_telegram : bool = False):
        self.api_key = api_key
        self.telegram_usage = use_for_telegram

    def ask_question(self,text):
        """
## Ask question from ai

By this function , you can send your question ,and receive its answer

`ask_question(text : str) -> response text`
        """
        header = {"Content-Type":"application/json"}

        data = {"contents":[
                        {"parts":
                            [
                                {"text":text},
                            ]
                        }
                    ]}
        
        try:
            res = post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}",
                    headers=header,json=data)
        except:
            raise Exception(f"Internet connection error !!")
        
        if res.ok:
            final_text = ""
            result = res.json()
            for texts in result["candidates"][0]["content"]["parts"]:
                if self.telegram_usage:
                    final_text += texts["text"]
                else:
                    final_text += get_display(reshape(texts["text"]))

            return final_text
        else:
            raise Exception(f"Unexpected error happened !! your error code is {res.status_code}\nContent : {res.content}")

    def ask_pdf_question(self,text : str,pdf_list : list[PDF],language : str = "English",sensivity : int = 6):
        """
## Ask question about your pdf

By this function , you can easily pass your pdf ,and ask different questions about it

`ask_pdf_question(self,text : str,pdf_list : list[PDF],language : str = "English",sensivity : int = 6) -> response text`
        """
        content = ""

        for pdf in pdf_list:
            database = DataBase(collection_name=pdf.collection_name,database_path=pdf.collection_folder)
            query_result = database.get_query_data(search_text=text,n_results=sensivity)
            
            for result in query_result["documents"][0]:
                if content != "":
                    content += f"-{result}"
                else:
                    content += result
            
        print(f"{Style.BRIGHT}{Fore.GREEN}Please wait for ai answer ...")

        prompt = f"""
You are a helpful bot which can answer my questions using text.
I'm a non-technical audience , please answer my question comprehensive ,and be sure to break down strike a friendly
and converstional tone.
If the context is irrelative to the answer , you may ignore it.

QUESTION : '{text}'
CONTEXT : '{get_display(reshape(content))}'

PLEASE ANSWER THIS QUESTION IN {language} WITHOUT ANY EXTRA INFORMATION
        """

        header = {"Content-Type":"application/json"}

        data = {"contents":[
                        {"parts":
                            [
                                {"text":prompt},
                            ]
                        }
                    ]}
        
        try:
            res = post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}",
                    headers=header,json=data)
        except:
            raise Exception(f"Internet connection error !!")
            
        if res.ok:
            final_text = ""
            result = res.json()
            for texts in result["candidates"][0]["content"]["parts"]:
                if self.telegram_usage:
                    final_text += texts["text"]
                else:
                    final_text += get_display(reshape(texts["text"]))

            return final_text
        else:
            raise Exception(f"Unexpected error happened !! your error code is {res.status_code}\nContent : {res.content}")

    def ask_image_question(self , text : str,image : str,language : str = "English"):
        """
## Aylize your images

This function gets your images then analyze them by gemini one by one , then return texts as result

`ask_image_question(self , text : str,image : str,language : str = "English") -> response text` 
        """
        if not exists(image):
            raise Exception(f"There is no image file with this path {image}")
        
        with open(image , "rb") as file:
            image_data = b64encode(file.read()).decode()

        prompt = f"""
CONTEXT : '{get_display(reshape(text))}'
PLEASE ANSWER THIS QUESTION IN {language} WITHOUT ANY EXTRA INFORMATION
        """

        header = {"Content-Type":"application/json"}

        data = {"contents":[
                        {"parts":
                            [
                                {
                                    "inline_data": {
                                        "mime_type":"image/jpeg",
                                        "data":image_data
                                    }
                                },
                                {"text":prompt},
                            ]
                        }
                    ]}
        
        try:
            res = post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}",
                    headers=header,json=data)
        except:
            raise Exception(f"Internet connection error !!")
            
        if res.ok:
            final_text = ""
            result = res.json()
            for texts in result["candidates"][0]["content"]["parts"]:
                if self.telegram_usage:
                    final_text += texts["text"]
                else:
                    final_text += get_display(reshape(texts["text"]))

            return final_text
        else:
            raise Exception(f"Unexpected error happened !! your error code is {res.status_code}\nContent : {res.content}")
            
    def ask_voice_question(self,text : str,audio : Audio,model : Whisper | Google,reply_language : str = "English"):
        """
## Reply on your question about voice/audio file

This function gets your voice/audio file then analyze that by gemini ,and reply on your question about that ,then return response text as result

This function uses Whisper or Google transcriers to transcribe text from voice/audio file then answering your question by Gemini

`ask_voice_question(self,text : str,audio : Audio,model : Whisper | Google,reply_language : str = "English") -> response text` 
        """
        data_text = ""
        data = model.transcribe(audio)

        if type(model) == Whisper:
            for segment in data[0]:
                data_text += segment.text
        else:
            data_text = data

        prompt = f"""
You are a helpful bot which can answer my questions using text.
I'm a non-technical audience , please answer my question comprehensive ,and be sure to break down strike a friendly
and converstional tone.
If the context is irrelative to the answer , you may ignore it.

QUESTION : '{text}'
CONTEXT : '{data_text}'

PLEASE ANSWER THIS QUESTION IN {reply_language} WITHOUT ANY EXTRA INFORMATION
        """

        return self.ask_question(prompt)

    def ask_question_from_voice(self,audio : Audio,model : Whisper | Google,reply_language : str = "English"):
        """
## Aylize your voices

This function gets your voice/audio file then analyze that by gemini , then return response text as result

This function uses Whisper or Google transcriers to transcribe text from voice/audio file 

`ask_question_from_voice(self,audio : Audio,model : Whisper | Google,reply_language : str = "English") -> response text` 
        """
        data_text = ""
        data = model.transcribe(audio)

        if type(model) == Whisper:
            for segment in data[0]:
                data_text += segment.text
        else:
            data_text = data

        prompt = f"""{data_text}
PLEASE ANSWER THIS QUESTION IN {reply_language} WITHOUT ANY EXTRA INFORMATION"""

        return self.ask_question(prompt)