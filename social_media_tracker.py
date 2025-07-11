import sqlite3
from termcolor import cprint
from tabulate import tabulate
from datetime import datetime
from InquirerPy import inquirer

conn = sqlite3.connect('social_media.db')
cursor = conn.cursor()

# Create table
def create_table():
    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS posts(
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                content TEXT NOT NULL,
                likes INTEGER DEFAULT 0 CHECK(likes >= 0),
                post_date TEXT NOT NULL
            )
        """
    )
    conn.commit()

# Valid check function
def is_valid_username(username):
    return 3 <= len(username) <= 15

def is_valid_content(content):
    return 1 <= len(content) <= 280

# Adds post
def add_post():
    username = input("Enter username (3-15 characters):- ").strip()
    content = input("Enter content (max 280 characters):- ").strip()

    if not is_valid_username(username):
        cprint("Error: Username must be between 3 and 15 characters.", "red")
        return
    if not is_valid_content(content):
        cprint("Error: Content must be between 1 and 280 characters.", "red")
        return
    
    post_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")
    try:
        cursor.execute("INSERT INTO posts (username,content,post_date) VALUES (?,?,?)",(username,content,post_date))
        conn.commit()
        cprint("Post added successfully!","green")
    except sqlite3.Error as e:
        cprint(f"SQLite Error: {e}","red")

# Views posts
def view_posts():
    try:
        cursor.execute("select * from posts")
        rows = cursor.fetchall()
        if rows:
            headers = ["Post ID","Username","Content","Likes","Post Date","Comments"]
            table = tabulate(rows,headers,tablefmt="fancy_grid",colalign=("center",))
            cprint(table,"cyan")
        else:
            cprint("No posts available.","red")
    except sqlite3.Error as e:
        cprint(f"SQLite Error: {e}","red")

# Likes post
def like_post():
    try:
        post_id = int(input("Enter Post Id to like: "))
        cursor.execute("UPDATE posts SET likes = likes + 1 WHERE post_id = ?", (post_id,))

        if cursor.rowcount == 0:
            cprint("No data found!!","red")
        else:
            conn.commit()
            cprint("Post liked!!","green")
    except ValueError:
        cprint("Invalid Post ID.","red")
    except sqlite3.Error as e:
        cprint(f"SQLite Error: {e}","red")

def add_comment():
    try:
        post_id = int(input("Enter Post ID to comment on: "))
        cursor.execute("SELECT comments FROM posts WHERE post_id = ?", (post_id,))
        row = cursor.fetchone()

        if not row:
            cprint("Post ID not found.", "red")
            return

        existing_comment = row[0]
        new_comment = input("Enter your comment: ").strip()

        if not new_comment:
            cprint("Comment cannot be empty.", "red")
            return

        if existing_comment and existing_comment.strip().lower() != "no comment":
            updated_comment = existing_comment + ", " + new_comment
        else:
            updated_comment = new_comment

        cursor.execute("UPDATE posts SET comments = ? WHERE post_id = ?", (updated_comment, post_id))
        conn.commit()
        cprint("Comment added successfully!", "green")

    except ValueError:
        cprint("Invalid Post ID.", "red")
    except sqlite3.Error as e:
        cprint(f"SQLite Error: {e}", "red")


# Delete post
def delete_post():
    try:
        post_id = int(input("Enter Post Id to delete: "))

        cursor.execute("delete from posts where post_id = ?",(post_id,))

        if cursor.rowcount == 0:
            cprint("Post Id not found!!","red")
        else:
            conn.commit()
            cprint("Post deleted!!","green")
    except ValueError:
        cprint("Invalid Post ID.","red")
    except sqlite3.Error as e:
        cprint(f"SQLite Error: {e}","red")

# Alter table adds column of comments
def alter_table():
    try:
        cursor.execute("alter table posts add column comments text default \"No Comment\"")
        conn.commit()
        cprint("Table altered: \"comments\" column added.","green")
    except sqlite3.Error as e:
        cprint(f"SQLite Error: {e}","red")

# Drops and recreates table
def drop_table():
    try:
        cursor.execute("drop table if exists posts")
        conn.commit()
        create_table()
        cprint("Posts table dropped and recreated.","green")
    except sqlite3.Error as e:
        cprint(f"SQLite Error: {e}","red")
        
# checks if comment column is present
def comment_present():
    try:
        cursor.execute("SELECT comments FROM posts LIMIT 1")
        return True
    except sqlite3.Error:
        return False

# main code
cprint("\n===SOCIAL MEDIA TRACKER===", "magenta")

while True:
    # Ordered functionalities
    functionalities_list = [
        ("Add Post", add_post),
        ("View Posts", view_posts),
        ("Like Post", like_post),
    ]

    # Insert Comment option only if comment column exists
    if comment_present():
        functionalities_list.append(("Comment on Post", add_comment))

    # Continue remaining options
    functionalities_list.extend([
        ("Delete Post", delete_post),
        ("Alter Table ( Add comments column )", alter_table),
        ("Drop and Recreate Table", drop_table),
        ("Exit", None)
    ])

    # Convert to dictionary
    functionalities = dict(functionalities_list)

    # It will be created like this
    # functionalities = {
    #     "Add Post": add_post,
    #     "View Posts": view_posts,
    #     "Like Post": like_post,
    #     "Comment on Post": add_comment, It will be shown only if comments column exists
    #     "Delete Post": delete_post,
    #     "Alter Table ( Add comments column )": alter_table,
    #     "Drop and Recreate Table": drop_table,
    #     "Exit": None
    # }

    # Inquirer package is used for selection in command with up and down arrow keys
    selected = inquirer.select(
        message="Select an option:",
        choices=list(functionalities.keys()),
        default="Add Post",
    ).execute()

    if selected == "Exit":
        cprint("Exiting program...", "magenta")
        break
    else:
        functionality = functionalities[selected]
        if functionality:
            functionality()
        else:
            cprint("Invalid Choice!!", "red")
