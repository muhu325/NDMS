from django.shortcuts import render, HttpResponse, redirect

def login(req):
    if req.method == "POST":
        username = req.POST.get("username")
        password = req.POST.get("password")
        req.session["is_login"] = True
        req.session["username"] = username
        req.session["password"] = password
        return redirect("/query_crt")
    else:
        return render(req, "login.html")


def logout(req):
    req.session.clear()
    return redirect("/login")


