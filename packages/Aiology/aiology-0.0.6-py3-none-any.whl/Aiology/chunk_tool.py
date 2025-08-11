class Chunk:
    """
    ## 🗃️ Chunk

    **by using this class you can easily make chunks of your input text ,document content in any size you want**

    This class need two parameters :

    `content -> Your text ,or document content`

    `chunk_size -> The size of the chunks which is int`
    """
    def __init__(self , content : str  , chunk_size : int):
        self.content = content
        self.chunk_size = chunk_size

    def make_chunk(self):
        """
    ## Make chunks

    This function is used to made chunks from our text ,or document content

    `make_chunk() -> text chunks` 
        """
        result = []
        self.content = self.content.replace("'","").replace('"',"").replace("\n"," ")
        split_chunks = self.content.split(" ")
        for _ in range(len(split_chunks)//self.chunk_size):
            result.append(' '.join(split_chunks[:self.chunk_size]))
            split_chunks[:self.chunk_size] = []
        result.append(' '.join([*split_chunks]))
        return result