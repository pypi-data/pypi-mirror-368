## Pogodoc Python SDK

The Pogodoc Python SDK enables developers to seamlessly generate documents and manage templates using Pogodoc’s API.

### Installation

To install the Python SDK, just execute the following command

```bash
$ pip install pogodoc
```

### Setup

To use the SDK you will need an API key which can be obtained from the [Pogodoc Dashboard](https://app.pogodoc.com)

### Example

```py
from pogodoc import PogodocClient, RenderConfig

def main():
    client = PogodocClient(
        token="YOUR_POGODOC_API_TOKEN",
    )

    response = client.generate_document(
        template_id = "your-template-id",
        data = {"name": "John Doe"},
        render_config = RenderConfig(
            type = "html",
            target = "pdf",
            format_opts = InitializeRenderJobRequestFormatOpts(
                from_page = 1,
            ),
        ),
    )

    print("Generated document url:\n", response.output.data.url)

if __name__ == "__main__":
    main()

```

### License

MIT License
