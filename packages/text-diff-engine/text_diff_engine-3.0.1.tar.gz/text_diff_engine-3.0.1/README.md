# text-diff-engine

A Python wrapper for the [Text Diff Engine with block moves API](https://www.formamind.com/en/diffEngine). This package provides an easy-to-use interface to compare two versions of text and highlight differences such as added, deleted, and moved blocks.

## Installation

Since this package is private and part of your Django repository, you can install it locally:

```bash
pip install text-diff-engine
```

## Usage

### Initializing the Client

Import the `TextDiffEngine` class and initialize it with your API key:

```python
from text_diff_engine import TextDiffEngine

# Replace 'YOUR_API_KEY' with your actual API key.
diff_engine = TextDiffEngine(api_key='YOUR_API_KEY')
```

### Comparing Texts

Use the `compare` method to compare an original text with an updated text. Choose the output format (`json` or `html`):

```python
old_text = "The quick brown fox jumps over the lazy dog."
new_text = "The quick red fox jumped over the sleeping dog."

# Compare the texts and get the result in JSON format.
result_json = diff_engine.compare(old_text, new_text, output_format="json")
print(result_json)

# Compare the texts and get the result in HTML format.
result_html = diff_engine.compare(old_text, new_text, output_format="html")
print(result_html)
```

### Return Structure

The `compare` method returns a dict object with two main sections:
- **`old_diff`**: Represents the differences in the old text.
- **`new_diff`**: Represents the differences in the new text.

Additional metadata:
- **`identical`**: Boolean indicating if the texts are identical.
- **`tokens_left`**: Number of API tokens remaining.

Like so:
```json
{
  "old_diff": [...],
  "new_diff": [...],
  "identical": false,
  "tokens_left": 467
}
```

#### HTML diff output structure

```html
<span class='deleted'>...</span> <!-- Marks removed text (old_diff) -->
<span class='added'>...</span> <!-- Marks newly added text (new_diff) -->
<span class='move-from-block' id='move-from-X'>...</span> <!-- Marks moved text origin (old_diff) -->
<span class='move-to-block' id='move-to-X'>...</span> <!-- Marks moved text destination (new_diff) -->
<span data-identifier='X'>...</span> <!-- Marks unchanged segments (for scroll sync) -->
```

#### JSON diff output structure

```json
{ "type": "DELETED", "text": "..." }  // Marks removed text (old_diff)
{ "type": "ADDED", "text": "..." }    // Marks newly added text (new_diff)
{ "type": "MOVE-FROM", "move_id": X, "blocks": [...] }  // Marks moved text origin (old_diff)
{ "type": "MOVE-TO", "move_id": X, "blocks": [...] }    // Marks moved text destination (new_diff)
{ "type": "UNCHANGED", "text": "...", "identifier": X} // Marks unchanged segments (for scroll sync)
```

### Example output of the `compare` method

```json
{
  "old_diff": [
    { "move_id": 2, "type": "MOVE-FROM", "blocks": [
      { "type": "UNCHANGED", "text": "The golden " },
      { "type": "DELETED", "text": "sunlight" },
      { "type": "UNCHANGED", "text": " filtered through the trees" },
      { "type": "DELETED", "text": ". Casting"},
      { "type": "UNCHANGED", "text": " long shadows on the quiet street." }
    ] },
    { "type": "DELETED", "text": " " },
    { "type": "UNCHANGED", "text": "A cat slept near the window.", "identifier": 1 },
    { "type": "DELETED", "text": "The clock ticked steadily." },
    { "type": "UNCHANGED", "text": "Wind moved the curtains slightly, making them sway gently.", "identifier": 2 }
  ],
  "new_diff": [
    { "type": "UNCHANGED", "text": "A cat slept near the window.", "identifier": 1 },
    { "type": "UNCHANGED", "text": "Wind moved the curtains slightly, making them sway gently.", "identifier": 2 },
    { "type": "ADDED", "text": " " },
    { "type": "ADDED", "text": "The clock ticked steadily." },
    { "move_id": 2, "type": "MOVE-TO", "blocks": [
      { "type": "UNCHANGED", "text": "The golden " },
      { "type": "ADDED", "text": "rays" },
      { "type": "UNCHANGED", "text": " filtered through the trees"},
      { "type": "ADDED", "text": ", casting" },
      { "type": "UNCHANGED", "text": " long shadows on the quiet street." }
    ] }
  ],
  "identical": false,
  "tokens_left": 467
}
```

For further details, refer to the [Formamind Text Diff Engine documentation](https://www.formamind.com/en/diffEngine).

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For support, contact your internal development team or email at contact@formamind.com

