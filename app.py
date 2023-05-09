# source myenv/bin/activate

from flask import Flask, render_template, jsonify, request, send_file, Response, session, redirect, url_for, flash, get_flashed_messages
from flask_cors import CORS, cross_origin
import cv2
import numpy as np
import os, shutil
from werkzeug.utils import secure_filename
from prediction.make_predictions import *
from OCR.ocr import apply_easyocr
from database_operations.DB_operstions import DBOperations
import os
import datetime
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['SECRET_KEY'] = 'supersecretkey'
app.secret_key = 'supersecretkey'


# 1. Home Page /  Default Page
@app.route('/', methods=['GET', "POST"])
@cross_origin()
def default_url():
    return redirect("/login")

# 2. Login Page
@app.route('/login', methods=['GET', "POST"])
@cross_origin()
def login_page():
    if "username" in session:
        return redirect(url_for("home_page"))
    messages = get_flashed_messages()
    if messages:
        alert = messages[0]
        alert_msg = messages[1]

        return render_template("login.html",  alert = alert , alert_meaage = alert_msg)

    return render_template("login.html")


# 3. Logout  redirect -> login page
@app.route('/logout', methods=['GET', "POST"])
@cross_origin()
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/signup', methods=['GET', "POST"])
@cross_origin()
def signup_page():

    session.clear()

    return render_template("signup.html")





# 4. Dashboard / Homepage
@app.route('/dashboard', methods=['GET', "POST"])
@cross_origin()
def home_page():
    # print(dir(request))
    print(request.url)
    print(request.headers.get('Referer'))
    db = DBOperations()

    db.create_Database_Table()
    fulldata, rows = db.showTable(table_name="user_details")
    dist_user = []
    for row in rows:
        dist_user.append(row[0])
    print("All users:\n", dist_user)
    print("dist users:\n", set(dist_user))


    if 'login' in str(request.headers.get('Referer')):
        try:
            username = request.form["username"]
            password = request.form["password"]


            if username not in  set(dist_user):
                alert = True
                alert_msg = "user not found"
                flash(alert)
                flash(alert_msg)
                return redirect(url_for('login_page'))

            elif username in set(dist_user):
                for row in rows:
                    if row[0] == username:
                        if row[1] == password:
                            session['username'] = username
                            session['password'] = password
                            success = True
                            break

                if not success:
                    alert = True
                    alert_msg = "Password not matched"
                    flash(alert)
                    flash(alert_msg)
                    return redirect(url_for('login_page'))

        except:
            pass

    elif 'signup' in str(request.headers.get('Referer')):
        try:
            print("enterd signup")

            username = request.form["username"]
            password = request.form["password"]

            if username in dist_user:
                alert = True
                alert_msg = "user already exists."
                flash(alert)
                flash(alert_msg)
                return redirect(url_for('login_page'))


            db = DBOperations()
            db.enter_recordTo_Table(user_name=username, password=password , type="user_details")

            # if username in all_users:

            session['username'] = username
            session['password'] = password

        except:
            "some error: not got proper response from signup page to dashboard"


    elif 'submit' in str(request.headers.get('Referer')):
        print("in submit")
        print(request.form)
        # if request.form.get('Next'):
        if True:
            global House_Number , Rider_Name , Rider_Phone_Number , Purpose

            House_Number = request.form['House_Number']
            Rider_Name = request.form['Rider_Name']
            Rider_Phone_Number = request.form['Rider_Phone_Number']
            Purpose = request.form['Purpose']


            print("\nHouse_Number : ",House_Number , "\nRider Name : ", Rider_Name , "\nRider_Phone_Number: ", Rider_Phone_Number, "\nPurpose:", Purpose)

            database = db = DBOperations()

            print("entering to db pred")
            database.enter_recordTo_Table(number_plate=str(easyocr_text), type="Predictions",user_name=str(session['username']) , Driver_name = Rider_Name, Vehicle_type = prediction, phone_number = Rider_Phone_Number , Destination = House_Number,  Puspose = Purpose)

            redirect(url_for("home_page"))

        # elif request.form.get('Back'):
        #     # print("request.form: ", request.form)
        #     print("Using Back")
        #     redirect(url_for("home_page"))



    try:
        cv2.destroyAllWindows()
    except:
        pass
    #
    # if "live" in request.headers.get('Referer'):
    #     global video_feed_active
    #     video_feed_active = False
    #     global camera
    #     if camera is not None:
    #         camera.release()
    #         camera = None
    #     return render_template('index2.html')

    print(f"\n\nusername: {session['username']} \n password:{session['password']}")
    database = db = DBOperations()
    # logger.write_logs("Someone Entered Homepage, Rendering Homepage!")
    database.create_Database_Table()

    return render_template("home_.html" , User_Profile = session['username'])



# 5. Submit page
@app.route('/submit', methods=["GET", "POST"])
@cross_origin()
def prediction_page():
    if ("username" not in session) and ("password" not in session):
        return redirect(url_for('login_page'))

    else:
        database = db = DBOperations()
        global detected_path, cropped_path, imageFilePath, easyocr_text, static_org, prediction

        print(f"type of static_org: {type(static_org)}")

        # static_org.save('static/files/input_img.jpg')
        imageFilePath = 'static/files/input_img.jpg'
        cv2.imwrite(imageFilePath , static_org)

        try:

            detected, cropped, detected_path, cropped_path = yolo_model(img_path=imageFilePath)


            print("\nImage FIle path : ", imageFilePath, "\ndetected_path : ", detected_path, "\ncropped_path : ",
                  cropped_path)

            easyocr_text = apply_easyocr((cropped))
            # database.enter_recordTo_Table(number_plate=str(easyocr_text), type="Predictions",
            #                               user_name=str(session['username']))

            # In daashboard -> submit

        except Exception  as e:
            # if "IndexError" in e:
            return render_template("error.html", message = "No Vehicle / Number Plate found in Image.")



        return render_template("img.html", input=imageFilePath, detected=detected_path, cropped=cropped_path,
                               easyocr_text=easyocr_text , vehicle_class = prediction , user_name = session['username'])  # , img_path_final = final_path

        ###         # if request.method == 'POST': end
    #
    # except Exception as e:
    #     if "'NoneType' object has no attribute 'shape'" in str(e):
    #         return render_template("error.html", message=f"Please select an image")
    #     elif "error: (-215:Assertion failed) !buf.empty() in function 'imdecode_'" in str(e):
    #         return render_template("error.html", message=f"No File Selected.")
    #     elif "is not defined" in str(e):
    #         return render_template("error.html",
    #                                message=f"First you have to enter an  image for prediction then you can see detailed preview of it.")
    #     else:
    #         return render_template("error.html", message="No Number Plate detected in image.")

    # except Exception as e:
    #     # print(str(e))
    #     return render_template("error.html", message=str(e))


# 6. About Page
@app.route('/about', methods=["GET", "POST"])
@cross_origin()
def about():
    return render_template("about.html")



# 7. Detailed Preview Page
@app.route('/detailed_preiew', methods=["GET", "POST"])
@cross_origin()
def detailed_preiew():
    try:
        return render_template("img.html", input=imageFilePath, detected=detected_path,
                               cropped=cropped_path, easyocr_text=easyocr_text)  # , img_path_final = final_path
    except Exception as e:
        if "is not defined" in str(e):
            msg = f"First you have to enter an  image for prediction then you can see detailed preview of it."
            return render_template("error.html",
                                   message=f"First you have to enter an  image for prediction then you can see detailed preview of it.")
            # return redirect(url_for(f"message" , msg = msg))


# 8. Database preview Page
@app.route('/database', methods=["GET", "POST"])
@cross_origin()
def display_data():
    database = db = DBOperations()
    _, rows = database.showTable(table_name = "Predictions" , user_name=session['username'])
    # print("start", rows, dir(rows), "end")
    return render_template('db.html', data=rows)



# 9. Reset Session  redirect -> Error page / message
@app.route('/reset_session', methods=["GET", "POST"])
@cross_origin()
def reset():
    database = DBOperations()

    database.delete_rows_per_user(user = session['username'])
    # database.create_Database_Table()
    return render_template('error.html', message="Reset Session Successful")
    # return  flask.url_for("home_page")



# 10. Download Data
@app.route('/downnload_data', methods=["GET", "POST"])
@cross_origin()
def download():
    database = DBOperations()
    data = database.getDatafromDatabase()
    output_path = "output/Number_plate_data.csv"
    data.to_csv(output_path)
    # downloads_path = str(Path.home() / "Downloads")
    # shutil.copy(output_path, downloads_path)
    shutil.copy(output_path, "static/Number_plate_data.csv")

    return send_file("static/Number_plate_data.csv")



# 11. Submit sample page
@app.route('/submit_sample', methods=["GET", "POST"])
@cross_origin()
def submit_sample():
    # try:
        if request.method == 'POST':
            database = db = DBOperations()
            global detected_path, cropped_path, imageFilePath, easyocr_text

            imageFilePath = os.path.join('static', 'Cars72.png')

            print("\n\n\n\nimageFilePath", imageFilePath)

            detected, cropped, detected_path, cropped_path = yolo_model(img_path=imageFilePath)

            print("\nImage FIle path : ", imageFilePath, "\ndetected_path : ", detected_path, "\ncropped_path : ",
                  cropped_path)

            easyocr_text = apply_easyocr((cropped))

            for i in range(3):
                if easyocr_text[i] == '6':
                    easyocr_text[i] = "G"
                    
            database.enter_recordTo_Table(number_plate = str(easyocr_text) , type = "Predictions" , user_name = session['username'])

            return render_template("img.html", input=imageFilePath, detected=detected_path, cropped=cropped_path,
                                   easyocr_text=easyocr_text)  # , img_path_final = final_path



    # except Exception as e:
    #     if "'NoneType' object has no attribute 'shape'" in str(e):
    #         return render_template("error.html", message=f"Please select an image")
    #     elif "error: (-215:Assertion failed) !buf.empty() in function 'imdecode_'" in str(e):
    #         return render_template("error.html", message=f"No File Selected.")
    #     elif "is not defined" in str(e):
    #         return render_template("error.html",
    #                                message=f"First you have to enter an image for prediction then you can see detailed preview of it.")
    #     else:
    #         return render_template("error.html", message="No Number Plate detected in image.")
    # except Exception as e:
    #     return render_template("error.html", message=str(e))



# Start Camera Function
def start_camera():
    global camera
    camera = cv2.VideoCapture(0)


count = 0


# Live camera / frame generative function
def gen_frames():
    global camera, count, buffer, frame, org
    while video_feed_active:
        success, frame = camera.read()
        # print(type(frame))

        org = frame.copy()


        if count < 1:
            start_time = datetime.datetime.now()

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            count +=1

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# 12. returns captured image as static response to the html page - img src tag
@app.route("/captured_img")
@cross_origin()
def captured_img():
    global buffer , frame , static_org
    ret, static_buffer = cv2.imencode('.jpg', static_org)
    static_frame = static_buffer.tobytes()

    return Response(static_frame, mimetype='image/jpeg')


# 13. Captures thr img and redirects to the captre.html page where it calls '/captured_img' for the image
@app.route("/capture")
@cross_origin()
def capture():
    global buffer , frame, org , static_buffer , static_frame , static_org, prediction

    static_org = org

    prediction = classify_vehicle(org)

    global video_feed_active
    video_feed_active = False
    global camera
    if camera is not None:
        camera.release()
        camera = None

    # return render_template("capture.html" , vehicle_class = prediction)
    return redirect("/submit")


# 14. starts and processes the live camera where the html page gets the input from  '/video_stram' path
@app.route('/live' , methods = ["GET" , "POST"])
def live():
    global video_feed_active
    video_feed_active = True
    start_camera()
    return render_template('live.html')


# 15. called for live video stram and returns responses from ''gen_frames' generative function'
@app.route('/video_stream')
def video_stream():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



# 16. closes the live camera stream
@app.route('/close'  , methods = ["GET" ])
def close():
    print(request.headers.get('Referer'))
    global video_feed_active
    video_feed_active = False
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return render_template('index2.html')


# # 18. Used to show
# @app.route("/message")
# @cross_origin()
# def message():
#     return render_template("error.html" , message = request.args.get('msg'))


# 19. for random testing purpose
@app.route("/tp")
@cross_origin()
def tp():
    # 1. Delete User Database
    db = DBOperations()
    # db.dropTabel(table_name="user_details")
    # db.dropTabel(table_name="Predictions")
    db.showTable(table_name="Predictions" , user_name=session['username'])

    return jsonify({"success":True})



if __name__ == "__main__":
    app.run(port=7070, debug=True)  #