from django.shortcuts import render, HttpResponse, redirect

def auth(func):
    def inner(req, *arg, **kw):
        is_login = req.session.get("is_login", False)
        username = req.session.get("username")
        password = req.session.get("password")
        # print(is_login,type(is_login))
        if is_login and username and password:
            return func(req, *arg, **kw)
        else:
            return redirect("/login")
    return inner