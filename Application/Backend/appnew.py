from flask import Flask, jsonify, request, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import csv
import json
from celery.schedules import crontab
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
from redis import Redis
import jsonpickle
from celery.utils.log import get_task_logger
from celery.result import AsyncResult
import workers
import tasks

SMPTP_SERVER_HOST = "localhost"
SMPTP_SERVER_PORT = 1025
SENDER_ADDRESS = "email@hasingh.com"
SENDER_PASSWORD = ""

app = Flask(__name__)

# configure 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretkey'
app.config['JWT_SECRET_KEY'] = 'super-secret' 
app.config['UPLOAD_FOLDER'] = 'upload'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}
app.config['CELERY_BROKER_URL'] = "redis://localhost:6379/1"
app.config['CELERY_RESULT_BACKEND'] = "redis://localhost:6379/2"
app.config['REDIS_URL'] = 'redis://localhost:6379/0'
redis_client = Redis.from_url(app.config['REDIS_URL'])

celery = workers.celery
celery.conf.update(
    broker_url = app.config["CELERY_BROKER_URL"],
    result_backend = app.config["CELERY_RESULT_BACKEND"]
)
celery.Task = workers.ContextTask
app.app_context().push()

CORS(app, resources={r"/*": {"origins": "*"}})


db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
logger = get_task_logger(__name__)
app.app_context().push()

# user model
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    following = db.Column(db.String(500), nullable=True)
    followers = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)


# post model
class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Post {}>'.format(self.image_url)

#lastlogin
class LastLogin(db.Model):
    __tablename__ = "lastlogin"
    id = db.Column(db.Integer, primary_key=True)
    login_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.before_first_request
def create_tables():
    db.create_all()

session = {}
usrid = 0

#to login
@app.route('/login', methods=['POST'])
def authenticate():
    
    data = request.get_json()
    username = data.get('name')
    password = data.get('password')
    print(username, password)
    
    user = User.query.filter_by(username=username).first()
    print(user)
  
    if user and check_password_hash(user.password, password):
        print(user.id)
        now = datetime.now()
        last_login_detail = LastLogin.query.filter_by(id=user.id).first()
        if last_login_detail is None :
            loginlast = LastLogin(id=user.id, login_at=now)
            db.session.add(loginlast)
        else: 
            last_login_detail.login_at = now

        userdata = {"name": username, "email":user.email}
        send_login_mail(userdata)
        
        db.session.commit()
        session['user_id'] = user.id
        global usrid 
        usrid = user.id
        print(usrid)
        access_token = create_access_token(identity=user.id)
        return jsonify({'token': access_token , 'id': user.id  }), 200

    else:
        return jsonify({'message': 'Invalid username or password'}), 401

#to edit a post
@app.route('/editcaption', methods=['POST'])
def editcaption():
    data = request.get_json()
    postid = int(data.get('id'))
    print(postid)
    newcap = data.get('caption')
    print(newcap)

    post = Post.query.filter_by(id=postid).first()
    print(post)
    try:
        post.caption = newcap
        db.session.commit()
        return jsonify({'message': 'Caption edited'}), 200
    except:
        return jsonify({'message': 'Post does not exit'}), 401
    
#to delete a post
@app.route('/deletepost', methods=['POST'])
def deletepost():
    data = request.get_json()
    postid = int(data.get('id'))
    print(postid)

    post = Post.query.filter_by(id=postid).first()
    print(post)
    try:
        del_pic_path = post.image_url
        if os.path.exists("./"+ del_pic_path):
            os.remove("./"+del_pic_path)
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted'}), 200
    except:
        return jsonify({'message': 'Post does not exit'}), 401

#to export a post
@app.route('/exportpost', methods=['POST'])
def export_post():
    
    data = request.get_json()
    postid = int(data.get('id'))
    print(postid)

    post = Post.query.filter_by(id=postid).first()
    print(post)
    # Convert post data to list of dictionaries
    post_data = [{'id': post.id, 'address': post.image_url, 'caption': post.caption, 'timestamp': post.created_at, 'userID':post.user_id}]

    # Create CSV file
    with open('post.csv', 'w', newline='') as csvfile:
        fieldnames = ['id', 'address', 'caption', 'timestamp', 'userID']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in post_data:
            writer.writerow(data)

    # Send CSV file as attachment
    return send_file('post.csv', mimetype='text/csv', as_attachment=True)    


# to get id 
@app.route('/getid', methods=['GET'])
def get_id():
    #cached_response = redis_client.get(request.url)
    #redis_client.setex(request.url, 300)
    print(usrid)
    usr = {}
    usr['id'] = usrid
    return jsonify(usr), 200

# to logout
@app.route('/api/logout', methods=['POST'])
def logout():
    usrid = 0
    session.pop('user_id', None)
    return jsonify({'message': 'Logout successful'}), 200

#to send email
def send_email(to_address, subject, message, content="text", attachment_file=None):
    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    if attachment_file:
        with open(attachment_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read()) 
        encoders.encode_base64(part)
        
        part.add_header(
            "Content-Disposition", f"attachment; filename= {attachment_file}",
        )
        msg.attach(part)

    s = smtplib.SMTP(host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
    
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    return True


def format_message(template_file, data={}):
    with open(template_file) as file_:
        template = Template(file_.read())
        return template.render(data=data)

#export complete mail
def send_export_complete():
    user = User.query.filter_by(id=usrid)
    data = {"name": user.username, "email": user.email}
    message = format_message("export_complete.html",data=data)
    send_email(
        to_address=data["email"],
        subject="Welcome",
        message=message,
        content="html",
        attachment_file="blogs.csv",
    )

#welcome mail
def send_welcome_message(data):
    message = format_message("welcome-email.html", data=data)
    send_email(
        to_address=data["email"],
        subject="Welcome",
        message=message,
        content="html",
        attachment_file="manual.pdf",
    )

#daily mail
def send_daily_mail(data):
    message = format_message("daily_scheduled_mail.html", data=data)
    send_email(
        to_address=data["email"],
        subject="Daily Reminder",
        message=message,
        content="html"
    )
#login mail
def send_login_mail(data):
    message = format_message("login-mail.html", data=data)
    send_email(
        to_address=data["email"],
        subject="Login detected",
        message=message,
        content="html"
    )

def scheduled_task():
    users = User.query.all()
    for user in users:
        last_login_detail = LastLogin.query.filter_by(id=user.id)
        try:
            time_diff = datetime.now() - last_login_detail.login_at
            if time_diff > timedelta(hours=24):
                data = {"name": user.username, "email":user.email}
                send_daily_mail(data)
        except:
            pass

#to signup
@app.route('/signup', methods=['POST'])
def register():
    # get username and password from request body
    data = request.get_json()
    username = data.get('name')
    email = data.get('email')
    password = data.get('password')
    print(username, email, password)

    user = User(username=username, email=email, password=generate_password_hash(password),followers="",following="")

    db.session.add(user)
    db.session.commit()
    userdata = {"name": username, "email": email}
    send_welcome_message(userdata)
    return jsonify({'message': 'Registration successful'}), 201

@app.route("/getphoto")
def get_photo():
    photo = Post.query.all().first()
    print(photo.image_url)
    return send_file("../upload/Picture16.png", mimetype='image/jpeg')
#to get posts
@app.route("/getposts")
def get_posts():
    print(usrid)
    user = User.query.filter_by(id=usrid).first()
    idlst = user.following.split(',')
    print(idlst)
    data = {}
    for i in idlst:
        print("id:")
        print(i)
        posts = Post.query.filter_by(user_id=i)
        print(posts)
        try:
            for post in posts:
                x = {}
                url = post.image_url.split("/")
                url_image = "http://localhost:5000/photos/"+url[-2]+"/"+url[-1]
                x[url_image] = post.caption
                print(post.image_url)
                print(post.caption)
                data[post.id] = x
        except:
            pass
    print(data) 
    return jsonify(data), 200

#to get my posts
@app.route("/getmyposts")
def get_myposts():
    print("user id: ")
    print(usrid)
    posts = Post.query.filter_by(user_id=usrid)
    data = {}
    '''try:
        for post in posts:
            #x = {}
            url = post.image_url.split("/")
            url_image = "http://localhost:5000/photos/"+url[-2]+"/"+url[-1]
            print(url_image)
            data[url_image] = post.caption
            #x['caption'] = post.caption
            print(post.caption)
        #data[post.id] = x
        print(data)'''
    try:
        for post in posts:
            x = {}
            url = post.image_url.split("/")
            url_image = "http://localhost:5000/photos/"+url[-2]+"/"+url[-1]
            x[url_image] = post.caption
            print(post.image_url)
            print(post.caption)
            data[post.id] = x
        print(data)
    except:
        pass  
    return jsonify(data), 200

# post upload 
def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
# post upload
@app.route("/api/users/<int:user_id>/posts", methods=["POST"])
def upload_post(user_id):
    
    if "user_id" not in session or session["user_id"] != user_id:
        return jsonify({"message": "Authentication required"}), 401

    if "image" not in request.files:
        return jsonify({"message": "No image uploaded"}), 400
    image = request.files["image"]
    if image.filename == "":
        return jsonify({"message": "No image uploaded"}), 400
    if not allowed_file(image.filename):
        return jsonify({"message": "Invalid file type"}), 400
    caption = request.form.get("caption", "")

    # save to disk
    filename = secure_filename(image.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(filepath)

    image_url = filepath
    created_at = datetime.now()
    user_id = usrid
    print(image_url)
    print(caption)
    print(created_at)
    print(user_id)
    posts = Post.query.all()
    post_id = len(posts)
    # new post
    post = Post(image_url=image_url, caption=caption, created_at=created_at, user_id=user_id)
    db.session.add(post)
    db.session.commit()
    return jsonify({
        "id": post_id,
        "user_id": user_id,
        "image_url": filepath,
        "caption": caption
    }), 201

#to get user profile data
@app.route('/fetchdata')
def fetchdata():
    print(usrid)
    user = User.query.filter_by(id=usrid).first()
    posts = Post.query.filter_by(user_id=usrid)
    print(user)
    x = 0
    for post in posts:
        x+=1
    data = {}
    data['username'] = user.username
    data['numPosts'] = x
    if user.followers == "":
        data['numFollowers'] = 0
    else:
        data['numFollowers'] = len(user.followers.split(','))
    if user.following == "":
        data['numFollowing'] = 0
    else:
        data['numFollowing'] = len(user.following.split(','))
    
    print(data)
    return jsonify(data), 200

#to get other profile data
@app.route('/fetchdata/other', methods=['POST'])
def fetchdataother():
    data = request.get_json()
    PostId = (data.get('id'))
    print(PostId)
    the_post = Post.query.filter_by(id=PostId).first()
    UsrId = the_post.user_id
    print(UsrId)
    user = User.query.filter_by(id=UsrId).first()
    posts = Post.query.filter_by(user_id=UsrId)
    print(user)
    x = 0
    for post in posts:
        x+=1
    data = {}
    data['username'] = user.username
    data['numPosts'] = x
    if user.followers == "":
        data['numFollowers'] = 0
    else:
        data['numFollowers'] = len(user.followers.split(','))
    if user.following == "":
        data['numFollowing'] = 0
    else:
        data['numFollowing'] = len(user.following.split(','))
    
    
    print(data)
    return jsonify(data), 200

#search for accounts
@app.route('/searchaccounts', methods=['POST'])
def searchaccounts():
    data = request.get_json()
    search_string = data.get('searchStr')
    results = User.query.filter(User.username.like('%{}%'.format(search_string))).all()
    data = {}
    try:
        for result in results:
            x = {}
            x['id'] = result.id
            x['name'] = result.username
            data[result.id] = x
        print(data)
        return jsonify(data), 200
    except:
        return jsonify({'message': 'no match found'}), 404

#to fetch the accounts 
@app.route('/api/accounts')
def get_accounts():
    #cached_response = redis_client.get(request.url)
    '''if cached_response:
        acc = jsonpickle.decode(cached_response)
        return jsonify(acc)'''

    accounts = User.query.all()
    print(accounts)
    acc = {}
    for account in accounts:
        x = {}
        x['id'] = account.id
        x['name'] = account.username
        acc[account.id] = x
    print(acc)
    #redis_client.setex(request.url, 300, jsonpickle.encode(acc))
    return jsonify(acc), 200

#to follows
@app.route('/accounts/<int:id>/follow', methods=['POST'])
def follow_account(id):
    try:
        print(usrid)
        user = User.query.filter_by(id=usrid).first()
        print(user)
        account = User.query.filter_by(id=id).first()
        print(account)
        follow_data = user.following
        follow_data_1 = account.followers
        print(follow_data)
        print(follow_data.split(","))
        if str(account.id) not in follow_data.split(','):
            follow_data = follow_data + ","+ str(account.id)
            follow_data_1 = follow_data_1 + "," +str(account.id)
        user.following = follow_data.lstrip(',')
        account.followers = follow_data_1.lstrip(',')
        db.session.commit()
    
        return jsonify({'message': f'You are now following {account.username}'})
    except:
        return jsonify({'message': f'You already follow {account.username}'})        

#to unfollow
@app.route('/accounts/<int:id>/unfollow', methods=['POST'])
def unfollow_account(id):
    user = User.query.filter_by(id=usrid).first()
    account = User.query.filter_by(id=id).first()
    try:
        follow_data = user.following
        follow_data_1 = account.followers
        
        if len(follow_data.split(',')) > 1:
            follow_data = follow_data.split(',').remove(str(account.id))
            user.following = follow_data.join().lstrip(',')
        else:
            follow_data = ""
            user.following = follow_data

        if len(follow_data_1.split(',')) > 1:
            follow_data_1 = follow_data_1.split(',').remove(str(account.id))
            account.followers = follow_data_1.join().lstrip(',')
        else:
            follow_data_1 = ""
            account.followers = follow_data_1
        
        db.session.commit()

        return jsonify({'message': f'You have unfollowed {account.username}'})
    except :
        return jsonify({'message': f'You do not follow {account.username}'}) 

#send back pics to the frontend 
@app.route('/photos/upload/<filename>', methods=['GET'])
def get_pics(filename):
    updir = os.listdir('upload')
    print(updir)
    #pics = os.listdir('upload')
    #print(pics)
    return send_file(f'./upload/{filename}', mimetype='image/png')

#to export csv
@app.route('/export/csv', methods=['POST'])
def export_blogs_csv():
    posts = Post.query.filter_by(user_id=usrid)
    with open('blogs.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'image_url', 'caption', 'created_at','author'])
        for post in posts:
            user = User.query.filter_by(id=post.user_id).first()
            writer.writerow([post.id, post.image_url, post.caption, post.created_at, user.username])
    user = User.query.filter_by(id=usrid).first()
    data = {"name": user.username, "email":user.email}
    message = format_message("export_complete.html",data=data)
    attachment_file = 'blogs.csv'
    address = user.email
    subject = "Export complete"
    task = tasks.send_export_csv.delay(subject,attachment_file, message, address)
    return jsonify(str(task), 202)

#sample monthly mail 
@app.route('/monthlymail', methods=['POST'])
def sample_monthly():
    posts = Post.query.filter_by(user_id=usrid)
    with open('blogs.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'image_url', 'caption', 'created_at','author'])
        for post in posts:
            user = User.query.filter_by(id=post.user_id).first()
            writer.writerow([post.id, post.image_url, post.caption, post.created_at, user.username])
    user = User.query.filter_by(id=usrid).first()
    lastlogin = LastLogin.query.filter_by(id=usrid).first()
    data = {"name": user.username, "email":user.email, 'followers': user.followers, 'following': user.following, 'lastlogin': lastlogin.login_at}
    message = format_message("monthly_engagement.html",data=data)
    attachment_file = 'blogs.csv'
    address = user.email
    subject = "Monthly report"
    task = tasks.send_export_csv.delay(subject, attachment_file, message, address)
    return jsonify(str(task), 202)

#sample daily mail
@app.route('/dailymail', methods=['POST'])
def sample_daily():
    posts = Post.query.filter_by(user_id=usrid)
    with open('blogs.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'image_url', 'caption', 'created_at','author'])
        for post in posts:
            user = User.query.filter_by(id=post.user_id).first()
            writer.writerow([post.id, post.image_url, post.caption, post.created_at, user.username])
    user = User.query.filter_by(id=usrid).first()
    data = {"name": user.username, "email":user.email}
    message = format_message("daily_scheduled_mail.html",data=data)
    attachment_file = 'blogs.csv'
    address = user.email
    subject = "Daily Report"
    task = tasks.send_export_csv.delay(subject,attachment_file, message, address)
    return jsonify(str(task), 202)
     
'''
celery.conf.beat_schedule = {
    'send_emails_every_30_secs': {
        'task': 'send_emails_every_30_secs',
        'schedule': 30.0
    },
    'scheduled_task': {
        'task': 'schduled_task',
        'schedule': crontab(hour=17, minute=0, day_of_week='*')
    }
}'''

@app. route ("/hello", methods=["GET", "POST"])
def hello():
    job = tasks.just_say_hello.delay('harsehraab')
    return str(job), 200

if __name__ == '__main__':    
   app.run(debug=True)
   celery.start()
   scheduled_task()