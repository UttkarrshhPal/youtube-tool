from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx
import os
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Brand Mentions Finder API",
    description="API to find brand mentions in YouTube videos",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# Models
class VideoResult(BaseModel):
    id: str
    title: str
    description: str
    thumbnail: str
    channel_title: str
    published_at: str
    view_count: int = 0
    match_type: List[str] = Field(default_factory=list)
    transcript_matches: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    videos: List[VideoResult]
    next_page_token: Optional[str] = None
    total_results: int


class SearchFilters(BaseModel):
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    min_views: Optional[int] = 0
    channel_name: Optional[str] = None


# Helper functions
def format_date(date_str):
    # Convert date to RFC 3339 format
    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def extract_video_id(url):
    # Extract video ID from YouTube URL
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/embed\/([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/v\/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


async def search_youtube_by_keyword(
    keyword, max_results=50, page_token=None, published_after=None
):
    # Search YouTube for videos with the keyword in title or description
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }

    if page_token:
        params["pageToken"] = page_token

    if published_after:
        params["publishedAfter"] = published_after

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            logger.error(f"YouTube API error: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"YouTube API error: {response.text}",
            )

        return response.json()


async def get_video_details(video_ids):
    # Get detailed information for videos
    if not video_ids:
        return []

    url = "https://www.googleapis.com/youtube/v3/videos"

    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            logger.error(f"YouTube API error: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"YouTube API error: {response.text}",
            )

        return response.json()


async def get_video_transcript(video_id):
    # Use YouTube API to get captions for a video (simplified for example)
    # In a real implementation, you might use a more robust library like youtube_transcript_api

    url = f"https://www.googleapis.com/youtube/v3/captions"
    params = {"part": "snippet", "videoId": video_id, "key": YOUTUBE_API_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

        if response.status_code != 200:
            logger.warning(
                f"Failed to get captions for video {video_id}: {response.text}"
            )
            return None

        data = response.json()
        captions = data.get("items", [])

        if not captions:
            return None

        # Get the caption track ID for the first caption
        caption_id = captions[0]["id"]

        # Get the actual transcript
        download_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}"
        download_params = {"key": YOUTUBE_API_KEY, "tfmt": "srt"}

        transcript_response = await client.get(download_url, params=download_params)

        if transcript_response.status_code != 200:
            logger.warning(f"Failed to download transcript for video {video_id}")
            return None

        # Simple parsing of SRT format (simplified for example)
        transcript_text = transcript_response.text

        # Remove time codes and numbers
        cleaned_text = re.sub(
            r"\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+|\d+", "", transcript_text
        )
        return cleaned_text.strip()


async def search_google_custom_search(keyword):
    # Use Google Custom Search API to find videos
    url = f"https://www.googleapis.com/customsearch/v1"

    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": f"{keyword} site:youtube.com",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code != 200:
            logger.error(f"Google Custom Search API error: {response.text}")
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Google Custom Search API error: {response.text}",
            )

        return response.json()


def filter_videos(videos, filters: SearchFilters):
    filtered_videos = []

    for video in videos:
        # Filter by date
        if filters.min_date and video.published_at < filters.min_date:
            continue
        if filters.max_date and video.published_at > filters.max_date:
            continue

        # Filter by views
        if filters.min_views and video.view_count < filters.min_views:
            continue

        # Filter by channel name
        if (
            filters.channel_name
            and filters.channel_name.lower() not in video.channel_title.lower()
        ):
            continue

        filtered_videos.append(video)

    return filtered_videos


async def find_mentions_in_transcript(transcript, keyword):
    if not transcript:
        return []

    # Simple keyword search in transcript (can be enhanced with NLP for better accuracy)
    keyword = keyword.lower()
    transcript = transcript.lower()

    # Find the keyword in the transcript
    matches = []
    for match in re.finditer(r"\b" + re.escape(keyword) + r"\b", transcript):
        start = max(0, match.start() - 40)
        end = min(len(transcript), match.end() + 40)

        # Get surrounding context
        context = transcript[start:end].strip()
        matches.append(f"...{context}...")

        # Limit to 5 matches for brevity
        if len(matches) >= 5:
            break

    return matches


@app.get("/api/search", response_model=SearchResponse)
async def search_videos(
    keyword: str = Query(..., description="Brand name or keyword to search for"),
    page_token: Optional[str] = None,
    max_results: int = Query(10, ge=1, le=50),
    min_date: Optional[str] = None,
    max_date: Optional[str] = None,
    min_views: Optional[int] = None,
    channel_name: Optional[str] = None,
):
    # Process dates
    published_after = None
    if min_date:
        published_after = format_date(min_date)

    # Create filters object
    filters = SearchFilters(
        min_date=min_date,
        max_date=max_date,
        min_views=min_views,
        channel_name=channel_name,
    )

    # Search YouTube directly
    youtube_results = await search_youtube_by_keyword(
        keyword,
        max_results=max_results,
        page_token=page_token,
        published_after=published_after,
    )

    # Process YouTube results
    videos = []
    video_ids = []

    # Safely extract video IDs and handle unexpected structures
    for item in youtube_results.get("items", []):
        try:
            if isinstance(item.get("id"), dict) and "videoId" in item["id"]:
                video_ids.append(item["id"]["videoId"])
            elif isinstance(item.get("id"), str):
                # Handle case where id might be a direct string
                video_ids.append(item["id"])
        except (KeyError, TypeError) as e:
            logger.warning(f"Skipping item with unexpected structure: {str(e)}")
            continue

    if video_ids:
        video_details = await get_video_details(video_ids)

        for item in video_details.get("items", []):
            video_id = item["id"]
            snippet = item["snippet"]
            statistics = item.get("statistics", {})

            # Check where the keyword appears
            match_types = []
            if keyword.lower() in snippet["title"].lower():
                match_types.append("title")
            if keyword.lower() in snippet["description"].lower():
                match_types.append("description")

            # Get transcript and check for mentions
            transcript = await get_video_transcript(video_id)
            transcript_matches = []

            if transcript and keyword.lower() in transcript.lower():
                match_types.append("transcript")
                transcript_matches = await find_mentions_in_transcript(
                    transcript, keyword
                )

            video = VideoResult(
                id=video_id,
                title=snippet["title"],
                description=snippet["description"],
                thumbnail=snippet["thumbnails"]["high"]["url"],
                channel_title=snippet["channelTitle"],
                published_at=snippet["publishedAt"],
                view_count=int(statistics.get("viewCount", 0)),
                match_type=match_types,
                transcript_matches=transcript_matches,
            )
            videos.append(video)

    # Try Google Custom Search API as well
    try:
        google_results = await search_google_custom_search(keyword)

        # Process Google results
        for item in google_results.get("items", []):
            video_id = extract_video_id(item["link"])

            if video_id and video_id not in [v.id for v in videos]:
                # Get video details
                video_details = await get_video_details([video_id])

                if video_details.get("items"):
                    detail = video_details["items"][0]
                    snippet = detail["snippet"]
                    statistics = detail.get("statistics", {})

                    # Check where the keyword appears
                    match_types = []
                    if keyword.lower() in snippet["title"].lower():
                        match_types.append("title")
                    if keyword.lower() in snippet["description"].lower():
                        match_types.append("description")

                    # Get transcript and check for mentions
                    transcript = await get_video_transcript(video_id)
                    transcript_matches = []

                    if transcript and keyword.lower() in transcript.lower():
                        match_types.append("transcript")
                        transcript_matches = await find_mentions_in_transcript(
                            transcript, keyword
                        )

                    video = VideoResult(
                        id=video_id,
                        title=snippet["title"],
                        description=snippet["description"],
                        thumbnail=snippet["thumbnails"]["high"]["url"],
                        channel_title=snippet["channelTitle"],
                        published_at=snippet["publishedAt"],
                        view_count=int(statistics.get("viewCount", 0)),
                        match_type=match_types,
                        transcript_matches=transcript_matches,
                    )
                    videos.append(video)
    except Exception as e:
        # Log error but continue with YouTube results
        logger.error(f"Error with Google Custom Search: {str(e)}")

    # Apply filters
    filtered_videos = filter_videos(videos, filters)

    return SearchResponse(
        videos=filtered_videos,
        next_page_token=youtube_results.get("nextPageToken"),
        total_results=len(filtered_videos),
    )


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
