import faiss
import pandas as pd
from uuid import uuid4
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from typing import Callable, Optional, Dict, Any
from langchain_core.documents import Document
import numpy as np  # optional, if you're using NumPy vectors
from langchain_core.embeddings import Embeddings

class BaseVectorStoreManager:
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings

    def generate_vector_store(self, docs):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def save(self, path):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def load(self, path):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def as_dataframe(self, formatter_fn: Optional[Callable[[Document, np.ndarray], Dict[str, Any]]] = None) -> pd.DataFrame:
        raise NotImplementedError("This method should be implemented by subclasses.")

class VectorStoreManager:
    def __init__(self, embeddings:Embeddings):
        self.embeddings = embeddings
        self.index = None
        self.vector_store = None

    # def generate_vector_store(self, docs):
    #     dimension = len(self.embeddings.embed_query("hello world"))
    #     self.index = faiss.IndexFlatL2(dimension)
    #     index_to_docstore_id = {}

    #     self.vector_store = FAISS(
    #         embedding_function=self.embeddings,
    #         index=self.index,
    #         docstore=InMemoryDocstore(),
    #         index_to_docstore_id=index_to_docstore_id,
    #     )

    #     uuids = [str(uuid4()) for _ in range(len(docs))]
    #     self.vector_store.add_documents(documents=docs, ids=uuids)
        
    
    def generate_vector_store(self, docs, handle_empty='zero'):
        """
        Generate a FAISS vector store from documents.

        Parameters:
            docs (list[Document]): List of LangChain Document objects.
            handle_empty (str): How to handle empty docs. Options:
                - 'zero': assign zero-vector
                - 'skip': skip the document
                - 'error': raise ValueError
        """

        # Step 1: Get embedding dimension from a sample input
        sample_embedding = self.embeddings.embed_query("hello world")
        dimension = len(sample_embedding)
        zero_vector = np.zeros(dimension, dtype=np.float32)

        self.index = faiss.IndexFlatL2(dimension)
        index_to_docstore_id = {}
        docstore = InMemoryDocstore()
        self.vector_store = FAISS(
            embedding_function=self.embeddings,
            index=self.index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
        )

        valid_docs = []
        valid_ids = []

        for doc in docs:
            content = doc.page_content if hasattr(doc, 'page_content') else ""
            if content and content.strip():
                valid_docs.append(doc)
                valid_ids.append(str(uuid4()))
            else:
                if handle_empty == 'skip':
                    continue
                elif handle_empty == 'zero':
                    # Assign zero vector manually
                    doc_id = str(uuid4())
                    index_to_docstore_id[len(docstore._dict)] = doc_id
                    docstore._dict[doc_id] = doc
                    self.index.add(np.array([zero_vector]))
                elif handle_empty == 'error':
                    raise ValueError("Document has empty or blank content.")
                else:
                    raise ValueError(f"Unknown handle_empty mode: {handle_empty}")

        # Step 2: Embed and add valid documents
        if valid_docs:
            self.vector_store.add_documents(documents=valid_docs, ids=valid_ids)
        elif handle_empty != 'zero':
            raise ValueError("No valid documents to embed.")

        print(f"✅ Vector store created with {self.index.ntotal} vectors.")
    
    def save(self, path):
        if self.vector_store:
            self.vector_store.save_local(path)
        else:
            raise ValueError("No vector store to save.")

    def load(self, path):
        self.vector_store = FAISS.load_local(
            path, self.embeddings, allow_dangerous_deserialization=True
        )
        self.index = self.vector_store.index

    def as_dataframe(
		self,
		formatter_fn: Optional[Callable[[Document, np.ndarray], Dict[str, Any]]] = None
	) -> pd.DataFrame:
				
        if not self.index or not self.vector_store:
            raise ValueError("Index or vector store not initialized.")

        vector_dict = {}
        for i in range(self.index.ntotal):
            vector = self.index.reconstruct(i)
            doc_id = self.vector_store.index_to_docstore_id[i]
            document = self.vector_store.docstore.search(doc_id)

            if formatter_fn:
                item = formatter_fn(document, vector)
            else:
                item = {
                    "embedding": vector,
                    **document.metadata
                }

            vector_dict[i] = item

        return pd.DataFrame.from_dict(vector_dict, orient='index')

    def get_data(self, id):
        if not self.index or not self.vector_store:
            raise ValueError("Index or vector store not initialized.")

        vector = self.index.reconstruct(id)
        doc_id = self.vector_store.index_to_docstore_id[id]
        document = self.vector_store.docstore.search(doc_id)
        return {"doc_id": doc_id, "document": document, "vector": vector}

    def get_all_vectors(self):
        if not self.index:
            raise ValueError("Index not initialized.")
        return self.index.reconstruct_n(0, self.index.ntotal)

    def get_vector_by_id(self, id):
        if not self.index:
            raise ValueError("Index not initialized.")
        return self.index.reconstruct(id)
		
    def get_document_by_index(self,index):
        doc_id = self.vector_store.index_to_docstore_id[index]
        document = self.vector_store.docstore.search(doc_id)
        return document
    
    def get_similar_embeddings(self, embedding_list, k):
        num_vectors, dim = embedding_list.shape

        # 2. Normalize for cosine similarity
        faiss.normalize_L2(embedding_list)

        # 3. Build FAISS index
        index = faiss.IndexFlatIP(dim)
        index.add(embedding_list)

        # 4. Query top-k+1 to exclude self-match
        # k = 4  # Request top 4, so we can drop self and keep 3
        D, I = index.search(embedding_list, k+1)

        # 5. Prepare output arrays
        top_k_ids_list = []
        top_k_avg_embeddings = []

        # id_list = desc_df['drugbank_id'].tolist()

        for i in range(num_vectors):
            indices = I[i]
            
            # Exclude self (assume it's the first match)
            filtered = [idx for idx in indices if idx != i][:k]

            # top_ids = [id_list[j] for j in filtered]
            top_embeds = embedding_list[filtered]

            avg_embed = np.mean(top_embeds, axis=0) if len(top_embeds) > 0 else np.zeros(dim)

            # top_k_ids_list.append(top_ids)
            top_k_ids_list.append(filtered)
            top_k_avg_embeddings.append(avg_embed)
        return top_k_ids_list, top_k_avg_embeddings
    
    def get_similar_docs(self, embedding, filter, top_k = 3):
        # Perform similarity search
        results = self.vector_store.similarity_search_with_score_by_vector(
            embedding,
            k=top_k ,  # Fetch more in case original sneaks in
            filter=filter
        )

        # Extract top-k drugbank_ids
        # top_k_ids = [doc.metadata.get("drugbank_id") for doc, score in results[:top_k]]
        # return top_k_ids
        return results[:top_k]
		

def custom_formatter(document: Document, vector: np.ndarray) -> Dict[str, Any]:
    return {
        "drugbank_id": document.metadata.get("drugbank_id", None),
        "type": document.metadata.get("type", None),
        "embedding": vector
    }
