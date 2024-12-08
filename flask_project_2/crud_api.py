''' 
run by command "flask run", to run it by this command:
Set the FLASK_APP Environment Variable: Tell Flask where your application is located. 
Run the following in your terminal (assuming your file is named app.py):
On Linux/macOS:  export FLASK_APP=app.py
On Windows (Command Prompt): set FLASK_APP= app.py  (in this case "crud_api.py" )

'''


from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

# Initialize Flask app
app = Flask(__name__)

# Update to use MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/task_manager"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Define the Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    done = db.Column(db.Boolean, default=False)

# Define the Marshmallow Schema for Task
class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True  # Return SQLAlchemy models on deserialization

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# Routes

## Get all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify(tasks_schema.dump(tasks))

## Get a single task by ID
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task_schema.dump(task))

## Create a new task
@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        new_task = task_schema.load(data, session= db.session)
        db.session.add(new_task)
        db.session.commit()
        return jsonify(task_schema.dump(new_task)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400







## Update a task (PUT)
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if request.is_json:
        data = request.get_json()
        try:
            # Use schema to load and validate the data
            updated_task = task_schema.load(data, session=db.session)
            
            # Replace the task's existing data with the new values
            task.title = updated_task.title
            task.description = updated_task.description
            task.done = updated_task.done

            db.session.commit()
            return jsonify(task_schema.dump(task)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
    else:
        return jsonify({"error": "Invalid content type, JSON expected"}), 400



## Partially update a task (PATCH)
@app.route('/tasks/<int:task_id>', methods=['PATCH'])
def partial_update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if request.is_json:
        data = request.get_json()
        try:
            # Load data using schema, but don't overwrite all attributes
            updated_task = task_schema.load(data, session=db.session)

            # Only update provided fields
            if 'title' in data:
                task.title = updated_task.title
            if 'description' in data:
                task.description = updated_task.description
            if 'done' in data:
                task.done = updated_task.done

            db.session.commit()
            return jsonify(task_schema.dump(task)), 200
        except ValidationError as err:
            return jsonify(err.messages), 400
    else:
        return jsonify({"error": "Invalid content type, JSON expected"}), 400





@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    # Look up the task by ID
    task = Task.query.get(task_id)
    if not task:
        # Return an error if the task does not exist
        return jsonify({"error": "Task not found"}), 404
    
    # Delete the task
    db.session.delete(task)
    db.session.commit()
    
    # Return a success message
    return jsonify({"message": "Task deleted successfully" , "task": task_schema.dump(task)}), 200


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
