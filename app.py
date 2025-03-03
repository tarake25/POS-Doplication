from flask import Flask, render_template, request, send_file, redirect, url_for, session
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# Dummy credentials
VALID_USERNAME = 'aymen'
VALID_PASSWORD = '010203'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded files
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')

        if not file1 or not file2:
            return "Error: Both Excel files are required."

        # Secure filenames and save the files
        filename1 = secure_filename(file1.filename)
        filename2 = secure_filename(file2.filename)

        filepath1 = os.path.join(UPLOAD_FOLDER, filename1)
        filepath2 = os.path.join(UPLOAD_FOLDER, filename2)

        file1.save(filepath1)
        file2.save(filepath2)

        try:
            # Read Excel files
            df = pd.read_excel(filepath1)
            df1 = pd.read_excel(filepath2)

            #SEARCH THE DATA BASE FOR OUR POS
            df_fin = pd.DataFrame({})
            for i in range(len(df1)):
                for j in range(len(df)):
                    if df1.iat[i, 0] == df.iat[j, 1]:

                        df_fin = pd.concat([df_fin, df.iloc[[j]]],
                                           ignore_index=True)

            df_fin = df_fin.sort_values(by='Code POS')

            df_db = pd.DataFrame({})
            j = 0
            for i in range(len(df_fin) - 1):
                if df_fin.iat[i, 1] != df_fin.iat[i + 1, 1]:
                    df_db = pd.concat([df_db, df_fin.iloc[[i]]],
                                      ignore_index=True)
                    df_db.iat[j, 2] = df_fin.iat[
                        i, 1] + f"-{int(df_fin.iat[i,2][-1])+1}"
                    j = j + 1
            if df_fin.iat[i, 1] != df_fin.iat[i + 1, 1]:
                df_db = pd.concat([df_db, df_fin.iloc[[i]]], ignore_index=True)
                df_db.iat[j,
                          2] = df_fin.iat[i + 1,
                                          1] + f"-{int(df_fin.iat[i,2][-1])+1}"

            output_path = os.path.join(UPLOAD_FOLDER, 'processed.xlsx')
            df_db.to_excel(output_path, index=False)

            # Clean up: Delete uploaded and processed files after sending
            response = send_file(output_path, as_attachment=True)

            os.remove(filepath1)
            os.remove(filepath2)
            os.remove(output_path)

            return response

        except Exception as e:
            return f"Error processing files: {e}"

    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['user'] = username
            return redirect(url_for('index'))

        return "Invalid credentials, try again."
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
