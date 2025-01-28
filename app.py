from flask import Blueprint, Flask, render_template, request, redirect
from sqlalchemy import desc, select

from database import db, DATABASE_URI
from models.todo import Todo

root_blueprint = Blueprint("root", __name__)


@root_blueprint.route("/")
def index():
    todos = db.session.execute(select(Todo)).scalars()
    sorted_todos = sorted(list(todos), key=lambda x: x.index)
    return render_template("index.html", todos=sorted_todos)


@root_blueprint.post("/add")
def add():
    last_todo = db.session.query(Todo).order_by(desc(Todo.index)).first()

    title = request.form.get("title")

    new_todo = Todo(title=title, index=last_todo.index + 1)

    db.session.add(new_todo)
    db.session.commit()

    return redirect("/")

@root_blueprint.post("/up/<int:todo_id>")
def up(todo_id):
    todos = db.session.execute(select(Todo)).scalars()
    todos = sorted(list(todos), key=lambda x: x.index)

    curr_todo_index = None

    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            curr_todo_index = i
            break

    if curr_todo_index != None and curr_todo_index != 0:
        todos[curr_todo_index], todos[curr_todo_index - 1] = todos[curr_todo_index - 1], todos[curr_todo_index]

    for i, todo in enumerate(todos):
        todo.index = i

    db.session.commit()

    return redirect("/")

@root_blueprint.post("/down/<int:todo_id>")
def down(todo_id):
    todos = db.session.execute(select(Todo)).scalars()
    todos = sorted(list(todos), key=lambda x: x.index)

    curr_todo_index = None

    for i, todo in enumerate(todos):
        if todo.id == todo_id:
            curr_todo_index = i
            break

    if curr_todo_index != None and curr_todo_index != len(todos) - 1:
        todos[curr_todo_index], todos[curr_todo_index + 1] = todos[curr_todo_index + 1], todos[curr_todo_index]

    for i, todo in enumerate(todos):
        todo.index = i

    db.session.commit()

    return redirect("/")


@root_blueprint.post("/complete/<int:todo_id>")
def complete(todo_id):
    statement = select(Todo).where(Todo.id == todo_id)
    todo = db.session.execute(statement).scalar_one()
    todo.completed = True
    db.session.commit()

    return redirect("/")


@root_blueprint.post("/delete/<int:todo_id>")
def delete(todo_id):
    statement = select(Todo).where(Todo.id == todo_id)
    todo = db.session.execute(statement).scalar_one()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


def initialize_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI

    db.init_app(app)

    app.register_blueprint(root_blueprint)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    initialize_app().run(debug=True)
