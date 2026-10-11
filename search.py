import os, requests, html
from dotenv import load_dotenv
from paths import ENV_FILE

#load the .env file containing secrets
load_dotenv(ENV_FILE)

class Search:
	def __init__(self, query, max_results):
		if not isinstance(query, str):
			raise TypeError("query must be a string.")
		query = query.strip()

		if not query:
			raise ValueError("Must provide a query.")

		if isinstance(max_results, bool) or not isinstance(max_results, int):
			raise TypeError("max_results must be an integer.")

		if not 1 <= max_results <= 10:
			raise ValueError("max_results must be between 1 and 10")

        
		# query is what is being searched up
		self.query = query
		# maximum amount of results to return
		self.max_results = max_results

	# youtube search function
	def search_youtube(self):
		#requests google API
		# We use google API instead of scraping for stability and consistency
		
		response = requests.get(
			"https://www.googleapis.com/youtube/v3/search",
			params={
				"part": "snippet",
				"q": self.query,
				"type": "video",
				"maxResults": self.max_results,
				"key": os.environ["YT_API_KEY"],
			},
			timeout=10,
		)
		response.raise_for_status()

		results = []
		
		# looks at the response in json and collects info
		for item in response.json()["items"]:
			video_id = item["id"]["videoId"]
			results.append({
				"platform" : "youtube",
				"source_id" : video_id,
				"title": html.unescape(item["snippet"]["title"]),
				"artist": html.unescape(item["snippet"]["channelTitle"]),
				"url": "https://www.youtube.com/watch?v=" + video_id,
			})
		return results





	