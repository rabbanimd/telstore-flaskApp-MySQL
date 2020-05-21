from flask import Flask
from flask import render_template, request, redirect, flash, session
import pymysql
import os

app = Flask(__name__, template_folder='templates')

# session created with 23 length string
app.secret_key = os.urandom(23)


# Database class that is used to create a database object
class Database():
    def __init__(self):
        # use localhost as host if it do not work
        host = "127.0.0.1"
        user = "<suername>"
        password = "<password>"
        db = "<databasename>"

        self.con = pymysql.connect(host=host, user=user, password=password, db=db,
                                   cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()


db = Database()


# Homepage
@app.route('/')
def index():
    if "authuser" in session:
        return redirect('/admin')
    else:
        return render_template('index.html')


# password reset
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        uname = request.form['username']
        key = request.form['key']
        db.cur.execute("SELECT * FROM admin WHERE username=%s AND security_key=%s", (uname, key))
        data = db.cur.fetchall()
        if data:
            return render_template('reset.html', status=0, uname=uname)
        else:
            return render_template('reset.html', status=1)

    else:
        return render_template('reset.html', status=1)


@app.route('/resetpass/<string:uname>', methods=['GET', 'POST'])
def resetpass(uname):
    passw = request.form['password']
    db.cur.execute("UPDATE admin SET password=%s WHERE username=%s", (passw, uname))
    db.con.commit()
    return redirect('/')


# add new users to login
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        fname = request.form['name']
        uname = request.form['username']
        email = request.form['email']
        passw = request.form['password']
        key = request.form['seckey']
        db.cur.execute("SELECT * FROM admin WHERE username=%s", uname)
        data = db.cur.fetchall()
        if data:
            return render_template('index.html', message="user exist with this username")
        else:
            db.cur.execute("INSERT INTO admin(name,username,email,password,security_key) VALUES(%s, %s, %s, %s,%s)",
                           (fname, uname, email, passw, key))
            db.cur.execute(
                "CREATE TABLE {0} (status varchar(10) DEFAULT 'active',srno int primary key auto_increment,name varchar(30),title varchar(30),company varchar(40),phone1 varchar(14),phone2 varchar(14),address varchar(90),groups varchar(25),email varchar(40),website varchar(40))".format(uname))
            db.con.commit()
            session['user'] = uname
            session['authuser'] = 1
            return redirect('/admin')
    else:
        return render_template('index.html')


# login validation
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        passw = request.form['password']
        db.cur.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (uname, passw))
        data = db.cur.fetchall()
        if data:
            session['user'] = uname
            session['authuser'] = 1
            return redirect('/admin')
        else:
            return render_template('index.html', msg="invalid username or password")
    else:
        return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('user')
    session.pop('authuser')
    return redirect('/')


# Route past successful login
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if "authuser" in session:
        if request.method == 'POST':
            word = request.form['search']
            ser = "%{0}%".format(word)
            db.cur.execute("SELECT * FROM {0} WHERE name LIKE '{1}'".format(session['user'], ser))
            data = db.cur.fetchall()
            return render_template('home.html', data=data, user=session['user'])
        else:
            user = session["user"]
            db.cur.execute("SELECT * FROM {0} WHERE status='active'".format(user))
            row = db.cur.rowcount
            data = db.cur.fetchall()
            return render_template('home.html', data=data, user=session['user'], row=row)
    else:
        return render_template('index.html')


@app.route('/addContact', methods=['GET', 'POST'])
def addContact():
    if request.method == 'POST':
        name = request.form.get('name')
        title = request.form.get('title')
        phone1 = request.form.get('phone1')
        phone2 = request.form.get('phone2')
        email = request.form.get('email')
        company = request.form.get('company')
        website = request.form.get('website')
        address = request.form.get('address')
        group = request.form.get('group')
        db.cur.execute("INSERT INTO {0}(name,title,phone1,phone2,email,company,website,address,groups) VALUES('{1}',"
                       "'{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}')".format(session['user'], name, title, phone1,
                                                                                 phone2, email, company, website,
                                                                                 address, group))
        db.con.commit()
        return redirect('/admin')
    else:
        group = ['family', 'friends', 'collegues', 'vip']
        return render_template('addnew.html', data=group)


@app.route('/search')
def search():
    search=request.args.get('search')
    db.cur.execute("SELECT * FROM {0} WHERE name like '%{1}%'".format(session['user'],search))
    data=db.cur.fetchall()
    row=db.cur.rowcount
    if data:
        return render_template('home.html', data=data, user=session['user'],row=row)
    else:
        return redirect('/admin')



@app.route('/updateContact/<int:id>', methods=['GET', 'POST'])
def updateContact(id):
    if request.method == 'POST':
        name = request.form['name']
        title = request.form['title']
        phone1 = request.form['phone1']
        phone2 = request.form['phone2']
        email = request.form['email']
        company = request.form['company']
        website = request.form['website']
        address = request.form['address']
        group = request.form['group']
        db.cur.execute("UPDATE {0} SET name='{1}',title='{2}',phone1='{3}',phone2='{4}',email='{5}',company='{6}',"
                       "website='{7}', "
                       "address='{8}',groups='{9}' WHERE srno='{10}'".format
                       (session['user'], name, title, phone1, phone2, email, company, website, address,
                        group, id))
        db.con.commit()
        return redirect('/admin')

    else:
        db.cur.execute("SELECT * FROM {0} WHERE srno={1}".format(session['user'], id))
        data = db.cur.fetchall()
        grp = ['', 'family', 'friends', 'collegues', 'vip']
        return render_template('update.html', data=data, id=id, grp=grp)


@app.route('/deleteContact/<int:id>', methods=['GET', 'POST'])
def deleteContact(id):
    db.cur.execute("UPDATE {0} set status='deleted' WHERE srno={1}".format(session['user'], id))
    db.con.commit()
    return redirect('/admin')


@app.route('/restore')
def restore():
    db.cur.execute("SELECT * FROM {0} WHERE status='deleted'".format(session['user']))
    data = db.cur.fetchall()
    if data:
        return render_template('restore.html', data=data,user=session['user'])
    else:
        return redirect('/admin')


@app.route('/restore/<string:act>/<int:id>')
def restore_contact(act, id):
    if act == "delete":
        db.cur.execute("DELETE FROM {0} WHERE srno={1}".format(session['user'], id))
        db.con.commit()
        return redirect('/admin')
    elif act == "restore":
        db.cur.execute("UPDATE {0} SET status='active' WHERE srno={1}".format(session['user'], id))
        db.con.commit()
        return redirect('/admin')
    else:
        return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True)
