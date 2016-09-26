from app import app
app.secret_key = 'xyz'
app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
