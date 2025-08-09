# Beets AI Sauce Plugin
*Because your tunes deserve a little extra flavor.*

Let artificial intelligence decipher and enhance the mysterious metadata of your music tracks.


## Who Needs This? (Definitely You)

- **You**: The person who once gazed at your MP3 folder and thought, "My beats need more AI jazz hands!"
- **Also You**: If you trust AI more than your friend who can't stop labeling everything "Track 1".
- **Definitely You**: If you own folders full of tracks from bootlegs, unknown rips, or suspect compilation albums.


## Features

- **Auto-Metadata Magic**: Automatically retrieve and correct track and album metadata using AI-generated suggestions.
- **Cleanup Crew**: Strip away unnecessary embellishments like "Free Download" in titles or SHOUTCAPS, giving your library a polished appearance.
- **Extensible System**: Leverage AI configurations and prompts custom tailored for your library needs.


## Installation

### Prerequisites
- **Beets**: Make sure you have Beets installed (`pip install beets`),
- **AI Service API Key**: Get an API key from your preferred AI service provider (e.g., OpenAI, Deepseek).
    - Any service that supports openAI endpoints should work.

### Plugin Setup

1. **Installation**: Obtain the sauce by installing the plugin via pip:
   ```bash
   pip install beets-aisauce
   ```
2. **Configuration**: Add the plugin to your Beets configuration file (`config.yaml`):
   ```yaml
    plugins: 
      - aisauce

    aisauce:
        providers:
            - id: openai
              model: gpt-4o
              api_key: YOUR_API_KEY_HERE
              api_base_url: https://api.openai.com/v1
    ```
3. Execute the Ai Sauce: Import your tracks through Beets to start receiving AI-enhanced metadata suggestions.


## Advanced Usage

- **Custom Rules**: Sometimes you have specific metadata correction rules that you want to apply. You can modify the default user and system prompts by adding a `source` to your configuration file:
    ```yaml
    aisauce:
        providers:
            - id: openai
              model: gpt-4o
              api_key: YOUR_API_KEY_HERE

        sources:
            - provider_id: openai
              user_prompt: '
                Additional rules:
                - Replace any occurrences of Vulgar or inappropriate words with "**sauced**".
                '
    ```
- Multiple sources can be defined allowing you to test different prompts or configurations for different types of music or metadata corrections and models.


## Contributing

Great ideas welcome! Especially if they include more puns. Open a PR or send us a message in a bottle (GitHub issues also work).

## License

This project is licensed under the MIT License—meaning you can do almost anything, but please don't sue us if the AI names your tracks "Untitled Jam 42."



## Development

The following sections are for developers who want to contribute to the project. Feel free to skip if you're just here for the AI sauce.

### Installation for Development

Clone the repository and install the package in editable mode:

```bash
git clone
pip install -e .[dev]
```

### Running Tests
To run the tests, you can use `pytest`. Make sure you have the necessary dependencies installed:

```bash
pytest .
```

### Running mypy locally

Running mypy local is a bit tricky due to the namespace packages used in this project. To run mypy, you need to specify the `--namespace-packages` and `--explicit-package-bases` flags.

```bash
mypy  --namespace-packages --explicit-package-bases .
```