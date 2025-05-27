from flask import Flask, request, jsonify
from openai import OpenAI
from pymongo import MongoClient
from config import OPENAI_API_KEY
from pymongo.errors import PyMongoError

app = Flask(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/generate", methods=["POST"])
def generate_text():
    data = request.get_json()
    prompt = data.get("prompt", "")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        message = response.choices[0].message.content
        return jsonify({"response": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Connect to MongoDB (local or Mongo Atlas connection string)
client = MongoClient("mongodb+srv://ivar06516:pplDdQwIyGPyk7jQ@cluster0.3u1bntz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # replace with your Mongo URI
db = client["vendor_evaluation_db"]  # replace with your database name
collection = db["vendor_evaluation_collection"]  # replace with your collection name

@app.route("/loaddata", methods=["POST"])
def add_document():
    try:
        data = request.json  # Get JSON payload from request

        if not data:
            return jsonify({"error": "No data provided"}), 400
        # Insert data into collection
        result = collection.insert_one(data)
        return jsonify({"message": "Document inserted", "id": str(result.inserted_id)}), 201

    except PyMongoError as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
