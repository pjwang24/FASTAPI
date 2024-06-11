# python3 -m venv venv or make sure its sourced here
# source venv/bin/activate
import psycopg
from psycopg.rows import dict_row
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from random import randrange
from pydantic import BaseModel
# to ensure we receive data from the front end and sending data that matches to our schema

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True # if user doesn't provide published, default to True, optional field for our schema
    # rating: Optional[int] = None # if rating not provided, default to None

while True:
    try:
        conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='Theking23!', row_factory=dict_row)
        cursor = conn.cursor()
        print("Database connection was successful!")
    except Exception as error:
        print("Connecting to database failed.")
        print("Error: ", error)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 7}, {"title": "favorite foods", "content": "I like pizza", "id": 2}]

async def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

async def find_index_post(id):
    for i,p in enumerate(my_posts):
        if p['id'] == id:
            return i
    return None

@app.get("/") # the first path operation tihat matches is gong to be the one that runs, order matters
async def login_user(): # async functions can operate concurrently
    return {"message": "Welcome to my API!!"}

@app.get("/posts")
async def get_posts():
    return {"data": my_posts} # automatically converts to JSON format

# get request is getting data from the server
# post request is sending data to the API server

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(post: Post): # extract all of the fields from the body and stores in Pydantic model new_post
    '''print(post.rating) # also have to match the BaseModel, .title or .content to get values
    print(post.dict()) # converts Pydantic model to a dictionary'''
    post_dict = post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

@app.get("/posts/{id}") # id represents a path parameter
async def get_post(id: int): # capture the value from the URL path parameter
    post = await find_post(id) # await keyword allows other coroutines to run while the paused one is waiting for an operation to complete
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
        '''response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"post with id: {id} was not found"}'''
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_posts(id: int):
    # deleting post, find index with required id, pop the index
    index = await find_index_post(id)
    if index == None: # if index is 0, the condition 'if not index' will return True and raise HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
async def update_posts(id: int, post: Post):
    index = await find_index_post(id)
    if index == None: # if index is 0, the condition 'if not index' will return True and raise HTTPException
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"data": post_dict}