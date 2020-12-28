# -*- coding: utf-8 -*-

##do not generate pnr on 0 passwnfers
"""
Created on Thu Nov 19 16:03:51 2020
@author: Asus
"""

from flask import Flask,render_template,url_for,flash,redirect,request,session
from allforms import AdminAddTrains,  LoginForm, RegistrationForm,BookTrains,Passengers
import psycopg2
from datetime import datetime  
from datetime import timedelta  

D = datetime.now() + timedelta(days=60)  
D_today = datetime.now() + timedelta(days=0)  

app=Flask(__name__)
app.config['SECRET_KEY']='5791628bb0b13ce0c676dfde280ba245'


try:
    connection = psycopg2.connect(user = "postgres",
                                    password = "bharat00",
                                    host = "127.0.0.1",
                                    port = "5432",
                                    database = "railway") 
    # connection.autocommit=True

except (Exception, psycopg2.Error) as error :
    print("Error while connecting to PostgreSQL :",error)

def compare_date(d1,D2):
    if int((str(d1)[0:4]))-int(D2.year) < 0:
        return False
    elif int((str(d1)[0:4]))==int(D2.year) and int((str(d1)[5:7]))-int(D2.month) < 0:
        return False
    elif int((str(d1)[0:4]))==int(D2.year) and int((str(d1)[5:7]))==int(D2.month)  and int((str(d1)[8:10]))-int(D2.day) < 0:
        return False
    else: 
        return True

def delete_old_trains(cursor):
    cursor.execute("\
    create or replace function delete_old_trains()\
    returns trigger\
    language plpgsql\
    as\
    $$\
        begin\
        DELETE from availabletrains WHERE  EXTRACT(YEAR FROM train_date) < "+str(D_today.year)+" or\
        EXTRACT(year FROM train_date) = "+str(D_today.year)+" and EXTRACT(month FROM train_date) < "+str(D_today.month)+" or \
        EXTRACT(year FROM train_date) = "+str(D_today.year)+" and EXTRACT(month FROM train_date) = "+str(D_today.month)+"and \
        EXTRACT(day FROM train_date) < "+str(D_today.day)+"; \
        return new;\
        end;\
    $$\
    ")
def trigger_delete_trains(cursor): ##to generate the passenger tickets, we send the form data to procedure to be executed
    cursor.execute("\
    CREATE TRIGGER trigger_delete_trains\
    BEFORE insert  ON availabletrains\
    FOR EACH ROW EXECUTE PROCEDURE delete_old_trains();\
    ")

def create_passenger_tickets_log(cursor,trainname):
    cursor.execute("\
    create or replace function "+trainname+"_passenger_tickets()\
    returns trigger\
    language plpgsql\
    as\
    $$\
        begin\
        delete from "+trainname+" where berth_no=new.berth_no and coach_no= new.coach_no; \
        return new;\
        end;\
    $$\
    ")
def trigger_passenger_tickets(cursor,trainname): ##to generate the passenger tickets, we send the form data to procedure to be executed
    cursor.execute("\
    CREATE TRIGGER trigger_book_tickets\
    BEFORE INSERT  ON "+trainname+"_passengers\
    FOR EACH ROW EXECUTE PROCEDURE "+trainname+"_passenger_tickets();\
    ")

##done
def addtrain(form):#add trigger to check if date is within limits
    
    cursor = connection.cursor()
    # print("INSERT INTO availabletrains(train_no,train_date,no_of_ac_coaches,no_of_slp_coaches) values(%s,%s,%s,%s)",(form.train_no.data,form.date.data,form.ac_coaches.data,form.slp_coaches.data))
    cursor.execute("select train_no,train_date from availabletrains where train_no=%s and train_date=%s",(form.train_no.data,form.date.data))
    if len(cursor.fetchall())!=0:
        return 0
    cursor.execute("INSERT INTO availabletrains(train_no,train_date,no_of_ac_coaches,no_of_slp_coaches) values(%s,%s,%s,%s)",(form.train_no.data,form.date.data,form.ac_coaches.data,form.slp_coaches.data))
    
    trainname="t"+str(form.train_no.data)+"_"+str(form.date.data)[0:4]+'_'+str(form.date.data)[5:7]+'_'+str(form.date.data)[8:]
    print(trainname)
    connection.commit()
    cursor.close()
    cursor = connection.cursor()
    cursor.execute("create table "+trainname+"(berth_no int,coach_no int,coach_type varchar(8),berth_type varchar(2),availability bool,primary key(berth_no,coach_no) )")
    cursor.execute("create table "+trainname+"_passengers (pnr varchar(40),name varchar(40),age int,gender varchar(40),coach_no int,berth_no int,berth_type varchar(40),coach_type varchar(40), primary key(pnr,coach_no,berth_no))")
    for i in range(1,1+form.ac_coaches.data):
        for j in range(1,19):
            berth_type='LB'
            if j==3 or j==4 or j==9 or j==10 or j==15 or j==16 :
                berth_type='UB'
            
            if j==5 or j==11 or j==17:
                berth_type='SL'
            
            
            if j==6 or j==12 or j==18 :
                berth_type='SU'
                
            cursor.execute("insert into "+trainname+"(berth_no, coach_no ,coach_type ,berth_type ,availability) values (%s,%s,%s,%s,%s)",(j,i,'AC',berth_type,"true")) 
                            

    for i in range(1,1+form.slp_coaches.data):
        for j in range(1,25):
            
            berth_type='LB'
            if j==2 or j==5 or j==18 or j==10 or j==13 or j==21 :
                berth_type='MB'
            
            if j==3 or j==11 or j==14 or j==6 or j==19 or j==42:
                berth_type='UB'
            
            
            if j==7 or j==15 or j==23 :
                berth_type='SL'
            if j==8 or j==16 or j==24 :
                berth_type="SU"
            cursor.execute("insert into  "+trainname+"(berth_no ,coach_no ,coach_type ,berth_type ,availability) values (%s,%s,%s,%s,%s)",(j,i+form.ac_coaches.data,'Sleeper',berth_type,"true")) 
    
    connection.commit()
    cursor.close()
    cursor = connection.cursor()
    with cursor as cur:
        create_passenger_tickets_log(cur,trainname)
        trigger_passenger_tickets(cur,trainname)    
    connection.commit()    
    cursor.close()
    return 1

def AvailableTrains():

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM availabletrains")
    trains=cursor.fetchall()
    connection.commit()
    for i in range(0,len(trains)):
        if compare_date(str(trains[i][1]),D_today):
            flash(str(trains[i][0])+"   "+str(trains[i][1]))
    cursor.close()
    
    
##done
def addbookingagent(form): #add trigger to check if same booking agent exists
    cursor = connection.cursor()
    cursor.execute("INSERT INTO bookingagents(name,password,creditcard,address) values (%s,%s,%s,%s)",(str(form.agent_name.data),str(form.confirm_password.data),str(form.credit_card.data),str(form.address.data)))
    connection.commit()
    cursor.execute("SELECT id from bookingagents where name = %s and password = %s",(form.agent_name.data,form.confirm_password.data))
    agent_id= cursor.fetchall()[0][0]
    connection.commit()
    cursor.close()
    return agent_id

def checkseats(form):
    if(form.passengers_no.data==0):
        flash("Sorry! Cannot Book a ticket for 0 passenegers",'danger')
        return
    trainname="t"+str(form.train_no.data)+"_"+str(form.date.data)[0:4]+'_'+str(form.date.data)[5:7]+'_'+str(form.date.data)[8:]
    cursor=connection.cursor()
    cursor.execute("select train_no,train_date from availabletrains where train_no=%s and train_date=%s",(form.train_no.data,form.date.data))
    if len(cursor.fetchall())==0:
        flash("Train"+str(form.train_no.data)+" not available on date"+str(form.date.data),'info')
        return -1
    cursor.execute("select count((berth_no,coach_no)) from "+trainname+" where availability=true and coach_type= '"+form.coach_type.data+"'")
    available_seats=cursor.fetchall()
    if available_seats[0][0]<form.passengers_no.data:
        
        return 0
    else: return 1

def bookticket(form): ##add trigger for addition to bookedtickets- for availablility in train, also assigning berthnumber
   
    trainname="t"+str(form.train_no.data)+"_"+str(form.date.data)[0:4]+'_'+str(form.date.data)[5:7]+'_'+str(form.date.data)[8:]
    
    coach_size=24
    if(form.coach_type=='AC'):
        coach_size=18
            
    cursor=connection.cursor()
    
    cursor.execute("select min(coach_no) from "+trainname+" where availability=true and coach_type= '"+form.coach_type.data+"'")
    coach=cursor.fetchall()[0][0]
    cursor.execute("select min(berth_no) from "+trainname+" where availability=true and coach_type= %s and coach_no=%s",(form.coach_type.data,coach))
    berth=cursor.fetchall()[0][0] 
    pnr=str(form.train_no.data)+str(form.date.data)+"_"+str(coach)+"_"+str(berth)
    connection.commit()
    for i in range(0,form.passengers_no.data):
        cursor=connection.cursor()
        cursor.execute("select berth_type from "+trainname+" where coach_no="+str(coach)+" and berth_no="+str(berth))
        btype=cursor.fetchall()[0][0]
        cursor.execute("insert into "+trainname+"_passengers (pnr,name,age,gender,coach_no,berth_no,coach_type,berth_type) values (%s,%s,%s,%s,%s,%s,%s,%s)",(str(pnr),str((form.passengers[i].namep).data),str((form.passengers[i].age).data),str((form.passengers[i].gender).data),str(coach),str(berth),str(form.coach_type.data),str(btype)))
        
        if berth==coach_size:
            coach=coach+1
            berth=1
        else:
            berth=berth+1
        connection.commit()
    cursor.execute("insert into bookedtickets(pnr,train_no,train_date,passenger_no,booking_ag) values (%s,%s,%s,%s,%s)",(pnr,form.train_no.data,str(form.date.data),form.passengers_no.data,session.get('username')))
    connection.commit()
    cursor.close()
    cursor=connection.cursor()
    
    return pnr
#    for i in range(form.passengers_no.data):
#        cursor.execute("insert into passenger(pnr,coach_no,berth_no,name,age,gender,berth_type) values (%s,%s,%s,%s,%s,%s,%s)",(pnr,coach,berth+i))

@app.route("/")
@app.route("/home")
def home():
    
    cursor = connection.cursor()
    cursor.execute("Drop trigger if exists trigger_delete_trains on availabletrains")
    with cursor as cur:
        delete_old_trains(cur)    
        trigger_delete_trains(cur)
    connection.commit()    
    cursor.close()

    return render_template('home.html')


##done
@app.route("/admin",methods=["POST","GET"])
def admintrains():
    admin_key='0000'
    form=AdminAddTrains()
    if request.method=="POST":
        
        #flash('Data'+str(form.train_no.data)+str(form.date.data)+str(form.ac_coaches.data)+str(form.slp_coaches.data))
                                           
        
        
        if form.security_key.data!=admin_key:
            flash('Security key not matching- permission to add train denied!','danger')
            return redirect(url_for('home'))
        
        if form.validate_on_submit():
            if int((str(form.date.data)[0:4]))-int(D.year) < 0:
                flash('Please enter a date after '+str(D)[0:10]+' (YYYY-MM-DD)')
            elif int((str(form.date.data)[0:4]))==int(D.year) and int((str(form.date.data)[5:7]))-int(D.month) < 0:
                flash('Please enter a date after '+str(D)[0:10]+' (YYYY-MM-DD)')
            elif int((str(form.date.data)[0:4]))==int(D.year) and int((str(form.date.data)[5:7]))==int(D.month)  and int((str(form.date.data)[8:10]))-int(D.day) < 0:
                flash('Please enter a date after '+str(D)[0:10]+' (YYYY-MM-DD)') 
            elif form.slp_coaches.data==0 and form.ac_coaches.data==0:
                flash("Can't book a train with 0 coaches")
            else:                
                new_t=addtrain(form)
                if new_t==1:
                    flash('Train'+str(form.train_no.data)+' Added for date: '+str(form.date.data),'success')
                else:
                    flash('Train'+str(form.train_no.data)+'for date: '+str(form.date.data)+' already exists! Not Added!','danger')
        else:
            flash ("Failed !")
        return redirect(url_for('admintrains'))
    else :
        return render_template('admintrain.html',title='Admin',form=form)

@app.route('/book/passengers',methods=["POST","GET"])
def passengers(npassengers=0):
    
    if request.method=="GET":
        npassengers=int(request.args['npassengers'])
        
    form=Passengers()
   
    for i in range(npassengers):
        form.passengers.append_entry()
  
    # form = Passenger(request.POST)
    if request.method=="POST":
        # bookform.passenegers=form.passengers
        pnr=bookticket(form)
        
        flash("Ticket booked with pnr"+pnr,'success') # add all details of ticket
        cursor=connection.cursor()
        
        cursor.execute("select * from t"+pnr[0:1]+"_"+pnr[1:5]+"_"+pnr[6:8]+"_"+pnr[9:12]+"passengers where pnr = '"+pnr+"'")
        data=cursor.fetchall()
        connection.commit()
        cursor.close()
        return render_template("ticket.html",title="ticket",form=form,data=data)
    return render_template("passengers.html",title="passengers",form=form)

@app.route("/book",methods=["POST","GET"])
def booktrains():
    form=BookTrains()

    # formp=Passengers(passengers_no=form.passengers_no)
    
    if form.coach_type.data=='Select Coach Type':
        flash("Please select a Coach Type : AC / Sleeper Class")
    elif  request.method=="POST":
        
        chkseats=checkseats(form)
        # if form.validate_on_submit():
        if chkseats==0:
            flash("Sorry seats not available",'danger')
        elif chkseats==1 and form.passengers_no.data>0: 
            
            return redirect(url_for('passengers',npassengers=form.passengers_no.data))
            
            
    return render_template('booktrains.html',title='Book',form=form)

##done
@app.route("/register",methods=["POST","GET"])
def register():
    
    form = RegistrationForm()
    if request.method=="POST":
        
        if form.validate_on_submit():
            # if form.password!=form.confirm_password:
            #     flash("Passwords do not match!",'danger')

            # else:
            agent_id = addbookingagent(form)
            flash('WELCOME : Account created for '+form.agent_name.data+'! Your AGENT ID is : '+str(agent_id),'success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect Details','danger')
    return render_template('register.html', title='Register', form=form)

@app.route("/trains",methods=["POST","GET"])
def available_trains():
    
    cursor=connection.cursor()
        
    cursor.execute("select * from availabletrains ")
    data=cursor.fetchall()
    connection.commit()
    cursor.close()
    return render_template('trains.html', title='Trains', data=data)

##done
@app.route("/login",methods=["POST","GET"])
def login():
    form = LoginForm()
    if request.method=='POST':
        if form.validate_on_submit():
        # if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            cursor = connection.cursor()
            cursor.execute("select name,password from bookingagents where id = "+form.agent_id.data)
            records=cursor.fetchall()
            for rec in records:
                if rec[0]==form.agent_name.data and rec[1]==form.password.data:
                    session['username']=form.agent_name
                    session['logged_in']=True
                    flash('You have been logged in!', 'success')
                    return redirect(url_for('booktrains'))
                else:
                    flash('Incorrect login details','danger')
                    return redirect(url_for('login'))

        
                    # return redirect(url_for('home'))
        #else:
        #     flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)



if __name__=='__main__':
    app.run(debug=True)

if(connection):
    
    connection.close()
    print("PostgreSQL connection is closed")
    
    
    #duplicate agent reg
