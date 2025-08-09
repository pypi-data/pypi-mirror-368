cosyvoice2-eu
====================

Minimal, plug-and-play CosyVoice2 European inference CLI that downloads the model from Hugging Face and runs cross-lingual cloning. It bundles the required `cosyvoice` runtime and `matcha` module so you don't need the full upstream repo.

Currently supports French, with German support coming soon!

## Features

- **Easy Installation**: Simple `pip install cosyvoice2-eu` command
- **Cross-lingual Voice Cloning**: Clone voices across different European languages
- **French Support**: Currently supports French text-to-speech with voice cloning
- **German Support**: Coming soon!
- **Bundled Runtime**: No need to install the full upstream CosyVoice2 repository
- **Hugging Face Integration**: Automatic model downloading from Hugging Face

## License

This project is licensed under the Apache License 2.0. 

**Note**: This package includes vendored code from:
- [CosyVoice2](https://github.com/FunAudioLLM/CosyVoice2) (Apache 2.0)
- [Matcha-TTS](https://github.com/shivammathur/Matcha-TTS) (Apache 2.0)

All original licenses and attributions are preserved.

## Quick Start

1. **Install the package:**
   ```bash
   pip install cosyvoice2-eu
   ```

2. **Run voice cloning:**
   ```bash
   cosy2-eu \
     --text "Bonjour, je m'appelle Louis! J'aime manger une baguette." \
     --prompt macron.wav \
     --out out.wav
   ```

That's it! The first run will automatically download the model from Hugging Face.

## Installation

### From PyPI (Recommended)

```bash
pip install cosyvoice2-eu
```

### For enhanced English phonemization (optional):
```bash
pip install cosyvoice2-eu[piper]
```

**Note**: The `piper` optional dependency requires compilation tools and may fail in some environments (like Google Colab). The package will work without it, using the standard phonemizer as fallback.

If you are on Linux with GPU, ensure you install torch/torchaudio matching your CUDA and have `onnxruntime-gpu` available. If CPU-only, `onnxruntime` will be sufficient.

### Development Installation

```bash
cd standalone_infer
pip install -e .
```

## Usage

```bash
cosy2-eu \
  --text "Bonjour, je m'appelle Louis! J'aime manger une baguette." \
  --prompt macron.wav \
  --out out.wav
```

First run will download the model assets to `~/.cache/cosyvoice2-eu` (configurable via `--model-dir`).

Advanced options: `--setting`, `--llm-run-id`, `--flow-run-id`, `--hifigan-run-id`, `--final`, `--stream`, `--speed`, `--no-text-frontend`, `--repo-id`, `--no-hf`.




