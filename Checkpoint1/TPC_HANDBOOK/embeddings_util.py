# -*- coding: utf-8 -*-
"""
Embeddings Utility — Document Loading & Embedding

Loads the TPC Handbook document, splits it into sections, and embeds them
using either a semantic embedding model (sentence-transformers) or a simple
TF-IDF baseline for testing.

Production model: sentence-transformers/all-MiniLM-L6-v2
Fallback (testing): TF-IDF vectorizer
"""

import os
import re
import sys
import numpy as np
from pathlib import Path

# Try to use production embedding model; fall back to TF-IDF if unavailable
print("[embeddings_util] Initializing embeddings...", file=sys.stderr)
try:
    print("[embeddings_util] Loading sentence-transformers...", file=sys.stderr)
    from sentence_transformers import SentenceTransformer
    EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"[embeddings_util] Loading model: {EMBED_MODEL}...", file=sys.stderr)
    model = SentenceTransformer(EMBED_MODEL)
    print("[embeddings_util] Model loaded successfully", file=sys.stderr)
    EMBED_DIM = 384  # Dimension of all-MiniLM-L6-v2
    USE_TFIDF = False
except Exception as e:
    print(f"[embeddings_util] Falling back to TF-IDF: {e}", file=sys.stderr)
    from sklearn.feature_extraction.text import TfidfVectorizer
    EMBED_DIM = 100  # arbitrary dimension for TF-IDF
    EMBED_MODEL = "TF-IDF (baseline)"
    USE_TFIDF = True
    model = None


def load_and_split_handbook():
    """
    Loads TPC HANDBOOK.txt from data/ and splits it into manageable chunks.
    
    Returns: (filenames, texts)
        filenames: list of section identifiers
        texts: list of text content for each section
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    handbook_path = os.path.join(data_dir, "TPC HANDBOOK.txt")
    
    if not os.path.exists(handbook_path):
        raise FileNotFoundError(f"Handbook not found at {handbook_path}")
    
    with open(handbook_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split on double newlines to create logical sections
    raw_sections = content.split('\n\n')
    
    filenames = []
    texts = []
    
    chunk_size = 5  # Combine sections to create reasonably-sized chunks
    current_chunk = []
    chunk_num = 0
    
    for section in raw_sections:
        section = section.strip()
        if len(section) > 50:  # Skip very short sections
            current_chunk.append(section)
            
            # When chunk reaches desired size or is substantial, save it
            if len(current_chunk) >= chunk_size or sum(len(s) for s in current_chunk) > 3000:
                chunk_num += 1
                chunk_text = '\n\n'.join(current_chunk)
                filenames.append(f"{chunk_num:02d}_handbook_section.txt")
                texts.append(chunk_text)
                current_chunk = []
    
    # Add any remaining content
    if current_chunk:
        chunk_num += 1
        chunk_text = '\n\n'.join(current_chunk)
        filenames.append(f"{chunk_num:02d}_handbook_section.txt")
        texts.append(chunk_text)
    
    # Fallback: if no sections were created, treat entire file as one
    if not texts:
        filenames = ["TPC_HANDBOOK.txt"]
        texts = [content]
    
    return filenames, texts



def embed_corpus():
    """
    Loads handbook, splits into sections, and embeds each.
    
    Returns:
        filenames: list of section filenames
        texts: list of section texts
        vectors: numpy array of shape (n_sections, EMBED_DIM)
        embed_fn: function to embed a list of strings -> numpy array
        model_name: string describing the embedding model used
    """
    print(f"[embed_corpus] Loading handbook...", file=sys.stderr)
    filenames, texts = load_and_split_handbook()
    print(f"[embed_corpus] Loaded {len(texts)} sections from TPC Handbook", file=sys.stderr)
    
    if USE_TFIDF:
        print(f"[embed_corpus] Using TF-IDF vectorizer...", file=sys.stderr)
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(max_features=EMBED_DIM, stop_words='english')
        vectors = vectorizer.fit_transform(texts).toarray().astype(np.float32)
        embed_fn = lambda texts_to_embed: vectorizer.transform(texts_to_embed).toarray().astype(np.float32)
    else:
        # Use sentence-transformers
        print(f"[embed_corpus] Encoding {len(texts)} texts with {EMBED_MODEL}...", file=sys.stderr)
        vectors = np.array(model.encode(texts, convert_to_numpy=True), dtype=np.float32)
        embed_fn = lambda texts_to_embed: np.array(
            model.encode(texts_to_embed, convert_to_numpy=True),
            dtype=np.float32
        )
    
    print(f"[embed_corpus] Embedding complete. Shape: {vectors.shape}", file=sys.stderr)
    return filenames, texts, vectors, embed_fn, EMBED_MODEL
