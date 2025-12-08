# 🧬 GeneStudio

### A Modern GUI Toolkit for DNA Sequence Analysis & Bioinformatics Algorithms

GeneStudio is a desktop application built in Python that brings powerful DNA sequence analysis tools and classical string-matching algorithms into a clean, intuitive GUI.

It is designed for students, researchers, and developers who need to explore DNA sequences using both basic biological operations and advanced computational algorithms — without requiring deep bioinformatics knowledge.

---

## 🚀 Features

### 🔹 **Sequence Processing**
- Load and parse FASTA files
- GC% calculation
- Reverse, Complement, Reverse-Complement
- DNA → Amino Acid Translation using a codon table
- Scrollable sequence viewer with colored highlighting

### 🔹 **Exact Pattern Matching**
- Boyer–Moore (Bad Character Rule)
- Boyer–Moore (Good Suffix Rule)
- Suffix Array construction
- Inverse Suffix Array
- Exact search via suffix array
- Visual highlighting of match positions

### 🔹 **Approximate Matching**
- Hamming Distance search
- Edit Distance (Dynamic Programming)
- Threshold-based approximate matching

### 🔹 **Graph Algorithms**
- Overlap Graph construction from multiple FASTA sequences
- Adjustable minimum overlap length
- Adjacency list view + optional graphical visualization

---

## 🖥️ GUI Overview (Screenshots)
> (Add your screenshots here later)

```

📂 File           🔍 Pattern Matching
🧬 Sequence       🎯 Approximate Matching
🧪 Operations     🕸️ Overlap Graph

```

---

## 🧩 Algorithms Implemented

| Category | Algorithms |
|----------|------------|
| Sequence Ops | GC%, Reverse, Complement, Reverse-Complement |
| Translation | DNA → Amino Acids |
| Exact Matching | Boyer–Moore (Bad Char), Boyer–Moore (Good Suffix), Suffix Array, Inverse SA |
| Approx Matching | Hamming Distance, Edit Distance (DP) |
| Graphs | Overlap Graph |

All algorithms are implemented from scratch — no external bioinformatics libraries.

---

## 🏗️ Project Structure

```

GeneStudio/
│
├── gui/                     # GUI components
├── algorithms/              # Core algorithms
├── assets/                  # Icons & images
├── main.py                  # Application entry point
└── README.md

````

---

## 📦 Installation

### 1. Clone the repository:
```bash
git clone https://github.com/<your-username>/GeneStudio.git
cd GeneStudio
````

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Run the app:

```bash
python main.py
```

---

## ⚙️ Technologies Used

* **Python 3.10+**
* **PyQt5 / PySide6** (GUI)
* **NetworkX** (optional graph visualization)
* **Standard Python algorithms (no heavy external libraries)**

---

## 📘 Documentation

A full **Software Requirements Specification (SRS)** is included, covering:

* System statement
* Functional requirements
* Non-functional requirements
* Formal algorithmic properties

---

## 🎯 Purpose of the Project

GeneStudio is an educational yet powerful tool that demonstrates how classical data-structure and string-matching algorithms can be applied to real biological sequences.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

## 📄 License

This project is licensed under the MIT License.

---

```