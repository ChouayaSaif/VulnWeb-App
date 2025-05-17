from flask import session, redirect

def logout():
    session.pop('username', None)
    return redirect('/')