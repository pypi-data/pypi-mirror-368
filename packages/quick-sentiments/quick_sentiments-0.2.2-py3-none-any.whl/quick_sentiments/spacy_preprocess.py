import re
import unicodedata

# --- Global spaCy NLP object ---
# Initialize as None. It will be assigned the loaded spaCy model if successful.
nlp = None 
spacy_available = False # Flag to indicate if spacy was successfully imported

try:
    import spacy
    spacy_available = True # Set flag to True if import succeeds
    # Attempt to load the spaCy model only if spaCy itself is imported
    try:
        nlp = spacy.load("en_core_web_sm")
        print("SpaCy and model 'en_core_web_sm' loaded successfully.")
    except OSError:
        print("SpaCy model 'en_core_web_sm' not found. Attempting to download...")
        try:
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
            print("SpaCy model 'en_core_web_sm' downloaded and loaded successfully.")
        except Exception as e:
            print(f"ERROR: Failed to download or load spaCy model: {e}")
            print("Please try downloading manually: python -m spacy download en_core_web_sm")
            nlp = None # Ensure nlp is None if model loading fails

except ImportError:
    print("\nWARNING: The 'spacy' library is not installed. ")
    print("If you plan to use 'tokenize=True', please install it using: pip install spacy")
    print("And then download the English model: python -m spacy download en_core_web_sm\n")
    # nlp remains None and spacy_available remains False
# --- Initialize spaCy components once ---

# --- Helper Cleaning Functions ---
def remove_square_brackets(text):
    """Removes text enclosed in square brackets."""
    cleaned_text = re.sub(r'\[.*?\]', '', text)
    return cleaned_text.strip()

def remove_urls_emails(text):
    """Removes URLs and email addresses from text."""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\S*@\S*\s?', '', text)
    return text

def remove_html_tags(text):
    """Removes HTML tags from text."""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def remove_extra_spaces(text):
    """Replaces multiple spaces with a single space and strips leading/trailing spaces."""
    return re.sub(r'\s+', ' ', text).strip()


def remove_emojis(text):
    """Removes common emojis from text using a regex pattern."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def normalize_unicode_characters(text): # <--- NEW HELPER FUNCTION
    """
    Normalizes unicode characters (e.g., smart quotes, accented chars)
    to their closest ASCII equivalents and removes non-ASCII.
    """
    # Normalize to NFKD form (decomposes characters like é to e + accent)
    # Then encode to ASCII, ignoring characters that can't be mapped
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

def pre_process_spacy(doc,
                remove_brackets=True,
                remove_urls=True,
                remove_html=True,
                remove_nums=False,
                remove_emojis_flag=False,
                normalize_unicode=True,
                to_lowercase=True,
                tokenize=True, # Note: This flag will now behave slightly differently
                remove_punct_tokens=True,
                remove_stop_words=True,
                lemmatize=True,
                remove_extra_space=True,
                return_string=True):

    # Stage 1: Text-level cleaning (remains largely the same)
    if remove_brackets:
        doc = remove_square_brackets(doc)
    if remove_urls:
        doc = remove_urls_emails(doc)
    if remove_html:
        doc = remove_html_tags(doc)
    if remove_emojis_flag:
        doc = remove_emojis(doc)
    if normalize_unicode:
        doc = normalize_unicode_characters(doc)
    if to_lowercase:
        doc = doc.lower()
    if remove_extra_space:
        doc = remove_extra_spaces(doc)

    # Stage 2 & 3: Tokenization & Token-level cleaning (combined for spaCy)
    # The 'tokenize' flag now controls whether we run the spaCy pipeline or not.
    if tokenize:
        doc_spacy = nlp(doc)  # The spaCy magic happens here
        processed_tokens = []
        for token in doc_spacy:
            # Check for punctuation first, as it can interfere with other checks
            if remove_punct_tokens and token.is_punct:
                continue

            # Check if the token is a stop word
            if remove_stop_words and token.is_stop:
                continue
            
            # Note: remove_nums is handled on the string level, but we can also
            # add a check here for more granular control if needed:
            if remove_nums and token.like_num:
                continue
            
            # Apply lemmatization
            processed_token = token.lemma_ if lemmatize else token.text
            
            # Final check to ensure we don't have empty strings or just whitespace
            if processed_token.strip():
                processed_tokens.append(processed_token)
    else:
        # If not tokenizing, we return the string after Stage 1 cleaning
        return [doc.strip()] if not return_string else doc.strip()

    # Stage 4: Final output
    if return_string:
        # Clean up any extra spaces that may have been created
        return " ".join(processed_tokens).strip()
    else:
        return processed_tokens