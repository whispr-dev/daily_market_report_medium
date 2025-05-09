def load_mailing_list(path="mailing_list.txt"):
    """
    Load recipients from a plaintext mailing list file.
    Each line should contain one email address.
    Blank lines and comments (#) are ignored.
    """
    try:
        with open(path, 'r') as f:
            return [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.strip().startswith("#")
            ]
    except Exception as e:
        print(f"Error loading mailing list: {e}")
        return []
