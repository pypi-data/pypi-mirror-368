import yaml
import logging


def validate_and_extract_sectiontitle(attributes):
    """Validate and extract the 'sectiontitle' attribute."""
    sectiontitle = attributes.pop("sectiontitle", None)
    if sectiontitle is None:
        return None

    # Ensure 'headline' exists and is a list
    headline = sectiontitle.get("headline")
    if headline is None:
        logging.error("The 'sectiontitle' must contain a 'headline'.")
        raise ValueError("Invalid 'sectiontitle': missing 'headline'")
    if not isinstance(headline, list):
        headline = [headline]
    sectiontitle["headline"] = headline

    # Validate 'image' if it exists
    if "image" in sectiontitle:
        if "url" not in sectiontitle["image"]:
            logging.error("The 'image' field must contain a 'url' field.")
            raise ValueError("Invalid 'sectiontitle': 'image' missing 'url'")

    return sectiontitle


def validate_titlepage(titlepage):
    """Validate and cleanup titlepage."""

    # Parse headline
    headline = titlepage.get("headline", None)
    if headline is None:
        logging.error("The 'titlepage' must contain a 'headline' <array>.")
        raise ValueError("Invalid 'titlepage': missing 'headline'")
    if not isinstance(headline, list):
        headline = [headline]
    titlepage["headline"] = headline
    # validate by if it exists
    if "by" in titlepage:
        by = titlepage.get("by")
        if not isinstance(by, list):
            by = [by]
        titlepage["by"] = by

    # validate byinf if it exists
    if "byinfo" in titlepage:
        byinfo = titlepage.get("byinfo")
        if not isinstance(byinfo, list):
            byinfo = [byinfo]
        titlepage["byinfo"] = byinfo


def parse_slide(file_path):
    """Parse an HTML slide and return its attributes and content."""
    logging.info(f"  Parsing file: {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Extract YAML header
    yaml_header = []
    content = []
    in_header = False
    for line in lines:
        if line.strip() == "---":
            in_header = not in_header
        elif in_header:
            yaml_header.append(line)
        else:
            content.append(line)

    try:
        attributes = yaml.safe_load("\n".join(yaml_header))
    except yaml.scanner.ScannerError as e:
        logging.error(f"Error in file: {file_path}")
        logging.error(f"YAML header causing the issue: {yaml_header}")
        raise e
    if not attributes:
        attributes = {}
    # Validate and extract 'sectiontitle' if it exists
    sectiontitle = validate_and_extract_sectiontitle(attributes)
    result = {"attributes": attributes, "content": "\n".join(content)}
    if sectiontitle:
        result["sectiontitle"] = sectiontitle

    return result


def dict_to_html_attrs(d):
    """
    Convert a dictionary to a string of HTML attributes.

    Parameters:
        d (dict): The dictionary containing the HTML attributes.

    Returns:
        str: The string of HTML attributes.
    """
    if not d:
        return ""
    keystr = " ".join(f'{key}="{value}"' for key, value in d.items())
    return keystr
