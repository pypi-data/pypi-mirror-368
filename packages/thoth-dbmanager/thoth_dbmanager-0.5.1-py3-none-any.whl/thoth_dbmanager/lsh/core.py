"""
Core LSH functionality extracted from helpers.
"""

import logging
from typing import Dict, List, Tuple

from datasketch import MinHash, MinHashLSH
from tqdm import tqdm


def create_minhash(signature_size: int, string: str, n_gram: int) -> MinHash:
    """
    Creates a MinHash object for a given string.

    Args:
        signature_size (int): The size of the MinHash signature.
        string (str): The input string to create the MinHash for.
        n_gram (int): The n-gram size for the MinHash.

    Returns:
        MinHash: The MinHash object for the input string.
    """
    m = MinHash(num_perm=signature_size)
    for d in [string[i : i + n_gram] for i in range(len(string) - n_gram + 1)]:
        m.update(d.encode("utf8"))
    return m


def skip_column(column_name: str, column_values: List[str]) -> bool:
    """
    Determines whether to skip processing a column based on its values.

    Args:
        column_name (str): The name of the column.
        column_values (List[str]): The list of values in the column.

    Returns:
        bool: True if the column should be skipped, False otherwise.
    """
    if "name" in column_name.lower():
        return False
    sum_of_lengths = sum(len(value) for value in column_values)
    average_length = sum_of_lengths / len(column_values)
    return (sum_of_lengths > 50000) and (average_length > 20)


def jaccard_similarity(m1: MinHash, m2: MinHash) -> float:
    """
    Computes the Jaccard similarity between two MinHash objects.

    Args:
        m1 (MinHash): The first MinHash object.
        m2 (MinHash): The second MinHash object.

    Returns:
        float: The Jaccard similarity between the two MinHash objects.
    """
    return m1.jaccard(m2)


def create_lsh_index(
    unique_values: Dict[str, Dict[str, List[str]]],
    signature_size: int,
    n_gram: int,
    threshold: float,
    verbose: bool = True,
) -> Tuple[MinHashLSH, Dict[str, Tuple[MinHash, str, str, str]]]:
    """
    Creates a MinHash Locality-Sensitive Hashing (LSH) index from unique values in a database.

    This function processes unique values from database tables and columns, creates MinHash
    signatures for each value, and builds an LSH index for efficient similarity search.

    Args:
        unique_values (Dict[str, Dict[str, List[str]]]): A nested dictionary containing unique values
            from the database. The structure is {table_name: {column_name: [values]}}.
        signature_size (int): The number of permutations to use in the MinHash signatures.
        n_gram (int): The size of n-grams to use when creating MinHash signatures.
        threshold (float): The similarity threshold for the LSH index. Values closer to 1 require
            higher similarity for matches.
        verbose (bool, optional): If True, displays a progress bar during processing. Defaults to True.

    Returns:
        Tuple[MinHashLSH, Dict[str, Tuple[MinHash, str, str, str]]]: A tuple containing:
            - MinHashLSH: The constructed LSH index.
            - Dict[str, Tuple[MinHash, str, str, str]]: A dictionary mapping unique keys to tuples
              containing (MinHash object, table name, column name, original value).

    Raises:
        Exception: If an error occurs during LSH creation, it's logged but not raised.

    Note:
        This function uses the datasketch library for MinHash and LSH operations.
    """
    lsh = MinHashLSH(threshold=threshold, num_perm=signature_size)
    minhashes: Dict[str, Tuple[MinHash, str, str, str]] = {}
    try:
        total_unique_values = sum(
            len(column_values)
            for table_values in unique_values.values()
            for column_values in table_values.values()
        )
        logging.info(f"Total unique values: {total_unique_values}")

        progress_bar = (
            tqdm(total=total_unique_values, desc="Creating LSH") if verbose else None
        )

        for table_name, table_values in unique_values.items():
            for column_name, column_values in table_values.items():
                if column_name.lower() == "doctype":
                    print("=" * 20)
                    print("Doctype found")
                    print("=" * 20)
                logging.info(
                    f"Processing {table_name} - {column_name} - {len(column_values)}"
                )

                for id, value in enumerate(column_values):
                    minhash = create_minhash(signature_size, value, n_gram)
                    minhash_key = f"{table_name}_{column_name}_{id}"
                    minhashes[minhash_key] = (minhash, table_name, column_name, value)
                    lsh.insert(minhash_key, minhash)

                    if verbose:
                        progress_bar.update(1)

        if verbose:
            progress_bar.close()
    except Exception as e:
        logging.error(f"Error creating LSH: {e}")

    return lsh, minhashes


def query_lsh_index(
    lsh: MinHashLSH,
    minhashes: Dict[str, Tuple[MinHash, str, str, str]],
    keyword: str,
    signature_size: int = 30,
    n_gram: int = 3,
    top_n: int = 10,
) -> Dict[str, Dict[str, List[str]]]:
    """
    Queries the LSH for similar values to the given keyword and returns the top results.

    Args:
        lsh (MinHashLSH): The LSH object.
        minhashes (Dict[str, Tuple[MinHash, str, str, str]]): The dictionary of MinHashes.
        keyword (str): The keyword to search for.
        signature_size (int, optional): The size of the MinHash signature.
        n_gram (int, optional): The n-gram size for the MinHash.
        top_n (int, optional): The number of top results to return.

    Returns:
        Dict[str, Dict[str, List[str]]]: A dictionary containing the top similar values.
        Example:{
        'table_name1': {
            'column_name1': ['value1', 'value2', 'value3'],
            'column_name2': ['value4', 'value5']
        },
        'table_name2': {
    """
    query_minhash = create_minhash(signature_size, keyword, n_gram)
    results = lsh.query(query_minhash)
    similarities = [
        (result, jaccard_similarity(query_minhash, minhashes[result][0]))
        for result in results
    ]
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]

    similar_values_trimmed: Dict[str, Dict[str, List[str]]] = {}
    for result, similarity in similarities:
        table_name, column_name, value = minhashes[result][1:] #type: ignore
        if table_name not in similar_values_trimmed:
            similar_values_trimmed[table_name] = {}
        if column_name not in similar_values_trimmed[table_name]:
            similar_values_trimmed[table_name][column_name] = []
        similar_values_trimmed[table_name][column_name].append(value)

    return similar_values_trimmed
