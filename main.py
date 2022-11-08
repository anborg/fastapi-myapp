import uvicorn
from typing import Union
from dataclasses import dataclass
from datetime import datetime
from typing import List
from fastapi import FastAPI, Form,File, Request, UploadFile,Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

api_app = FastAPI(title="api app")

app = FastAPI(title="main app")
app.mount("/ui", StaticFiles(directory="ui", html="true"), name="ui")
templates = Jinja2Templates(directory="ui") # Change this path accordingly
app.mount("/api", api_app)

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@api_app.post(path="/uploadFiles")
async def extract_data_from_images(images: List[UploadFile] = File(...)):
    return f"Name: {images[0].filename}, now: {datetime.now()}"

@api_app.get("/form_userconfig", response_class=HTMLResponse)
def form_get():
    return '''<form method="post" action="form_userconfig_post"> 
    <input type="text" name="userid" value="1"/> 
    <input type="text" name="username" value="abcd"/> 
    <input type="submit"/> 
    </form>'''

@dataclass
class UserConfigModel:
    userid: int = Form(...)
    username: str = Form(...)

@api_app.post("/form_userconfig_post")
def form_post(form_data: UserConfigModel = Depends()):
    #process long running steps asynchronously.
    import os, tempfile, json
    tmp = tempfile.NamedTemporaryFile(mode='w+',delete=False)
    try:
        print("Config file path:",tmp.name)
        # convert to JSON string
        # jsonStr = json.dumps(form_data.__dict__, indent=4)
        json.dump(form_data.__dict__, tmp)
        tmp.flush()
        tmp.seek(0, 0)  # This will rewind the cursor
        # system('nano %s' % fname)
        content = tmp.readlines()
        print("Config file content:", content[0])
    finally:
        tmp.close()
        os.unlink(tmp.name)
    return form_data

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)