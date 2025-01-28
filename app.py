from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import bcrypt
from datetime import date,datetime

today = date.today()
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sdl2'
mysql = MySQL(app)

# Create users table if it doesn't exist
with app.app_context():
    cursor = mysql.connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(255)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income_sources (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            source_id INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (source_id) REFERENCES income_sources(id)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expense (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_id INT NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            date DATE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (item_id) REFERENCES expense_items(id)
        );
    """)
    mysql.connection.commit()
    cursor.close()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Save user to database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('login'))
    return render_template('index.html')



@app.route('/edit_user', methods=['GET', 'POST'])
def edit_user():
    if 'user_id' in session:
        if request.method == 'POST':
            
            name = request.form['user_name']
            uid = request.form['id']
            email = request.form['email']
            password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET name = %s, email = %s, password =%s WHERE id = %s", (name, email, password,uid))
            mysql.connection.commit()
            cur.close()
            
            return redirect(url_for('show_users'))
    else:
        return redirect(url_for('login'))

@app.route('/delete_user', methods=['POST'])
def delete_user():
    email = request.form['id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (email,))
    mysql.connection.commit()
    cur.close()
    
    #session.pop('user_id', None)
    return redirect(url_for('show_users'))

@app.route('/show_users')
def show_users():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        user = cur.fetchall()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()  
        return render_template('show_users.html', user=user, user2=user2)
    else:
        return redirect(url_for('login'))

@app.route('/edits',  methods=['GET', 'POST'])
def edits():
    if 'user_id' in session:
        uid = request.form['id']
        email = request.form['email']
        name = request.form['name']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()
        return render_template('user_edit.html', name=name, email=email, user2=user2, uid=uid)
    else:
        return redirect(url_for('login'))


@app.route('/ch_role', methods=['GET', 'POST'])
def ch_role():
    if 'user_id' in session:
        if request.method == 'POST':
            
            rolee = request.form['role']
            users = request.form['user']
            cur = mysql.connection.cursor()
            cur.execute("UPDATE users SET role = %s WHERE name = %s", (rolee,users))
            mysql.connection.commit()
            cur.close()
            
            return redirect(url_for('show_users'))
    else:
        return redirect(url_for('login'))



@app.route('/add_expences_item', methods=['GET', 'POST'])
def add_expences_item():
    if request.method == 'POST':
        # Fetch form data
        name = request.form['name']

        # Save user to database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO expense_items (name) VALUES (%s)", (name,))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('show_expences_item'))
    return render_template('index.html')

@app.route('/show_expences_item')
def show_expences_item():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM expense_items")
        user = cur.fetchall()

        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()
        
            
        return render_template('show_expences_item.html', user=user, user2=user2)
    else:
        return redirect(url_for('login'))

@app.route('/delete_expences_item', methods=['POST'])
def delete_expences_item():
    ids = request.form['id']
    print(ids)
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM expense_items WHERE id = %s", (ids))
    mysql.connection.commit()
    cur.close()
    
    #session.pop('user_id', None)
    return redirect(url_for('show_expences_item'))

@app.route('/edits_expences_item',  methods=['GET', 'POST'])
def edits_expences_item():
    if 'user_id' in session:
        uid = request.form['id']
        name = request.form['name']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()
        return render_template('edit_expences_item.html', name=name, user2=user2, uid=uid)
    else:
        return redirect(url_for('login'))

@app.route('/edit_expences_item', methods=['GET', 'POST'])
def edit_expences_item():
    if 'user_id' in session:
        if request.method == 'POST':
            
            name = request.form['user_name']
            uid = request.form['id']
            cur = mysql.connection.cursor()
            cur.execute("UPDATE expense_items SET name = %s WHERE id = %s", (name,uid))
            mysql.connection.commit()
            cur.close()
            
            return redirect(url_for('show_expences_item'))
    else:
        return redirect(url_for('login'))



@app.route('/add_incum', methods=['GET', 'POST'])
def add_incum():
    if request.method == 'POST':
        # Fetch form data
        amount = request.form['amount']
        namee = request.form['name']
        userid = session['user_id']
        # Save user to database
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE name = %s", (namee,))
        usere = cur.fetchone()
        cur.execute("INSERT INTO income (user_id,source_id,amount,date) VALUES (%s,%s,%s,%s)", (usere,1,amount,today,))
        mysql.connection.commit()
        
        cur.close()
        
        return redirect(url_for('show_incum'))
    return render_template('index.html')

@app.route('/show_incum')
def show_incum():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT income.id,users.name,income.amount,income.date FROM users,income WHERE income.user_id	= users.id")
        user = cur.fetchall()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.execute("SELECT name FROM users")
        user3 = cur.fetchall()
        cur.close()  
        return render_template('show_incum.html', user=user, user2=user2, user3=user3)
    else:
        return redirect(url_for('login'))

@app.route('/delete_incum', methods=['POST'])
def delete_incum():
    ids = request.form['id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM income WHERE id = %s", (ids,))
    mysql.connection.commit()
    cur.close()
    
    #session.pop('user_id', None)
    return redirect(url_for('show_incum'))



@app.route('/edits_income',  methods=['GET', 'POST'])
def edits_income():
    if 'user_id' in session:
        uid = request.form['id']
        name = request.form['name']
        amounte = request.form['amount']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT name FROM users")
        user3 = cur.fetchall()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()
        return render_template('edit_income.html',amounte=amounte, name=name, user2=user2, uid=uid,user3=user3)
    else:
        return redirect(url_for('login'))

@app.route('/edit_income', methods=['GET', 'POST'])
def edit_income():
    if 'user_id' in session:
        if request.method == 'POST':
            
            name = request.form['amount']
            uid = request.form['id']
            namer = request.form['name']
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE name = %s", (namer,))
            user2 = cur.fetchone()
            cur.execute("UPDATE income SET amount = %s, user_id=%s WHERE id = %s", (name,user2,uid))
            mysql.connection.commit()
            cur.close()
            
            return redirect(url_for('show_expense'))
    else:
        return redirect(url_for('login'))




@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        # Fetch form data
        amount = request.form['amount']
        item = request.form['item']
        userid = session['user_id']
        # Save user to database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO expense (user_id,item_id,amount,date) VALUES (%s,%s,%s,%s)", (userid,item,amount,today,))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('show_expense'))
    return render_template('index.html')

@app.route('/show_expense')
def show_expense():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT expense.id,users.name,expense_items.name,expense.amount,expense.date FROM users,expense,expense_items WHERE expense.user_id=users.id and expense_items.id = expense.item_id")
        user = cur.fetchall()
        cur.execute("SELECT * FROM expense_items")
        item = cur.fetchall()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()  
        return render_template('show_expense.html', user=user, user2=user2, item=item)
    else:
        return redirect(url_for('login'))

@app.route('/delete_expense', methods=['POST'])
def delete_expense():
    ids = request.form['id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM expense WHERE id = %s", (ids))
    mysql.connection.commit()
    cur.close()
    
    #session.pop('user_id', None)
    return redirect(url_for('show_expense'))


@app.route('/edits_expences',  methods=['GET', 'POST'])
def edits_expences():
    if 'user_id' in session:
        uid = request.form['id']
        name = request.form['name']
        # amounte = request.form['amount']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()
        return render_template('edit_expences.html', name=name, user2=user2, uid=uid)
    else:
        return redirect(url_for('login'))

@app.route('/edit_expences', methods=['GET', 'POST'])
def edit_expences():
    if 'user_id' in session:
        if request.method == 'POST':
            
            name = request.form['amount']
            uid = request.form['id']
            cur = mysql.connection.cursor()
            cur.execute("UPDATE expense SET amount = %s WHERE id = %s", (name,uid))
            mysql.connection.commit()
            cur.close()
            
            return redirect(url_for('show_expense'))
    else:
        return redirect(url_for('login'))




@app.route('/year_steatment')
def year_steatment():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT YEAR(date) AS month_year, SUM(amount) AS total_amount FROM expense GROUP BY YEAR(date);")
        user = cur.fetchall()
        cur.execute("""SELECT SUM(total_amount) AS overall_total
                    FROM (
                        SELECT SUM(amount) AS total_amount
                        FROM expense
                        GROUP BY YEAR(date)
                    ) AS monthly_totals;""")
        total = cur.fetchone()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close() 
        return render_template('year_steatment.html', user=user, user2=user2, total=total)
    else:
        return redirect(url_for('login'))



@app.route('/month_steatment', methods=['GET', 'POST'])
def month_steatment():
    if 'user_id' in session:
        year = request.form['year']
        cur = mysql.connection.cursor()
        cur.execute("SELECT MONTHNAME(date), YEAR(date) AS month_year, SUM(amount) AS total_amount FROM expense WHERE YEAR(date) = %s GROUP BY MONTH(date), YEAR(date)", (year,))
        user = cur.fetchall()
        
        cur.execute("""SELECT SUM(total_amount) AS overall_total
                    FROM (
                        SELECT SUM(amount) AS total_amount
                        FROM expense
                        WHERE YEAR(date) = %s
                        GROUP BY MONTH(date), YEAR(date)
                    ) AS monthly_totals;""", (year,))
        total = cur.fetchone()
        
        
        
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()
        
            
        return render_template('month_steatment.html', user=user, user2=user2, total=total)
    else:
        return redirect(url_for('login'))



@app.route('/daily_steatment', methods=['GET', 'POST'])
def daily_steatment():
    if 'user_id' in session:
        month = request.form['month']
        year = request.form['year']
        
        cur = mysql.connection.cursor()
        cur.execute("""SELECT users.name,expense_items.name,expense.amount,expense.date
                    FROM expense
                    JOIN expense_items ON expense.item_id = expense_items.id
                    JOIN users ON expense.user_id = users.id
                    WHERE MONTHNAME(expense.date) = %s and YEAR(expense.date)= %s""", (month,year))
        user = cur.fetchall()
        cur.execute("""SELECT SUM(total_amount) AS overall_total
                    FROM (
                        SELECT SUM(amount) AS total_amount
                        FROM expense
                        WHERE MONTHNAME(date) = %s and YEAR(expense.date)= %s
                        GROUP BY MONTH(date), YEAR(date)
                    ) AS monthly_totals;""", (month,year))
        total = cur.fetchone()
        
        
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()
        
            
        return render_template('daily_steatment.html', user=user, user2=user2, total=total)
    else:
        return redirect(url_for('login'))





@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        
        if user and bcrypt.checkpw(password, user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('Cost_Spliting'))
        else:
            error = 'Invalid email or password'

    return render_template('index.html', error=error)





@app.route('/search_page')
def search_page():
    if 'user_id' in session:
        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        
        cur.execute("SELECT * FROM users ")
        user = cur.fetchall()
        cur.execute("SELECT * FROM expense_items ")
        item = cur.fetchall()
        cur.close()
        
            
        return render_template('search_page.html', user=user, user2=user2, item=item)
    else:
        return redirect(url_for('login'))



@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' in session:
        fromDate = request.form['fromDate']
        toDate = request.form['toDate']
        name = request.form['name']
        itemname = request.form['itemname']

        # Convert the date string to a datetime object
        fromDate = datetime.strptime(fromDate, '%d/%m/%Y')

        # Format the datetime object into 'yyyy-mm-dd' format
        fromDate = fromDate.strftime('%Y-%m-%d')
        
                # Convert the date string to a datetime object
        toDate = datetime.strptime(toDate, '%d/%m/%Y')

        # Format the datetime object into 'yyyy-mm-dd' format
        toDate = toDate.strftime('%Y-%m-%d')

        # Prepare the SQL query with placeholders for dynamic values
        sql = """SELECT
                    users.name AS user_name,
                    expense_items.name AS ex_it,
                    expense.amount,
                    expense.date
                FROM
                    expense
                JOIN expense_items ON expense.item_id = expense_items.id
                JOIN users ON expense.user_id = users.id
                WHERE 1=1"""

        params = ()
        print(sql)
        # Add conditions based on user input
        if fromDate:
            sql = sql+ " AND DATE(expense.date) >= %s"
            params= params+(fromDate,)
        if toDate:
            sql =sql+ " AND DATE(expense.date) <= %s"
            params= params+(toDate,)
        if name:
            sql =sql+ " AND users.name = %s"
            params= params+(name,)
        if itemname:
            sql =sql+ " AND expense_items.name = %s"
            params= params+(itemname,)
        print(sql)
        

        print(params)
        cur = mysql.connection.cursor()
        
        cur.execute(sql, params)
        results = cur.fetchall()
                
        sql = """SELECT SUM(expense.amount) AS total_amount
                FROM expense
                JOIN expense_items ON expense.item_id = expense_items.id
                JOIN users ON expense.user_id = users.id
                WHERE 1=1"""

        params1 = ()

        # Add conditions based on user input
        if fromDate:
            sql = sql+ " AND DATE(expense.date) >= %s"
            params1= params1+(fromDate,)
        if toDate:
            sql =sql+ " AND DATE(expense.date) <= %s"
            params1= params1+(toDate,)
        if name:
            sql =sql+ " AND users.name = %s"
            params1= params1+(name,)
        if itemname:
            sql =sql+ " AND expense_items.name = %s"
            params1= params1+(itemname,)
        print(sql)
        cur.execute(sql, params1)
        total = cur.fetchone()[0]
        
        
        
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()
        
            
        return render_template('search.html', user=results, user2=user2,total=total)
    else:
        return redirect(url_for('login'))



@app.route('/Receipt_Verification')
def Receipt_Verification():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT expense.id,users.name,expense_items.name,expense.amount,expense.date FROM users,expense,expense_items WHERE expense.user_id=users.id and expense_items.id = expense.item_id")
        user = cur.fetchall()
        cur.execute("SELECT * FROM expense_items")
        item = cur.fetchall()
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        cur.close()  
        return render_template('Receipt_Verification.html', user=user, user2=user2, item=item)
    else:
        return redirect(url_for('login'))

@app.route('/Cost_Spliting', methods=['GET', 'POST'])
def Cost_Spliting():
    if 'user_id' in session:
        
        cur = mysql.connection.cursor()
        
        # Fetch distinct Year-Month values
        query = """
        SELECT DISTINCT 
            DATE_FORMAT(date, '%Y-%m') AS YearMonth
        FROM 
            expense
        ORDER BY 
            YearMonth ASC;
        """
        cur.execute(query)
        YearMonth = cur.fetchall()
        
        # Get YearMonth from form or default to current month
        YearMonth2 = request.form.get('YearMonth')
        if not YearMonth2:  # If empty, use current month and year
            YearMonth2 = datetime.now().strftime('%Y-%m')

        # Query to calculate expenses
        query = f"""
        WITH total_expense AS (
            SELECT 
                SUM(e.amount) AS total_expense_amount
            FROM 
                expense e
            WHERE 
                DATE_FORMAT(e.date, '%Y-%m') = '{YearMonth2}'
        ),
        user_count AS (
            SELECT 
                COUNT(*) AS total_users
            FROM 
                users
        ),
        user_expenses AS (
            SELECT 
                u.id AS user_id,
                u.name AS Name,
                IFNULL(SUM(e.amount), 0) AS Paid_Amount
            FROM 
                users u
            LEFT JOIN 
                income e ON u.id = e.user_id AND DATE_FORMAT(e.date, '%Y-%m') = '{YearMonth2}'
            GROUP BY 
                u.id, u.name
        )
        SELECT 
            ue.Name,
            ROUND(te.total_expense_amount / uc.total_users, 2) AS Expense_Share,
            ue.Paid_Amount,
            ROUND((te.total_expense_amount / uc.total_users) - ue.Paid_Amount, 2) AS Due_Amount
        FROM 
            user_expenses ue
        CROSS JOIN 
            total_expense te
        CROSS JOIN 
            user_count uc;
        """
        cur.execute(query)
        results = cur.fetchall()
        
        query = f"""
        SELECT 
            (SELECT COUNT(*) FROM users) AS total_users,
            (SELECT SUM(amount) FROM expense WHERE DATE_FORMAT(date, '%Y-%m') = '{YearMonth2}') AS total_expense_amount
        """
        cur.execute(query)
        cost = cur.fetchone()

        total_users = cost[0] if cost[0] is not None else 0
        total_expense_amount = cost[1] if cost[1] is not None else 0.0


        # Get current user's name
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user2 = cur.fetchone()
        
        # Fetch all users for display
        cur.execute("SELECT * FROM users ")
        user = cur.fetchall()
        
        cur.close()
        
        return render_template('Cost_Spliting.html', YearMonth2=YearMonth2, total_expense_amount=total_expense_amount, total_users=total_users, user=user, user2=user2, results=results, YearMonth=YearMonth)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

