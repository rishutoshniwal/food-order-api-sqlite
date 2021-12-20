from flask import Flask, jsonify, request
from flask import Flask,render_template,request,session,logging,url_for,redirect,flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from flask_session import Session
import random
from passlib.hash import sha256_crypt
from datetime import timedelta
# from flask_login import LoginManager

engine=create_engine("mysql+pymysql://root:Rishu0703@localhost/ssd3")
db=scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)
app.secret_key='rishutoshniwal'
# login_manager=LoginManager()
# login_manager.init_app(app)

loggedin=False
loggedinUserName=''
i=0
start=db.execute("SELECT count(*) from ordermap").fetchone()
for c in start:
    i=c


@app.route("/", methods =['GET', 'POST'])
def index():
    return render_template("index.html")


             
@app.route('/register', methods = [ 'GET','POST'])
def register():
    global loggedin
    if loggedin==True:
        message=[]
        message.append("A new user can login only when current user logout")
        return redirect(url_for('index',message=message))
    if request.method=="POST":
        data = request.form
        username = data['username']
        pass1 = data['password']
        type1 = data['type']
        check=db.execute("SELECT username from users WHERE username=:username",{"username":username}).fetchone()
            
        
        if check!=None:
            message=[]
            message.append("You are already registered, you can login with your credentials")
            return redirect(url_for('login',message=message))

        db.execute("INSERT INTO users(username,password,usertype) VALUES(:username,:pass1,:type1)",
                {"username":username,"pass1":pass1,"type1":type1})
        db.commit()
    
        message=[]
        message.append("New user registered succesfully")
        return redirect(url_for('login',message=message))
    return render_template("register.html")    

@app.route('/login', methods =['GET', 'POST'])
def login():
    global loggedin
    if loggedin==True:
        message=[]
        message.append("You are already logged in")
        return redirect(url_for('index',message=message))
    if request.method=="POST":
        data = request.form
        username = data['username']
        pass1 = data['password']
    

        check=db.execute("SELECT * from users WHERE username=:username",{"username":username}).fetchone()
        
       

        if check is None :
            message=[]
            message.append("User does not exist,you need to register first")
            return redirect(url_for('register',message=message))
    
        else:
            currentLoginUserType=check['usertype']
            if pass1==check['password']:
            
                session['loggedin']=True
                session['id']=check['username']
                session['username']=check['username']
                global loggedinUserName
                
                loggedin=True
                loggedinUserName=check['username']
                if(currentLoginUserType=="chef"):
                    message=[]
                    message.append("Chef , Successfully Logged in")
                    return redirect(url_for('index',message=message))
                else :  
                   message=[]   
                   message.append("Customer , Successfully Logged in")
                   return redirect(url_for('index',message=message))
            else:
                message=[]
                message.append("Wrong Password")
                return redirect(url_for('login',message=message))
    return render_template("login.html")        

@app.route('/logout', methods =['GET', 'POST'])	
def logout():
    global loggedin
    global loggedinUserName
    if loggedin==False:
         message=[]
         message.append("User already logged out, login again to perform any action")
         return redirect(url_for('login',message=message))
    else:  
        loggedin=False
        loggedinUserName=''
        message=[]
        message.append("Logout successfull")
        return redirect(url_for('login',message=message))	

@app.route('/show_menu', methods =['GET', 'POST'])	
def show_menu():
    global loggedin
    if loggedin==False:
        message=[]
        message.append("You need to login first")
        return redirect(url_for('login',message=message))
    
    # res="itemno"+"\t\t"+"halfplate"+"\t\t"+"fullplate\n"
    menu=db.execute("SELECT * from menu").fetchall()
    return render_template("show_menu.html",menu=menu)
    
# @app.route('/getotherdetails', methods =['GET', 'POST'])	
# def getotherdetails():
#     data = request.get_json()
#     username=data['username']
#     orderid=data['orderid']
#     tip=data['tip']
#     people=data['people']
#     discount=data['discount']
#     db.execute("Update ordermap set tip=:tip,people=:people,discount=:discount WHERE (username=:username and orderid=:orderid)"
#     ,{"username":username,"orderid":orderid,"tip":tip,"people":people,"discount":discount})
#     db.commit()	

#     out=""
#     check=db.execute("SELECT itemno,platetype,quantity,total from transaction WHERE orderid=:orderid",{"orderid":orderid}).fetchall()
#     for c in check:
#         out=out+"item "+str(c['itemno'])+" ["+str(c['platetype'])+"] ["+str(c['quantity'])+"] : "+str(c['total'])+"\n"
#     check=db.execute("SELECT sum(total) from transaction WHERE orderid=:orderid",{"orderid":orderid}).fetchall()
#     val=0
#     for c in check:
#         val=int(c['sum(total)'])
#         out=out+"total_cost_of_all_items : "+str(c['sum(total)'])+"\n"
#     out=out+"Tip percentage : "+str(tip)+"\n" 
#     out=out+"Discount/Increase : "+str(discount)+"\n"

#     val=(val* (100+tip)/100) *((100+discount)/100)
#     out=out+"Final total_cost_of_all_items : "+str('%.2f'%val)+"\n"
#     out=out+"Count of people who shares bill : "+str(people)+"\n"
#     share=val/people
#     out=out+"Updated amount_with_tip to be paid per menu_head : "+str('%.2f'%share)

#     return out

@app.route('/previous_order', methods =['GET', 'POST'])	
def previous_order():
    data = request.get_json()
    username = data['username']
    check=db.execute("SELECT orderid from ordermap WHERE username=:username",{"username":username}).fetchall()
    res="Your order ids are : \n"
    for c in check:
        res=res+"Order id : "+str(c['orderid'])+"\n"
    return res

@app.route('/insert_menu', methods =['GET', 'POST'])	
def insert_menu():  
    global loggedin
    if loggedin==False:
        message=[]
        message.append("You need to login first")
        return redirect(url_for('login',message=message))
    global loggedinUserName
    username=loggedinUserName
    check=db.execute("SELECT usertype from users WHERE username=:username",{"username":username}).fetchone()
    if check['usertype']=="customer":
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
            
            db.execute("INSERT INTO menu(itemno,halfplate,fullplate) VALUES(:itemno,:halfplate,:fullplate)",
                    {"itemno":itemno,"halfplate":halfplate,"fullplate":fullplate})
            db.commit()
        message=[]
        message.append("Item added to menu succesfully")
        return render_template("add_items_to_menu.html",message=message)

    return render_template("add_items_to_menu.html")
    

@app.route('/fetch_that_bill/<orderid>/<username>', methods =['GET', 'POST'])	
def fetch_that_bill(orderid,username): 
    #  data = request.get_json()
    #  username=data['username']
    #  orderid=data['orderid']
     check=db.execute("SELECT tip from ordermap WHERE (orderid=:orderid and username=:username)",{"orderid":orderid,"username":username}).fetchone()
     tip=check['tip']
     check=db.execute("SELECT people from ordermap WHERE (orderid=:orderid and username=:username)",{"orderid":orderid,"username":username}).fetchone()
     people=check['people']  
     check=db.execute("SELECT discount from ordermap WHERE (orderid=:orderid and username=:username)",{"orderid":orderid,"username":username}).fetchone()
     discount=check['discount'] 
     check=db.execute("SELECT sum(total) from transaction WHERE orderid=:orderid",{"orderid":orderid}).fetchone()
     subtotal=check['sum(total)']  
     orderlist=db.execute("SELECT itemno,platetype,quantity,total from transaction WHERE orderid=:orderid",{"orderid":orderid}).fetchall()
    
     val=float(subtotal)* ((100 + float(tip) )/100) * ((100 + float(discount) )/100)
     total=str('%.2f'%val)
     val=val/people
     sharePerHead=str('%.2f'%val)
    

     return render_template('bill.html',orderid=orderid,username=username,tip=tip,people=people,subtotal=subtotal,discount=discount,orderlist=orderlist,total=total,sharePerHead=sharePerHead)
       
    

@app.route('/ordermap', methods =['GET', 'POST'])	
def ordermap():
    global i
    i=i+1
    # data = request.get_json()
    global loggedinUserName
    username = loggedinUserName
    db.execute("INSERT INTO ordermap(username,orderid) VALUES(:username,:orderid)",{"username":username,"orderid":i})
    db.commit()
    return str(i)
    

@app.route('/insert_order', methods =['GET', 'POST'])	
def insert_order():
    global loggedin
    if loggedin==False:
        message=[]
        message.append("You need to login first")
        return redirect(url_for('login',message=message))
        
    if request.method=="POST":
        
        data = request.form
        global loggedinUserName
        orderid=int(ordermap())

        itemnoList=data.getlist('itemno[]')
        platetypeList=data.getlist('platetype[]')
        quantityList=data.getlist('quantity[]')
        length=len(itemnoList)
        print(length)
        for i in range(length):
            itemno=int(itemnoList[i])
            platetype=platetypeList[i]
            quantity=int(quantityList[i])
            costPerUnit=db.execute("select fullplate from menu where itemno=:itemno",{"itemno":itemno}).fetchone()
            if(platetype=="half"):
                costPerUnit=db.execute("select halfplate from menu where itemno=:itemno",{"itemno":itemno}).fetchone()

            total=0
            for c in costPerUnit:
                total=c*quantity
            check=db.execute("select quantity,total from transaction where (orderid=:orderid and itemno=:itemno and platetype=:platetype)",{"orderid":orderid,"itemno":itemno,"platetype":platetype}).fetchone()
            
            if check is None :
                db.execute("INSERT INTO transaction(orderid,itemno,platetype,quantity,total) VALUES(:orderid,:itemno,:platetype,:quantity,:total)",{"orderid":orderid,"itemno":itemno,"platetype":platetype,"quantity":quantity,"total":total})
                db.commit()	 
            else :
                db.execute("delete from transaction where (orderid=:orderid and itemno=:itemno and platetype=:platetype)",{"orderid":orderid,"itemno":itemno,"platetype":platetype})
                db.commit()
                # for c in check:
                quantity=quantity+check['quantity']
                total=total+check['total']
                    
                db.execute("INSERT INTO transaction(orderid,itemno,platetype,quantity,total) VALUES(:orderid,:itemno,:platetype,:quantity,:total)",{"orderid":orderid,"itemno":itemno,"platetype":platetype,"quantity":quantity,"total":total})
                db.commit()	 
            username=loggedinUserName    
            tip=data['tip']
            people=data['people']
            discount=0
            if data['play_luck_game']=="yes":
                arr_of_luck=[-50,-25,-25,-10,-10,-10,0,0,0,0,20,20,20,20,20,20,20,20,20,20]
                index=random.randint(0,19)
                discount=arr_of_luck[index]

            db.execute("Update ordermap set tip=:tip,people=:people,discount=:discount WHERE (username=:username and orderid=:orderid)"
            ,{"username":username,"orderid":orderid,"tip":tip,"people":people,"discount":discount})
            db.commit()	       

        return redirect(url_for("fetch_that_bill",orderid=orderid,username=username))
    return render_template("placeOrder.html")

if __name__ == '__main__':
	app.run(debug=True)
