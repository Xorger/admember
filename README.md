# Admember
#### Video URL: https://youtu.be/6PVs9D5kA-Y
---
## What is admember
Admember is a simple member management application (the name comes from the Latin _ad-_, meaning _to_ and member). Think the of system used at a daycare/school but a bit different in a few aspects:

* Admember does not have a self service mode. This means that customers/members will not be able to check themselves in. This task must be performed by the system administrator
* Admember does not engage in the storage or retrival of personally identifing information execpt names, including contact information

## How to install it
To install admember, clone this GitHub repository at <https://github.com/Xorger/admember> with the command:

```shell
git commit https://github.com/Xorger/admember
```
Next ensuring that python3 and pip3 are installed, run the following commands:
```shell
cd admember
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```
After this we can run the application like so:
```shell
python3 app.py
```
We can now interact with the web interface at <http://127.0.0.1:5000>
## Explanation of the main app structure
The app is structured into 4 main sections:
1. The imports section: this is where we have the standard python imports.
2. The initialization section: this is where we initialize the
    * Flask app
    * SQLAlchemy database connection
    * Secret key
    * Login manager
3. The models section: this is where all of the SQLAlchemy models are initialized for things like storing users, members and families.
4. The functions/routes section: this is where all the functions, mostly routes, are defined. They will be explained individually below.
## The functions/routes
### `load_user()`
This is a simple function used only by flask-login. It simply tells flask login how to retrieve the current user's id.
### `signup()`
This is the main function for the `/signup` route, which excepts both `GET` and `POST` requests. It works as follows:

`GET`:

This simply displays the [`signup.html` template](#signuphtml).

`POST`:

This takes the input submitted to the form and does the following:

1. Retrieves all fields (username, password, again) and stores them in variables
2. Checks whether all fields were filled
3. Checks whether both passwords match
4. Checks whether the user already exists using a SQLAlchemy query
5. Creates a new_user object
6. Add to database, commits, and redirects to [`/login`](#login)

### `login()`
This is the main function for the `/login` route, which accepts both `GET` and `POST` requests. It works as follows:

`GET`:

This simply displays the [`login.html` template](#loginhtml).

`POST`:

This takes the input submitted to the form and does the following:

1. Retrieves all fields (username, password, again, remember) and stores them in variables
2. Checks whether all fields were filled
3. Checks whether both passwords match
4. Check if the user actually exists
5. Take the user-supplied password, hash it, and compare it to the hashed password in the database
6. If password-hashes match, then login the user with flask-login's `login_user()`, making sure to set the remember value, and then redirect to [`/`](#index)

### `logout()`
This is the main function for the `/logout` route, which only accepts `GET` requests. It works as follows:

`GET`:

This simply calls the `logout_user()` function of flask-login, and then returns a redirect to [`/`](#index)

### `index()`
This is the main function for the `/` route, which accepts both `GET` and `POST` requests. It works as follows:

`GET`:

This first checks if the user has filled in the search field. If so, the function returns a list of all members whose first name matches the user submitted query via a SQLAlchemy select statement.

If instead the user checks in or checks out the member, the function will flip the member's status column using the SQLAlchemy ORM

If instead the user deletes the member, the function will use a SQLAlchemy statement to delete the member

If instead the user does none of the above, the function will display a list of all members

`POST`:

This takes the input submitted to the member adding form and does the following:

1. Retrieves all fields (name and family name) and stores them in variables
2. Checks whether all fields were filled
3. Checks whether the family exists
4. Use the SQLAlchemy ORM to add the member to the database and redirect to [`/`](#index)

### `families()`
This is the main function for the `/families` route, which accepts both `GET` and `POST` requests. It works as follows:

`GET`:

This first checks if the user has filled in the search field. If so, the function returns a list of all families whose name matches the user submitted query via a SQLAlchemy select statement

If instead the user has selected the delete option, the function uses the SQLAlchemy ORM to delete the family. The function must first check if the family is in use by members

If instead the user does nothing, the function displays a list of all families

`POST`:

This takes the input submitted to the family adding form and does the following:

1. Retrieves all fields (name) and stores them in variables
2. Checks whether all fields were filled
3. Checks that the family does not already exist
3. Use the SQLAlchemy ORM to add the family to the database and redirect to [`/families`](#families)

### `user()`
This is the main function for the `/user` route, which accepts both `GET` and `POST` requests. It works as follows:

`GET`:

This simply displays the [`user.html` template](#userhtml)

`POST`:

This takes the input submitted to the form and does the following:

If the user chose to delete themselves, the function will first check if they have entered their password and that it is valid. If so, the funtion will use SQLAlchemy to
delete that user

If instead the user chose to change their password, the function will first check if they have entered their old password correctly. It will then check if the new password matches with the confirmation password

## Other files

### database.db
This is an autogenerated file created on program startup by SQLAlchemy. It is a simple sqlite database file.
### style.css
This is the css file with custom css to override bootstrap.
### layout.html
This is the main template file that is extended by all other templates. It mostly contains the code for the navbar.
### index.html
This is the template file for the index page. It contains code for a table of members, a search bar, and a form to add members
### families.html
This is the template file for the families page. It contains code for a table of families, a search bar, and a form to add families
### signup.html
This is the template for the signup page. It contains code for an account creation form.
### login.html
This is the template for the login page. It contains code for a form for logging in
### user.html
This is the template for the account page. It containd code for deleting the account or changing the password

## Other thoughts
I used bootstrap for the main css, and flask-login for the user management, with SQLAlchemy + sqlite for the database
