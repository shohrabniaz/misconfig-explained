from flask import Flask, render_template, request
import core

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result, error, content, filename = None, None, "", "main.tf"
    if request.method == "POST":
        content = request.form.get("content", "")
        filename = request.form.get("filename") or "main.tf"
        up = request.files.get("file")
        if up and up.filename:
            filename, content = up.filename, up.read().decode("utf-8", "replace")
        try:
            result = core.analyse(content, filename)
        except Exception as e:
            error = str(e)
    return render_template("index.html", result=result, error=error, content=content, filename=filename)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
