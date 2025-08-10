---
title: Chattr
emoji: 💬
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
short_description: Chat with Characters
---

## **Chattr**: App part of the Chatacter Backend

### Environment Variables

The configuration of the server is done using environment variables:

| Name                       | Description                      | Required | Default Value                              |
|:---------------------------|:---------------------------------|:--------:|:-------------------------------------------|
| `MODEL__URL`               | OpenAI-compatible endpoint       |    ✘     | `https://api.groq.com/openai/v1`           |
| `MODEL__NAME`              | Model name to use for chat       |    ✘     | `llama3-70b-8192`                          |
| `MODEL__API_KEY`           | API key for model access         |    ✔     | `None`                                     |
| `MODEL__TEMPERATURE`       | Model temperature (0.0-1.0)      |    ✘     | `0.0`                                      |
| `SHORT_TERM_MEMORY__URL`   | Redis URL for memory store       |    ✘     | `redis://localhost:6379`                   |
| `VECTOR_DATABASE__NAME`    | Vector database collection name  |    ✘     | `chattr`                                   |
| `VOICE_GENERATOR_MCP__URL` | MCP service for audio generation |    ✘     | `http://localhost:8001/gradio_api/mcp/sse` |
| `VIDEO_GENERATOR_MCP__URL` | MCP service for video generation |    ✘     | `http://localhost:8002/gradio_api/mcp/sse` |
| `DIRECTORY__ASSETS`        | Base assets directory            |    ✘     | `./assets`                                 |
| `DIRECTORY__LOG`           | Log files directory              |    ✘     | `./logs`                                   |
| `DIRECTORY__IMAGE`         | Image assets directory           |    ✘     | `./assets/image`                           |
| `DIRECTORY__AUDIO`         | Audio assets directory           |    ✘     | `./assets/audio`                           |
| `DIRECTORY__VIDEO`         | Video assets directory           |    ✘     | `./assets/video`                           |
