"""UMF parsing functionality."""

from typing import Optional
from .metadata import Metadata
from .error import UMFError


def parse(input_text: str) -> Metadata:
    """Parse UMF formatted text into a Metadata object.
    
    Args:
        input_text: The UMF formatted text to parse
        
    Returns:
        A Metadata object containing the parsed data
        
    Raises:
        UMFError: If there are parsing errors
    """
    lines = input_text.split('\n')

    media_name = lines[0].strip() if lines else ""
    if not media_name:
        raise UMFError('Empty Media Name', 1, lines[0] if lines else "")

    metadata = Metadata(media_name)
    header: Optional[str] = None

    for i in range(1, len(lines)):
        line = lines[i].strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        elif line.startswith('[') and line.endswith(']'):
            # Parse header
            header = line[1:-1].strip()
            if not header:
                raise UMFError('Empty Header Name', i + 1, line)
        elif ':' in line:
            # Parse field
            separator_index = line.index(':')
            name = line[:separator_index].strip()
            value = line[separator_index + 1:].strip()

            if not name:
                raise UMFError('Empty Field Name', i + 1, line)
            if not value:
                raise UMFError('Empty Field Value', i + 1, line)

            metadata.set(header, name, value)
        else:
            raise UMFError('Invalid Line', i + 1, line)

    return metadata
