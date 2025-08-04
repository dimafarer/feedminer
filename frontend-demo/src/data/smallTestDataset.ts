// Small test dataset for debugging multi-upload functionality
// Based on actual Instagram export structure but with minimal data

export const smallTestDataset = {
  "type": "instagram_export",
  "user_id": "demo-user",
  "modelPreference": {
    "provider": "nova",
    "model": "us.amazon.nova-micro-v1:0",
    "temperature": 0.7
  },
  "exportInfo": {
    "dataTypes": ["saved_posts", "liked_posts"],
    "extractedAt": "2025-08-03T18:33:33.060Z",
    "exportFolder": "meta-2025-Jul-13-19-10-01/instagram-test-2025-07-13-ar06JOIC/"
  },
  "saved_posts": {
    "saved_saved_media": [
      {
        "title": "nathandickeson",
        "string_map_data": {
          "Saved on": {
            "href": "https://www.instagram.com/reel/DL-9eewSDaI/",
            "timestamp": 1752408896
          }
        }
      },
      {
        "title": "fitfight_",
        "string_map_data": {
          "Saved on": {
            "href": "https://www.instagram.com/reel/DLS17TuMCzi/",
            "timestamp": 1752322461
          }
        }
      },
      {
        "title": "bodybuilding_motivation",
        "string_map_data": {
          "Saved on": {
            "href": "https://www.instagram.com/p/C9abc123def/",
            "timestamp": 1752200000
          }
        }
      }
    ]
  },
  "liked_posts": {
    "likes_media_likes": [
      {
        "title": "fitness_inspiration",
        "string_map_data": {
          "Liked on": {
            "href": "https://www.instagram.com/p/C8xyz789abc/",
            "timestamp": 1752100000
          }
        }
      },
      {
        "title": "tech_news",
        "string_map_data": {
          "Liked on": {
            "href": "https://www.instagram.com/p/C7def456ghi/",
            "timestamp": 1752000000
          }
        }
      }
    ]
  },
  "dataTypes": ["saved_posts", "liked_posts"]
};

export default smallTestDataset;