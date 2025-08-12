#!/usr/bin/env python3
"""
Documentation Language Checker
Enforces "underpromise, overdeliver" policy by detecting overselling language.

Usage:
    python check_documentation_language.py [file1] [file2] ...
    
    If no files specified, checks all .md and .py files in the repository.
"""

import re
import sys
import os
from pathlib import Path
from typing import List, Tuple, Dict

# POLICY DEFINITIONS
BANNED_WORDS = [
    r'\bperfect(ly)?\b',
    r'\bamazing(ly)?\b', 
    r'\bincredible\b',
    r'\brevolutionary\b',
    r'\bultimate\b',
    r'\bbest\b(?!\s+practice)',  # Allow "best practice"
    r'\bseamlessly\b',
    r'\beffortlessly\b',
    r'\bguaranteed?\b',
    r'\bnever fails?\b',
    r'\balways works?\b',
    r'\bflawless(ly)?\b',
    r'\bspectacular\b',
    r'\bfantastic\b',
    r'\bawesome\b',
    r'\boutstanding\b'
]

EXCESSIVE_EMOJIS = [
    r'🚀.*🚀',  # Multiple rockets
    r'✨',      # Sparkles
    r'💥',      # Explosion  
    r'🔥',      # Fire
    r'🚀.*🚀.*🚀'  # 3+ rockets
]

ABSOLUTE_STATEMENTS = [
    r'\b(will|shall)\s+(always|never)\b',
    r'\bguaranteed?\s+to\s+work\b',
    r'\bworks?\s+in\s+all\s+situations?\b',
    r'\bcompletely?\s+solve(s)?\s+all\b',
    r'\bperfect\s+solution\b'
]

SUGGESTED_REPLACEMENTS = {
    'perfectly': 'well',
    'perfect': 'good/improved',
    'amazing': 'useful/helpful',
    'incredible': 'useful',
    'revolutionary': 'new/updated',
    'ultimate': 'comprehensive',
    'seamlessly': 'easily',
    'guaranteed': 'typically/usually',
    'never fails': 'is reliable',
    'always works': 'generally works'
}

class DocumentationChecker:
    def __init__(self):
        self.violations = []
        
    def check_file(self, filepath: Path) -> List[Dict]:
        """Check a single file for policy violations."""
        violations = []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                # Check banned words
                for pattern in BANNED_WORDS:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        violations.append({
                            'file': str(filepath),
                            'line': line_num,
                            'type': 'banned_word',
                            'text': match.group(),
                            'suggestion': SUGGESTED_REPLACEMENTS.get(match.group().lower(), 'use more modest language'),
                            'context': line.strip()
                        })
                
                # Check excessive emojis
                for pattern in EXCESSIVE_EMOJIS:
                    if re.search(pattern, line):
                        violations.append({
                            'file': str(filepath),
                            'line': line_num,
                            'type': 'excessive_emoji',
                            'text': 'emoji overuse',
                            'suggestion': 'limit emojis, max 1 rocket per document',
                            'context': line.strip()
                        })
                
                # Check absolute statements
                for pattern in ABSOLUTE_STATEMENTS:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        violations.append({
                            'file': str(filepath),
                            'line': line_num,
                            'type': 'absolute_statement',
                            'text': match.group(),
                            'suggestion': 'use qualifiers like "should", "typically", "generally"',
                            'context': line.strip()
                        })
                        
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            
        return violations
    
    def check_files(self, filepaths: List[Path]) -> Dict:
        """Check multiple files and return summary."""
        all_violations = []
        files_checked = 0
        
        for filepath in filepaths:
            if filepath.suffix in ['.md', '.py', '.rst', '.txt']:
                violations = self.check_file(filepath)
                all_violations.extend(violations)
                files_checked += 1
                
        return {
            'total_violations': len(all_violations),
            'files_checked': files_checked,
            'violations': all_violations
        }
    
    def print_results(self, results: Dict):
        """Print formatted results."""
        violations = results['violations']
        
        if not violations:
            print("✅ No documentation policy violations found!")
            print(f"📁 Checked {results['files_checked']} files")
            return True
            
        print(f"❌ Found {len(violations)} documentation policy violations:")
        print(f"📁 Checked {results['files_checked']} files\n")
        
        # Group by file
        by_file = {}
        for v in violations:
            filepath = v['file']
            if filepath not in by_file:
                by_file[filepath] = []
            by_file[filepath].append(v)
            
        for filepath, file_violations in by_file.items():
            print(f"📄 {filepath}:")
            for v in file_violations:
                print(f"   Line {v['line']}: {v['type'].upper()}")
                print(f"   Found: '{v['text']}'")
                print(f"   Suggestion: {v['suggestion']}")
                print(f"   Context: {v['context']}")
                print()
                
        return False

def find_documentation_files(root_dir: Path) -> List[Path]:
    """Find all documentation files in the repository."""
    patterns = ['*.md', '*.rst', '*.txt']
    files = []
    
    for pattern in patterns:
        files.extend(root_dir.rglob(pattern))
    
    # Also check Python files for docstrings
    files.extend(root_dir.rglob('*.py'))
    
    # Exclude some directories
    excluded_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 'venv', 'env'}
    files = [f for f in files if not any(exc in f.parts for exc in excluded_dirs)]
    
    return files

def main():
    checker = DocumentationChecker()
    
    if len(sys.argv) > 1:
        # Check specific files
        filepaths = [Path(f) for f in sys.argv[1:]]
    else:
        # Check all documentation files
        root_dir = Path.cwd()
        filepaths = find_documentation_files(root_dir)
        
    results = checker.check_files(filepaths)
    success = checker.print_results(results)
    
    # Exit with error code if violations found (useful for CI/CD)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
