from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix

def fit_tfidf(texts: List[str],
            max_features: int = 5000,
            ngram_range: Tuple[int, int] = (1, 2),
            lowercase: bool = True,
            min_df: int = 1,
            max_df: float = 1.0) -> Tuple[TfidfVectorizer, csr_matrix]:
    """
    Fit a TF-IDF vectorizer on a list of texts and return (vectorizer, features).

    Parameters
    ----------
    texts : list of str
        Training documents.
    max_features : int
        Limit vocabulary size.
    ngram_range : (min_n, max_n)
        Use word n-grams in this range.
    lowercase : bool
        Lowercase text before vectorizing.
    min_df : int
        Ignore terms that appear in fewer than min_df documents.
    max_df : float
        Ignore terms that appear in more than max_df proportion of documents.

    Returns
    -------
    vectorizer : TfidfVectorizer
    X : csr_matrix
        Sparse TF-IDF feature matrix of shape (n_docs, n_features).
    """
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        lowercase=lowercase,
        min_df=min_df,
        max_df=max_df
    )
    X = vectorizer.fit_transform(texts)
    return vectorizer, X


def transform_tfidf(vectorizer: TfidfVectorizer, texts: List[str]) -> csr_matrix:
    """
    Transform new texts using a fitted TF-IDF vectorizer.

    Parameters
    ----------
    vectorizer : TfidfVectorizer
        A fitted TF-IDF vectorizer.
    texts : list of str
        New documents.

    Returns
    -------
    X : csr_matrix
        Sparse TF-IDF feature matrix.
    """
    return vectorizer.transform(texts)
