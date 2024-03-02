from bcrypt import hashpw, gensalt, checkpw
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID, uuid1
from string import ascii_lowercase
from random import random
from enum import Enum
from datetime import date, datetime
from fastapi import Header
from fastapi import FastAPI, Form, Cookie, Header, Response


app = FastAPI()


valid_users = dict()
valid_profiles = dict()
pending_users = dict()
discussion_posts = dict()
request_headers = dict()
cookies = dict()



class User(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    firstname: str
    lastname: str
    middle_initial: str
    age: Optional[int]


class ValidUser(BaseModel):
    id: UUID
    username: str
    password: str
    passphrase: str


class UserType(str, Enum):
    admin = "admin"
    teacher = "teacher"
    alumni = "alumni"
    student = "student"


class Post(BaseModel):
    topic: Optional[str] = None
    message: str
    date_posted: datetime


class PostType(str, Enum):
    information = "information" 
    inquiry = "inquiry"
    quote = "quote"
    twit = "twit"


class ForumPost(BaseModel):
    id: UUID
    topic: Optional[str] = None
    message: str
    post_type: PostType
    date_posted: datetime
    username: str


class ForumDiscussion(BaseModel):
    id: UUID
    main_post: ForumPost
    replies: Optional[List[ForumPost]] = None
    author: UserProfile


@app.get("/ch01/index")
def index():
    return {"message": "Welcome FastAPI Nerd checking live reloads"}


@app.post("/ch01/login/signup")
def signup(uname: str, passwd: str):
    if (uname == None and passwd == None):
        return {"message": "User exist"}
    elif not valid_users.get(uname) == None:
        return {"message": "User exist"}
    else:
        user = User(username=uname, password=passwd)
        pending_users[uname] = user
        return user


@app.post("/ch01/list/users/pending")
def list_pending_users():
    """ Still to develop """
    pending_users = "Building this functionality"
    return pending_users


@app.post("/ch01/login/validate", response_model=ValidUser)
def approve_user(user: User):
    
    if not valid_users.get(user.username) == None:
        return ValidUser(id=None, username = None, password = None, passphrase = None)
    else:
        valid_user = ValidUser(
            id=uuid1(),
            username=user.username,
            password=user.password,
            passphrase=hashpw(
                user.password.encode(),
                gensalt()
            ))
        valid_users[user.username] = valid_user
        # del pending_users[user.username]
        return valid_user


@app.put("/ch01/account/profile/update/{username}")
def update_profile(username: str, id: UUID, new_profile: UserProfile):
    if valid_users.get(username) == None:
        return {"message": "User does not exist"}
    else:
        user = valid_users.get(username)
        if user.id == id:
            valid_profiles[username] = new_profile
            return {"message": "Successfully updated"}
        else:
            return {"message": "User does not exist"}


@app.delete("ch01/discussion/posts/remove/{username}")
def delete_discussion(username: str, id: UUID):
    if valid_users.get(username)  == None:
        return {"message": "user does not exist"}
    elif discussion_posts.get(id) == None:
        return {"message": "Post does not exist"}
    else:
        del discussion_posts[id]
        return {"message": "Main post deleted"}


@app.get("/ch01/list/users/valid")
def list_valid_users():
    valid_users = "Building this functionality"
    return valid_users
        

@app.delete("/ch01/login/remove/{username}")
def delete_user(username: str):
    if username == None:
        return {"message": "Invalid user"}
    else:
        # del valid_users[username]
        return {"message": "Deleted User"}


@app.get("/ch01/login/details/info")
def login_info():
    """
    This will give us an HTTP Status Code 422 (Unprocessable Entity) when 
    accessing http://localhost:8080/ch01/login/details/info. 
    There should be no problem accessing the URL, since the API service is almost a 
    stub or trivial JSON data. What happened in this scenario is that the fixed path’s 
    details and info path directories were treated as username and password parameter 
    values, respectively. Because of confusion, the built-in data validation of FastAPI
    will show us a JSON-formatted error message that says, 
    {"detail":[{"loc":["query","id"],"msg":"field required","type":"value_error.missing"}]}.
    To fix this problem, all fixed paths should be declared first before the dynamic endpoint 
    URLs with path parameters. Thus, the preceding login_info() service should
    be declared first before login_with_token().
    
    In short if I move this logic below to login_with_token() logic it will give the error explained above!
    """
    return {"message": "username and password are needed"}


@app.get("/ch01/login/}")
def login(username: str, password: str):
    """
    When I was giving this method below of login_with_token method it was also producing 442 response
    error and reason was same given in the above method.
    
    This method in current state works fine.
    """
    if valid_users.get(username) == None:
        return {"message": "User does not exist"}
    else:
        user = valid_users.get(username)
        if checkpw(password.encode()):
            return user
        else:
            return {"message": "Invalid user"}


@app.get("/ch01/login/{username}/{password}")
def login_with_token(username:str, password:str, id:UUID):
    if valid_users.get(username) == None:
        return {"message": "User does not exist"}
    else:
        user = valid_users[username]
        if user.id == id and checkpw(password.encode(), user.passphrase):
            return user
        else:
            return {"message": "Invalid user"}



@app.delete("/ch01/login/remove/all")
def delete_users(usernames: List[str]):
    for user in usernames:
        # del valid_users[user]
        pass
    return {"message": "Deleted users"}


@app.patch("/ch01/account/profile/update/names/{username}")
def update_profile_names(username: str, id: UUID, new_names: Dict[str, str]):
    if valid_users.get(username) == None:
        return {"message": "User does not exist"}
    elif new_names == None:
        return {"message": "New names are required"}
    else:
        user = valid_users.get(username)
        if user.id == id:
            profile = valid_profiles[username]
            profile.firstname = new_names['fname']
            profile.lastname = new_names['lname']
            profile.middle_initial = new_names['mi']
            valid_profiles[username] = profile
        else:
            return {"message": "User does not exist"}


@app.delete("/ch01/delete/users/pending")
def delete_pending_users(accounts: List[str] = []):
    for user in accounts:
        pass
        # del pending_users[user]
    return {"message": "Deleted pending users"}


@app.get("/ch01/login/password/change")
def change_password(username: str, old_passw: str="", new_passw: str = ""):
    """
    gensalt:
    This will generate a salt using bcrypt's default parameters. 
    The generated salt can then be used with bcrypt's hashpw() function to hash passwords securely.
    """
    passwd_len = 8
    if valid_users.get(username)  == None:
        return {"message": "User does not exist"}
    elif old_passw == "" or new_passw == "":
        characters = ascii_lowercase
        temporary_passw = ''.join(random.choice(characters) for i in range(passwd_len))
        
        user = valid_users.get(username)
        user.password = temporary_passw
        user.passphrase = hashpw(temporary_passw.encode, gensalt())
        return user
    else:
        user = valid_users.get(username)
        if user.password == old_passw:
            user.password = new_passw
            user.passphrase = hashpw(new_passw.encode(), gensalt())
        else:
            return {"message": "Invalid user"}


@app.post("/ch01/login/username/unlock")
def unlock_username(id: Optional[UUID] = None):
    if id == None:
        return {"message": "token needed"}
    else:
        for key, val in valid_users.items():
            if val.id == id:
                return {"username": val.username}
        return {"message": "user does not exist"}


@app.post("/ch01/login/password/unlock")
def unlock_password(username: Optional[str] = None, 
                    id: Optional[UUID] = None):
    if username == None:
        return {"message": "username is required"}
    elif valid_users.get(username) == None:
        return {"message": "user does not exist"}
    else:
        if id == None:
            return {"message": "token needed"}
        else:
            user = valid_users.get(username)
            if user.id == id:
                return {"password": user.password}
            else:
                return {"message": "invalid token"}


@app.patch("/ch01/account/profile/update/names/{username}")
def update_profile_names(id: UUID, username: str = '' , 
           new_names: Optional[Dict[str, str]] = None):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    elif new_names == None:
        return {"message": "new names are required"}
    else:
        user = valid_users.get(username)
        if user.id == id:
            profile = valid_profiles[username]
            profile.firstname = new_names['fname']
            profile.lastname = new_names['lname']
            profile.middle_initial = new_names['mi']
            valid_profiles[username] = profile
            return {"message": "successfully updated"}
        else:
            return {"message": "user does not exist"}


@app.post("/ch01/login/validate", response_model=ValidUser)
def approve_user(user: User):
    if not valid_users.get(user.username) == None:
        return ValidUser(id=None, username = None, 
             password = None, passphrase = None)
    else:
        valid_user = ValidUser(id=uuid1(), 
             username= user.username, 
             password  = user.password, 
             passphrase = hashpw(user.password.encode(),
                          gensalt()))
        valid_users[user.username] = valid_user
        del pending_users[user.username]
        return valid_user


@app.put("/ch01/account/profile/update/{username}")
def update_profile(username: str, id: UUID, 
                   new_profile: UserProfile):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    else:
        user = valid_users.get(username)
        if user.id == id:
            valid_profiles[username] = new_profile
            return {"message": "successfully updated"}
        else:
            return {"message": "user does not exist"}


@app.get("/ch01/headers/verify")
def verify_headers(host: Optional[str] = Header(None), 
                   accept: Optional[str] = Header(None),
                   accept_language: 
                       Optional[str] = Header(None),
                   accept_encoding: 
                       Optional[str] = Header(None),
                   user_agent: 
                       Optional[str] = Header(None)):
    request_headers["Host"] = host
    request_headers["Accept"] = accept
    request_headers["Accept-Language"] = accept_language
    request_headers["Accept-Encoding"] = accept_encoding
    request_headers["User-Agent"] = user_agent
    return request_headers


@app.post("/ch01/discussion/posts/add/{username}")
def post_discussion(username: str, post: Post, 
                    post_type: PostType):
    if valid_users.get(username) == None:
        return {"message": "user does not exist"}
    elif not (discussion_posts.get(id) == None):
        return {"message": "post already exists"}
    else:
        forum_post = ForumPost(id=uuid1(), 
          topic=post.topic, message=post.message, 
          post_type=post_type, 
          date_posted=post.date_posted, username=username)
        user = valid_profiles[username]
        forum = ForumDiscussion(id=uuid1(), 
         main_post=forum_post, author=user, replies=list())
        discussion_posts[forum.id] = forum
        return forum


@app.post("/ch01/login/validate", response_model=ValidUser)
def approve_user(user: User):
    
    if not valid_users.get(user.username) == None:
        return ValidUser(id=None, username = None, 
                   password = None, passphrase = None)
    else:
        valid_user = ValidUser(id=uuid1(), 
         username= user.username, password = user.password,
          passphrase = hashpw(user.password.encode(),
                 gensalt()))
        valid_users[user.username] = valid_user
        del pending_users[user.username]
        return valid_user


from fastapi import FastAPI, Form
@app.post("/ch01/account/profile/add", response_model=UserProfile)
def add_profile(uname: str, 
                fname: str = Form(...), 
                lname: str = Form(...),
                mid_init: str = Form(...),
                user_age: int = Form(...),
                sal: float = Form(...),
                bday: str = Form(...),
                utype: UserType = Form(...)):
    if valid_users.get(uname) == None:
        return UserProfile(firstname=None, lastname=None, 
              middle_initial=None, age=None, 
              birthday=None, salary=None, user_type=None)
    else:
        profile = UserProfile(firstname=fname, 
             lastname=lname, middle_initial=mid_init, 
             age=user_age, birthday=datetime.strptime(bday,
                '%m/%d/%Y'), salary=sal, user_type=utype)
        valid_profiles[uname] = profile
        return profile


@app.post("/ch01/login/rememberme/create/")
def create_cookies(resp: Response, id: UUID, 
                   username: str = ''):
    resp.set_cookie(key="userkey", value=username)
    resp.set_cookie(key="identity", value=str(id))
    return {"message": "remember-me tokens created"}


@app.get("/ch01/login/cookies")
def access_cookie(userkey: Optional[str] = Cookie(None), 
           identity: Optional[str] = Cookie(None)):
    cookies["userkey"] = userkey
    cookies["identity"] = identity
    return cookies