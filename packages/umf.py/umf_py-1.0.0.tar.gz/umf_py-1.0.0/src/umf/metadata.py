"""The UMF metadata class."""

from typing import Dict, Optional


class Metadata:
    """The metadata container for UMF data."""

    def __init__(self, media_name: str):
        """Initialize the metadata.
        
        Args:
            media_name: The name of the media
        """
        self.media_name = media_name
        self.global_fields: Dict[str, str] = {}
        self.groups: Dict[str, Dict[str, str]] = {}

    def has(self, header: Optional[str], name: str) -> bool:
        """Check if a field exists.
        
        Args:
            header: The header name (None for global fields)
            name: The field name
            
        Returns:
            True if the field exists, False otherwise
        """
        return self.get(header, name) is not None

    def get(self, header: Optional[str], name: str) -> Optional[str]:
        """Get a field value.
        
        Args:
            header: The header name (None for global fields)
            name: The field name
            
        Returns:
            The field value or None if not found
        """
        if header:
            group = self.groups.get(header)
            
            if group:
                value = group.get(name)
                
                if value is not None:
                    return value
            
            # Fall back to global fields
            return self.global_fields.get(name)
        
        return self.global_fields.get(name)

    def set(self, header: Optional[str], name: str, value: str) -> None:
        """Set a field value.
        
        Args:
            header: The header name (None for global fields)
            name: The field name
            value: The field value
        """
        if header is None:
            self.global_fields[name] = value
        else:
            if header not in self.groups:
                self.groups[header] = {}
            
            self.groups[header][name] = value

    def __str__(self) -> str:
        """Get string representation of the metadata.
        
        Returns:
            The UMF formatted string
        """
        lines = [self.media_name]

        if self.global_fields:
            lines.append("")
            
            for name, value in self.global_fields.items():
                lines.append(f"{name}: {value}")

        if not self.groups:
            return "\n".join(lines)

        for header, group in self.groups.items():
            lines.append(f"\n[ {header} ]\n")
            
            for name, value in group.items():
                lines.append(f"{name}: {value}")

        return "\n".join(lines)
