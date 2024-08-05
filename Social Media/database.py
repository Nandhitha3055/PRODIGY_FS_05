import sqlite3
conn = sqlite3.connect("Users.db",check_same_thread=False)

c = conn.cursor()
class UserClass:
  def __init__(self):
      pass
  def create_table(self):
      with conn:
        c.execute('''CREATE TABLE IF NOT EXISTS users(
        First_Name TEXT, 
        Last_Name TEXT,
        Phone_Number INTEGER ,
        Email TEXT PRIMARY KEY,
        Image TEXT,
        Password TEXT,
        User_Type TEXT)''')
  def followTable(self):
    c.execute('''create TABLE IF NOT EXISTS follow(
    user TEXT,
    following TEXT)''')
  def post_table(self):
    with conn:
      c.execute('''CREATE TABLE IF NOT EXISTS posts(
      Id TEXT, 
      Post_Id INTEGER PRIMARY KEY AUTOINCREMENT,
      Title TEXT,
      Content TEXT,
      FOREIGN KEY (Id) REFERENCES users(Email) )''')

  def comment_table(self):
    with conn:
      c.execute('''CREATE TABLE IF NOT EXISTS comments(
      commenter TEXT, 
      Post_Id INTEGER,
      comment TEXT,
      FOREIGN KEY (Post_Id) REFERENCES posts(Post_Id) )''')

  
  def insert_user(self,first_name,last_name,phone_number,email,file_path,password,user_type):
      with conn:
        c.execute("INSERT INTO users(First_Name, Last_Name,Phone_Number, Email,Image, Password,User_Type) VALUES(?,?,?,?,?,?,?)",
                  (first_name,last_name,phone_number,email,file_path,password,user_type))

  def delete_User(self,email):
      with conn:
        c.execute(f"DELETE FROM posts WHERE Id = '{email}'")
        c.execute(f"DELETE FROM users WHERE Email = '{email}'")

  def existing_User(self,email):
      c.execute(f"SELECT * FROM users WHERE Email = '{email}'")
      if c.fetchone() is None:
        return False
      else:
        return True

  def get_user(self,email):
    c.execute(f"SELECT Password FROM users WHERE Email = '{email}'")
    result = c.fetchone()
    if result:
        return result[0]
    else:
        return None

  def get_user_details(self,email):
        c.execute(f"SELECT * FROM users WHERE Email = '{email}'")
        result = c.fetchone()
        return result

  def get_user_type(self,email):
      c.execute(f"SELECT User_Type FROM users WHERE Email = '{email}'")
      return c.fetchone()[0]
    
  def all_user(self):  
    c.execute("SELECT Email,First_Name FROM users WHERE User_Type = 'User'")
    result = c.fetchall()
    leng = len(result)  
    return [result,leng]  
      
  def get_user_img(self,email):
    c.execute(f"SELECT Image FROM users WHERE Email = '{email}'") 
    return c.fetchone()[0]


  # functions for posts =================================================
  def insert_post(self,title,content,email):
    with conn:
      c.execute("INSERT INTO posts(Id,Title,Content) VALUES(?,?,?)",(email,title,content))
  
  def get_post(self,email):
    c.execute(f"SELECT * FROM posts WHERE Id = '{email}'")
    result = c.fetchall()
    return result

  def getPost(self,postId):
    c.execute(f"SELECT * FROM posts where Post_Id = ?",(postId,) )
    result = c.fetchone()
    return result
  
  def get_others_post(self,email):
    c.execute(f"SELECT * FROM posts")
    result = c.fetchall()
    return result
  def delete_post(self,postId):
    with conn:
      c.execute(f"DELETE FROM posts WHERE Post_Id = '{postId}'")
#Table for comments================================================
  def insert_comment(self,commenter,postId,comment):
    with conn:
      c.execute("INSERT INTO comments(commenter,Post_Id,comment) VALUES(?,?,?)",(commenter,postId,comment))
  def get_comments(self,postId):
    c.execute(f"SELECT * FROM comments WHERE Post_Id = '{postId}'")
    result = c.fetchall()
    return result
  def addFollower(self,userId,following):
    c.execute(f"SELECT * from follow where user = ? and following = ?",(userId,following))
    follower = c.fetchone()
    if not follower:
      with conn:
          c.execute(f"INSERT INTO follow(user,following) VALUES(?,?)",(userId,following))
  def removeFollower(self,userId,following):
    c.execute(f"SELECT * from follow where user = ? and following = ?",(userId,following))
    follower = c.fetchone()
    if follower:
      with conn:
        c.execute(f"DELETE FROM follow where user = ? and following = ?",(userId,following))
        
  def getFollower(self,userId):
    c.execute(f"SELECT following from follow where user = ?",(userId,))
    restructureFollowers = []
    for i in c.fetchall():
        restructureFollowers.append(i[0])
    return restructureFollowers
    
  def getMyFollowers(self,userId):
    c.execute(f"SELECT user from follow where following = ?",(userId,))
    restructureFollowers = []
    for i in c.fetchall():
        restructureFollowers.append(i[0])
    return restructureFollowers
    
  def isFollowing(self,userId,following):
    c.execute(f"SELECT * from follow where user = ? and following = ?",(userId,following))
    
    return c.fetchone()