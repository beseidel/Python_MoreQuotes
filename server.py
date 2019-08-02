from flask import Flask, render_template, redirect, request, session, flash

from flask_bcrypt import Bcrypt

import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

from MySQLconnection import connectToMySQL 
# import the function that will return an instance of a connection

app = Flask(__name__)
app.secret_key = "keep it secret"
app.secret_key ="keep it secret"
bcrypt = Bcrypt(app)

#flash require a secret key as well as session

# show a page with a form to create a new user


# show a page with a form to create a new user
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index_total():
    return render_template('/index-total.html')

@app.route('/register', methods=['POST'])
def register():
    is_valid = True

    mysql = connectToMySQL('quotes')
    query = 'SELECT * FROM users_table WHERE email = %(em)s;'
    data = {
    'em': request.form['email']
    }
    email_result = mysql.query_db(query, data)
    
    if len(email_result) >= 1:
      is_valid = False
      flash("email already registered in database")
    print(email_result)
    
    if len(request.form['fname']) < 1:
      is_valid = False
      flash("Please enter a first name")

    if len(request.form['lname']) < 1:
      is_valid = False
      flash("Please enter a last name")
   
    if len(request.form['email']) < 1:
      is_valid = False
      flash("Email cannot be blank.")

    if len(request.form['pw']) < 8:
      is_valid = False
      flash('Password must be atleast 8 characters')

    if (request.form['pw'] != request.form['cpw']):
      is_valid = False
      flash('Passwords do NOT match')
 
    if not EMAIL_REGEX.match(request.form['email']):
      # test whether a field matches the pattern.  If it does not fit the pattern, then redirect. if email fits pattern, continue.
      is_valid = False
      flash("email cannot be blank or invalid")
   
    ##### at this point, I have checked every field
    ##### if any of the fields weren't valid, is_valid will be False
    ##### if all the fields are valid, is_valid will be True
    if not is_valid:
      return redirect('/')
      # return render_template('/') could use also in this case
    else:
        pw_hash = bcrypt.generate_password_hash(request.form['pw'])
        # pw_hash can be called anything including mickey
        print(pw_hash)   
        # put the pw_hash in our data dictionary, NOT the password the user provided
        # prints something like b'$2b$12$sqjyok5RQccl9S6eFLhEPuaRaJCcH3Esl2RWLm/cimMIEnhnLb7iC'
        # be sure you set up your database so it can store password hashes this long (60 characters)
      
        mysql = connectToMySQL("quotes")
    
        query = "INSERT INTO users_table (first_name,last_name, email, password) VALUES (%(fn)s, %(ln)s, %(em)s, %(pw)s);"
    # put the pw_hash in our data dictionary, NOT the password the user provided
    
        data = {
          "fn": request.form['fname'],
          "ln": request.form['lname'],
          "em": request.form['email'],
          "pw": pw_hash
        }
    #make the call of the function to the database. 
        result = mysql.query_db(query, data)
        session['id_mickey_user']=result
    # never render on a post, always redirect!
        flash("Login info successfuly added.  Please login!")
        
      # either way the application should return to the index and display the messag
      #   never render on a post, always redirect!
        return redirect("/")

# login the database  
@app.route('/login', methods = ['POST'])
def login():
    mysql = connectToMySQL('quotes')
    query = 'SELECT * FROM users_table WHERE email = %(em)s;'
    data = {
    'em': request.form['email']
    }
    result = mysql.query_db(query, data)
   
    if len(result)>0:
   
      if bcrypt.check_password_hash(result[0]['password'], request.form['pw']):
        session['id_mickey_user'] = result[0]['id_user']
# This is setting id_mickey_user to session which is equal the id_user logged in.
      session['mickeys_first_name'] = result[0]['first_name']
      #look in session and result the first name at login
      return redirect('/dashboard')
      flash("You could not be logged in")
    return redirect('/')
    
@app.route('/dashboard', methods=['GET'])
def show_all_quotes_dashboard():
    if 'id_mickey_user' not in session:
      flash("You need to be logged in to view this page")
      return redirect('/')
    else:
      flash("welcome to the dashboard")
        
      MySQL = connectToMySQL('quotes')

      query_show_quotes = 'SELECT * FROM quotes_table JOIN users_table ON quotes_table.user_added_by = users_table.id_user;'

      quotes = MySQL.query_db(query_show_quotes)
      print('show page hitting 0')
      return render_template('/dashboard.html', all_quotes=quotes)
      print('show page before Hitting 1')

@app.route('/add_quote', methods = ['POST'])
def process_book():
    print("Hitting 1")
    print(request.form)
    print(session['id_mickey_user'])
    print("Hitting 2")
    print(request.form)
    if len(request.form['q_name']) < 3:
      if len(request.form['q_content']) < 10:
    # post_content is the name in the form on the dashboard.html
        print("Hitting if")
        flash('Input Needs to be longer')
      return redirect('/dashboard')
    else:
      print(request.form)
    db = connectToMySQL('quotes')
    print("Hitting 4")

# #  # #this is telling the computer to find the table name posts 
  
    query = "INSERT INTO quotes_table (name,quote_content,user_added_by,created_at, updated_at) VALUES (%(qn)s, %(qc)s, %(use_added)s, NOW(), NOW());"
    print("Hitting 5")

    data = {
      'qn': request.form['q_name'],
      'qc': request.form['q_content'],
      'use_added': session['id_mickey_user'],
    }
    print("hitting 6")
    add_book = db.query_db(query, data)
#     print(request.form)
    print("hitting 7")
    return redirect('/dashboard')


@app.route('/edit/update/<id>', methods=['POST'])
def process_edit_form(id):
    print(id)
    # #connect to db to show users info in the form
    print('hittingprocessingeditpage')
    MySQL = connectToMySQL("books")
    # # # # #write query for getting specific users
 
    query = "UPDATE quotes_table SET book_title = %(bt)s,book_description=%(bd)s, id_cont=%(id_mickey_user)s, created_at = NOW(), updated_at = NOW() WHERE id_user = %(id)s;"
    print('hitting query')

    data = {
      'bt': request.form['book_name'],
      'bd': request.form['book_summary'],
      'id_cont':session['id_mickey_user'],
    }
    print("hitting 6")
    # #possibly a value from the url,

    MySQL.query_db(query, data)
   
   # where to go after this is complete
    return redirect('/edit/'+str(id))
   
#     #orange is what you do in the HTML

@app.route('/delete/<id>', methods=['GET'])
def delete_book(id):
    #     print('user to ??')
    MySQL = connectToMySQL("quotes")

    # #write an UPDATE query
    query = "DELETE from quotes_table WHERE id_book = %(idb)s;"
    print(id)
    
    data = {
        'idb': id
    }
    MySQL.query_db(query, data)
    flash("removed")
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    print(session)
    session.clear()
    flash("You've been logged out")
    return redirect('/')


# @app.route('/new_user', methods=["GET"])
# def index():
#     return render_template("new_user_form.html", )

# process user requires an action and redirect
# @app.route('/create', methods=["POST"])
# def process_user():
#     # add user to database
#     # print("Post data")
#     print(request.form)
#     fname = request.form['fname']
#     lname = request.form['lname']
#     em= request.form['email']
#     return render_template("show_one_user.html", fname='first_name', lname='last_name', em='email')
#     # connect to to the MySQL schema name
    
#     # #this is telling the computer to find the table name users 
#     query = "INSERT INTO users_table (first_name,last_name, email, created_at,updated_at) VALUES ( %(fn)s, %(ln)s, %(em)s, NOW(), NOW() );"
#     #users_table has the above variables..first_name, last_name, etc and we are setting these variables in the database to be %(fn)s.
#     # #fname is the variable name from the form and fn is from whatever we create the variable to be and first_name is what I have in database. 
#     data = {
#         "fn": request.form["fname"],
#         "ln": request.form["lname"],
#         "em": request.form["email"]
#     }
# # to the form dictionary where the name field is set to variable fname
#     db=connectToMySQL("quotes")
#     user_id = db.query_db(query, data)
#     # return render_template('/show_one_user.html')
#     #this prints it to show the show_one_user
#     return redirect('/show_one_user/' + str(user_id))
  #change this route in the futureto users/create/show_one_user

@app.route('/edit_user/<id>', methods=["GET"])
def show_edit_form(id):
    MySQL = connectToMySQL("quotes")

    query = "(SELECT * FROM users_table WHERE id_user= %(mickey_id)s);"
    print(id)
    # this is the id above which is passed through the browser.
    data = {
        'mickey_id': session['id_mickey_user']
        
        #mickey_id is an id that we set so that the id_user in database matches the id in blue that goes to the browser.
    } 
    # # # # #run query
    users = MySQL.query_db(query, data)
    return render_template("edit_user.html", all_users=users)

@app.route('/edit_user/<id>', methods=['POST'])
def process_edit(id):
    #browser and forms like an id that is a string
    # #     print(<id>)
        # print(id)
    # #connect to db to show users info in the form
    MySQL = connectToMySQL("quotes")
    # # # # # #write query for getting specific users
 
    query = "UPDATE users_table SET first_name = %(fn)s,last_name=%(ln)s, email=%(em)s, created_at = NOW(), updated_at = NOW() WHERE id_user = %(mickey_id)s;"

    data = {
    "fn": request.form["fname"],
    "ln": request.form["lname"],
    "em": request.form["email"],
    "mickey_id": session['id_mickey_user']
    #if this is a message like in the wall or a hidden input, then request.form['id'] would be required to access it.  
    }
    # #possibly a value from the url,

    MySQL.query_db(query, data)
   
   # where to go after this is complete
    return redirect('/edit_user/' + str(id))
    #need to convert to a string since the browser understands strings.
   

@app.route('/show_one_user/<id>', methods=['GET'])
def show_one_user(id):
    #to get info about a specific user, you need to pass in an id through the browser

    # return render_template (show_one_user.html)
    #for temporary solution use this render_template

    MySQL = connectToMySQL("quotes")
    #connect to to the MySQL schema name
 
    query = "(SELECT * FROM users_table WHERE id_user= %(mickey_id)s);"  
    # id_user is the variable name found in the database that intiates a user_id
    print(id)
    #printing the blue id in shown above is id passed in through the browser and not the database.
    
    data = {
         'mickey_id': session['id_mickey_user']
    }  #data is required when we need to define specific data.
    # In this case, id_user in table users_table, there is data for the query to get and this is this data called id which is in blue and it is passed through the both the URL as well as the function above. 
   
    data_id_call = MySQL.query_db(query, data)
    # this is the call to run the function to get the ID in the database where the database will then pass results to the browser page. This database_id is database_id and it will be set to the browswer in orange which will be written in jinja

    MySQL = connectToMySQL('quotes')

    query_show_quotes = 'SELECT * FROM quotes_table JOIN users_table ON quotes_table.user_added_by = users_table.id_user;'

    quotes = MySQL.query_db(query_show_quotes)
    print('show page hitting 0')
    
    print('show page before Hitting 1')

    return render_template ("show_one_user.html", all_users=data_id_call, all_quotes=quotes)        
  #all_users in orange is going to be jinja in the show one user form

#the routing in show_all_users with method GET is to show_all_users
@app.route('/show_all_users', methods=['GET'])
def show_all_users():
    # #make a connection to the database
    # since all users will be shown, then nothing needs to be passed in through the browser or show_all_users function
    MySQL = connectToMySQL("quotes")
    # get info from db and pass results to the page
    # # # #write a query
    query = "(SELECT * FROM users_table);"
    print(id)
    #do not need to define data because we are requesting all data
    #run query
    #connection to the datapage
    results = MySQL.query_db(query)
    #results is a variable used to define the call in the return statement
    # # # #pass results to the template for rendering
    return render_template ("/show_all_users.html", all_users=results)
    #the orange is what you see in the HTML

# # show the form to edit specific users

    #orange is what you do in the HTML

@app.route('/delete/<id>', methods=['GET'])
def process_delete(id):
    #     print('user to ??')
    MySQL = connectToMySQL("quotes")

    # #write an UPDATE query
    query = "DELETE from users_table WHERE ID_user = %(mickey_id)s;"
    print(id)
    
    data = {
        'mickey_id': id
        # if id is from a form unlike this case where there is no form for id, then you will need to do a request.form like above for hidden inputs or like in the messages inthe wall. 
    }
    MySQL.query_db(query, data)
    flash("removed")
    return redirect ('/show_all_users')

if __name__ == "__main__":
    app.run(debug=True)



# # # # # show the form to edit specific users
# @app.route('/edit/<id>', methods=["GET"])
# def show_edit_form(id):
#     MySQL = connectToMySQL("books")

#     query = "(SELECT * FROM quotes_table WHERE id_quote = %(idq)s);"
#     print(id)
#     data = {
#         'idq':id
#     } 
#     # # # # #run query
#     books = MySQL.query_db(query, data)
#     print('hitting edit page')
#     return render_template("edit.html", book=books)


# 



# 




