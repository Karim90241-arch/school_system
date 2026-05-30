from flask import Flask, render_template, request, redirect, url_for, session, Response

app = Flask(__name__)
app.secret_key = 'super_secret_laptop_key'

# قاعدة البيانات الحية للأقسام السبعة
sections_data = {
    "إعلام آلي (ميكرو-إنفورماتيك)": [
        {"id": 101, "name": "أحمد محمد", "parent_phone": "+213555123456", "status": "حاضر"},
        {"id": 102, "name": "سارة علي", "parent_phone": "+213666987654", "status": "غائب"},
        {"id": 103, "name": "عماد مراد", "parent_phone": "+213777888999", "status": "حاضر"}
    ],
    "كهرباء معماري": [
        {"id": 201, "name": "ياسين كمال", "parent_phone": "+213777112233", "status": "حاضر"},
        {"id": 202, "name": "ليندة كريم", "parent_phone": "+213555443322", "status": "غائب"}
    ],
    "ميكانيك خودرو": [],
    "إلكترونيات صناعية": [],
    "تسيير الموارد البشرية": [],
    "محاسبة وتسيير": [],
    "أمانة مكتبية": []
}

def get_all_trainees():
    all_t = []
    for sec, t_list in sections_data.items():
        for t in t_list:
            all_t.append({"id": t['id'], "name": t['name'], "section": sec, "parent_phone": t['parent_phone'], "status": t['status']})
    return all_t

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth():
    if request.form.get('username') == 'admin' and request.form.get('password') == '1234':
        session['user'] = 'admin'
        return redirect(url_for('dashboard'))
    return "خطأ في الدخول! <a href='/'>عودة</a>"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', total=len(get_all_trainees()), absent=len([t for t in get_all_trainees() if t['status'] == 'غائب']))

@app.route('/register', methods=['GET', 'POST'])
def register_trainee():
    if 'user' not in session: return redirect(url_for('login'))
    list_of_sections = ["إعلام آلي (ميكرو-إنفورماتيك)", "كهرباء معماري", "ميكانيك خودرو", "إلكترونيات صناعية", "تسيير الموارد البشرية", "محاسبة وتسيير", "أمانة مكتبية"]
    if request.method == 'POST':
        section = request.form.get('section').strip()
        bulk_names = request.form.get('bulk_names')
        default_phone = request.form.get('default_phone')
        if section not in sections_data: sections_data[section] = []
        if section and bulk_names:
            names_list = [name.strip() for name in bulk_names.split('\n') if name.strip()]
            for name in names_list:
                new_id = len(get_all_trainees()) + 101
                sections_data[section].append({"id": new_id, "name": name, "parent_phone": default_phone if default_phone else "+213000000000", "status": "حاضر"})
            return redirect(url_for('sections_page'))
    return render_template('register.html', sections=list_of_sections)

@app.route('/trainees')
def trainees_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('trainees.html', trainees=get_all_trainees())

@app.route('/sections')
def sections_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('sections.html', sections=sections_data)

@app.route('/toggle_status/<int:t_id>')
def toggle_status(t_id):
    if 'user' not in session: return redirect(url_for('login'))
    for sec, t_list in sections_data.items():
        for t in t_list:
            if t['id'] == t_id:
                t['status'] = 'غائب' if t['status'] == 'حاضر' else 'حاضر'
                break
    return redirect(url_for('trainees_page'))

@app.route('/send_sms_ajax/<int:t_id>')
def send_sms_ajax(t_id): return "success"

# مسار الإحصائيات العامة المطور لحساب بيانات الـ 7 أقسام تلقائياً
@app.route('/stats')
def stats_page():
    if 'user' not in session: return redirect(url_for('login'))
    
    # بناء قاموس الإحصائيات لكل قسم
    stats_summary = {}
    for section_name, trainees in sections_data.items():
        total = len(trainees)
        absent = len([t for t in trainees if t['status'] == 'غائب'])
        present = total - absent
        # حساب نسبة الحضور المئوية بأمان منعاً للقسمة على صفر
        rate = round((present / total) * 100) if total > 0 else 0
        
        stats_summary[section_name] = {
            "total": total,
            "present": present,
            "absent": absent,
            "rate": rate
        }
    
    return render_template('stats.html', stats=stats_summary)

@app.route('/export_excel')
def export_excel():
    if 'user' not in session: return redirect(url_for('login'))
    csv_data = "\uFEFF" + "القسم,العدد الكلي,حاضر,غائب\n"
    return Response(csv_data, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=report.csv"})

@app.route('/qrcodes')
def qrcodes_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('qrcodes.html', trainees=get_all_trainees())

@app.route('/settings')
def settings():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('settings.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)