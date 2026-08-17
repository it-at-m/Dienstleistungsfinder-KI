import re
from difflib import SequenceMatcher
from os import getenv

from errors import QuoteNotFoundException
from logtools import getLogger

logger = getLogger()

DLF_QUOTE_MIN_MATCH_RATIO = float(getenv("DLF_QUOTE_MIN_MATCH_RATIO", 0.5))
BOUNDARIES_LEFT = [".", "!", "?", "…", ":", ";", "\n", "*"]
BOUNDARIES_RIGHT = [".", "!", "?", "…", ";"]


def _get_best_match(query, corpus, step=4, flex=3, case_sensitive=False, verbose=False) -> tuple[str, float]:
    """Return best matching substring of corpus.
    https://stackoverflow.com/questions/36013295/find-best-substring-match/36132391#36132391

    Parameters
    ----------
    query : str
    corpus : str
    step : int
        Step size of first match-value scan through corpus. Can be thought of
        as a sort of "scan resolution". Should not exceed length of query.
    flex : int
        Max. left/right substring position adjustment value. Should not
        exceed length of query / 2.

    Outputs
    -------
    output0 : str
        Best matching substring.
    output1 : float
        Match ratio of best matching substring. 1 is perfect match.
    """

    def _match(a, b):
        """Compact alias for SequenceMatcher."""
        return SequenceMatcher(None, a, b).ratio()

    def scan_corpus(step):
        """Return list of match values from corpus-wide scan."""
        match_values = []

        m = 0
        while m + qlen - step <= len(corpus):
            match_values.append(_match(query, corpus[m : m - 1 + qlen]))
            if verbose:
                print(
                    query,
                    "-",
                    corpus[m : m + qlen],
                    _match(query, corpus[m : m + qlen]),
                )
            m += step

        return match_values

    def index_max(v):
        """Return index of max value."""
        return max(range(len(v)), key=v.__getitem__)

    def adjust_left_right_positions():
        """Return left/right positions for best string match."""
        # bp_* is synonym for 'Best Position Left/Right' and are adjusted
        # to optimize bmv_*
        p_l, bp_l = [pos] * 2
        p_r, bp_r = [pos + qlen] * 2

        # bmv_* are declared here in case they are untouched in optimization
        bmv_l = match_values[p_l // step]
        bmv_r = match_values[p_l // step]

        for f in range(flex):
            ll = _match(query, corpus[p_l - f : p_r])
            if ll > bmv_l:
                bmv_l = ll
                bp_l = p_l - f

            lr = _match(query, corpus[p_l + f : p_r])
            if lr > bmv_l:
                bmv_l = lr
                bp_l = p_l + f

            rl = _match(query, corpus[p_l : p_r - f])
            if rl > bmv_r:
                bmv_r = rl
                bp_r = p_r - f

            rr = _match(query, corpus[p_l : p_r + f])
            if rr > bmv_r:
                bmv_r = rr
                bp_r = p_r + f

            if verbose:
                print("\n" + str(f))
                print("ll: -- value: %f -- snippet: %s" % (ll, corpus[p_l - f : p_r]))
                print("lr: -- value: %f -- snippet: %s" % (lr, corpus[p_l + f : p_r]))
                print("rl: -- value: %f -- snippet: %s" % (rl, corpus[p_l : p_r - f]))
                print("rr: -- value: %f -- snippet: %s" % (rl, corpus[p_l : p_r + f]))

        return bp_l, bp_r, _match(query, corpus[bp_l:bp_r])

    if not case_sensitive:
        query = query.lower()
        corpus = corpus.lower()

    qlen = len(query)

    if flex >= qlen / 2:
        print("Warning: flex exceeds length of query / 2. Setting to default.")
        flex = 3

    match_values = scan_corpus(step)
    pos = index_max(match_values) * step

    pos_left, pos_right, match_value = adjust_left_right_positions()

    return pos_left, pos_right, match_value


def _check_link(article_md: str, sentence_start: int, sentence_end: int) -> int:
    """
    Check if the text starting at pos_left and ending at pos_right has an
    incomplete Markdown link (e.g. "[link text](" without a closing ')').
    If so, extend pos_right to include the rest of the link

    Args:
        article_md (str): The markdown text to check.
        sentence_end (int): The ending position of the sentence (after the quote).

    Returns:
        sentence_end (int): end index of quote

    """

    # Check for an incomplete Markdown link pattern at pos_right
    quote = article_md[sentence_start:sentence_end]

    # The pattern looks for:
    #   - '[' followed by one or more non-']' characters,
    #   - then ']' and '(',
    #   - then any number of characters that are not ')'
    #   until the end of the string.
    incomplete_link_pattern = re.compile(r"\[[^\]]+\]\([^\)]*$")

    # If the extracted quote contains an incomplete Markdown link...
    if incomplete_link_pattern.search(quote):
        # Try to find the corresponding closing parenthesis in the entire article,
        # starting at the current sentence_end.
        closing_paren_index = article_md.find(")", sentence_end)
        if closing_paren_index != -1:
            # Extend sentence_end to include the closing parenthesis.
            sentence_end = closing_paren_index + 1

    # Pattern to detect if the quote starts with a closing part of a link, e.g., "muenchen.de)"
    partial_link_pattern = re.compile(r"^\S+\)")

    if partial_link_pattern.search(quote.strip()):
        logger.debug("Partial Link at beginning of quote found")
        # Look for the nearest opening `[link text](` before `sentence_start`
        opening_bracket_index = article_md.rfind("[", 0, sentence_start)
        opening_paren_index = article_md.rfind("](", 0, sentence_start)

        # If both `[` and `](` exist, adjust `sentence_start` to capture the full link
        if opening_bracket_index != -1 and opening_paren_index != -1 and opening_paren_index > opening_bracket_index:
            # Adjust `sentence_start` to include the full Markdown link
            sentence_start = opening_bracket_index

    return sentence_start, sentence_end


def _extend_numeric_list(article_md: str, sentence_end: int) -> int:
    """
    Ensures that the extracted quote does not end in the middle of a numeric list item.

    If the quote ends on a numbered list pattern like:
    "1. some information" or "2. more info",
    it extends the `sentence_end` to capture the full list item.

    Args:
        article_md (str): The full text of the article.
        sentence_end (int): The current end position of the quote.

    Returns:
        int: Updated sentence_end if a numeric list item is detected.
    """

    # Extract the text after the current `sentence_end`,
    # while ensuring that the beginning of a list (usually indicated with 1.) remains in the remainder
    remainder = article_md[sentence_end - 2 :]

    # Pattern to detect numbered list items: "1. text" or "23. text"
    md_list_pattern = re.compile(r"^\s*\d+\.\s+[^\n]+")

    while True:
        # Check for Markdown numbered list items
        md_match = md_list_pattern.match(remainder)

        if md_match:
            # Extend `sentence_end` to capture the entire numbered list item
            sentence_end += md_match.end()

            # Move forward and update remainder to check for further list items
            remainder = article_md[sentence_end - 1 :]

        else:
            # Stop if no more list items are detected
            break

        # Stop if the next line is blank, a Markdown header (##), or other section delimiter
        next_lines = remainder.lstrip().split("\n", 1)
        next_line = next_lines[0] if next_lines else ""

        if not next_line.strip() or next_line.startswith("##") or next_line.startswith("#"):
            break

    return sentence_end


def process_quote(quote, article_md) -> str:
    """
    Process a quote within an article and return the quote, plus its prefix & suffix.

    Args:
        quote (str): The quote to be processed.
        article_md (str): The text of the article.

    Returns:
        tuple[str, str, str]: (prefix, matched_quote, suffix)

    Raises:
        QuoteNotFoundException: If the match ratio < DLF_QUOTE_MIN_MATCH_RATIO
    """

    # heuristic suggestions: step < len(quote)*3/4, flex < len(quote)/3
    # Cap step size to ensure we don't skip over matches for longer quotes
    step = min(max(1, len(quote) // 2), 20)
    flex = max(1, len(quote) // 4)

    pos_left, pos_right, match_value = _get_best_match(
        query=quote, corpus=article_md, step=step, flex=flex, case_sensitive=False, verbose=False
    )

    matched_quote = article_md[pos_left:pos_right]

    # If match is below threshold, raise an error
    if match_value < DLF_QUOTE_MIN_MATCH_RATIO:
        raise QuoteNotFoundException(quote, article_md)

    # Always find the beginning of the sentence that contains the quote
    sentence_boundaries_left = [article_md.rfind(p, 0, pos_left) for p in BOUNDARIES_LEFT]
    sentence_start = max(sentence_boundaries_left, default=-1)

    # If we didn't find any boundary, set to 0; otherwise jump just after the punctuation
    if sentence_start == -1:
        sentence_start = 0
    else:
        sentence_start += 1

    # Skip leading spaces if any
    while sentence_start < len(article_md) and article_md[sentence_start] in (" ", "\n"):  # , "#"):
        sentence_start += 1

    # Identify the lowest position of '.', '!', or '?' after pos_right
    sentence_boundaries_right = [article_md.find(p, pos_right, len(article_md)) for p in BOUNDARIES_RIGHT]

    # Find the end of the sentence containing the quote
    valid_boundaries_right = [b for b in sentence_boundaries_right if b != -1]

    if not valid_boundaries_right:
        sentence_end = len(article_md)
    else:
        sentence_end = min(valid_boundaries_right)

        # Move just past the punctuation
        if sentence_end < len(article_md) and article_md[sentence_end] in BOUNDARIES_RIGHT:
            sentence_end += 1

    # make sure to include full md links at end of quote
    sentence_start, sentence_end = _check_link(article_md, sentence_start, sentence_end)
    sentence_end = _extend_numeric_list(article_md, sentence_end)
    # TODO: OPTIONAL: finish full date if quote ends on date, e.g. question: Wo ist mein Wahlbüro für die Bundestagswahl?

    # Prefix is from the start of this sentence up to pos_left
    prefix = article_md[sentence_start:pos_left]
    matched_quote = article_md[pos_left:pos_right]

    # Suffix is the text after the quote
    suffix_end = min(len(article_md), sentence_end)
    suffix = article_md[pos_right:suffix_end]

    # Return matched_quote including prefix and suffix
    full_quote = prefix + matched_quote + suffix
    logger.debug(f"Full quote: {full_quote}")

    # Ensure full_quote starts with a newline character and citation indicators
    if not full_quote[0].isalpha():
        full_quote = "\n\n[...] " + full_quote + " [...]"
    else:
        full_quote = "\n\n[...] " + full_quote + " [...]"
    return full_quote
