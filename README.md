# Textual Narrative Mapping

Textual Narrative Mapping compares stories, historical events, and public narratives by mapping their actors, roles, events, goals, and causal relationships. An orchestrated LLM pipeline builds and aligns narrative graphs, then highlights where an analogy is structurally strong, merely surface-similar, or potentially misleading.

The system separates four signals:

- **Structural alignment** — role, event, goal, causal, and outcome correspondence.
- **Context similarity** — thematic and semantic proximity.
- **Prototypical pull** — how readily both narratives feel like instances of the same familiar pattern.
- **False-equivalence risk** — whether important causal, power, scale, or role differences weaken the comparison.

## Main workflow

1. Choose a bundled narrative pair or write your own, then select the reasoning depth in Analysis Setup.
2. Run the GPT-5.4 orchestration pipeline.
3. Inspect side-by-side role graphs and cross-narrative mappings.
4. Review event alignment and false-equivalence warnings.
5. Download the complete structured analysis as JSON.

## LLM orchestration

The application uses a fixed and inspectable pipeline rather than an open-ended autonomous loop:

1. **Parallel narrative extractors** convert both texts into validated Pydantic graph schemas.
2. **Deterministic normalisation** removes invalid graph references and standardises the representation.
3. **Embedding-assisted candidate generation** proposes likely element correspondences.
4. **Structural mapper** evaluates roles, temporal position, power, agency, and causal neighbourhoods.
5. **Counter-analogy critic** searches for power asymmetry, causal mismatch, role inversion, scale mismatch, outcome cherry-picking, and omitted actors.
6. **Final judge** adjudicates the mapping and critic output.
7. **Deterministic scoring** calculates the weighted structural score and combined false-equivalence risk.

All orchestration agents use `gpt-5.4`. Semantic candidate generation uses `text-embedding-3-small`.

## Tech stack

- Python 3.11 or 3.12
- Streamlit
- OpenAI Responses API with Structured Outputs
- GPT-5.4
- OpenAI embeddings
- Pydantic v2
- NetworkX
- Plotly
- Pytest

## Project structure

```text
narrative_dna/
├── app.py
├── requirements.txt
├── .env.example
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── examples/
│   └── examples.json
├── prompts/
│   ├── extract_narrative.txt
│   ├── map_structures.txt
│   ├── critique_analogy.txt
│   └── judge_analogy.txt
├── narrative_dna/
│   ├── schemas.py
│   ├── openai_service.py
│   ├── normalisation.py
│   ├── similarity.py
│   ├── scoring.py
│   ├── orchestration.py
│   ├── visualisation.py
│   ├── styles.py
│   └── utils.py
└── tests/
```

## Run in VS Code on Windows

Use Python 3.12 for the cleanest dependency compatibility.

### 1. Open the project

Open the extracted `narrative_dna` folder in VS Code.

### 2. Create a virtual environment

In the VS Code terminal:

```powershell
py -3.12 -m venv venv
```

Activate it in PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

For Command Prompt:

```cmd
venv\Scripts\activate.bat
```

If PowerShell blocks activation for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure the OpenAI key

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder:

```env
OPENAI_API_KEY=your_real_key_here
```

The key is intentionally not displayed in the Streamlit sidebar.

### 5. Start the application

```powershell
python -m streamlit run app.py
```

Streamlit normally opens the application at:

```text
http://localhost:8501
```

Stop it with `Ctrl+C` in the terminal.

## Run tests

```powershell
python -m pytest -q
```

The tests cover deterministic scoring, graph sanitisation, and bundled example validation. They do not call the OpenAI API.

## Configuration

The orchestration model is fixed in `app.py`:

```python
MODEL = "gpt-5.4"
```

The reasoning selector maps:

- **Balanced** to `medium` reasoning effort
- **Deep** to `high` reasoning effort

Both extraction agents run in parallel. Extraction uses low reasoning effort because its primary job is schema-grounded information extraction.

## Output

The downloadable JSON includes:

- source and target narrative graphs;
- candidate element pairs;
- selected structural mappings;
- relation correspondences;
- critic warnings;
- final judgement;
- calculated scores;
- model and runtime metadata.

## Scope

Textual Narrative Mapping analyses the structure of the text supplied by the user. It does not independently verify whether a historical or political account is factually complete.
