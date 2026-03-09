import asyncio
import sys
import json
sys.path.insert(0, '/scripts')
from reddit_poster import post_comment

post_url = sys.argv[1]
comment_text = sys.argv[2]

result = asyncio.run(post_comment(post_url, comment_text))
print(json.dumps(result))
```

Your repo structure should look like:
```
blox-marketing-bot/
├── Dockerfile
├── reddit_poster.py
└── post_comment.py