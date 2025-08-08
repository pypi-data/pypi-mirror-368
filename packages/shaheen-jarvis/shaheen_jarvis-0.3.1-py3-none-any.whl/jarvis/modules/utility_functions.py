"""
Utility functions for Shaheen-Jarvis framework.
Includes password generation, note management, and other utilities.
"""

import json
import os
import random
import string
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional


def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """
    Generate a secure password.
    
    Args:
        length: Password length (default: 12)
        include_symbols: Whether to include special characters
        
    Returns:
        Generated password
    """
    try:
        if length < 4:
            return "Error: Password length must be at least 4 characters"
        
        if length > 128:
            return "Error: Password length cannot exceed 128 characters"
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""
        
        # Ensure at least one character from each required set
        password = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(digits)
        ]
        
        if include_symbols:
            password.append(random.choice(symbols))
        
        # Fill remaining length with random characters
        all_chars = lowercase + uppercase + digits + symbols
        remaining_length = length - len(password)
        
        for _ in range(remaining_length):
            password.append(random.choice(all_chars))
        
        # Shuffle the password
        random.shuffle(password)
        
        return f"Generated password: {''.join(password)}"
    
    except Exception as e:
        return f"Error generating password: {str(e)}"


def note_something(note: str, category: str = "general") -> str:
    """
    Save a note to the notes file.
    
    Args:
        note: Note content
        category: Note category (default: general)
        
    Returns:
        Success message
    """
    try:
        notes_file = "jarvis_notes.json"
        
        # Load existing notes
        notes = []
        if os.path.exists(notes_file):
            with open(notes_file, 'r', encoding='utf-8') as f:
                notes = json.load(f)
        
        # Create new note
        new_note = {
            'id': len(notes) + 1,
            'content': note,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        notes.append(new_note)
        
        # Save notes
        with open(notes_file, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        
        return f"Note saved successfully! (ID: {new_note['id']}, Category: {category})"
    
    except Exception as e:
        return f"Error saving note: {str(e)}"


def recall_note(query: Optional[str] = None, category: Optional[str] = None, limit: int = 10) -> str:
    """
    Recall notes based on query or category.
    
    Args:
        query: Search query (optional)
        category: Filter by category (optional)
        limit: Maximum number of notes to return
        
    Returns:
        Found notes or message
    """
    try:
        notes_file = "jarvis_notes.json"
        
        if not os.path.exists(notes_file):
            return "No notes found. Create your first note with note_something()!"
        
        with open(notes_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        if not notes:
            return "No notes found."
        
        # Filter notes
        filtered_notes = notes
        
        if category:
            filtered_notes = [note for note in filtered_notes if note.get('category', '').lower() == category.lower()]
        
        if query:
            query = query.lower()
            filtered_notes = [
                note for note in filtered_notes 
                if query in note.get('content', '').lower() or query in note.get('category', '').lower()
            ]
        
        if not filtered_notes:
            search_info = []
            if query:
                search_info.append(f"query '{query}'")
            if category:
                search_info.append(f"category '{category}'")
            return f"No notes found matching {' and '.join(search_info) if search_info else 'criteria'}."
        
        # Sort by most recent
        filtered_notes.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit results
        filtered_notes = filtered_notes[:limit]
        
        # Format output
        result = [f"Found {len(filtered_notes)} note(s):"]
        for note in filtered_notes:
            result.append(f"\nID: {note.get('id', 'N/A')}")
            result.append(f"Date: {note.get('date', 'N/A')}")
            result.append(f"Category: {note.get('category', 'general')}")
            result.append(f"Content: {note.get('content', '')}")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error recalling notes: {str(e)}"


def hash_text(text: str, algorithm: str = "sha256") -> str:
    """
    Generate hash of text.
    
    Args:
        text: Text to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
    Returns:
        Hash value or error message
    """
    try:
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
        
        if algorithm.lower() not in algorithms:
            return f"Error: Unsupported algorithm '{algorithm}'. Supported: {list(algorithms.keys())}"
        
        hash_func = algorithms[algorithm.lower()]
        hash_value = hash_func(text.encode('utf-8')).hexdigest()
        
        text_preview = text[:50] + ('...' if len(text) > 50 else '')
        return f"{algorithm.upper()} hash of '{text_preview}':\n{hash_value}"
    
    except Exception as e:
        return f"Error generating hash: {str(e)}"


def encode_decode_base64(text: str, operation: str = "encode") -> str:
    """
    Encode or decode text using Base64.
    
    Args:
        text: Text to encode/decode
        operation: 'encode' or 'decode'
        
    Returns:
        Encoded/decoded text or error message
    """
    try:
        import base64
        
        if operation.lower() == "encode":
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            return f"Base64 encoded:\n{encoded}"
        
        elif operation.lower() == "decode":
            decoded = base64.b64decode(text.encode('utf-8')).decode('utf-8')
            return f"Base64 decoded:\n{decoded}"
        
        else:
            return "Error: Operation must be 'encode' or 'decode'"
    
    except Exception as e:
        return f"Error with Base64 operation: {str(e)}"


def generate_uuid() -> str:
    """Generate a UUID."""
    try:
        import uuid
        new_uuid = str(uuid.uuid4())
        return f"Generated UUID: {new_uuid}"
    
    except Exception as e:
        return f"Error generating UUID: {str(e)}"


def word_count(text: str) -> str:
    """
    Count words, characters, and lines in text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Text statistics
    """
    try:
        lines = text.split('\n')
        words = text.split()
        characters = len(text)
        characters_no_spaces = len(text.replace(' ', ''))
        
        return f"Text Statistics:\nLines: {len(lines)}\nWords: {len(words)}\nCharacters (with spaces): {characters}\nCharacters (without spaces): {characters_no_spaces}"
    
    except Exception as e:
        return f"Error counting words: {str(e)}"


def list_notes_categories() -> str:
    """List all note categories."""
    try:
        notes_file = "jarvis_notes.json"
        
        if not os.path.exists(notes_file):
            return "No notes found."
        
        with open(notes_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        if not notes:
            return "No notes found."
        
        # Get unique categories
        categories = set()
        for note in notes:
            categories.add(note.get('category', 'general'))
        
        category_counts = {}
        for note in notes:
            cat = note.get('category', 'general')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        result = ["Note categories:"]
        for cat in sorted(categories):
            result.append(f"  {cat}: {category_counts[cat]} note(s)")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error listing categories: {str(e)}"


# For compatibility with the module loading system
__all__ = [
    "generate_password",
    "note_something",
    "recall_note",
    "hash_text",
    "encode_decode_base64",
    "generate_uuid",
    "word_count",
    "list_notes_categories"
]
