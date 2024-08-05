from werkzeug.security import generate_password_hash, check_password_hash

class Pass_hashing:
  def __init__(self):
    pass

  def hashing_pass(self,password):
    hashed = generate_password_hash(password)
    return hashed

  def verify_pass(self,hashed,password):
    if check_password_hash(hashed,password):
      return True
    else:
      return False
