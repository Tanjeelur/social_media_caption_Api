# Social Media Caption API

## Overview

A FastAPI-based service for generating and editing social media captions using OpenAI API.

## Features

- Generate platform-specific captions and hashtags
- Edit existing captions with various styles
- Single unified endpoint for both operations

## Getting Started

### Installation

1. Clone the repository:
    ```
    git clone <your-repo-url>
    cd social_media_caption_Api
    ```

2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the project root and add your OpenAI API key:
    ```env
    OPENAI_API_KEY=your_openai_api_key_here
    ```

### Running the API

Start the FastAPI server with Uvicorn:

```
uvicorn main:app --reload
```

The API will be available at:  
`http://127.0.0.1:8000`

### API Endpoints

#### Unified Caption Endpoint

- **POST** `/api/v1/caption/caption`

**Parameters:**
- `platforms` (required): List of platforms (e.g., ["facebook", "instagram", "linkedin"])
- `post_type` (optional): Type of post (e.g., "Story", "Post")
- `post_topic` (optional): Topic of the post (e.g., "Food", "Travel")
- `caption` (optional): Existing caption to edit
- `edit_type` (optional): Type of edit (e.g., "rephrase", "make more casual", "shorten")
- `image` (optional): Image file

**Logic:**
- If `edit_type` is empty → generates a new caption
- If `edit_type` has a value → edits the existing caption

**Example Request (Generate):**
```json
{
  "platforms": ["instagram", "facebook"],
  "post_type": "Story",
  "post_topic": "Food"
}
```

**Example Request (Edit):**
```json
{
  "platforms": ["instagram"],
  "caption": "Original caption here",
  "edit_type": "make more casual"
}
```

**Response (Generate):**
```json
{
  "instagram": {
    "caption": "Generated caption...",
    "hashtags": ["#tag1", "#tag2"]
  },
  "facebook": {
    "caption": "Generated caption...",
    "hashtags": ["#tag1", "#tag2"]
  }
}
```

**Response (Edit):**
```json
{
  "caption": "Edited caption..."
}
```

## Project Structure

```
social_media_caption_Api/
│
├── main.py
├── README.md
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           └── caption.py
│   ├── models/
│   │   └── captions.py
│   └── services/
│       └── captions_service.py
└── requirements.txt
```

## License

MIT License
