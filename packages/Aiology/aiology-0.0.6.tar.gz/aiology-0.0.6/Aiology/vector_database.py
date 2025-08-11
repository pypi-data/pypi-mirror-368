import chromadb as chroma
    
class DataBase:
    """
## 🗃️ DataBase

**Make a vector database ,and save your information chunks by using this class**

This class need two parameters :

`collection_name -> Your vector database collection name`

`database_path -> Database saving path`
    """
    def __init__(self , collection_name , database_path):
        db = chroma.PersistentClient(database_path)
        self.database = db.get_or_create_collection(collection_name)
          
    def add_collection(self , chunked_content : list[str] , ids : list[str] = None):
        """
## Add new collection

This function is used to made new collections of information in database

`add_collection(chunked_content : list(str) , ids : str = None) -> None` 
        """
        if ids == None:
            ids = [f"Doc{i+self.database.count()}" for i in range(len(chunked_content))]
        elif len(ids) != len(chunked_content):
            raise Exception(f"Chunked content size is {len(chunked_content)} ,so you should pass {len(chunked_content)} id(s) tag !!\nYou pass this list of ids : {ids}")
        self.database.add(documents=chunked_content,ids=ids)

    def remove_from_collection(self , data_ids : list[str]):
        """
## Remove item from collection

This function is used to remove a data from collection by its id

`remove_from_collection(self , data_ids : list[int]) -> None` 
        """
        self.database.delete(ids=data_ids)

    def get_query_data(self , search_text , n_results : int):
        """
## Get query data

This function is used to search in database

`get_query_data(self , search_text , n_results : int) -> query result` 
        """
        return self.database.query(query_texts=search_text,n_results=n_results)