Custom Middleware for Request Rate Limiting


Overview
This project contains a custom Django middleware designed to implement request rate limiting based on IP addresses. The middleware limits requests to a maximum of 100 requests per 5-minute rolling window for each IP.

Features
-Tracks and limits requests by IP address.
-Utilizes a caching mechanism for efficient request tracking.
-Adds response headers to indicate remaining allowed requests.
-Handles high-traffic scenarios efficiently and safely.
