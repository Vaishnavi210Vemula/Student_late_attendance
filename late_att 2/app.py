import mysql.connector
from twilio.rest import Client
from datetime import datetime
from flask import Flask, render_template, request,flash

app = Flask(__name__)
app.secret_key='xxx'

# Connect to the database
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="password",
    database="late_report"
)

# Function to update the student's details
def update_student_details():
    student_id = request.form['roll_no']

    if not student_id:
        flash("Please enter a student ID.", "error")
        return
    cursor=None
    try:
        # Create a cursor to execute SQL queries
        cursor = db.cursor()

        # Increment the count column by 1 for the specified student
        update_query = f"UPDATE stu_details SET Late_no = Late_no + 1 WHERE stu_id = '{student_id}'"
        cursor.execute(update_query)
        db.commit()

        # Get the parent's phone number based on the student's ID
        select_query = f"SELECT Phonenumber,Late_no FROM stu_details WHERE stu_id = '{student_id}'"
        cursor.execute(select_query)
        result=cursor.fetchone()
        Phonenumber = result[0]
        count=result[1]

        # Get the current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if count >= 3:
            # Create the message content with the count of absences
            message_content = f"Your ward is lante to college. Date and Time: {current_datetime}. It's been {count} times your ward is late to college in this Semester."
        else:
            # Create the message content without the count of absences
            message_content = f"Your ward is late to college. Date and Time: {current_datetime}"

        # Send a message to the student's parent
        account_sid = "AC1b1080b5926f500522c325d4ab272909"
        auth_token = "b37622ef500cc9e8f2f89f5e0b21e609"
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=message_content,
            from_="+15393287224",
            to=Phonenumber
        )

        flash("Student count updated successfully. Message sent to the student's parent.", "success")

    except mysql.connector.Error as error:
        flash(f"Error updating student count:\n{error}", "error")

    finally:
        cursor.close()
        db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        update_student_details()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,port=5501)
