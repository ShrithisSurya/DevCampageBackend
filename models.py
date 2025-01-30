from mongoengine import *
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import request


class Subscription_Plan(Document):
    meta={'collection':'subscription_plan'}


    id=StringField(primary_key=True,default=lambda:str(uuid4()))
    name = StringField(required=True,unique=True)
    price = StringField(required=True)
    email_quota = IntField()
    api_quota = IntField()
    added_time=DateTimeField(default=datetime.now())
    updated_time = DateTimeField()
    description=StringField(required=True)
       

class User(Document):
    meta = {'collection':'users'}
    
    id = StringField(primary_key=True, default=lambda: str(uuid4()))
    username = StringField(required=True, max_length=150)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    def set_hashed_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password,password)
    phone=IntField(required=True,unique=True)
    status = BooleanField(default=True) 
    added_time=DateTimeField(default=datetime.now())
    updated_time = DateTimeField(default=datetime.now())
    is_active = BooleanField(default=True) 
    subscription_plan = ReferenceField(Subscription_Plan, reverse_delete_rule=CASCADE, null=True)
    
class Billing_Address(Document):
    meta={'collection':'billing_address'}
    
    id = StringField(primary_key=True, default=lambda: str(uuid4()))
    user=ReferenceField(User,reverse_delete_rule=CASCADE,null=True)
    address_one=StringField(required=True)
    address_two=StringField(required=True)
    city=StringField(required=True)
    state=StringField(required=True)
    country=StringField(required=True)
    pin_code=IntField(required=True)
    added_time=DateTimeField(default=datetime.now())
    updated_time=DateTimeField()
    
class Tag(Document):
    meta={'collection':"tags"}

    user = ReferenceField(User, reverse_delete_rule=CASCADE, null=True)
    id=StringField(primary_key=True,default=lambda:str(uuid4()))
    tag_name=StringField(required=True,unique_with="user")
    added_time=DateTimeField(default=datetime.now())
    updated_time=DateTimeField()  
    
class Subscriber(Document):
    meta ={'collection':'subscribers'}
     
    id=StringField(primary_key=True,default=lambda:str(uuid4()))
    email=EmailField(required=True,unique=True)
    tags=ListField(ReferenceField(Tag,required=True))
    added_time=DateTimeField(default=datetime.now())
    updated_time=DateTimeField()
    custom_field=ListField(DictField())
    status=StringField(default="active",choices=("active","bounced", "unsubscribed"))
    user = ReferenceField(User, reverse_delete_rule=CASCADE, null=True)


class Email_Campaign(Document):
    meta={'collection':'email_campaign'}

    id=StringField(primary_key=True,default=lambda:str(uuid4()))
    user=ReferenceField(User,reverse_delete_rule=CASCADE,null=True)
    campaign_name=StringField(required=True,unique=True)
    audience_tag=ListField(ReferenceField(Tag,required=True))
    subject=StringField(required=True)
    content=StringField(required=True)
    status=StringField(default="draft", choices=("draft","scheduled","sent","failed", "in_progress"))
    scheduled_at=DateTimeField(null=True)
    added_time=DateTimeField(default=datetime.now())
    updated_time=DateTimeField()

class Campaign_Analytics(Document):
    meta ={'collection':'campaign_analytics'}

    id=StringField(primary_key=True,default=lambda:str(uuid4()))
    sent_count=IntField(default=0)
    opened_count=IntField(default=0)
    clicked_count=IntField(default=0)
    bounced_count=IntField(default=0)
    unsubscribed_count=IntField(default=0)
    updated_time=DateTimeField(default=datetime.now())
    campaign=ReferenceField(Email_Campaign,required=True,reverse_delete_rule=CASCADE,null=True)
    user=ReferenceField(User,reverse_delete_rule=CASCADE,null=True)



class Tickets(Document):
    meta = {'collection': 'tickets'}
    
    id = StringField(primary_key=True, default=lambda: str(uuid4()))
    user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    title = StringField(required=True)
    description = StringField(required=True)
    status = StringField(default="open", choices=("open", "in_progress", "sent", "resolved"))
    date_of_resolved=DateTimeField()
    added_time = DateTimeField(default=datetime.now())
    updated_time = DateTimeField()
    

class Api_Log(Document):
    meta={'collection':'api_log'}
    
    id = StringField(primary_key=True, default=lambda: str(uuid4()))
    user = ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    log_time=DateTimeField(default=datetime.now)
    endpoint=StringField(max_length=120)
    domain=StringField(max_length=120)
    platform=StringField(max_length=50)
    response=StringField()
    status=StringField()
    method=StringField()

class Templates(Document):
    meta={'collection':'template'}

    id = StringField(primary_key=True, default=lambda: str(uuid4()))
    template_name=StringField(required=True)
    description=StringField(required=True)
    image=FileField()
    content=StringField()
    added_time = DateTimeField(default=datetime.now())
    updated_time=DateField()
    user=ReferenceField(User,reverse_delete_rule=CASCADE,null=True)

    

class Billing_Address(Document):
    meta={'collection':'billing_address'}
    
    id = StringField(primary_key=True, default=lambda: str(uuid4()))
    address_one=StringField(required=True)
    address_two=StringField(required=True)
    city=StringField(required=True)
    state=StringField(required=True)
    country=StringField(required=True)
    pin_code=IntField(required=True)
    user=ReferenceField(User,reverse_delete_rule=CASCADE,null=True)
    added_time=DateTimeField(default=datetime.now())
    updated_time=DateTimeField()
    
    

class Codeless_Subscriber(Document):
    meta={'collection':'codeless_subscriber'}
    
    id=StringField(primary_key=True,default=lambda:str(uuid4()))
    user=ReferenceField(User,reverse_delete_rule=CASCADE,null=True)
    email=EmailField(required=True,unique=True)
    stream=StringField(default="Codeless Mail")
    added_time=DateTimeField(default=datetime.now())
    updated_time=DateTimeField()
   
    
    
class Contact_us(Document):
    meta={'collection':'contact_us'}
    
    id=StringField(primary_key=True,default=lambda:str(uuid4()))
    user=ReferenceField(User,reverse_delete_rule=CASCADE,null=True)
    full_name=StringField(required=True)
    email=EmailField(required=True,unique=True)
    subject=StringField(reuqired=True)
    message=StringField(required=True)
    added_time=DateTimeField(default=datetime.now())
    updated_time=DateTimeField()
    