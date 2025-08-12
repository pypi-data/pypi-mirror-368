"""
Body Module - Data Containers
=============================

The `Body` module in JIPSO represents the **raw content or data** that AI is expected to reason about.

While the `Mind` layer performs thinking (e.g., AI model inference), the `Body` layer simply **holds the data** —
whether it's a text passage, an audio clip, an image, or a video — without modifying or interpreting it.

Philosophy:
-----------
JIPSO separates the representation of data (`Body`) from the process of reasoning (`Mind`).
This clean division allows for:
- Transparent orchestration pipelines
- Swappable components
- Consistent logging, tracking, and comparison of inputs/outputs

Supported Modalities:
---------------------
- `Text`: Plain or formatted text
- `Audio`: Raw or encoded audio files
- `Image`: Any visual content (e.g., PNG, JPG)
- `Video`: Time-based multimedia files

Responsibilities:
-----------------
- **Store** input/output content
- **Tag** modality-specific metadata (e.g., MIME type, encoding)
- **Pass through** the orchestration layer without transformation
- Ensure data is **AI-ready**, but not AI-processed
"""
