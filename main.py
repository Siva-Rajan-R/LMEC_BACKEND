from fastapi import FastAPI,Form,Query,BackgroundTasks
from fastapi.responses import FileResponse
from database import db
from backendschema import TakeAttedenceInput,DownloadInput
from typing import Optional,List
from datetime import datetime
import pytz
import pandas as pd
import requests
"""import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')"""
#MACCJXNHWGRWVB9XMPH2RS9Z
app=FastAPI()


def send_message(message,ph_no):
    url = f"https://www.fast2sms.com/dev/bulkV2?authorization=EixFb1Oqnv4kC2JU9g3S0LAyGcMwYeKRThNfodIWZH5ar87tjXwXY5G9yMzNBCAnbjfrp682KhtWg0LS&route=q&message={message}&flash=0&numbers={ph_no}"
    response = requests.get(url)
    print(response.json())

@app.post('/add-student-details')
def add_student_details(dep:str=Form(...),sem:str=Form('SEM-{NUMBER}'),reg_no:int=Form(...),student_name:str=Form(...),student_ph_no:int=Form(...),parent_ph_no:int=Form(...)):
    
    if db.child("latha-mathavan-student-details").child(dep.upper()).get().val()==None:
        db.child("latha-mathavan-student-details").child(dep.upper()).set({sem:{reg_no:{'student_name':student_name,'student_ph_no':student_ph_no,'parent_ph_no':parent_ph_no,'presents':[0]}}})
        #data[dep]={sem:[{'reg_no':reg_no,'student_name':student_name,'student_ph_no':student_ph_no,'parent_ph_no':parent_ph_no,'ispresent':ispresent}]}
    elif db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).child(reg_no).get().val()==None:
        db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).update({reg_no:{'student_name':student_name,'student_ph_no':student_ph_no,'parent_ph_no':parent_ph_no,'presents':[0]}})
        #data[dep].update({sem:[{'reg_no':reg_no,'student_name':student_name,'student_ph_no':student_ph_no,'parent_ph_no':parent_ph_no}]})
    else:
        isexists=False
        if db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).child(reg_no).get().val():
            isexists=True

        if isexists==False:
            db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).set({reg_no:{'student_name':student_name,'student_ph_no':student_ph_no,'parent_ph_no':parent_ph_no,'presents':[0]}})
            #data[dep][sem].append({'reg_no':reg_no,'student_name':student_name,'student_ph_no':student_ph_no,'parent_ph_no':parent_ph_no})
        else:
            return 'Student Already Exists'
    return 'Successfully Added'

@app.put('/update-student-student-details')
def update_student_details(dep:str=Form(...),sem:str=Form('SEM-{NUMBER}'),reg_no:int=Form(...),student_name:str=Form(...),student_ph_no:int=Form(...),parent_ph_no:int=Form(...)):
    if db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).child(reg_no).get().val()!=None:
        db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).child(reg_no).update({'student_name':student_name,'student_ph_no':student_ph_no,'parent_ph_no':parent_ph_no})
        return 'Updated Successfully'
    else:
        return 'No Student Found !'

@app.get('/download-student-details')
def download_student_details(data:DownloadInput):
    print(data.data)
    df = pd.DataFrame(data.data)
    df.to_excel('student.xlsx',index=False)
    return FileResponse('student.xlsx', media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename="student.xlsx")
    
@app.get('/verify-password')
def verify_password(password:str=Form(...)):
    if db.child("latha-mathavan-admin-details").child('password').get().val()!=None:
        if password==db.child("latha-mathavan-admin-details").child('password').get().val():
            return True
        else:
            return 'Incorrecr Password'
    return 'Create A Password by clicking Forgot'

@app.post('/create-password')
def create_password(admin_mail:str=Form(...),new_password:str=Form(...)):
    if db.child("latha-mathavan-admin-details").child('admin').get().val()==None:
        print('hi')
        db.child("latha-mathavan-admin-details").child('admin').set(admin_mail)
        db.child("latha-mathavan-admin-details").child('password').set(new_password)
    else:
        if db.child("latha-mathavan-admin-details").child('admin').get().val()==admin_mail:
            if db.child("latha-mathavan-admin-details").child('password').get().val()!=None:
                db.child("latha-mathavan-admin-details").child('password').set(new_password)
            else:
                db.child("latha-mathavan-admin-details").child('password').update(new_password)
            return True
        return 'Incorrect Email'

    
@app.post('/add-attedence')
def add_attedence(data:TakeAttedenceInput,bgtask:BackgroundTasks):
    today_date=datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
    if db.child("latha-mathavan-student-details").child('attedence-takened').child(data.dep).child(data.sem).get().val()==None or today_date not in db.child("latha-mathavan-student-details").child('attedence-takened').child(data.dep).child(data.sem).get().val():
        for i in list(data.presents.keys()):
            reg_no=int(i)
            if data.presents.get(i)=="True":
                temp=db.child("latha-mathavan-student-details").child(data.dep.upper()).child(data.sem).child(reg_no).child('presents').get().val()
                print(temp)
                if temp and today_date not in temp:
                    print(temp)
                    temp.append(today_date)
                    db.child("latha-mathavan-student-details").child(data.dep.upper()).child(data.sem).child(reg_no).child('presents').set(temp)
            else:
                student_data=db.child("latha-mathavan-student-details").child(data.dep.upper()).child(data.sem).child(reg_no).get().val()
                ph_no=int(student_data.get('parent_ph_no'))
                name=student_data.get('student_name')
                #லதா மாதவன் கல்லூரி:\nஉங்கள் மகன்/மகள் {name}, இன்று கல்லூரிக்கு வரவில்லை ஏதேனும் தகவல் இருக்குமாயின் கல்லூரிக்கு தெரிய படுத்துங்கள் நன்றி
                
                message=f'From Latha Mathavan Group of Insitute,\nYour Son/Daughter {name.title()} Today Was Not Present Please Kindly Inform To Your Department\nThank You !'
                bgtask.add_task(send_message,message,ph_no)

        
        if db.child("latha-mathavan-student-details").child('attedence-takened').child(data.dep).child(data.sem).get().val()!=None:
            t=db.child("latha-mathavan-student-details").child('attedence-takened').child(data.dep).child(data.sem).get().val()
            t.append(today_date)
            db.child("latha-mathavan-student-details").child('attedence-takened').child(data.dep).child(data.sem).set(t)

        elif db.child("latha-mathavan-student-details").child('attedence-takened').child(data.dep).child(data.sem).get().val()==None:
            db.child("latha-mathavan-student-details").child('attedence-takened').child(data.dep).update({data.sem:[today_date]})

        else:
            print('veliya')
            db.child("latha-mathavan-student-details").update({'attedence-takened':{data.dep:{data.sem:[today_date]}}})  
        return f'{today_date} Attedence Taken Successfully'
    else:
        return 'Today Attedence Already Taken'
    
    

@app.put('/edit-attedence')
def edit_attedence(data:TakeAttedenceInput):
    today_date=datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
    if db.child("latha-mathavan-student-details").child('attedence-takened').child(data.dep).child(data.sem).get().val()!=None and today_date in db.child("latha-mathavan-student-details").child('attedence-takened').child(data.dep).child(data.sem).get().val():
        for i in list(data.presents.keys()):
            reg_no=int(i)
            temp=db.child("latha-mathavan-student-details").child(data.dep.upper()).child(data.sem).child(reg_no).child('presents').get().val()
            if data.presents.get(i)=="True":
                if temp and today_date not in temp:
                    temp.append(today_date)
            else:
                if temp and today_date in temp:
                    temp.remove(today_date)
            db.child("latha-mathavan-student-details").child(data.dep.upper()).child(data.sem).child(reg_no).child('presents').set(temp)

        return f'{today_date} Attedence Edited Successfully'
    else:
        return 'Today Attedence was Not Taken'


@app.get('/show-all-student-details')
def show_student_details(dep:str=Query(),sem:str=Query('SEM-{NUMBER}'),isforattedence:bool=Query()):
    temp=True
    today_date=datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
    print(today_date)
    if isforattedence:
        if db.child("latha-mathavan-student-details").child('attedence-takened').child(dep).child(sem).get().val()==None or today_date not in db.child("latha-mathavan-student-details").child('attedence-takened').child(dep).child(sem).get().val():
            temp=True
        else:
            temp=False
    if temp:
        return db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).get().val()
    else:
        return f'{today_date} Attedence Already Taken'

@app.get('/show-particular-date-student-details')
def show_particular_student_detail(dep:str=Query(),sem:str=Query('SEM-{NUMBER}'),date_of_student_details:str=Query(),isforeditattedence:bool=Query()):
    temp={'presents':[],'absents':[]}
    today_date=datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y")
    print(today_date)
    flag=True
    print(isforeditattedence,flag)
    if isforeditattedence:
        if db.child("latha-mathavan-student-details").child('attedence-takened').child(dep.upper()).child(sem).get().val()==None or today_date not in db.child("latha-mathavan-student-details").child('attedence-takened').child(dep.upper()).child(sem).get().val():
            flag=False
    else:
        if db.child("latha-mathavan-student-details").child('attedence-takened').child(dep.upper()).child(sem).get().val()==None or date_of_student_details not in db.child("latha-mathavan-student-details").child('attedence-takened').child(dep.upper()).child(sem).get().val():
            flag=False
    print(flag)
    if flag:
        print('ull')
        if db.child("latha-mathavan-student-details").child(dep.upper()).get().val() and db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).get().val():
            print(db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).get().val())
            for i in db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).get().val():
                data={db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).child(i).get().key():db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).child(i).get().val()}
                if date_of_student_details in db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).child(i).child('presents').get().val():
                    temp['presents'].append(data)
                else:
                    temp['absents'].append(data)
            return temp
        return 'Department Not Found!'
    else:
        return f'{date_of_student_details} Attedence Was Not Taken'


@app.get('/show-old-student-details')
def show_old_student_details(dep:str=Query(),year:str=Query()):
    req=db.child("latha-mathavan-student-details").child("old-student-details").child(dep.upper()).child(year).get().val()
    if req!=None:
        return req
    else:
        return 'No Student Record Fount At this Date'

@app.get('/calculate-student-attedence')
def calculate_student_attedence(nod_student_present:int=Query(),dep:str=Query(),sem:str=Query()):
    if db.child("latha-mathavan-student-details").child('attedence-takened').child(dep.upper()).child(sem).get().val()!=None:
        nod_attedence_taken=len(db.child("latha-mathavan-student-details").child('attedence-takened').child(dep.upper()).child(sem).get().val())
        print(nod_attedence_taken)
        return nod_attedence_taken-nod_student_present

@app.delete('/delete-current-student-details')
def delete_student_details(delete_all:bool=Form(...),dep:str=Form(...),sem:str=Form('SEM-{NUMBER}'),reg_no:Optional[int]=Form(None)):
    if db.child("latha-mathavan-student-details").child(dep.upper()).get().val() and db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).get().val():
        if delete_all:
            db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).remove()
            return 'All Students Deleted Successfully'
        else:
            db.child("latha-mathavan-student-details").child(dep.upper()).child(sem).child(reg_no).remove()
            return 'Student Deleted Successfully'    
    return 'There Is No Department'

@app.delete('/delete-old-student-details')
def delete_student_details(delete_all:bool=Form(...),dep:str=Form(...),year:str=Form(...),reg_no:Optional[int]=Form(None)):
    if db.child("latha-mathavan-student-details").child('old-student-details').child(dep.upper()).get().val() and db.child("latha-mathavan-student-details").child('old-student-details').child(dep.upper()).child(year).get().val():
        if delete_all:
            db.child("latha-mathavan-student-details").child('old-student-details').child(dep.upper()).child(year).remove()
            return 'all students deleted successfully'
        else:
            db.child("latha-mathavan-student-details").child('old-student-details').child(dep.upper()).child(year).child(reg_no).remove()
            return 'Student Deleted Successfully'    
    return 'There Is No Department'

@app.put('/move-to-next-sem')
def move_to_next_sem(dep:str=Form(...)):
    if db.child("latha-mathavan-student-details").child(dep.upper()).get().val():
        length=list(db.child("latha-mathavan-student-details").child(dep.upper()).get().val().keys())
        data=dict(db.child("latha-mathavan-student-details").child(dep.upper()).child(length[-1]).get().val())
        if db.child("latha-mathavan-student-details").child("old-student-details").child(dep.upper()).child(int(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y"))-4).get().val()!=None:
            print('ulla')
            db.child("latha-mathavan-student-details").child("old-student-details").child(dep.upper()).child(int(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y"))-4).update(data)
        else:
            db.child("latha-mathavan-student-details").child("old-student-details").child(dep.upper()).child(int(datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y"))-4).set(data)
        db.child("latha-mathavan-student-details").child(dep.upper()).child(length[-1]).remove()
        for i in range(len(length)-1,-1,-1):
            print(length,i,length[i-1])
            if i!=0:
                temp=db.child("latha-mathavan-student-details").child(dep.upper()).child(length[i-1]).get().val()
                db.child("latha-mathavan-student-details").child(dep.upper()).child(length[i]).set(temp)
                db.child("latha-mathavan-student-details").child(dep.upper()).child(length[i-1]).remove()
            else:
                break
        return 'Successfully Moved'

    return 'There Is No Department'



