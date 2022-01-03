from flask import Flask, jsonify, request
from flask import Flask,render_template,request,session,logging,url_for,redirect,flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from flask_session import Session
import random
from passlib.hash import sha256_crypt
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from sqlalchemy import desc




app = Flask(__name__)
app.secret_key='rishutoshniwal'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(username):
    return Users.query.get(username)


class Users(UserMixin,db.Model):
    username = db.Column(db.String(80), unique=True, nullable=False,primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    usertype=  db.Column(db.String(120), nullable=False)

    def get_id(self):
           return (self.username)

class Menu(db.Model):
    itemno= db.Column(db.Integer, primary_key=True,unique=True, nullable=False)
    halfplate=db.Column(db.Integer, nullable=False)
    fullplate=db.Column(db.Integer, nullable=False)

class Ordermap(db.Model):   
    orderid=db.Column(db.Integer, primary_key=True,unique=True, nullable=False)
    username = db.Column(db.String(80),nullable=False)
    tip=db.Column(db.Integer, nullable=False)
    people=db.Column(db.Integer, nullable=False)
    discount=db.Column(db.Integer, nullable=False)

class Transaction(db.Model):
    orderid=db.Column(db.Integer, db.ForeignKey('ordermap.orderid'), nullable=False,primary_key=True) 
    itemno=db.Column(db.Integer,db.ForeignKey('menu.itemno'), nullable=False,primary_key=True)  
    platetype=db.Column(db.String(80), nullable=False,primary_key=True)
    quantity=db.Column(db.Integer, nullable=False)
    total=db.Column(db.Integer, nullable=False)





# loggedin=False
# loggedinUserName=''



@app.route("/", methods =['GET', 'POST'])
def index():
    return render_template("index.html")


             
@app.route('/register', methods = [ 'GET','POST'])
def register():
    if request.method=="POST":
        data = request.form
        username = data['username']
        pass1 = data['password']
        type1 = data['type']
        check=Users.query.filter_by(username=username).first()

        if check!=None:
            message=[]
            message.append("You are already registered, you can login with your credentials")
            return redirect(url_for('login',message=message))

        
        obj=Users(username=username,password=pass1,usertype=type1)
        db.session.add(obj)
        db.session.commit()

        
        message=[]
        message.append("New user registered succesfully")
        return redirect(url_for('login',message=message))
    return render_template("register.html")    

@app.route('/login', methods =['GET', 'POST'])
def login():
    

    if request.method=="POST":
        data = request.form
        username = data['username']
        pass1 = data['password']
    

        check=Users.query.filter_by(username=username).first()
       

        if check is None :
            message=[]
            message.append("User does not exist,you need to register first")
            return redirect(url_for('register',message=message))
    
        else:
            currentLoginUserType=check.usertype
            if pass1==check.password:
                if(currentLoginUserType=="chef"):
                    message=[]
                    message.append("Chef , Successfully Logged in")
                    login_user(check)
                    return redirect(url_for('index',message=message))
                else :  
                   message=[]   
                   message.append("Customer , Successfully Logged in")
                   login_user(check)
                   return redirect(url_for('index',message=message))
            else:
                message=[]
                message.append("Wrong Password")
                return redirect(url_for('login',message=message))
    return render_template("login.html")        

@app.route('/logout', methods =['GET', 'POST'])	
def logout():
    
    if current_user.is_authenticated:
        message=[]
        message.append("Logout successfull")
        logout_user()
        return redirect(url_for('login',message=message))	
    else:
        message=[]
        message.append("User already logged out, login again to perform any action")
        return redirect(url_for('login',message=message))


@app.route('/show_menu', methods =['GET', 'POST'])	
def show_menu():
    
    if current_user.is_authenticated==False:
        message=[]
        message.append("You need to login first")
        return redirect(url_for('login',message=message))
    
   
    menu=Menu.query.all()
    return render_template("show_menu.html",menu=menu)
    


@app.route('/previous_order', methods =['GET', 'POST'])	
def previous_order():
    if current_user.is_authenticated==False:
        message=[]
        message.append("You need to login first")
        return redirect(url_for('login',message=message))
    username=current_user.get_id()
    orderlist=Ordermap.query.filter_by(username=username).all()
    return render_template("previous_orders.html",orderlist=orderlist,username=username)

@app.route('/insert_menu', methods =['GET', 'POST'])	
def insert_menu():  
    if current_user.is_authenticated==False:
        message=[]
        message.append("You need to login first")
        return redirect(url_for('login',message=message))

    
    username=current_user.get_id()
    check=Users.query.filter_by(username=username).first()

    if check.usertype=="customer":
        message=[]
        message.append("Only chefs are allowed to perform this operation")
        return redirect(url_for('index',message=message))

    if request.method=="POST":
        data = request.form
        itemnoList=data.getlist('itemno[]')
        halfplateList=data.getlist('halfplate[]')
        fullplateList=data.getlist('fullplate[]')
        length=len(itemnoList)
        for i in range(length):
            itemno=int(itemnoList[i])
            halfplate=int(halfplateList[i])
            fullplate=int(fullplateList[i])

            check=Menu.query.filter_by(itemno=itemno).first()
            if check!=None:
                check.itemno=itemno
                check.halfplate=halfplate
                check.fullplate=fullplate
                db.session.add(check)
                db.session.commit()
            
            else:
                obj=Menu(itemno=itemno,halfplate=halfplate,fullplate=fullplate)
                db.session.add(obj)
                db.session.commit()
        message=[]
        message.append("Items added to menu succesfully")
        return render_template("add_items_to_menu.html",message=message)

    return render_template("add_items_to_menu.html")
    

@app.route('/fetch_that_bill/<orderid>/<username>', methods =['GET', 'POST'])	
def fetch_that_bill(orderid,username): 
    if current_user.is_authenticated==False:
        message=[]
        message.append("You need to login first")
        return redirect(url_for('login',message=message))

    
    
    currentLoginUsername=current_user.get_id()
    if username!=currentLoginUsername:
        message=[]
        message.append("You can not see other users' bill ")
        return redirect(url_for('login',message=message))

    

    check=Ordermap.query.filter_by(orderid=orderid ,username=username).first()

    tip=check.tip
    people=check.people  
    discount=check.discount
    
    orderlist=Transaction.query.filter_by(orderid=orderid).all()
    subtotal=0
    for order in orderlist:
        subtotal=subtotal+order.total  
    
    val=float(subtotal)* ((100 + float(tip) )/100) * ((100 + float(discount) )/100)
    total=str('%.2f'%val)
    val=val/people
    sharePerHead=str('%.2f'%val)
    

    return render_template('bill.html',orderid=orderid,username=username,tip=tip,people=people,subtotal=subtotal,discount=discount,orderlist=orderlist,total=total,sharePerHead=sharePerHead)
       
    
    

@app.route('/insert_order', methods =['GET', 'POST'])	
def insert_order():
    if current_user.is_authenticated==False:
        message=[]
        message.append("You need to login first")
        return redirect(url_for('login',message=message))
        
    if request.method=="POST":
        data = request.form
        username=current_user.get_id()
        tip=data['tip']
        people=data['people']
        discount=0
        if data['play_luck_game']=="yes":
            arr_of_luck=[-50,-25,-25,-10,-10,-10,0,0,0,0,20,20,20,20,20,20,20,20,20,20]
            index=random.randint(0,19)
            discount=arr_of_luck[index]
        
        maxOrderId=0
        allRows=Ordermap.query.all()
        for row in allRows:
            if row.orderid > maxOrderId:
                maxOrderId=row.orderid

       
        orderid=maxOrderId+1

        obj=Ordermap(orderid=orderid,username=username,tip=tip,people=people,discount=discount)
        db.session.add(obj)
        db.session.commit()

        itemnoList=data.getlist('itemno[]')
        platetypeList=data.getlist('platetype[]')
        quantityList=data.getlist('quantity[]')

        length=len(itemnoList)

        for i in range(length):
            itemno=int(itemnoList[i])
            platetype=platetypeList[i]
            quantity=int(quantityList[i])
            itemrow=Menu.query.filter_by(itemno=itemno).first()
            costPerUnit=itemrow.fullplate
            
            if(platetype=="half"):
                costPerUnit=itemrow.halfplate
            
            
               
           
            total=costPerUnit*quantity
            check=Transaction.query.filter_by(orderid=orderid,itemno=itemno,platetype=platetype).first()
            
            if check is None :
                obj=Transaction(orderid=orderid,itemno=itemno,platetype=platetype,quantity=quantity,total=total)
                db.session.add(obj)
                db.session.commit()
            else :
                check.quantity=check.quantity+quantity
                check.total=check.total+total
                db.session.add(check)
                db.session.commit()

        return redirect(url_for("fetch_that_bill",orderid=orderid,username=username))
    return render_template("placeOrder.html")

if __name__ == '__main__':
	app.run(debug=True)
