from flask import Flask, request
from flask import jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
from PIL import Image
from PIL.ExifTags import TAGS

#Creating flask object
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rest.db'

#Creating db object for sqlaalchemy
db = SQLAlchemy(app)
db.init_app(app)


#database model for storing user data
class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    ip = db.Column(db.String(length=20), nullable=False)
    time_req = db.Column(db.DateTime, nullable=False)
    filename = db.Column(db.String(50),nullable=False)

#Initlising database with models defined
with app.app_context(): 
    db.create_all()


#Get route for root
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    #ip_ad = request.remote_addr

    return 'REST TEST' 


#PoST CALL with IMAGE
@app.route('/image',methods=['GET', 'POST'])
def image_metadata():
    #extracting image from POST call
    file = request.files['image']

    if file:
        print("type of file is:",type(file))
        print("filename is:",file.filename)

        #saving file in local folder
        img_file_name = file.filename
        file.save(os.path.join(app.config['uploadFolder'], img_file_name))

        #Storing Request details in database
        time = datetime.now()

        print("time at which user requested is:",time)
        ip_ad = request.environ['REMOTE_ADDR']
        print("user requested is:",ip_ad)

        new_request = User(ip = ip_ad, time_req = time, filename = img_file_name)
        db.session.add(new_request)
        db.session.commit()

        #loading image and getting basic height,width,filename
        try:
            img = Image.open(file)
        except IOError:
            return "please provide images only"
            
        img_dim = img.size
        img_meta = {}
        img_meta["name"] = img_file_name
        img_meta["width"] = img_dim[0]
        img_meta["height"] = img_dim[1]

        #Getting other metadata using image.getexif
        for tag,value in img.getexif().items():
            print(tag,value)
            if tag in TAGS:
                tag_name = TAGS[tag]
                img_meta[tag_name] = value
    

        return jsonify(img_meta)
    else:
        return "Please send file with the post request"
  
# main driver function
if __name__ == '__main__':

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['uploadFolder'] = os.getcwd() + '/static/'
    app.run(debug=True, host='0.0.0.0', port=8000)
    # run() method of Flask class runs the application 
    # on the local development server.
