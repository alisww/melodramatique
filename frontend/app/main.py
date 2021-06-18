from quart_auth import (
    AuthUser,
    AuthManager,
    Unauthorized,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from quart import Quart, jsonify, render_template, request, url_for, redirect

from db import *

import yaml, os, datetime, uuid

import traceback

with open("schema.yaml") as f:
    schema = yaml.safe_load(f)

app = Quart(__name__)
app.config["JSON_AS_ASCII"] = False
app.secret_key = os.environ["SECRET"]
auth = AuthManager(app)
db = MelodramatiqueDB(app, os.environ["DATABASE_URL"])


def convert(f, t, val):
    if f == "semicolon_list" and t == "tag_array":
        return list(filter(None,val.split(";")))
    elif f == "pipe_list" and t == "tag_array":
        return list(filter(None,val.split("|")))
    elif f == "single" and t == "tag_array":
        return [val]
    elif f == "datestring" and t == "timestamp":
        return (
            datetime.datetime(1970, 1, 1) - datetime.datetime.strptime(val, "%d/%m/%Y")
        ).days

def deconvert(f, t, val):
    if f == "semicolon_list" and t == "tag_array":
        return ';'.join(val)
    elif f == "pipe_list" and t == "tag_array":
        return '|'.join(val)
    elif f == "single" and t == "tag_array":
        return val[0]
    elif f == "datestring" and t == "timestamp":
        return (
            datetime.datetime(1970, 1, 1) + datetime.timedelta(days=val)
        ).strftime("%d/%m/%Y")

@app.route("/submit", methods=["GET", "POST"])
@login_required
async def submit():
    if request.method == "GET":
        if "id" in request.args:
            presets = await db.get_by_id(request.args["id"])
            for k,v in presets.items():
                if k in schema:
                    presets[k] = deconvert(schema[k]["converter"]["from"], schema[k]["converter"]["to"],v) if "converter" in schema[k] else v
            presets["id"] = request.args["id"]
        else:
            presets = {}
        return await render_template("schema.html.j2", presets=presets, schema=schema)
    else:
        data = await request.get_json()
        res = {}
        try:
            for k, v in data.items():
                if k in schema:
                    res[k] = (
                        convert(
                            schema[k]["converter"]["from"],
                            schema[k]["converter"]["to"],
                            v,
                        )
                        if "converter" in schema[k]
                        else v
                    )

            if 'id' in data:
                await db.add_doc(res,doc_id=uuid.UUID(data['id']))
            else:
                await db.add_doc(res)

            print(res)
            return {"status": 200}, 200
        except Exception as e:
            print(e)
            traceback.print_exc()
            return {"status": 500}, 500


@app.route("/")
async def search():
    return await render_template("search.html.j2",logged_in=(await current_user.is_authenticated))


@app.route("/login", methods=["GET", "POST"])
async def login():
    if request.method == "GET":
        return await render_template("login.html.j2")
    elif request.method == "POST":
        form = await request.form
        if await db.check_user(form["user"], form["pw"]):
            login_user(AuthUser(form["user"]))
            return redirect(url_for("submit"))
        else:
            return await render_template("login.html.j2", error=True)


@app.route("/tags/<field>", methods=["GET"])
async def tags(field):
    return jsonify(await db.get_tags(field))


@app.route("/logout")
async def logout():
    logout_user()
    return redirect(url_for("search"))


@app.errorhandler(Unauthorized)
async def redirect_to_login(*_):
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
