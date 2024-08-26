from flask import request, jsonify, send_file
from app import app, db, load_csv_data
from tasks import generate_report
import uuid
import os

@app.route('/trigger_report', methods=['POST'])
def trigger_report():
  report_id = str(uuid.uuid4())
  task = generate_report.apply_async(args=[report_id])
  return jsonify({'report_id': report_id}), 202

@app.route('/get_report', methods=['GET'])
def get_report():
  report_id = request.args.get('report_id')
  task = generate_report.AsyncResult(report_id)

  if task.state == 'PENDING':
    response = {
      'state': task.state,
      'status': 'Running'
    }
  elif task.state != 'FAILURE':
    if task.state == 'SUCCESS':
      return send_file(task.result, as_attachment=True, attachment_filename=f'report_{report_id}.csv')
    else:
      response = {
        'state': task.state,
        'status': 'Running'
      }
  else:
    response = {
      'state': task.state,
      'status': str(task.info)
    }
  return jsonify(response)

if __name__ == "__main__":
  with app.app_context():
    if not os.path.exists('store_data.db'):
      db.create_all()
      load_csv_data()
  app.run(debug=True)
