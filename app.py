from flask import Flask, request, redirect, render_template, url_for, session
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
app = Flask(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app.secret_key = os.getenv('SECRET_KEY')

@app.route('/')
def switchboard():
    if 'user_id' in session:
        return redirect(url_for('dash'))
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            data = supabase.auth.sign_in_with_password({
                "email":email,
                "password": password
            })

            session['supabase_session'] = data.session.access_token

            session['user_id'] = data.user.id

            return redirect(url_for('dash'))
        
        except Exception as e:
            return f'Error occured: {e}'
        
    return render_template('login.html')

@app.route('/register',methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        response = supabase.auth.sign_up({
            "email":email,
            "password" : password,
            "options" : {
                "data":{
                    'name':name
                }
            }
        })

        if response.user:
            return redirect(url_for('login'))
        
        else:
            return 'Registration Failed'

    return render_template('register.html')

@app.route('/dashboard', methods=['GET','POST'])
def dash():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # values that needed
    # 1. Total Projects [] 2. Active Projects [] 3.hold Projects [] 4. Compeleted Projects []
    # Project_name, project description,  progress value, module compeleted
        # get the data from the SUPABASE Table
        # reference r example data

    user_id = session['user_id']
        # Fetch projects from correct table
    proj_data = supabase.table('projects').select('*').eq('id', user_id).execute().data
    mod_data  = supabase.table('modules').select('*').execute().data

    proj_title = []
    Type = []
    project_desc = []
    proj_data = supabase.table('projects').select('*').eq('id', user_id).execute().data

    projects = [{'title': p['title'], 'status': p['status'], 'description': p['description']} for p in proj_data]

    return render_template('dashboard.html',
                        Total_Projects      = len(proj_data),
                        Active_projects     = sum(1 for p in proj_data if p['status'] == 'active'),
                        Holded_projects     = sum(1 for p in proj_data if p['status'] == 'on-hold'),
                        Completed_projects  = sum(1 for p in proj_data if p['status'] == 'completed'),
                        projects            = projects)

    

@app.route('/newproj', methods=['GET', 'POST'])
def create_project():
    token = session.get('supabase_session')
    user_id = session.get('user_id')

    if not token or not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        proj_name = request.form.get('name')
        desp = request.form.get('description')
        rtype = request.form.get('status')

        raw_id = os.urandom(4).hex()
        proj_id = proj_name[:3] + raw_id  # os.urandom(4) is bytes, .hex() makes it a clean string

        data = {
            'id': session['user_id'],
            'proj_id': proj_id,
            'title': proj_name,
            'description': desp,
            'status': rtype
        }

        try:
            supabase.table('projects').insert(data).execute()
            session['current_proj_id'] = proj_id  # ← store it in session
            return redirect(url_for('daahboard'))
        except Exception as e:
            return f"Database error: {str(e)}"

    return render_template('create_project.html')

if __name__ == '__main__':
    app.run()
