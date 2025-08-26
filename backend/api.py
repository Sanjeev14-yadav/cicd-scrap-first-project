from flask import Flask, jsonify, request
import math
import pymysql

app = Flask(__name__)
# --- Database Configuration ---
#flask cors removed here
db_config = {
     'host': 'cicdrdsdb.cjgiuuuoiuzk.ap-south-1.rds.amazonaws.com',
     'user': 'admin',
     'password': 'password123',
     'database': 'dbtenders'
}
#
# --- DB Helper ---
def query_db(query, args=(), one=False):
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, args)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return (result[0] if result else None) if one else result
    except Exception as e:
        return {"error": str(e)}

# --- Routes ---

@app.route('/get-tenders', methods=['GET'])
def get_tenders():
    try:
        tenders = query_db("SELECT * FROM mytender")
        return jsonify(tenders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-name/<tender_id>', methods=['GET'])
def get_tender_name(tender_id):
    try:
        result = query_db("SELECT work_description FROM mytender WHERE tender_id = %s", (tender_id,), one=True)
        if result:
            return jsonify(result)
        return jsonify({"error": "Tender not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-page', methods=['GET'])
def get_paginated_tenders():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit

        tenders = query_db("SELECT * FROM mytender LIMIT %s OFFSET %s", (limit, offset))
        total = query_db("SELECT COUNT(*) as count FROM mytender", one=True)['count']
        return jsonify({"page": page, "limit": limit, "total": total, "tenders": tenders})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-by-organisation/<organisation>', methods=['GET'])
def get_by_organisation(organisation):
    try:
        result = query_db("SELECT * FROM mytender WHERE tender_organisation LIKE %s", ('%' + organisation + '%',))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/post-page', methods=['GET', 'POST'])
def post_page_data():
    try:
        if request.method == 'GET':
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        else:
            data = request.get_json()
            page = int(data.get('page', 1))
            limit = int(data.get('limit', 10))

        offset = (page - 1) * limit
        total_entries = query_db("SELECT COUNT(*) as count FROM mytender", one=True)['count']
        total_pages = math.ceil(total_entries / limit)
        tenders = query_db("SELECT * FROM mytender LIMIT %s OFFSET %s", (limit, offset))

        return jsonify({
            "page": page,
            "limit": limit,
            "total_entries": total_entries,
            "total_pages": total_pages,
            "tenders": tenders
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Main ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
