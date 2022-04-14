import asyncio
import aiohttp
from flask import Flask, request
from functools import cache

app = Flask(__name__)

#list of acceptable sortBy and direction inputs
argumentsList = ['tags', 'sortBy', 'direction']
sortByList = ['id', 'reads', 'likes', 'popularity']
directionList = ['desc', 'asc']

#verifies the endpoint exists and can accept requests
@app.route("/api/ping", methods=['GET'])
def ping():
	return {
			"success": True
			}

#returns posts matching given query parameters
@app.route("/api/posts", methods=['GET'])
def get_posts():

	#checks query arguments for errors
	args = request.args
	for arg in args:
		if arg not in argumentsList:
			return {"error": "'{}' is an invalid parameter key".format(arg)}, 400
	tags = args.get('tags')
	sortBy = args.get('sortBy', default='id', type=str)
	direction = args.get('direction', default='asc', type=str)		
	if tags == None:
		return {"error": "Tags parameter is required"}, 400
	if sortBy not in sortByList:
		return {"error": "sortBy parameter is invalid"}, 400
	if direction not in directionList:
		return {"error": "direction parameter is invalid"}, 400
	
	#creates list of posts, making sure not to duplicate posts already in the list
	tagList = tags.split(',')
	postList = []
	postIds = {}
	posts = asyncio.run(get_tags(tagList))
	for post in posts['posts']:
		if post['id'] not in postIds:
			postIds[post['id']] = post['id']
			postList.append(post)
	sortedPostList = sort_posts(postList, sortBy, direction)
	return {"posts": sortedPostList}


#caches responses from api calls with a given tag
@cache
async def get_api_response(session, tag):
	URL = "https://api.hatchways.io/assessment/blog/posts?tag={}".format(tag)
	response = await session.get(URL, ssl=False)
	await asyncio.sleep(0)
	return await response.json()

#creates a list of asynchronous tasks to be performed (list of api calls in this case)
def get_tasks(session, tagList):
	tasks = []
	for tag in tagList:
		tasks.append(asyncio.create_task(get_api_response(session, tag)))
	return tasks

#gathers responses from the list of of asynchronous api calls and returns a json response with list of posts
async def get_tags(tagList):
	async with aiohttp.ClientSession() as session:
		list = []
		tasks = get_tasks(session, tagList)
		responses = await asyncio.gather(*tasks)
		for response in responses:
			for post in response['posts']:
				list.append(post)
		await session.close()
		return {"posts": list}


#sort posts according to query arguments
def sort_posts(postList, sortBy, direction):
	sortReverse = (direction == 'desc')
	return sorted(postList, key=lambda i: i[sortBy], reverse=sortReverse)


if __name__ == "__main__":
	app.run(host='localhost', port=5000)

