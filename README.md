# tool-flow
-
# 🔧 Natural Language CLI Generator

Convert simple English commands into powerful CLI commands like `ffmpeg`,`pdftk`, `imagemagick`.

---

## 🚀 Overview

This project allows users to write commands in plain English:

```bash
>> compress input.pdf to output.pdf
```

And automatically converts them into:

```bash
pdftk input.pdf output output.pdf compress
```

---

## 🧠 Architecture

The system follows a compiler-like pipeline:

```
User Input
   ↓
Intent Matcher
   ↓
Parser
   ↓
Intermediate Representation (IR)
   ↓
Tool Resolver
   ↓
Command Builder
   ↓
Final CLI Command
```

---

## 📁 Project Structure

```
core/
 ├── matcher.py      # Intent detection
 ├── parser.py       # Parameter extraction
 ├── ir_builder.py   # Normalized IR
 ├── resolver.py     # Tool selection
 └── builder.py      # Command generation

intents/
 ├── pdf/
 ├── video/
 └── image/

tools/
 ├── pdf/
 ├── video/
 └── image/

main.py              # Entry point
```

---

## ⚙️ How It Works

### 1. Intent Matching

Finds the best matching intent using keywords and scoring.

### 2. Parsing

Extracts:

* file names
* timestamps
* ranges
* resolutions

### 3. IR (Intermediate Representation)

Standardizes parameters across all tools.

### 4. Tool Resolution

Chooses the best CLI tool (`ffmpeg`, `pdftk`, etc.).

### 5. Command Building

Fills templates from tool JSON configs.

---

## 🧩 Example

### Input:

```
trim video.mp4 from 00:10 to 00:20
```

### Output:

```
ffmpeg -i video.mp4 -ss 00:10 -to 00:20 output.mp4
```

---

## 📦 Adding New Features

### Add New Intent

Create a JSON file in `intents/<domain>/`

```json
{
  "name": "compress_pdf",
  "keywords": ["compress", "reduce size"],
  "file_type": "pdf",
  "parameters": {
    "input_file": {"type": "file"},
    "output_file": {"type": "file"}
  }
}
```

---

### Add New Tool

Create a JSON file in `tools/<domain>/`

```json
{
  "tool": "pdftk",
  "intents": {
    "compress_pdf": {
      "template": "pdftk {input_file} output {output_file} compress"
    }
  }
}
```

---

## 🧪 Running the Project

```bash
python main.py
```

Then type:

```
>> compress file.pdf
```

---

## 🧠 Key Concepts

* Intent Recognition
* Rule-Based Parsing
* Intermediate Representation (IR)
* Template-Based Code Generation
* Plugin Architecture via JSON

---

## 🔮 Future Improvements

* Add more tools (ImageMagick, yt-dlp)
* Improve with confidence scoring
* Better parser and IR_Builder

---

## 🤝 Contributing

PRs are welcome. Add new intents, tools, or improve parsing.

---

## 📜 License

MIT License
