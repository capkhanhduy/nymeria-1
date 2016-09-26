from flask import *
import subprocess
from datetime import datetime
from app import app
import hashlib
import base64
from models import *
from pagination import Pagination
from checkpid import check_pid


@app.template_filter('timesince')
def timesince(time=False):
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


@app.before_request
def check_login():
    if (not 'gid' in session or session['gid'] <= 0) and (request.endpoint != 'login' and '/static/' not in request.path):
        return redirect(url_for('login'))

@app.route('/start', methods=['POST', 'GET'])
def start():
    if check_pid(settings.get_all().pid) == False:
        p = subprocess.Popen(["python", "app//track.py"], shell=True)
        settings.update_pid(p.pid)
        return 'Tracking is running with pid '+str(p.pid)
    return 'Tracking is already running'
@app.route('/', methods=['POST', 'GET'], defaults={'page': 1})
@app.route('/index', methods=['POST', 'GET'], defaults={'page': 1})
@app.route('/page/<int:page>', methods=['POST', 'GET'])
@app.route('/index/page/<int:page>', methods=['POST', 'GET'])
def index(page):

    return render_template('index.html',m_count_users=m_count_users(),m_count_sites=m_count_sites(),\
                           m_count_blacklist=m_count_blacklist(),m_list_sites=m_list_sites(),m_count_waf_log=m_count_waf_log(),\
                           m_count_antiddos_log=m_count_antiddos_log(),m_list_blacklist=m_list_blacklist())


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = m_login(username,password)
        if result > 0:
            session['username'] = str(username)
            session['gid'] = str(result)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'GET':
        return render_template('add.html',m_count_users=m_count_users(),m_count_sites=m_count_sites(),\
                           m_count_blacklist=m_count_blacklist(),m_count_waf_log=m_count_waf_log(),\
                           m_count_antiddos_log=m_count_antiddos_log())
    else:
        domain = request.form['domain']
        ip = request.form['ip']
        port = request.form['port']
        m_add_site(domain,ip,port)
        return render_template('add.html',m_count_users=m_count_users(),m_count_sites=m_count_sites(),\
                           m_count_blacklist=m_count_blacklist(),m_count_waf_log=m_count_waf_log(),\
                           m_count_antiddos_log=m_count_antiddos_log())

@app.route('/detail', methods=['GET'])
def detail():
    if request.method == 'GET':
        get_site = request.args.get('site')
        return render_template('detail.html',m_list_log=m_list_log(get_site),m_list_waf_log=m_list_waf_log(get_site))

@app.route('/setting', methods=['POST', 'GET'])
def setting():
    if request.method == 'GET':
        return render_template('setting.html',m_count_users=m_count_users(),m_count_sites=m_count_sites(),\
                           m_count_blacklist=m_count_blacklist(),m_count_waf_log=m_count_waf_log(),\
                           m_count_antiddos_log=m_count_antiddos_log())
    else:
        get_url = request.form['url']
        if sites.add(get_url, 'Normal', 'error') == -1:
            return render_template('setting.html', m_count_users=m_count_users(),m_count_sites=m_count_sites(),\
                           m_count_blacklist=m_count_blacklist(),m_count_waf_log=m_count_waf_log(),\
                           m_count_antiddos_log=m_count_antiddos_log())
        else:
            return render_template('setting.html',m_count_users=m_count_users(),m_count_sites=m_count_sites(),\
                           m_count_blacklist=m_count_blacklist(),m_count_waf_log=m_count_waf_log(),\
                           m_count_antiddos_log=m_count_antiddos_log())

@app.route('/logs', methods=['POST', 'GET'], defaults={'page': 1})
@app.route('/logs/page/<int:page>', methods=['POST', 'GET'])
def logs(page):
    if request.method == 'POST':
        if request.form['submit'] == 'deleteall':
            list_checkbox = request.form.getlist('deleteChk')
            for item in list_checkbox:
                logs_obj.delete(item)
            count = logs_obj.count_all_logs()['all']
            result = logs_obj.get_logs_for_page(page, 20, count)
            pagination = Pagination(page, 20, count)
            return render_template('logs.html', pagination=pagination, result=result)
        elif request.form['submit'] == 'search':
            pattern = request.form['pattern']
            pattern = base64.b64encode(pattern)
            return redirect(url_for('search', pattern=pattern, page=1))
    count = logs_obj.count_all_logs()['all']
    result = logs_obj.get_logs_for_page(page, 20, count)
    pagination = Pagination(page, 20, count)
    return render_template('logs.html', pagination=pagination, result=result)


@app.route('/general', methods=['POST', 'GET'])
def general_func():
    if request.method == 'POST':
        get_duration = request.form['duration']
        get_timeout = request.form['timeout']
        get_retry = request.form['retry']
        settings.update_duration(get_duration)
        settings.update_timeout(get_timeout)
        settings.update_retry(get_retry)
        return render_template('general.html', settings=settings.get_all(), success=1)

    return render_template('general.html', settings=settings.get_all())


@app.route('/alert', methods=['POST', 'GET'])
def alert():
    if request.method == 'POST':
        get_phonenumber = request.form['phonenumber']
        get_emailto = request.form['emailto']
        get_checkbox = request.form.getlist('method')
        if 'sms' in get_checkbox and 'email' in get_checkbox:
            get_method = "Both"
        elif 'sms' in get_checkbox:
            get_method = "SMS"
        elif 'email' in get_checkbox:
            get_method = "Email"
        else:
            get_method = "Disable"
        settings.update_numberphone(get_phonenumber)
        settings.update_emailto(get_emailto)
        settings.update_method(get_method)
        return render_template('alert.html', success=1, settings=settings.get_all())
    return render_template('alert.html', settings=settings.get_all())


@app.route('/changepass', methods=['POST', 'GET'])
def changepass():
    if request.method == 'POST':
        admin_id = 1
        get_oldpassword = hashlib.md5(request.form['current_pass']).hexdigest()
        get_newpassword = hashlib.md5(request.form['new_pass']).hexdigest()
        get_confirm = hashlib.md5(request.form['new_pass_conf']).hexdigest()
        if get_newpassword != get_confirm:
            return render_template('changepass.html', error="Password does not match the confirm password.")
        if users.update_pass(get_oldpassword, get_newpassword, admin_id) == -1:
            return render_template('changepass.html', error="Old password is incorrect.")
        else:
            return render_template('changepass.html', success=1)
    return render_template('changepass.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session = []
    return redirect(url_for('login'))


@app.route('/search/page/<string:pattern>/<int:page>', methods=['POST', 'GET'], defaults={'page': 1})
def search(pattern, page):
    if request.method == 'POST':
        if request.form['submit'] == 'search':
            pattern = request.form['pattern']
            pattern = base64.b64encode(pattern)
            return redirect(url_for('search', pattern=pattern, page=1))
    pattern = base64.b64decode(pattern)
    result = logs_obj.find(pattern, page, 20)
    pagination = Pagination(page, 20, result['count'])
    return render_template('search.html', pagination=pagination, result=result['logs_found'], pattern=pattern)


@app.route('/blacklist', methods=['POST', 'GET'], defaults={'page': 1})
@app.route('/blacklist/page/<int:page>', methods=['POST', 'GET'])
def blacklist(page):
    if request.method == 'POST':
        if request.form['submit'] == 'deleteall':
            list_checkbox = request.form.getlist('deleteChk')
            for item in list_checkbox:
                blacklist_obj.delete(item)
            count = blacklist_obj.count_all_keywords()
            result = blacklist_obj.get_keywords_for_page(page, 5, count)
            pagination = Pagination(page, 5, count)
            return render_template('blacklist.html', pagination=pagination, result=result)
        elif request.form['submit'] == 'add':
            get_keyword = request.form['keyword']
            get_keyword = get_keyword.lower()
            if blacklist_obj.add(get_keyword) == -1:
                count = blacklist_obj.count_all_keywords()
                result = blacklist_obj.get_keywords_for_page(page, 5, count)
                pagination = Pagination(page, 5, count)
                return render_template('blacklist.html', duplicate=1, pagination=pagination, result=result)
            else:
                count = blacklist_obj.count_all_keywords()
                result = blacklist_obj.get_keywords_for_page(page, 5, count)
                pagination = Pagination(page, 5, count)
                return render_template('blacklist.html', success=1, pagination=pagination, result=result)
    count = blacklist_obj.count_all_keywords()
    result = blacklist_obj.get_keywords_for_page(page, 5, count)
    pagination = Pagination(page, 5, count)
    return render_template('blacklist.html', pagination=pagination, result=result)
