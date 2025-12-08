# GeneStudio User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [File & Sequence Tab](#file--sequence-tab)
3. [Basic Operations Tab](#basic-operations-tab)
4. [Translation Tab](#translation-tab)
5. [Pattern Matching Tab](#pattern-matching-tab)
6. [Suffix Array Tab](#suffix-array-tab)
7. [Overlap Graph Tab](#overlap-graph-tab)
8. [Approximate Matching Tab](#approximate-matching-tab)
9. [Tips & Troubleshooting](#tips--troubleshooting)

---

## Getting Started

### Launching the Application

1. **Activate virtual environment**:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

2. **Run GeneStudio**:
   ```bash
   python main.py
   ```

3. The application window will open with 7 tabs for different analysis tools.

---

## File & Sequence Tab

### Purpose
Load FASTA files and view DNA sequences.

### How to Use

1. **Click "Load FASTA File" button**
2. **Select a FASTA file** from your computer
   - Sample file provided: `data/sample.fasta`
3. **Select a sequence** from the dropdown menu if multiple sequences are loaded
4. **View sequence details** in the text area

### Input Format
- **FASTA files** (`.fasta` or `.fa` extension)
- Must contain valid DNA sequences (only A, T, C, G characters)
- Example format:
  ```
  >sequence_header
  ATCGATCGATCG
  >another_sequence
  GCTAGCTAGCTA
  ```

### Expected Output
- **Sequence count**: Number of sequences loaded
- **Header**: Sequence identifier
- **Length**: Number of base pairs
- **Sequence**: Full DNA sequence displayed

### Example
**Input**: Load `data/sample.fasta`
**Output**:
```
Header: example_sequence
Length: 240 bp

Sequence:
ATGCGATCGATCGATCG...
```

---

## Basic Operations Tab

### Purpose
Perform fundamental DNA sequence transformations and calculate GC content.

### Features

#### 1. GC Percentage
**What it does**: Calculates the percentage of Guanine (G) and Cytosine (C) bases in the sequence.

**How to use**:
1. Load a sequence first
2. Click "GC Percentage" button

**Expected Output**:
```
GC%: 50.00%
```

**Hint**: GC-rich sequences (>50%) are often found in gene promoter regions.

---

#### 2. Reverse
**What it does**: Reverses the sequence from 3' to 5'.

**How to use**:
1. Load a sequence
2. Click "Reverse" button

**Input**: `ATCG`
**Output**: `GCTA`

---

#### 3. Complement
**What it does**: Replaces each base with its complement (A↔T, C↔G).

**How to use**:
1. Load a sequence
2. Click "Complement" button

**Input**: `ATCG`
**Output**: `TAGC`

**Hint**: Useful for finding the complementary DNA strand.

---

#### 4. Reverse Complement
**What it does**: Combines reverse and complement operations (equivalent to the opposite strand).

**How to use**:
1. Load a sequence
2. Click "Reverse Complement" button

**Input**: `ATCG`
**Output**: `CGAT`

**Hint**: This represents the sequence on the opposite DNA strand in 5' to 3' direction.

---

## Translation Tab

### Purpose
Translate DNA sequences into amino acid sequences using the standard genetic code.

### How to Use

1. **Load a sequence** (must be loaded first)
2. **Click "Translate to Amino Acids" button**
3. **View amino acid sequence** in the result area

### Input Requirements
- DNA sequence (A, T, C, G)
- Sequence is read in triplets (codons)
- Incomplete codons at the end are ignored

### Expected Output
- **Amino acid sequence** using single-letter codes
- `*` represents stop codons (TAA, TAG, TGA)
- `X` represents unknown/invalid codons

### Example
**Input DNA**: `ATGATGATGATG`
**Output**: `MMMM`

**Input DNA**: `ATGTAA`
**Output**: `M*`

### Codon Table Reference
- `ATG` → M (Methionine, start codon)
- `TAA`, `TAG`, `TGA` → * (Stop codons)
- `GCT`, `GCC`, `GCA`, `GCG` → A (Alanine)
- etc.

**Hint**: Use sequences that are multiples of 3 for complete translation.

---

## Pattern Matching Tab

### Purpose
Find exact occurrences of a DNA pattern within the loaded sequence using Boyer-Moore algorithm.

### How to Use

1. **Load a sequence**
2. **Enter a pattern** in the "Pattern" field (e.g., `ATCG`)
3. **Choose algorithm**:
   - Click "Boyer-Moore (Bad Char)" for bad character rule
   - Click "Boyer-Moore (Good Suffix)" for good suffix rule (bonus)
4. **View results**: Match positions and count

### Input
- **Pattern**: DNA sequence to search for (e.g., `ATCG`, `GC`, `ACGT`)
- Pattern is case-insensitive (automatically converted to uppercase)

### Expected Output
```
Found 5 match(es) at positions: [0, 10, 20, 30, 40]
```

### Example
**Sequence**: `ATCGATCGATCG`
**Pattern**: `ATCG`
**Output**: `Found 3 match(es) at positions: [0, 4, 8]`

### Hints
- **Short patterns** (2-4 bases) will find many matches
- **Longer patterns** (8+ bases) are more specific
- **Both algorithms** should return the same positions (different performance)
- **Position 0** means the pattern starts at the beginning of the sequence

---

## Suffix Array Tab

### Purpose
Build a suffix array and inverse suffix array for the loaded sequence.

### How to Use

1. **Load a sequence**
2. **Click "Build Suffix Array" button**
3. **View results**: First 20 elements of suffix array and inverse suffix array

### What is a Suffix Array?
A suffix array is an array of integers representing the starting positions of all suffixes of a string, sorted in lexicographical order.

### Expected Output
```
Suffix Array (first 20): [15, 7, 3, 11, 0, 8, 4, 12, 1, 9, 5, 13, 2, 10, 6, 14, ...]
Inverse Suffix Array (first 20): [4, 8, 12, 2, 6, 10, 14, 1, 5, 9, 13, 3, 7, 11, 15, ...]
```

### Example
**Sequence**: `BANANA`
**Suffix Array**: `[5, 3, 1, 0, 4, 2]`
- Position 5: `A`
- Position 3: `ANA`
- Position 1: `ANANA`
- Position 0: `BANANA`
- Position 4: `NA`
- Position 2: `NANA`

### Hints
- **Longer sequences** will show only first 20 elements
- **Suffix arrays** enable efficient pattern searching
- **Inverse suffix array** satisfies: `ISA[SA[i]] = i`

---

## Overlap Graph Tab

### Purpose
Construct an overlap graph from multiple loaded sequences, showing which sequences have suffix-prefix overlaps.

### How to Use

1. **Load a FASTA file with multiple sequences** (at least 2)
2. **Enter minimum overlap length** (e.g., `3`)
3. **Click "Build Graph" button**
4. **View adjacency list**: Shows which sequences overlap

### Input
- **Multiple sequences** (minimum 2 required)
- **Minimum overlap**: Integer value (e.g., 1, 3, 5)

### Expected Output
```
Overlap Graph (min overlap: 3):
Seq 0 -> [1, 2]
Seq 1 -> [2]
Seq 3 -> [0]
```

This means:
- Sequence 0's suffix overlaps with sequences 1 and 2's prefixes
- Sequence 1's suffix overlaps with sequence 2's prefix
- Sequence 3's suffix overlaps with sequence 0's prefix

### Example
**Sequences**:
- Seq 0: `ATGATG`
- Seq 1: `ATGATG`
- Seq 2: `GATGAT`

**Min overlap**: `3`

**Output**:
```
Seq 0 -> [1, 2]
Seq 1 -> [2]
```

### Hints
- **Lower minimum overlap** = more edges in graph
- **Higher minimum overlap** = fewer, more significant edges
- **No overlaps found** = increase sequence count or decrease minimum overlap
- **Useful for** sequence assembly and genome reconstruction

---

## Approximate Matching Tab

### Purpose
Find approximate matches of a pattern allowing for mismatches (Hamming distance) or insertions/deletions (edit distance).

### How to Use

1. **Load a sequence**
2. **Enter a pattern** (e.g., `ATCG`)
3. **Enter max distance** (e.g., `1` or `2`)
4. **Choose method**:
   - Click "Hamming Distance" for substitution-only matching
   - Click "Edit Distance" for insertions/deletions/substitutions
5. **View results**: Positions where pattern matches within threshold

### Input
- **Pattern**: DNA sequence to search for
- **Max Distance**: Maximum allowed differences (typically 1-3)

### Expected Output
```
Found 8 match(es) at positions: [0, 5, 10, 15, 20, 25, 30, 35]
```

---

### Hamming Distance

**What it does**: Counts positions where characters differ (strings must be same length).

**Example**:
- Pattern: `ATCG`
- Substring: `ATGG`
- Hamming distance: `1` (one mismatch at position 2)

**Use case**: Find similar sequences with point mutations.

**Hint**: Pattern and substring must be **same length**.

---

### Edit Distance

**What it does**: Minimum number of insertions, deletions, or substitutions to transform one string into another.

**Example**:
- Pattern: `ATCG`
- Substring: `ATG`
- Edit distance: `1` (delete C)

**Use case**: Find sequences with insertions, deletions, or substitutions.

**Hint**: Works with **different length** strings.

---

### Distance Threshold Examples

**Max Distance = 0**: Exact matching only
**Max Distance = 1**: Allow 1 mismatch/edit
**Max Distance = 2**: Allow 2 mismatches/edits

**Recommendation**: Start with distance 1-2 for meaningful results.

---

## Tips & Troubleshooting

### General Tips

1. **Always load a sequence first** before using other features
2. **Use the sample file** (`data/sample.fasta`) to test features
3. **Pattern matching** is case-insensitive (automatically converted to uppercase)
4. **Multiple sequences** are required for overlap graph
5. **Longer sequences** may take more time for approximate matching

### Common Issues

#### "No sequence loaded"
**Solution**: Go to "File & Sequence" tab and load a FASTA file first.

#### "Pattern cannot be empty"
**Solution**: Enter a DNA pattern in the input field before searching.

#### "Need at least 2 sequences to build overlap graph"
**Solution**: Load a FASTA file containing multiple sequences (use `data/sample.fasta`).

#### "Invalid DNA sequence"
**Solution**: Ensure your FASTA file contains only A, T, C, G characters (case-insensitive).

#### "Strings must have equal length for Hamming distance"
**Solution**: Use Edit Distance instead, or ensure pattern length matches the sequence regions you're searching.

### Performance Notes

- **Basic operations**: Very fast, even for long sequences
- **Pattern matching**: Fast with Boyer-Moore algorithm
- **Suffix array**: Fast for sequences up to 200k bases
- **Edit distance**: Slower for very long sequences (recommended for sequences <10k bases with approximate matching)

### Best Practices

1. **Start simple**: Test with short sequences and patterns first
2. **Use appropriate algorithms**: 
   - Exact matches → Boyer-Moore
   - Approximate matches → Hamming (same length) or Edit Distance (any length)
3. **Overlap graphs**: Use minimum overlap of 3-5 for meaningful results
4. **Translation**: Ensure sequence length is multiple of 3 for complete codons

---

## Example Workflow

### Complete Analysis Example

1. **Load data**:
   - Go to "File & Sequence" tab
   - Load `data/sample.fasta`
   - Select "example_sequence"

2. **Basic analysis**:
   - Go to "Basic Operations" tab
   - Click "GC Percentage" → See GC content
   - Click "Reverse Complement" → See opposite strand

3. **Translation**:
   - Go to "Translation" tab
   - Click "Translate to Amino Acids" → See protein sequence

4. **Pattern search**:
   - Go to "Pattern Matching" tab
   - Enter pattern: `ATCG`
   - Click "Boyer-Moore (Bad Char)" → Find exact matches

5. **Approximate search**:
   - Go to "Approximate Matching" tab
   - Enter pattern: `ATCG`
   - Enter max distance: `1`
   - Click "Edit Distance" → Find similar matches

6. **Overlap analysis**:
   - Load `data/sample.fasta` (has multiple sequences)
   - Go to "Overlap Graph" tab
   - Enter minimum overlap: `3`
   - Click "Build Graph" → See sequence overlaps

---

## Quick Reference Card

| Feature | Tab | Input | Output |
|---------|-----|-------|--------|
| Load sequences | File & Sequence | FASTA file | Sequence display |
| GC% | Basic Operations | Loaded sequence | Percentage value |
| Reverse | Basic Operations | Loaded sequence | Reversed sequence |
| Complement | Basic Operations | Loaded sequence | Complement sequence |
| Reverse Complement | Basic Operations | Loaded sequence | Rev-comp sequence |
| Translation | Translation | Loaded sequence | Amino acid sequence |
| Boyer-Moore | Pattern Matching | Pattern string | Match positions |
| Suffix Array | Suffix Array | Loaded sequence | SA and ISA arrays |
| Overlap Graph | Overlap Graph | Min overlap value | Adjacency list |
| Hamming Distance | Approximate Matching | Pattern + threshold | Match positions |
| Edit Distance | Approximate Matching | Pattern + threshold | Match positions |

---

## Additional Resources

### Understanding the Algorithms

- **Boyer-Moore**: Efficient pattern matching that skips characters
- **Suffix Array**: Enables fast substring searches
- **Hamming Distance**: Counts mismatches (substitutions only)
- **Edit Distance**: Counts all types of edits (insertions, deletions, substitutions)
- **Overlap Graph**: Shows sequence relationships for assembly

### Sample Data

The `data/sample.fasta` file contains:
- `example_sequence`: Long sequence for general testing
- `short_sequence_1/2/3`: Short sequences with overlaps for graph testing
- `gc_rich_sequence`: High GC content sequence
- `at_rich_sequence`: High AT content sequence
- `pattern_test_sequence`: Repeating pattern for pattern matching tests

---

**Enjoy using GeneStudio for your DNA sequence analysis!**
