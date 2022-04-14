import hatchways 
import unittest
import warnings
import json

class TestHatchways(unittest.TestCase):

	def setUp(self):
		hatchways.app.testing = True
		self.app = hatchways.app.test_client()
		#silences warning given from asyncio known .close() internal details
		warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

	#tests the json response and status code from ping()
	def test_ping(self):
		response = self.app.get('/api/ping')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content_type, "application/json")
		self.assertEqual(response.json, {"success": True})

	#tests the json response and status code from get_posts()
	def test_get_posts(self):
		#if tags parameter is not present, return status_code 400 and json error message
		response = self.app.get('api/posts')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content_type, "application/json")
		self.assertEqual(response.json, {"error": "Tags parameter is required"})
		
		#if parameter is invalid, return status_code 400 and json error message
		response = self.app.get('api/posts?tags=science&dogs=id')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content_type, "application/json")
		self.assertEqual(response.json, {"error": "'dogs' is an invalid parameter key"})

		#if tags parameter is present and sortBy parameter is in sortBy list, return status_code 200 and json response
		sortByList = ['id', 'reads', 'likes', 'popularity']
		for sortBy in sortByList:
			response = self.app.get('api/posts?tags=science&sortBy={}'.format(sortBy))
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.content_type, "application/json")

		#if tags parameter is present and direction parameter is in direction list, return status_code 200 and json response
		directionList = ['desc', 'asc']
		for direction in directionList:	
			response = self.app.get('api/posts?tags=science&direction={}'.format(direction))
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.content_type, "application/json")	

		#if sortBy parameter not in sortyBy list, return status_code 400 and json error message
		response = self.app.get('api/posts?tags=science&sortBy=ranking')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content_type, "application/json")
		self.assertEqual(response.json, {"error": "sortBy parameter is invalid"})
		
		#if direction parameter not in direction list, return status_code 400 and json error message
		response = self.app.get('api/posts?tags=science&direction=north')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(response.content_type, "application/json")
		self.assertEqual(response.json, {"error": "direction parameter is invalid"})

		#tests json response against data saved in test_data.json(data from prompt example results) 
		response = self.app.get('api/posts?tags=history,tech&sortBy=likes&direction=desc')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content_type, "application/json")
		with open('test_data.json', 'r') as file:
			test_data = json.load(file)
		self.assertEqual(response.json, test_data)


if __name__ == "__main__":
	unittest.main()

