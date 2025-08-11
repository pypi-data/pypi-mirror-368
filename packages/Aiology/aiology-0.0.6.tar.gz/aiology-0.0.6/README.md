# Aiology
This is an easy to use ai communication package which you can easily setting it up and start working with it !!

To download ,and use this package : `pip install Aiology`
Have a look to our [website](https://aiology.pythonanywhere.com/) here

This package includes four modules :


## AI
By using this module you can start a text base communication with *Gemini* ai

## PDF
By using this module you can extract pdf files text (it works for Persian pdf too !!)

## TOOLS
Including Chunk ,and Database to chunk contents ,or save/remove data from database 

## Audio
Easily ask AI about your audio file or communicate by AI throw your microphone !!

Use Whisper , Google , Audio modules to communicate by AI base on audio

### Using PDF module :
This module needs four parameters which is your pdf path , use_for_telegram , collection_name ,and collection_directory:

> [!NOTE]
>
>`use_for_telegram` -> This argument isn't crucial , if you use this module for telegram bot you should set it as
>
>True ,otherwise it's False as default 
>
>`collection_name` -> This argument is used as vector database **name** when you wanna pass pdf object to AI module
>
>`collection_directory` -> This argument is used for set **vector database saving location** when you wanna pass pdf 
>
>object to AI module

```Python
#import our PDF module
from Aiology import PDF

#specify your pdf location
pdf_path = "YOUR_PDF_PATH"

#set up
pdf = PDF(pdf_path)
```

Then you can get your pdf content by using these three functions :
*get_pdf_content*
*get_pdf_page_content*
*chunk_pdf_content*

`get_pdf_content` -> extract all pdf pages content
`get_pdf_page_content` -> extract specific pdf page content
`chunk_pdf_content` -> extract pdf content (also by page number) ,then return a list of content chunks (used for AI module)

```Python
pdf.get_pdf_content() #will extract all pdf pages content
pdf.get_pdf_page_content() #will extract specific pdf page content
pdf.chunk_pdf_content() #return a list of content chunks which be used for AI module
```


If you wanna use AI module , you should use `prepare_for_ai` function before that :
*prepare_for_ai*

`prepare_for_ai` -> This function is used to make vector database for AI module ,and it gets three arguments which are **chunk_size** , **chunks_ids** ,and **page_num**

`chunk_size` -> The size of the content chunks which stored in database
`chunks_ids` -> You can pass ids for each chunks
`page_num` -> You can define a pdf page to extract and save in database

> [!WARNING]
>
>Use this function before using AI module !!

```Python
pdf.prepare_for_ai() #it will make a vector database for AI module
```


### Using AI module :
This module needs two parameters which is your *Gemini* api key , and use_for_telegram:

> [!NOTE]
>
>`use_for_telegram` -> This argument isn't crucial , if you use this module for telegram bot you should set it as
>
>True ,otherwise it's False as default 

```Python
#import our AI module
from Aiology import AI

#specify your Gemini api key
api_key = "YOUR_GEMINI_API_KEY"

#set up
ai = AI(api_key)
```

Then you can start communication by ai by these two functions :
*ask_question*
*ask_pdf_question*

`ask_question` -> Ask anything you want from Gemini by your api token
`ask_pdf_question` -> Ask about your pdf contents from Gemini by your api token

```Python
#ask anything from ai
result = ai.ask_question("YOUR_TEXT_HERE")

#print ai answer
print(result)
```

If you want to ask ai questions about your pdf file ,you should pass `PDF` which is represents your collection data to `ask_pdf_question` ,also you need to call `PDF.prepare_for_ai` before using AI module :

> [!NOTE] :
>
> `ask_pdf_question` takes 4 arguments :
>
> text -> Your text
>
> pdf -> PDF object which represent your collection data
>
>language -> You can define your output language as string (e.g "English")
>
> sensitivity -> You can define search sensitivity that how many chosen chunks of content send to ai

```Python
#import modules
from Aiology import PDF , AI

#variables
pdf_path = "YOUR_PDF_PATH"
api_key = "YOUR_GEMINI_API_KEY"

vector_database_save_address = "ADDRESS_TO_SAVE_DATABASE"
vector_database_name = "A_NAME_FOR_DATABASE"

#PDF set up
pdf = PDF(pdf_path , collection_name=vector_database_name , collection_directory=vector_database_save_address)

#Ai set up
ai = AI(api_key)

#ask about your pdf content
result = ai.ask_pdf_question("YOUR_QUESTION",[pdf],language="Persian")

#print result
print(result)
```

### Audio 
just some tips when wanna ask AI about an audio or microphone input :

> [!NOTE] :
>
>You can pass audio file to Audio module ,or you can get inputs from your microphone by setting `use_microphone` to True
>
>Then you need a model to analyze your audio ,or microphone input for AI module ,you have two options (Whisper,Google)
>
>Whisper -> Will download whisper model for the first of usage ,set `whisper_model` to any whisper model you want ,and >set `download_root` to download your whisper model there
>
>Google -> Google module doesn't need any requirements
>
>pass your audio object ,and audio modules to AI when using these two functions `ask_voice_question` ,and >`ask_question_from_voice`


# Advanced

you can do different tricks like this :

```Python
#variables
gemini_api_key = "YOUR_GEMINI_API_KEY"

#Our pdf files (when their collection name and collection directory are the same , so they are in a group)
pdf_files = [PDF("test1.pdf",collection_name="Collection-1"),PDF("test2.pdf",collection_name="Collection-1"),PDF("test3.pdf",collection_name="Collection-2"),PDF("test4.pdf",collection_name="Collection-2")]

#prepare each pdf for ai
for pdf in pdf_files:
    pdf.prepare_for_ai()

#AI
ai = AI(gemini_api_key)

#ask your question (we use pdf_paths[0] ,and pdf_paths[2] ,because their collection groups)
result = ai.ask_pdf_question("Do you know about Aiology library ?",[pdf_files[0] , pdf_files[2]],language="English")

#print result
print(result)
```

This is how to pass pdf list to ask_pdf_question function :
![pdf files with the same collection name ,and directory are in the same group](pdf-description-image.png)

# What's new ?
Reduce package size ,and fix all errors

# Conclusion
This is a powerful ,but small ai package which provide you useful tools

I hope this will be useful for you

### Single Star
### Seyed Moied Seyedi 