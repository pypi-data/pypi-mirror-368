from flask import Blueprint, make_response, request

from abstra_internals.jwt_auth import USER_AUTH_COOKIE_KEY
from abstra_internals.repositories.authn import authn_repository_factory

from .templates.render import render


def get_login_bp():
    bp = Blueprint("login", __name__)
    authn = authn_repository_factory()
    def check_redirect_url():
        args_redirect_url = request.args.get("redirect_url")
        form_redirect_url = request.form.get("redirect_url")
        redirect_url = args_redirect_url or form_redirect_url or "/"
        if redirect_url is None:
            raise ValueError("redirect_url is required")
        return redirect_url

    def create_redirect(url: str):
        response = make_response(url)
        response.headers["HX-Redirect"] = url
        response.delete_cookie(USER_AUTH_COOKIE_KEY)
        return response

    @bp.get("/")
    def _login():
        redirect_url = check_redirect_url()
        return render(
            template=["page", "get_email"],
            context=dict(
                redirect_url=redirect_url
            ))
    
    @bp.delete("/")
    def _logout():
        return create_redirect("/")
    
    @bp.post("/claim_email")
    def _claim_email():
        redirect_url = check_redirect_url()
        email = request.form["email"]
        ok = authn.authenticate(email)
        if not ok:
            return render(
                template=["page", "get_email"],
                context=dict(
                    errors=["Something went wrong. Please try again."],
                    redirect_url=redirect_url
                )
            )
        return render(
            template=["page", "get_token"],
            context=dict(
                redirect_url=redirect_url,
                email=email
            ))
    
    @bp.post("/claim_token")
    def _claim_token():
        redirect_url = check_redirect_url()
        email = request.form["email"]
        token = request.form["token"]
        jwt = authn.verify(email, token)
        if jwt is None:
            return render(
                template=["page", "get_token"],
                context=dict(
                    errors=["Invalid token. Please try again."],
                    redirect_url=redirect_url,
                    email=email
                )
            )
        response = create_redirect(redirect_url)
        response.set_cookie(USER_AUTH_COOKIE_KEY, jwt)
        return response

    return bp