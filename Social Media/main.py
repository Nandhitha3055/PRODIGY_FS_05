from flask import *
import sqlite3
from flask_session import Session
from hash import Pass_hashing
from database import UserClass
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
hp = Pass_hashing()
db = UserClass()
secret_key = os.urandom(24)
app.config['SECRET_KEY'] = secret_key
UPLOAD_FOLDER = 'static/uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_COOKIE_NAME'] = 'my_session'
app.config['SESSION_COOKIE_SECURE'] = True
Session(app)


@app.route('/')  #login page
def home():
    return render_template("home.html", name ="")


@app.route('/index')
def index():
    if 'name' in session:
        email = session['name']
        res = db.get_others_post(email)[::-1]
        following = db.getFollower(email)
        return render_template("index.html",where = "index",posts = res,following = following,user = email)
    else:
        return redirect(url_for('home'))
    
@app.route("/post")
def post():
    email = session['name']
    if 'name' in session:
        postId = request.args.get('id')
        if  postId:
            res = db.getPost(postId)
            if res:
                following = db.getFollower(email)
                return render_template("index.html",where = "post",post = res,following = following,user = email)
    return redirect(url_for('home'))
    
@app.route("/signup") #signup page
def signup():
    return render_template("home.html", name="signup")

@app.route('/follow', methods=['POST'])
def follow():
    email = session['name']
    emailIdToFollow = request.args.get('userId')
    followType = request.args.get("type")
    if(followType == "follow"):
        db.addFollower(email,emailIdToFollow)
    else:
        db.removeFollower(email,emailIdToFollow)
    return "user added";
    
@app.route('/get', methods=['POST']) #login verification and admin or user 
def get():
    email = request.form['email']
    password = request.form['Password']
    hashed = db.get_user(email)
    if hashed != None:
        if hp.verify_pass(hashed,password):
            session["name"] = email
            session["user_type"] = db.get_user_type(email)
            return redirect(url_for("index"))   
    return render_template("home.html", name ="Email or Password is not a match")

@app.route('/profile')
def profile():
    email = session['name']
    otherUser = False
    isFollowing = False
    if request.args.get('userid'):
        otherUserEmail = request.args.get('userid')
        if email != otherUserEmail:
            isFollowing = db.isFollowing(email,otherUserEmail)
            otherUser = True
            email = otherUserEmail
    img = db.get_user_img(email)
    details = db.get_user_details(email)
    followerCount = len(db.getMyFollowers(email))
    
    return render_template("index.html",name="profile",image = img,first = details[0],last = details[1],phone = details[2],email = details[3],followerCount = followerCount,otherUser = otherUser,isFollowing = isFollowing)


@app.route('/verify', methods=['POST']) #signup page string data in database
def verify():
    if request.method == "POST":
        first = request.form["FirstName"]
        last = request.form["LastName"]
        phone = request.form["PhoneNumber"]
        email = request.form["email"]
        password = hp.hashing_pass(request.form["Password"])
        # print(password)
        file = request.files['file']
        if file:
            original_filename = secure_filename(file.filename)
            new_filename = email+'.png'
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            file.save(file_path)
        if not db.existing_User(email):
            db.insert_user(first,last,phone,email,file_path,password,"User")
            return render_template("user.html",name = "Account Successfully Created",page = "login")
        else:
            return render_template("user.html",name = "User Already Exists",page = "login")
    return render_template("home.html",name ="Sign in")

@app.route('/save_post',methods=['POST'])
def save_post():
    if request.method == "POST":
        email = session['name']
        title = request.form["title"]
        content = request.form["post"]
        db.insert_post(title,content,email)
        return redirect(url_for("profile"))
        
@app.route('/My_posts')
def My_posts():
    email = session['name']
    res = db.get_post(email)
    return render_template("index.html",name = "Saved",posts = res,who = "You")


@app.route("/liked", methods=['POST'])
def liked():
    postId = request.form['postId']
    db.delete_post(postId)
    return redirect("/My_posts")

@app.route("/liked_posts", methods=['POST'])
def liked_posts():
    postId = request.form['postId']
    db.delete_post(postId)
    return redirect("/My_posts")

@app.route("/insert_comments",methods = ["POST"])
def insert_comments():
    if request.method == "POST":
        commenter = session['name']
        postId = session['postId']
        comment = request.form['comment']
        db.insert_comment(commenter,postId,comment)
        return redirect("/comments")



@app.route("/comments", methods=["POST", "GET"])
def comments():
    if request.method == "POST":
        postId = request.form.get('postId')
        session['postId'] = postId
        comments = db.get_comments(postId)
        return render_template("index.html",name="comments", comments=comments,create = "yes")
    else:
        postId = session.get('postId')
        comments = db.get_comments(postId) if postId else []
        session.pop('postId', None)
        return render_template("index.html", name="comments", comments=comments,create = "yes")

@app.route("/comments_on_my_post", methods=["POST", "GET"])
def comments_on_my_post():
    if request.method == "POST" or not session['postId']:
        postId = request.form.get('postId')
        session['postId'] = postId
        comments = db.get_comments(postId)
        return render_template("index.html",name="comments", comments=comments)
    else:
        # GET request handling or redirection
        postId = session.get('postId')
        comments = db.get_comments(postId) if postId else []
        session.pop('postId', None)
        return render_template("index.html", name="comments", comments=comments)




@app.route("/delete-post", methods=['POST'])
def admin_delete():
    postId = request.form['postId']
    db.delete_post(postId)
    return redirect("/My_posts")



@app.route("/Logout")
def logout():
    session.pop('name', None)
    session.pop('user_type', None)
    return redirect("/")


@app.route("/delete")
def delete():
    uploads_folder = UPLOAD_FOLDER
    file_to_remove = session['name']+'.png'
    file_path = os.path.join(uploads_folder, file_to_remove)
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        pass
    db.delete_User(session.get("name"))
    return render_template("user.html",name = "Account Successfully Deleted !",page = "Signup")



if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080,debug = True)
