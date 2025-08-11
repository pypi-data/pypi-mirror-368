import pandas as pd
from langchain.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain.text_splitter import TextSplitter
from typing import Callable, Optional, Dict, Any, List
import numpy as np

from ddi_fw.langchain.faiss_storage import BaseVectorStoreManager
from langchain.document_loaders import DataFrameLoader


def split_dataframe(df, min_size=512):
    total_size = len(df)
    # If the dataframe is smaller than min_size, return the dataframe as a whole
    if total_size <= min_size:
        return [df]

    # List to store partial DataFrames
    partial_dfs = []
    start_idx = 0

    # Calculate the minimum number of chunks we need to ensure each chunk has at least min_size
    num_chunks = total_size // min_size
    remaining_rows = total_size
    # Split into chunks
    for i in range(num_chunks):
        # If there are fewer rows left than the size of the chunk, adjust the chunk size
        chunk_size = min_size
        if (remaining_rows - chunk_size) < min_size:
            chunk_size = remaining_rows  # Last chunk takes all remaining rows

        partial_dfs.append(df.iloc[start_idx:start_idx + chunk_size])

        # Update the start index and remaining rows
        start_idx += chunk_size
        remaining_rows -= chunk_size

    # If there are any remaining rows left after the loop, they should form the last chunk
    if remaining_rows > 0:
        partial_dfs.append(df.iloc[start_idx:start_idx + remaining_rows])

    return partial_dfs


def split_dataframe_indices(df, min_size=512):
    total_size = len(df)

    # If the dataframe is smaller than min_size, return the entire range
    if total_size <= min_size:
        return [(0, total_size - 1)]

    # List to store the start and end indices of each chunk
    chunk_indices = []
    start_idx = 0

    # Calculate the minimum number of chunks needed to ensure each chunk has at least min_size
    num_chunks = total_size // min_size
    remaining_rows = total_size

    # Split into chunks
    for i in range(num_chunks):
        chunk_size = min_size
        if (remaining_rows - chunk_size) < min_size:
            chunk_size = remaining_rows  # Last chunk takes all remaining rows

        # Calculate the ending index of the chunk (exclusive, hence chunk_size - 1)
        end_idx = start_idx + chunk_size - 1
        chunk_indices.append((start_idx, end_idx))

        # Update the start index and remaining rows
        start_idx += chunk_size
        remaining_rows -= chunk_size

    # If there are any remaining rows after the loop, they should form the last chunk
    if remaining_rows > 0:
        end_idx = start_idx + remaining_rows - 1
        chunk_indices.append((start_idx, end_idx))

    return chunk_indices



class ChromaVectorStoreManager(BaseVectorStoreManager):
    def __init__(
        self,
        embeddings: Embeddings,
        collection_name: str,
        persist_directory: str,
        text_splitter: TextSplitter,
        batch_size: int = 1024
    ):
        super().__init__(embeddings)
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.text_splitter = text_splitter
        self.batch_size = batch_size
        


    # def __split_docs(self, documents):
    #     docs = self.text_splitter.split_documents(documents)
    #     return docs

    # def __split_list(self, input_list, batch_size):
    #     # for i in range(0, len(input_list), batch_size):
    #     batch_size = len(input_list) if batch_size == None else batch_size
    #     for s, e in split_dataframe_indices(input_list, batch_size):
    #         yield input_list[s:e+1]

    # def store_documents(self, df, columns, page_content_columns, partial_df_size=None):
    #     """
    #     Core function that processes the documents and adds them to the vector database.
    #     """
    #     for page_content_column in page_content_columns:
    #         copy_columns = columns.copy()
    #         copy_columns.append(page_content_column)
    #         col_df = df[copy_columns].copy()
    #         col_df.dropna(subset=[page_content_column], inplace=True)
    #         col_df['type'] = page_content_column  # Set the type column
    #         if partial_df_size:
    #             total = 0
    #             partial_dfs = split_dataframe(col_df, min_size=partial_df_size)
    #             for partial_df in partial_dfs:
    #                 # import torch

    #                 documents = []
    #                 loader = DataFrameLoader(
    #                     data_frame=partial_df, page_content_column=page_content_column)
    #                 loaded_docs = loader.load()
    #                 # print(loaded_docs)
    #                 documents.extend(self.__split_docs(loaded_docs))
    #                 split_docs_chunked = self.__split_list(
    #                     documents, self.batch_size)
    #                 for split_docs_chunk in split_docs_chunked:
    #                     print("entered chunks")
    #                     self.vector_store.add_documents(split_docs_chunk)
    #                     self.vector_store.persist()
    #                 total += len(partial_df)
    #                 print(f"{page_content_column}: {total}/{len(col_df)}")
    #         else:
    #             documents = []
    #             print(col_df.shape)
    #             loader = DataFrameLoader(
    #                 data_frame=col_df, page_content_column=page_content_column)
    #             loaded_docs = loader.load()
    #             documents.extend(self.__split_docs(loaded_docs))
    #             print(f"Documents size: {len(loaded_docs)}")
    #             split_docs_chunked = self.__split_list(
    #                 documents, self.batch_size)
    #             for split_docs_chunk in split_docs_chunked:
    #                 # import torch
    #                 # torch.cuda.empty_cache()
    #                 self.vector_store.add_documents(split_docs_chunk)
    #                 self.vector_store.persist()
    #                 print(f"{page_content_column}, size:{len(split_docs_chunk)}")



    def generate_vector_store(self, docs: List[Document]):
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        if self.text_splitter:
            docs = self.text_splitter.split_documents(docs)
        # Chunk docs for batch processing
        for i in range(0, len(docs), self.batch_size):
            chunk = docs[i:i+self.batch_size]
            self.vector_store.add_documents(chunk)
            self.vector_store.persist()
        print(f"✅ Chroma vector store created with {len(docs)} documents.")

    def save(self, path):
        # Chroma persists automatically, but you can copy files if needed
        print("ChromaDB persists automatically. No explicit save needed.")

    def load(self, path):
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            persist_directory=path,
            embedding_function=self.embeddings
        )

    def as_dataframe(
        self,
        formatter_fn: Optional[Callable[[Document, np.ndarray], Dict[str, Any]]] = None
    ) -> pd.DataFrame:
        # Chroma does not expose direct vector access, so we fetch all docs and embeddings
        results = self.vector_store.get()
        docs = results['documents']
        metadatas = results['metadatas']
        embeddings = results['embeddings']
        items = []
        for doc, meta, emb in zip(docs, metadatas, embeddings):
            document = Document(page_content=doc, metadata=meta)
            if formatter_fn:
                item = formatter_fn(document, np.array(emb))
            else:
                item = {"embedding": emb, **meta}
            items.append(item)
        return pd.DataFrame(items)

    def get_data(self, id):
        # Chroma does not use integer IDs, but document IDs (UUIDs)
        results = self.vector_store.get(ids=[id])
        if not results['documents']:
            raise ValueError("Document not found.")
        return {
            "doc_id": id,
            "document": Document(page_content=results['documents'][0], metadata=results['metadatas'][0]),
            "vector": np.array(results['embeddings'][0])
        }

    def get_all_vectors(self):
        results = self.vector_store.get()
        return np.array(results['embeddings'])

    def get_vector_by_id(self, id):
        results = self.vector_store.get(ids=[id])
        if not results['embeddings']:
            raise ValueError("Vector not found.")
        return np.array(results['embeddings'][0])

    def get_document_by_index(self, index):
        results = self.vector_store.get()
        docs = results['documents']
        metadatas = results['metadatas']
        if index >= len(docs):
            raise IndexError("Index out of range.")
        return Document(page_content=docs[index], metadata=metadatas[index])

    def get_similar_embeddings(self, embedding_list, k):
        # Chroma does not provide direct similarity search on arbitrary embeddings
        # You can use vector_store.similarity_search_by_vector for a single embedding
        raise NotImplementedError("Chroma does not support batch similarity search by embedding list.")

    def get_similar_docs(self, embedding, filter=None, top_k=3):
        results = self.vector_store.similarity_search_by_vector(
            embedding, k=top_k, filter=filter
        )
        return results[:top_k]