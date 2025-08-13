# TransparentMeta

[TransparentMeta](https://github.com/Transparent-Audio/transparentmeta) is the standard for compliance with AI audio transparency
legislation with metadata.

It's an open-source Python library developed by 
[Transparent Audio](https://www.transparentaudio.ai/). It allows users to add and verify cryptographically signed metadata in 
audio files. 

TransparentMeta helps generative AI companies comply with AI transparency laws, 
such as the *EU AI Act* and the *California AI Transparency Act*. By using cryptographic signing, robust file 
validation, and a modular SDK, users can label AI-generated audio 
content with transparent metadata simply and effectively.

## 🗣️ Community

- 🗨️ Join the [Transparent Audio Discord](https://discord.gg/pE9yRt7b9N) for real-time support and 
  discussion
- 🐛 If you discover bugs, please report them in the [GitHub issue tracker](https://github.com/Transparent-Audio/transparentmeta/issues)

## 🚀 Features

- Add cryptographically signed transparency metadata to MP3 and WAV files  
- Read and verify metadata to detect AI-generated audio  
- Key pair generation and signature verification built-in  
- Simple Python SDK for easy integration in your application
- 100% test coverage via unit and integration tests  

## 🔧 Use Cases

- Speech synthesis and voice cloning labeling output with transparency metadata  
- Generative AI music and sound effects tagging output with metadata and attribution  
- Compliance with EU AI Act & California AI Transparency Act  
- Building trusted pipelines with verifiable audio provenance  

## 📦 Installation

### From PyPi
Installing TransparentMeta from PyPI using pip is the recommended way:

```bash
pip install transparentmeta
```

### From Source
Or, you can install directly from the repository. This project uses 
[Poetry](https://python-poetry.org/) for dependency management. You’ll need to 
install Poetry first.

To install TransparentMeta from source code run:
```bash
git clone https://github.com/Transparent-Audio/transparentmeta.git
cd transparentmeta
make install
```

To install in development mode, after cloning the repository, run:
```bash
make install_dev
```

`make install` and `make install_dev` wrap relevant Poetry commands. They can 
be found along with other useful commands in the [Makefile](Makefile).


## 📚 Getting Started 
- Check the [getting started guide](https://transparentmeta.readthedocs.io/en/stable/learning/getting_started.html) in the documentation to pick up the 
  basic functionality of TransparentMeta in 5 minutes
- Check the `/examples` folder for quick usage examples. Start by reading the 
[README.md file](examples/README.md) inside the folder
- For a more thorough introduction to TransparentMeta, check the [tutorials](https://transparentmeta.readthedocs.io/en/stable/learning/tutorials.html) 
  in the documentation
- If you're a visual learner, watch the video
  tutorials on [YouTube](https://www.youtube.com/playlist?list=PL-a9rWjvfqdRqYS1E6oJlC39TOz_N3yDJ)

## 📖 Documentation 
Check full documentation on [Read the Docs](https://transparentmeta.readthedocs.io/en/stable/).

## 📂 Project Structure 
- `transparentmeta/` - Main library code
- `examples/` - Example scripts and usage
- `tests/` - Unit and integration tests
- `docs/` - Sphinx documentation
- `Makefile` - Useful commands for development

## 🧩 Dependencies 
TransparentMeta relies on the following core libraries:
- [mutagen](https://mutagen.readthedocs.io/en/latest/) – for reading and writing audio metadata (MP3, WAV, etc.)
- [cryptography](https://cryptography.io/en/latest/) – for generating and verifying digital signatures 
- [pydantic](https://docs.pydantic.dev/latest/) – for data validation and 
  data structures

You can find all dependencies in `pyproject.toml`.

## ✅ Running tests and quality checks 
To run tests, linting, and type checks, use:
```bash
make checklist
```

## 🐍 Python version 
TransparentMeta supports Python 3.12 and above. Ensure you have a compatible 
version installed.

## 📝 License 
This project is licensed under GPL-3.0 or later. See the [LICENSE](LICENSE) 
file for details.

## ✍️ Contribution
While we don’t currently accept contributions, we plan to set up the 
necessary infrastructure to do so in the future. If you’re interested in contributing, please contact us.

## 📬 Contact 
If you have any pressing questions or issues, please 
write to Transparent Audio's CTO Valerio Velardo at valerio@transparentaudio.ai.

The best way to get support or suggest requests is by joining the [Transparent Audio Discord](https://discord.gg/pE9yRt7b9N)


