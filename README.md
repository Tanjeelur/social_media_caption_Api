# social_media_caption_Api

## Overview

A FastAPI-based service for generating and editing social media captions and hashtags using the Gemini API.

## Features

- Generate platform-specific captions and hashtags (`/api/v1/generate`)
- Edit existing captions (`/api/v1/edit`)

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

### Running the API

Start the FastAPI server with Uvicorn:

```
uvicorn main:app --reload
```

The API will be available at:  
`http://127.0.0.1:8000`

### API Endpoints

#### Generate Captions

- **POST** `/api/v1/generate`
- Request body:  
  ```json
  {
    "content": "Your post content here",
    "platforms": ["instagram", "twitter"]
  }
  ```
- Response:  
  ```json
  {
    "instagram": {
      "caption": "...",
      "hashtags": ["#tag1", "#tag2"]
    },
    "twitter": {
      "caption": "...",
      "hashtags": ["#tag1", "#tag2"]
    }
  }
  ```

#### Edit Caption

- **POST** `/api/v1/edit`
- Request body:  
  ```json
  {
    "caption": "Original caption",
    "instructions": "Make it more engaging"
  }
  ```
- Response:  
  ```json
  {
    "caption": "Edited caption"
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