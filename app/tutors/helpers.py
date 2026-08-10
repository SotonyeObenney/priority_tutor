from flask import Flask, abort, request
from flask_login import current_user
from functools import wraps

def tutor_required(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
      if current_user.is_tutor:
        return func(*args, **kwargs)
      else: 
        #Link this to an error page sha
        abort(403)
  return wrapper