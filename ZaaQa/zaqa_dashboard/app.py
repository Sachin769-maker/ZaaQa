from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
import re, csv, os, smtplib, time, threading, random
import requests as req_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'zaqa_secret_2025'

# ═══════════════════════════════════════════════════════════════════════════════
#  MONGODB
# ═══════════════════════════════════════════════════════════════════════════════
MONGO_URI       = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
client          = MongoClient(MONGO_URI)
db              = client['zaaq_food']
users_col       = db['users']
admins_col      = db['admins']
restaurants_col = db['restaurants']
menu_items_col  = db['menu_items']
orders_col      = db['orders']
notifications_col = db['notifications']
reviews_col     = db['reviews']
coupons_col     = db['coupons']

# ═══════════════════════════════════════════════════════════════════════════════
#  EMAIL CONFIG  ← Enter your email
# ═══════════════════════════════════════════════════════════════════════════════
EMAIL_USER     = 'Youremail@gmail.com'       
EMAIL_PASSWORD = 'xxxx xxxx xxxx xxxx'     # Gmail App Password

# ═══════════════════════════════════════════════════════════════════════════════
#  TRANSLATIONS
# ═══════════════════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    'en': {'name':'English','flag':'🇬🇧','welcome_back':'Welcome back 👋','login_sub':'Login and place your order','email':'Email Address','password':'Password','login_btn':'Login','no_account':"Don't have an account?",'register_link':'Register','create_account':'Create Account 🎉','reg_sub':'Register for free','full_name':'Full Name','phone':'Phone','address':'Delivery Address','already_account':'Already have an account?','login_link':'Login','hungry':"Hungry? Let's ZaaQa! 🤤",'restaurants_available':'restaurants available','search_placeholder':'Search restaurant or cuisine...','all_amritsar':'📍 All Amritsar','search_btn':'Search','all_restaurants':'All Restaurants 🏪','top_rated':'Top Rated','fast_delivery':'Fast Delivery','safe_payment':'Safe Payment','add_to_cart':'Add','cart_title':'Your Cart 🛒','clear_cart':'Clear cart','checkout_btn':'Checkout','add_more':'Add more items','order_summary':'Order Summary','subtotal':'Subtotal','delivery':'Delivery','free':'FREE 🎉','total':'Total','cart_empty':'Cart is empty!','browse_restaurants':'Browse Restaurants','delivery_address':'Delivery Address','payment_method':'Payment Method','online_payment':'Online Payment','online_sub':'UPI, Card, Net Banking','cod':'Cash on Delivery','cod_sub':'Pay when delivered','place_order':'Place Order','my_orders':'My Orders 📋','no_orders':'No orders yet','order_now':'Order Now','track':'Track','restaurant':'Restaurant','date':'Date','health_title':'🥗 Health-Based Food Guide','health_sub':'Find the best food for your health','blood_pressure':'Blood Pressure','blood_sugar':'Blood Sugar','get_recs':'Get Recommendations 🌿','min_order':'Min Order','no_min':'No minimum','or_text':'or','amritsar_tagline':"Amritsar's own food delivery platform",'hero_tagline':'25+ restaurants, 125+ dishes — all in one place'},
    'hi': {'name':'हिंदी','flag':'🇮🇳','welcome_back':'वापस स्वागत है 👋','login_sub':'लॉगिन करें और ऑर्डर करें','email':'ईमेल पता','password':'पासवर्ड','login_btn':'लॉगिन','no_account':'नया अकाउंट?','register_link':'रजिस्टर करें','create_account':'अकाउंट बनाएं 🎉','reg_sub':'फ्री में रजिस्टर करें','full_name':'पूरा नाम','phone':'फोन','address':'डिलीवरी पता','already_account':'पहले से अकाउंट है?','login_link':'लॉगिन करें','hungry':'भूख लगी? ZaaQa करो! 🤤','restaurants_available':'रेस्टोरेंट उपलब्ध','search_placeholder':'रेस्टोरेंट या खाना खोजें...','all_amritsar':'📍 पूरा अमृतसर','search_btn':'खोजें','all_restaurants':'सभी रेस्टोरेंट 🏪','top_rated':'टॉप रेटेड','fast_delivery':'तेज़ डिलीवरी','safe_payment':'सुरक्षित भुगतान','add_to_cart':'जोड़ें','cart_title':'आपकी कार्ट 🛒','clear_cart':'कार्ट साफ करें','checkout_btn':'चेकआउट','add_more':'और आइटम जोड़ें','order_summary':'ऑर्डर सारांश','subtotal':'उपकुल','delivery':'डिलीवरी','free':'मुफ्त 🎉','total':'कुल','cart_empty':'कार्ट खाली है!','browse_restaurants':'रेस्टोरेंट देखें','delivery_address':'डिलीवरी पता','payment_method':'भुगतान विधि','online_payment':'ऑनलाइन भुगतान','online_sub':'UPI, कार्ड, नेट बैंकिंग','cod':'कैश ऑन डिलीवरी','cod_sub':'डिलीवरी पर भुगतान करें','place_order':'ऑर्डर दें','my_orders':'मेरे ऑर्डर 📋','no_orders':'अभी तक कोई ऑर्डर नहीं','order_now':'ऑर्डर करें','track':'ट्रैक करें','restaurant':'रेस्टोरेंट','date':'तारीख','health_title':'🥗 स्वास्थ्य आधारित खाद्य मार्गदर्शिका','health_sub':'अपने स्वास्थ्य के अनुसार सबसे अच्छा खाना खोजें','blood_pressure':'रक्तचाप','blood_sugar':'रक्त शर्करा','get_recs':'सुझाव पाएं 🌿','min_order':'न्यूनतम ऑर्डर','no_min':'कोई न्यूनतम नहीं','or_text':'या','amritsar_tagline':'अमृतसर का अपना फूड डिलीवरी प्लेटफॉर्म','hero_tagline':'25+ रेस्टोरेंट, 125+ व्यंजन — सब एक जगह'},
    'pa': {'name':'ਪੰਜਾਬੀ','flag':'🌾','welcome_back':'ਵਾਪਸ ਆਉਣ ਤੇ ਸੁਆਗਤ 👋','login_sub':'ਲੌਗਿਨ ਕਰੋ ਅਤੇ ਆਰਡਰ ਕਰੋ','email':'ਈਮੇਲ ਪਤਾ','password':'ਪਾਸਵਰਡ','login_btn':'ਲੌਗਿਨ','no_account':'ਨਵਾਂ ਖਾਤਾ?','register_link':'ਰਜਿਸਟਰ ਕਰੋ','create_account':'ਖਾਤਾ ਬਣਾਓ 🎉','reg_sub':'ਮੁਫ਼ਤ ਵਿੱਚ ਰਜਿਸਟਰ ਕਰੋ','full_name':'ਪੂਰਾ ਨਾਮ','phone':'ਫ਼ੋਨ','address':'ਡਿਲੀਵਰੀ ਪਤਾ','already_account':'ਪਹਿਲਾਂ ਤੋਂ ਖਾਤਾ ਹੈ?','login_link':'ਲੌਗਿਨ ਕਰੋ','hungry':'ਭੁੱਖ ਲੱਗੀ? ZaaQa ਕਰੋ! 🤤','restaurants_available':'ਰੈਸਟੋਰੈਂਟ ਉਪਲਬਧ','search_placeholder':'ਰੈਸਟੋਰੈਂਟ ਜਾਂ ਖਾਣਾ ਲੱਭੋ...','all_amritsar':'📍 ਪੂਰਾ ਅੰਮ੍ਰਿਤਸਰ','search_btn':'ਖੋਜੋ','all_restaurants':'ਸਾਰੇ ਰੈਸਟੋਰੈਂਟ 🏪','top_rated':'ਟਾਪ ਰੇਟਡ','fast_delivery':'ਤੇਜ਼ ਡਿਲੀਵਰੀ','safe_payment':'ਸੁਰੱਖਿਅਤ ਭੁਗਤਾਨ','add_to_cart':'ਜੋੜੋ','cart_title':'ਤੁਹਾਡੀ ਕਾਰਟ 🛒','clear_cart':'ਕਾਰਟ ਸਾਫ਼ ਕਰੋ','checkout_btn':'ਚੈੱਕਆਊਟ','add_more':'ਹੋਰ ਆਈਟਮ ਜੋੜੋ','order_summary':'ਆਰਡਰ ਸਾਰਾਂਸ਼','subtotal':'ਉਪ-ਕੁੱਲ','delivery':'ਡਿਲੀਵਰੀ','free':'ਮੁਫ਼ਤ 🎉','total':'ਕੁੱਲ','cart_empty':'ਕਾਰਟ ਖਾਲੀ ਹੈ!','browse_restaurants':'ਰੈਸਟੋਰੈਂਟ ਦੇਖੋ','delivery_address':'ਡਿਲੀਵਰੀ ਪਤਾ','payment_method':'ਭੁਗਤਾਨ ਵਿਧੀ','online_payment':'ਔਨਲਾਈਨ ਭੁਗਤਾਨ','online_sub':'UPI, ਕਾਰਡ, ਨੈੱਟ ਬੈਂਕਿੰਗ','cod':'ਕੈਸ਼ ਆਨ ਡਿਲੀਵਰੀ','cod_sub':'ਡਿਲੀਵਰੀ ਤੇ ਭੁਗਤਾਨ ਕਰੋ','place_order':'ਆਰਡਰ ਦਿਓ','my_orders':'ਮੇਰੇ ਆਰਡਰ 📋','no_orders':'ਅਜੇ ਕੋਈ ਆਰਡਰ ਨਹੀਂ','order_now':'ਆਰਡਰ ਕਰੋ','track':'ਟਰੈਕ ਕਰੋ','restaurant':'ਰੈਸਟੋਰੈਂਟ','date':'ਤਾਰੀਖ਼','health_title':'🥗 ਸਿਹਤ ਆਧਾਰਿਤ ਖੁਰਾਕ ਗਾਈਡ','health_sub':'ਆਪਣੀ ਸਿਹਤ ਅਨੁਸਾਰ ਸਭ ਤੋਂ ਵਧੀਆ ਖਾਣਾ ਲੱਭੋ','blood_pressure':'ਬਲੱਡ ਪ੍ਰੈਸ਼ਰ','blood_sugar':'ਬਲੱਡ ਸ਼ੂਗਰ','get_recs':'ਸੁਝਾਅ ਲਓ 🌿','min_order':'ਘੱਟੋ-ਘੱਟ ਆਰਡਰ','no_min':'ਕੋਈ ਘੱਟੋ-ਘੱਟ ਨਹੀਂ','or_text':'ਜਾਂ','amritsar_tagline':'ਅੰਮ੍ਰਿਤਸਰ ਦਾ ਆਪਣਾ ਫੂਡ ਡਿਲੀਵਰੀ ਪਲੇਟਫਾਰਮ','hero_tagline':'25+ ਰੈਸਟੋਰੈਂਟ, 125+ ਪਕਵਾਨ — ਸਭ ਇੱਕ ਥਾਂ'},
    'ur': {'name':'اردو','flag':'🌙','welcome_back':'خوش آمدید 👋','login_sub':'لاگ ان کریں اور آرڈر کریں','email':'ای میل','password':'پاس ورڈ','login_btn':'لاگ ان','no_account':'نیا اکاؤنٹ؟','register_link':'رجسٹر کریں','create_account':'اکاؤنٹ بنائیں 🎉','reg_sub':'مفت میں رجسٹر کریں','full_name':'پورا نام','phone':'فون','address':'ڈیلیوری پتہ','already_account':'پہلے سے اکاؤنٹ ہے؟','login_link':'لاگ ان کریں','hungry':'بھوک لگی؟ ZaaQa کریں! 🤤','restaurants_available':'ریستوران دستیاب','search_placeholder':'ریستوران یا کھانا تلاش کریں...','all_amritsar':'📍 پورا امرتسر','search_btn':'تلاش','all_restaurants':'تمام ریستوران 🏪','top_rated':'ٹاپ ریٹڈ','fast_delivery':'تیز ڈیلیوری','safe_payment':'محفوظ ادائیگی','add_to_cart':'شامل کریں','cart_title':'آپ کی کارٹ 🛒','clear_cart':'کارٹ صاف کریں','checkout_btn':'چیک آؤٹ','add_more':'مزید آئٹم شامل کریں','order_summary':'آرڈر خلاصہ','subtotal':'ذیلی کل','delivery':'ڈیلیوری','free':'مفت 🎉','total':'کل','cart_empty':'کارٹ خالی ہے!','browse_restaurants':'ریستوران دیکھیں','delivery_address':'ڈیلیوری پتہ','payment_method':'ادائیگی کا طریقہ','online_payment':'آن لائن ادائیگی','online_sub':'UPI، کارڈ، نیٹ بینکنگ','cod':'کیش آن ڈیلیوری','cod_sub':'ڈیلیوری پر ادائیگی کریں','place_order':'آرڈر دیں','my_orders':'میرے آرڈر 📋','no_orders':'ابھی تک کوئی آرڈر نہیں','order_now':'آرڈر کریں','track':'ٹریک کریں','restaurant':'ریستوران','date':'تاریخ','health_title':'🥗 صحت پر مبنی خوراک گائیڈ','health_sub':'اپنی صحت کے مطابق بہترین کھانا تلاش کریں','blood_pressure':'بلڈ پریشر','blood_sugar':'بلڈ شوگر','get_recs':'تجاویز حاصل کریں 🌿','min_order':'کم از کم آرڈر','no_min':'کوئی کم از کم نہیں','or_text':'یا','amritsar_tagline':'امرتسر کا اپنا فوڈ ڈیلیوری پلیٹ فارم','hero_tagline':'25+ ریستوران، 125+ پکوان — سب ایک جگہ'},
}
SUPPORTED_LANGS = list(TRANSLATIONS.keys())
def get_lang(): return session.get('lang','en')
def t(key):
    lang = get_lang()
    return TRANSLATIONS.get(lang,TRANSLATIONS['en']).get(key,TRANSLATIONS['en'].get(key,key))
@app.context_processor
def inject_globals():
    lang = get_lang()
    return {'t':t,'current_lang':lang,'lang_info':TRANSLATIONS.get(lang,TRANSLATIONS['en']),
            'all_langs':{k:{'name':v['name'],'flag':v['flag']} for k,v in TRANSLATIONS.items()}}

# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def fix_id(doc):
    if doc and '_id' in doc: doc['id'] = str(doc['_id'])
    return doc
def fix_ids(docs): return [fix_id(d) for d in docs]
def to_oid(s):
    try: return ObjectId(s)
    except: return None

# ═══════════════════════════════════════════════════════════════════════════════
#  EMAIL FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
def send_email(to_email, subject, body_html):
    try:
        msg            = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From']    = f'ZaaQa Food Delivery <{EMAIL_USER}>'
        msg['To']      = to_email
        msg.attach(MIMEText(body_html, 'html'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(EMAIL_USER, EMAIL_PASSWORD)
            s.sendmail(EMAIL_USER, to_email, msg.as_string())
        print(f"✅ Email sent → {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def send_order_email(user, restaurant_name, order_id, amount, payment, status='placed'):
    templates = {
        'placed':           {'subject':'🎉 Order Placed — ZaaQa',       'color':'#FF5200','icon':'🎉','heading':'Order Placed Successfully!',   'msg':f'Your order from <b>{restaurant_name}</b> has been placed. We will notify you once it is confirmed!'},
        'Confirmed':        {'subject':'✅ Order Confirmed — ZaaQa',     'color':'#16A34A','icon':'✅','heading':'Order Confirmed!',             'msg':f'<b>{restaurant_name}</b> has confirmed your order and will start preparing soon!'},
        'Preparing':        {'subject':'👨‍🍳 Being Prepared — ZaaQa',   'color':'#D97706','icon':'👨‍🍳','heading':'Your Food is Being Prepared!','msg':f'The chefs at <b>{restaurant_name}</b> are cooking your food right now!'},
        'Out for Delivery': {'subject':'🛵 On the Way! — ZaaQa',        'color':'#2563EB','icon':'🛵','heading':'Order Out for Delivery!',       'msg':'Your delivery partner is on the way. Please be available at your address!'},
        'Delivered':        {'subject':'🏠 Delivered! — ZaaQa',         'color':'#16A34A','icon':'🏠','heading':'Order Delivered!',             'msg':f'Your order from <b>{restaurant_name}</b> has been delivered. Enjoy your meal! 😋'},
        'Cancelled':        {'subject':'❌ Order Cancelled — ZaaQa',    'color':'#DC2626','icon':'❌','heading':'Order Cancelled',               'msg':'Your order has been cancelled. Please contact support if needed.'},
    }
    t = templates.get(status, templates['placed'])
    html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#F7F7F7;font-family:Arial,sans-serif">
<div style="max-width:520px;margin:30px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.08)">
  <div style="background:{t['color']};padding:32px;text-align:center">
    <div style="font-size:40px;margin-bottom:10px">{t['icon']}</div>
    <h1 style="color:#fff;margin:0;font-size:22px">{t['heading']}</h1>
  </div>
  <div style="padding:28px">
    <p style="color:#374151;font-size:15px;margin-bottom:16px">Hello <b>{user.get('name','')}</b>,</p>
    <p style="color:#374151;font-size:15px;line-height:1.6">{t['msg']}</p>
    <table style="width:100%;border-collapse:collapse;margin:20px 0;border-radius:10px;overflow:hidden">
      <tr style="background:#F9FAFB"><td style="padding:12px 16px;color:#6B7280;font-size:13px;border-bottom:1px solid #F3F4F6">Order ID</td><td style="padding:12px 16px;font-weight:700;font-size:13px;border-bottom:1px solid #F3F4F6">#{str(order_id)[:8].upper()}</td></tr>
      <tr><td style="padding:12px 16px;color:#6B7280;font-size:13px;border-bottom:1px solid #F3F4F6">Restaurant</td><td style="padding:12px 16px;font-weight:600;font-size:13px;border-bottom:1px solid #F3F4F6">{restaurant_name}</td></tr>
      <tr style="background:#F9FAFB"><td style="padding:12px 16px;color:#6B7280;font-size:13px;border-bottom:1px solid #F3F4F6">Amount</td><td style="padding:12px 16px;font-weight:700;color:{t['color']};font-size:13px;border-bottom:1px solid #F3F4F6">₹{amount:.0f}</td></tr>
      <tr><td style="padding:12px 16px;color:#6B7280;font-size:13px">Payment</td><td style="padding:12px 16px;font-size:13px">{payment}</td></tr>
    </table>
    <div style="text-align:center;margin:20px 0">
      <span style="background:{t['color']}20;color:{t['color']};padding:8px 24px;border-radius:40px;font-weight:700;font-size:14px">Status: {status.replace('placed','Pending')}</span>
    </div>
  </div>
  <div style="background:#F9FAFB;padding:20px;text-align:center;border-top:1px solid #F3F4F6">
    <p style="margin:0;color:#9CA3AF;font-size:12px">ZaaQa — Amritsar Food Delivery 🍽️</p>
    <p style="margin:6px 0 0;color:#9CA3AF;font-size:11px">Amritsar, Punjab, India</p>
  </div>
</div></body></html>"""
    return send_email(user['email'], t['subject'], html)

# ═══════════════════════════════════════════════════════════════════════════════
#  NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════
def create_notification(user_id, title, message, notif_type='info', order_id=None):
    notifications_col.insert_one({'user_id':user_id,'title':title,'message':message,'type':notif_type,'order_id':order_id,'read':False,'created_at':datetime.now()})

def notify_user(user_id, title, message, notif_type='info', order_id=None,
                restaurant_name='', amount=0, payment='', status='placed'):
    create_notification(user_id, title, message, notif_type, order_id)
    user = users_col.find_one({'_id': to_oid(user_id)})
    if user and user.get('email') and EMAIL_USER != 'tumhara@gmail.com':
        send_order_email(user, restaurant_name, order_id or '', amount, payment, status)

# ═══════════════════════════════════════════════════════════════════════════════
#  SEED DATA
# ═══════════════════════════════════════════════════════════════════════════════
def init_db():
    users_col.create_index('email', unique=True)
    admins_col.create_index('username', unique=True)
    if admins_col.count_documents({}) == 0:
        admins_col.insert_one({'username':'admin','password':generate_password_hash('admin123'),'created_at':datetime.now()})
    if restaurants_col.count_documents({}) == 0:
        rdata = [
            ('Kesar Da Dhaba','Chowk Passian','Chowk Passian, Near Golden Temple, Amritsar','North Indian',4.7,'25-35 min',150,'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&q=80'),
            ('Brothers Dhaba','Lawrence Road','Lawrence Road, Amritsar','North Indian, Punjabi',4.5,'30-40 min',100,'https://images.unsplash.com/photo-1552566626-52f8b828329b?w=600&q=80'),
            ('Surjit Food Plaza','Nehru Shopping','Nehru Shopping Complex, Amritsar','Mughlai, Chicken',4.6,'20-30 min',200,'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=80'),
            ('Bharawan Da Dhaba','Town Hall','Near Town Hall, Amritsar','Punjabi, Kulcha',4.8,'15-25 min',100,'https://images.unsplash.com/photo-1537047902294-62a40c20a6ae?w=600&q=80'),
            ('Beera Chicken Corner','Majitha Road','Majitha Road, Amritsar','Chicken, Tandoori',4.4,'30-45 min',150,'https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=600&q=80'),
            ('Crystal Restaurant','Queens Road','Queens Road, Amritsar','Multi-cuisine',4.3,'35-45 min',250,'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80'),
            ('Amritsari Kulcha Wala','Hall Bazaar','Hall Bazaar, Amritsar','Kulcha, Chole',4.6,'15-20 min',80,'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=600&q=80'),
            ('Gurdas Ram Jalebi','Katra Jaimal Singh','Katra Jaimal Singh, Amritsar','Sweets, Jalebi',4.9,'10-15 min',50,'https://images.unsplash.com/photo-1571167530149-c1105da4c2a8?w=600&q=80'),
            ('Pind Balluchi','Ranjit Avenue','Ranjit Avenue, Amritsar','Punjabi, Tandoori',4.2,'40-50 min',300,'https://images.unsplash.com/photo-1424847651672-bf20a4b0982b?w=600&q=80'),
            ('Ahuja Milk Bhandar','Lawrence Road','Lawrence Road, Amritsar','Dairy, Lassi',4.7,'10-20 min',50,'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&q=80'),
            ('Bade Bhaiye Da Dhaba','GT Road','GT Road, Amritsar','North Indian',4.1,'35-45 min',120,'https://images.unsplash.com/photo-1466978913421-dad2ebd01d17?w=600&q=80'),
            ('Moti Mahal','Mall Road','Mall Road, Amritsar','Mughlai, Butter Chicken',4.5,'30-40 min',200,'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=600&q=80'),
            ('Pizza Hub Amritsar','Ranjit Avenue','Ranjit Avenue, Amritsar','Pizza, Fast Food',4.0,'25-35 min',199,'https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=600&q=80'),
            ('Burger King','Alpha One Mall','Alpha One Mall, Amritsar','Burgers, Fast Food',4.1,'20-30 min',150,'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=80'),
            ('Dominos Pizza','Lawrence Road','Lawrence Road, Amritsar','Pizza',4.2,'30-40 min',199,'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=600&q=80'),
            ('KFC Amritsar','GT Road','GT Road, Near Bus Stand, Amritsar','Fried Chicken',4.0,'25-35 min',199,'https://images.unsplash.com/photo-1562967916-eb82221dfb92?w=600&q=80'),
            ('Cafe Coffee Day','Mall Road','Mall Road, Amritsar','Cafe, Beverages',3.9,'15-25 min',100,'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600&q=80'),
            ('Subway Amritsar','Ranjit Avenue','Ranjit Avenue, Amritsar','Sandwiches, Wraps',4.1,'20-30 min',150,'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=600&q=80'),
            ('Punjabi Rasoi','Green Avenue','Green Avenue, Amritsar','Punjabi Home Food',4.4,'30-45 min',120,'https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=600&q=80'),
            ('Gopal Sweets','Lawrence Road','Lawrence Road, Amritsar','Sweets, Mithai',4.6,'15-25 min',80,'https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=600&q=80'),
            ('Sindhi Sweets','Majitha Road','Majitha Road, Amritsar','Sweets, Chaat',4.5,'20-30 min',60,'https://images.unsplash.com/photo-1560717845-968823efbee1?w=600&q=80'),
            ('Bikanervala','Mall Road','Mall Road, Amritsar','Sweets, Snacks',4.3,'20-30 min',100,'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&q=80'),
            ('Amritsar Haveli','GT Road','GT Road, Amritsar','Punjabi, Tandoori',4.4,'35-50 min',250,'https://images.unsplash.com/photo-1590846406792-0adc7f938f1d?w=600&q=80'),
            ('Chhota Mota Dhaba','Sultanwind Road','Sultanwind Road, Amritsar','North Indian',4.0,'30-40 min',100,'https://images.unsplash.com/photo-1567521464027-f127ff144326?w=600&q=80'),
            ('Lal Sweets','Katra Ahluwalia','Katra Ahluwalia, Amritsar','Sweets, Pinni',4.7,'10-20 min',50,'https://images.unsplash.com/photo-1571167530149-c1105da4c2a8?w=600&q=80'),
            ('Fame 5 Food Court','Airport Road Amritsar Colony','Airport Road Amritsar Colony, Amritsar','Non Veg, Multi-cuisine',4.7,'30-40 min',150,'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=80'),
            ('Avtar Non Veg Dhaba','Albert Road Rani Ka Bagh','Albert Road Rani Ka Bagh, Amritsar','Non Veg, Chicken',3.6,'25-35 min',100,'https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=600&q=80'),
            ('Prince Chicken Bar','Fatehgarh Churian Road','Fatehgarh Churian Road, Amritsar','Chicken, Non Veg',4.7,'20-30 min',120,'https://images.unsplash.com/photo-1562967916-eb82221dfb92?w=600&q=80'),
            ('Dawat Non Veg Point','Mahindra Colony','Mahindra Colony, Amritsar','Non Veg, Mutton',4.2,'30-40 min',100,'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=600&q=80'),
            ('Kitchen 1574','Summer Palace Road Anand Avenue','Summer Palace Road Anand Avenue, Amritsar','Non Veg, Multi-cuisine',4.0,'35-45 min',200,'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80'),
            ('The Chicken Wala','Main Road Hakima Gate','Main Road Hakima Gate, Amritsar','Chicken, Non Veg',5.0,'20-30 min',100,'https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=600&q=80'),
            ('Time Tandoori','Bhagat Kabir Marg Ekta Nagar','Bhagat Kabir Marg Ekta Nagar, Amritsar','Tandoori, Non Veg',3.9,'25-35 min',120,'https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=600&q=80'),
            ('Jiggle Belly','Ranjit Avenue','Ranjit Avenue, Amritsar','Non Veg, Fast Food',4.0,'20-30 min',120,'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&q=80'),
            ('Rai Chicken','Fateh Garh Churian Road','Fateh Garh Churian Road, Amritsar','Chicken, Non Veg',4.2,'25-35 min',100,'https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=600&q=80'),
            ('Aviruchis Flour Fairy','Circular Road Sehaj Avenue','Circular Road Sehaj Avenue, Amritsar','Non Veg, Bakes',4.7,'30-40 min',150,'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=80'),
            ('Wholemeal','Ranjeet Avenue Block D','Ranjeet Avenue Block D, Amritsar','Non Veg, Continental',4.1,'35-45 min',200,'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&q=80'),
            ('Finch Brew Cafe','27 Feet Road','27 Feet Road, Amritsar','Non Veg, Cafe',4.1,'25-35 min',150,'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600&q=80'),
            ('Barbeque Nation','Mall Road White Avenue','Mall Road White Avenue, Amritsar','Non Veg, BBQ',4.4,'40-50 min',800,'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&q=80'),
            ('The Yellow Chilli','GRD Towers Ranjeet Avenue Block B','GRD Towers Ranjeet Avenue, Amritsar','Non Veg, North Indian',3.9,'35-45 min',700,'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=600&q=80'),
        ]
        menus = {
            'Kesar Da Dhaba':[('Dal Makhani','Slow cooked black lentils in cream',139,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Paneer Butter Masala','Cottage cheese in rich tomato gravy',169,'Main Course','https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400&q=80'),('Amritsari Lassi','Thick creamy sweet lassi',59,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Tandoori Roti','Fresh tandoor baked bread',20,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Saag Paneer','Mustard greens with cottage cheese',159,'Main Course','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80')],
            'Brothers Dhaba':[('Butter Chicken','Creamy tomato chicken curry',199,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Chicken Tikka','Grilled spicy chicken pieces',229,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Naan','Soft leavened bread',30,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Raita','Yoghurt with cucumber',49,'Sides','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Mutton Curry','Slow cooked mutton',279,'Main Course','https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80')],
            'Surjit Food Plaza':[('Amritsari Chicken','Famous Amritsari style chicken',249,'Main Course','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Fish Tikka','Grilled spiced fish',219,'Starters','https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&q=80'),('Seekh Kebab','Minced meat on skewers',199,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Rumali Roti','Thin handkerchief bread',25,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Lassi','Sweet chilled lassi',49,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Bharawan Da Dhaba':[('Amritsari Kulcha','Stuffed bread baked in tandoor',60,'Main Course','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Chole','Spiced chickpea curry',49,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Paneer Kulcha','Paneer stuffed kulcha',80,'Main Course','https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400&q=80'),('Lassi','Sweet thick lassi',49,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Aloo Kulcha','Potato stuffed kulcha',60,'Main Course','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80')],
            'Beera Chicken Corner':[('Half Chicken Fry','Crispy fried half chicken',299,'Main Course','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Full Chicken Fry','Full crispy fried chicken',549,'Main Course','https://images.unsplash.com/photo-1562967916-eb82221dfb92?w=400&q=80'),('Chicken Wings','Spicy fried wings',199,'Starters','https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=400&q=80'),('Rumali Roti','Thin soft bread',25,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Cold Drink','Chilled soft drink',40,'Beverages','https://images.unsplash.com/photo-1527960471264-932f39eb5846?w=400&q=80')],
            'Crystal Restaurant':[('Veg Thali','Complete vegetarian meal',249,'Thali','https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&q=80'),('Non Veg Thali','Complete non-veg meal',349,'Thali','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Paneer Tikka','Grilled cottage cheese',199,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Gulab Jamun','Soft milk dumplings',79,'Desserts','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Mango Lassi','Chilled mango lassi',79,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Amritsari Kulcha Wala':[('Aloo Kulcha','Potato stuffed kulcha',50,'Main Course','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Paneer Kulcha','Paneer stuffed kulcha',70,'Main Course','https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400&q=80'),('Mix Kulcha','Mix stuffed kulcha',80,'Main Course','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Lassi','Sweet lassi',40,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Chole','Extra chole',30,'Sides','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80')],
            'Gurdas Ram Jalebi':[('Jalebi','Crispy sweet jalebi',80,'Sweets','https://images.unsplash.com/photo-1571167530149-c1105da4c2a8?w=400&q=80'),('Rabri Jalebi','Jalebi with rabri',120,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Imarti','Flower shaped sweet',90,'Sweets','https://images.unsplash.com/photo-1571167530149-c1105da4c2a8?w=400&q=80'),('Lassi','Thick sweet lassi',60,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Khoya Barfi','Milk solid sweet',100,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80')],
            'Pind Balluchi':[('Sarson Da Saag','Mustard greens with makki roti',199,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Makki Di Roti','Cornmeal flatbread',40,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Tandoori Chicken','Whole roasted chicken',399,'Main Course','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Lassi','Traditional lassi',79,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Phirni','Rice pudding dessert',99,'Desserts','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80')],
            'Ahuja Milk Bhandar':[('Sweet Lassi','Thick sweet lassi',50,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Salted Lassi','Thick salted lassi',50,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Mango Lassi','Mango flavoured lassi',70,'Beverages','https://images.unsplash.com/photo-1527961393-1eacb9d98f43?w=400&q=80'),('Rabri','Thickened sweetened milk',80,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Doodh','Fresh full cream milk',30,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Moti Mahal':[('Butter Chicken','Original Moti Mahal butter chicken',249,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Dal Bukhara','Slow cooked lentils',179,'Main Course','https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&q=80'),('Tandoori Platter','Mixed tandoori platter',499,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Garlic Naan','Garlic butter naan',45,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Kulfi','Traditional Indian ice cream',79,'Desserts','https://images.unsplash.com/photo-1560717845-968823efbee1?w=400&q=80')],
            'Pizza Hub Amritsar':[('Margherita Pizza','Classic tomato mozzarella',199,'Pizza','https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=400&q=80'),('Chicken Pizza','Loaded chicken pizza',299,'Pizza','https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400&q=80'),('Paneer Pizza','Paneer tikka pizza',249,'Pizza','https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=400&q=80'),('Garlic Bread','Toasted garlic bread',99,'Sides','https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=400&q=80'),('Cold Drink','Chilled soft drink',49,'Beverages','https://images.unsplash.com/photo-1527960471264-932f39eb5846?w=400&q=80')],
            'Burger King':[('Whopper','Classic flame grilled burger',199,'Burgers','https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80'),('Veg Burger','Crispy veg patty burger',129,'Burgers','https://images.unsplash.com/photo-1550317138-10000687a72b?w=400&q=80'),('Chicken Burger','Crispy chicken burger',169,'Burgers','https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80'),('French Fries','Golden crispy fries',79,'Sides','https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&q=80'),('Cold Drink','Chilled beverage',59,'Beverages','https://images.unsplash.com/photo-1527960471264-932f39eb5846?w=400&q=80')],
            'Dominos Pizza':[('Farmhouse Pizza','Loaded veg pizza',299,'Pizza','https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=400&q=80'),('Peppy Paneer','Paneer and capsicum pizza',279,'Pizza','https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400&q=80'),('Chicken Dominator','Ultimate chicken pizza',349,'Pizza','https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400&q=80'),('Pasta Italiano','Creamy white pasta',149,'Pasta','https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=400&q=80'),('Garlic Bread','Cheesy garlic bread',119,'Sides','https://images.unsplash.com/photo-1573140247632-f8fd74997d5c?w=400&q=80')],
            'KFC Amritsar':[('Crispy Chicken','Original crispy fried chicken',199,'Chicken','https://images.unsplash.com/photo-1562967916-eb82221dfb92?w=400&q=80'),('Chicken Bucket','6 piece chicken bucket',599,'Chicken','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Zinger Burger','Spicy crispy chicken burger',179,'Burgers','https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80'),('French Fries','Crispy salted fries',89,'Sides','https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&q=80'),('Pepsi','Chilled Pepsi',59,'Beverages','https://images.unsplash.com/photo-1527960471264-932f39eb5846?w=400&q=80')],
            'Cafe Coffee Day':[('Cappuccino','Classic Italian cappuccino',149,'Coffee','https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&q=80'),('Cold Coffee','Chilled blended coffee',169,'Coffee','https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&q=80'),('Sandwich','Grilled veg sandwich',129,'Snacks','https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&q=80'),('Brownie','Warm chocolate brownie',99,'Desserts','https://images.unsplash.com/photo-1564355808539-22fda35bed7e?w=400&q=80'),('Masala Tea','Spiced Indian tea',59,'Tea','https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&q=80')],
            'Subway Amritsar':[('Veg Delite Sub','6 inch fresh veggie sub',129,'Subs','https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&q=80'),('Chicken Teriyaki','6 inch chicken teriyaki',179,'Subs','https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&q=80'),('Paneer Tikka Sub','6 inch paneer tikka sub',159,'Subs','https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&q=80'),('Cookie','Freshly baked cookie',49,'Desserts','https://images.unsplash.com/photo-1564355808539-22fda35bed7e?w=400&q=80'),('Cold Drink','Chilled beverage',59,'Beverages','https://images.unsplash.com/photo-1527960471264-932f39eb5846?w=400&q=80')],
            'Punjabi Rasoi':[('Rajma Chawal','Kidney beans with rice',129,'Main Course','https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&q=80'),('Kadhi Pakora','Yoghurt curry with fritters',119,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Aloo Paratha','Potato stuffed flatbread',80,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Lassi','Homestyle sweet lassi',49,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Kheer','Rice milk pudding',79,'Desserts','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80')],
            'Gopal Sweets':[('Pinni','Traditional Punjabi wheat sweet',60,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Barfi','Milk solid sweet',80,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Ladoo','Round sweet balls',70,'Sweets','https://images.unsplash.com/photo-1571167530149-c1105da4c2a8?w=400&q=80'),('Halwa','Semolina sweet',80,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Jalebi','Crispy sweet jalebi',60,'Sweets','https://images.unsplash.com/photo-1571167530149-c1105da4c2a8?w=400&q=80')],
            'Sindhi Sweets':[('Samosa','Crispy fried samosa',20,'Snacks','https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80'),('Aloo Tikki','Spiced potato patty',25,'Snacks','https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80'),('Chaat','Tangy spiced snack',40,'Chaat','https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80'),('Gol Gappa','Crispy puri with tangy water',30,'Chaat','https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80'),('Dahi Bhalla','Lentil dumplings in yoghurt',50,'Chaat','https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80')],
            'Bikanervala':[('Kachori','Spiced fried bread',30,'Snacks','https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80'),('Rasgulla','Soft cheese balls in syrup',80,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Namkeen','Assorted salty snacks',99,'Snacks','https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80'),('Ghewar','Honeycomb sweet with rabri',120,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Lassi','Sweet chilled lassi',60,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Amritsar Haveli':[('Amritsari Fish','Famous Amritsari fried fish',249,'Starters','https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&q=80'),('Sarson Da Saag','Mustard greens Punjabi style',179,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Tandoori Platter','Assorted tandoori items',549,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Makki Roti','Cornmeal bread',40,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Lassi','Traditional Amritsari lassi',79,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Chhota Mota Dhaba':[('Dal Tadka','Yellow lentils with tempering',99,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Aloo Gobi','Potato and cauliflower curry',99,'Main Course','https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&q=80'),('Chapati','Thin whole wheat bread',15,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Rice','Plain steamed rice',49,'Rice','https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?w=400&q=80'),('Chaas','Thin salted buttermilk',30,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Lal Sweets':[('Pinni','Punjabi wheat flour sweet',80,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Gajrela','Carrot halwa',100,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80'),('Til Rewri','Sesame jaggery sweet',60,'Sweets','https://images.unsplash.com/photo-1571167530149-c1105da4c2a8?w=400&q=80'),('Shakkar Para','Fried sweet pastry',50,'Sweets','https://images.unsplash.com/photo-1571167530149-c1105da4c2a8?w=400&q=80'),('Moong Dal Halwa','Rich lentil sweet',120,'Sweets','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80')],
            'Bade Bhaiye Da Dhaba':[('Chicken Curry','Home style chicken curry',179,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Dal Fry','Tempered yellow lentils',89,'Main Course','https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&q=80'),('Egg Curry','Boiled eggs in spiced gravy',119,'Main Course','https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80'),('Paratha','Layered butter flatbread',30,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Tea','Masala chai',20,'Beverages','https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&q=80')],
            'Fame 5 Food Court':[('Chicken Biryani','Aromatic non-veg biryani',249,'Main Course','https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&q=80'),('Butter Chicken','Rich creamy butter chicken',229,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Seekh Kebab','Spiced minced meat skewers',199,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Fish Fry','Crispy Amritsari fish',219,'Starters','https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&q=80'),('Naan','Tandoor baked naan',35,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80')],
            'Avtar Non Veg Dhaba':[('Mutton Curry','Slow cooked mutton',279,'Main Course','https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80'),('Chicken Masala','Spicy chicken masala',199,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Egg Bhurji','Scrambled spiced eggs',99,'Main Course','https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80'),('Tandoori Roti','Fresh tandoor roti',20,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Lassi','Sweet chilled lassi',50,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Prince Chicken Bar':[('Half Chicken Fry','Crispy fried half chicken',299,'Main Course','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Full Chicken','Whole crispy chicken',549,'Main Course','https://images.unsplash.com/photo-1562967916-eb82221dfb92?w=400&q=80'),('Chicken Wings','Spicy fried wings',199,'Starters','https://images.unsplash.com/photo-1527477396000-e27163b481c2?w=400&q=80'),('Rumali Roti','Thin handkerchief bread',25,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Cold Drink','Chilled soft drink',40,'Beverages','https://images.unsplash.com/photo-1527960471264-932f39eb5846?w=400&q=80')],
            'Dawat Non Veg Point':[('Mutton Rogan Josh','Aromatic mutton curry',299,'Main Course','https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80'),('Chicken Handi','Slow cooked chicken',229,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Keema Naan','Minced meat stuffed naan',89,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Raita','Yoghurt with cucumber',49,'Sides','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80'),('Shahi Tukda','Royal bread dessert',99,'Desserts','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80')],
            'Kitchen 1574':[('Continental Chicken','Grilled chicken with sauce',349,'Main Course','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Lamb Chops','Herb marinated lamb',449,'Main Course','https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80'),('Prawn Cocktail','Chilled prawn starter',299,'Starters','https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&q=80'),('Soup','Chef special soup',149,'Starters','https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80'),('Tiramisu','Classic Italian dessert',199,'Desserts','https://images.unsplash.com/photo-1564355808539-22fda35bed7e?w=400&q=80')],
            'The Chicken Wala':[('Tandoori Chicken','Whole tandoori chicken',399,'Main Course','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Chicken Tikka','Juicy grilled chicken pieces',249,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Chicken Roll','Chicken stuffed paratha roll',149,'Snacks','https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&q=80'),('Garlic Naan','Butter garlic naan',45,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Lassi','Cold sweet lassi',60,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Time Tandoori':[('Tandoori Chicken','Classic tandoori chicken',349,'Main Course','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Boti Kebab','Tender meat kebab',249,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Chicken Tikka Masala','Tikka in rich gravy',229,'Main Course','https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400&q=80'),('Paratha','Butter layered paratha',35,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Raita','Fresh cucumber raita',49,'Sides','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Jiggle Belly':[('Chicken Burger','Crispy chicken patty burger',179,'Burgers','https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&q=80'),('Loaded Fries','Fries with chicken topping',149,'Sides','https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400&q=80'),('Chicken Wrap','Grilled chicken wrap',169,'Wraps','https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&q=80'),('Chicken Nuggets','Crispy nuggets 6 pc',129,'Snacks','https://images.unsplash.com/photo-1562967916-eb82221dfb92?w=400&q=80'),('Cold Drink','Chilled beverage',59,'Beverages','https://images.unsplash.com/photo-1527960471264-932f39eb5846?w=400&q=80')],
            'Rai Chicken':[('Fresh Chicken 1kg','Premium raw chicken whole',299,'Raw Chicken','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Chicken Legs 500g','Fresh chicken legs',169,'Raw Chicken','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Chicken Breast 500g','Boneless chicken breast',179,'Raw Chicken','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Grilled Chicken','Ready to eat grilled',249,'Cooked','https://images.unsplash.com/photo-1562967916-eb82221dfb92?w=400&q=80'),('Chicken Keema 500g','Minced chicken',159,'Raw Chicken','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80')],
            'Aviruchis Flour Fairy':[('Chicken Cake','Special chicken flavored cake',450,'Cakes','https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=400&q=80'),('Egg Tart','Creamy egg custard tart',149,'Pastries','https://images.unsplash.com/photo-1564355808539-22fda35bed7e?w=400&q=80'),('Chicken Puff','Flaky chicken puff pastry',89,'Snacks','https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80'),('Brownie','Rich chocolate brownie',129,'Desserts','https://images.unsplash.com/photo-1564355808539-22fda35bed7e?w=400&q=80'),('Cold Coffee','Blended cold coffee',149,'Beverages','https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400&q=80')],
            'Wholemeal':[('Grilled Chicken Salad','Healthy grilled chicken salad',299,'Salads','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Chicken Sandwich','Whole grain chicken sandwich',249,'Sandwiches','https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&q=80'),('Prawn Pasta','Whole wheat prawn pasta',349,'Pasta','https://images.unsplash.com/photo-1555949258-eb67b1ef0ceb?w=400&q=80'),('Chicken Soup','Hearty chicken broth',179,'Soups','https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80'),('Lemonade','Fresh squeezed lemonade',99,'Beverages','https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&q=80')],
            'Finch Brew Cafe':[('Chicken Sandwich','Grilled chicken cafe sandwich',249,'Sandwiches','https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&q=80'),('Cappuccino','Italian style cappuccino',159,'Coffee','https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&q=80'),('Eggs Benedict','Poached eggs with chicken',299,'Breakfast','https://images.unsplash.com/photo-1547592180-85f173990554?w=400&q=80'),('Chicken Quesadilla','Grilled chicken quesadilla',279,'Snacks','https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=400&q=80'),('Craft Beer','Local craft beer',199,'Beverages','https://images.unsplash.com/photo-1527960471264-932f39eb5846?w=400&q=80')],
            'Barbeque Nation':[('BBQ Chicken Platter','Unlimited BBQ chicken',699,'BBQ','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Mutton Seekh','Grilled mutton seekh kebab',349,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Fish Tikka','Grilled spiced fish tikka',299,'Starters','https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&q=80'),('Chicken Tangdi','Marinated chicken legs',299,'BBQ','https://images.unsplash.com/photo-1598514982901-8d0df55ad5dd?w=400&q=80'),('Gulab Jamun','Soft sweet dumplings',99,'Desserts','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80')],
            'The Yellow Chilli':[('Dal Bukhara','Slow cooked black lentils',299,'Main Course','https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400&q=80'),('Chicken Tikka','Classic chicken tikka',349,'Starters','https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400&q=80'),('Mutton Biryani','Aromatic mutton biryani',399,'Main Course','https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=400&q=80'),('Butter Naan','Soft butter naan',55,'Breads','https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400&q=80'),('Phirni','Creamy rice pudding',149,'Desserts','https://images.unsplash.com/photo-1548365328-8c6db3220e4c?w=400&q=80')],
        }
        for r in rdata:
            rid = restaurants_col.insert_one({'name':r[0],'area':r[1],'address':r[2],'cuisine':r[3],'rating':r[4],'delivery_time':r[5],'min_order':r[6],'image_url':r[7],'is_open':True,'created_at':datetime.now()}).inserted_id
            for item in menus.get(r[0],[]):
                menu_items_col.insert_one({'restaurant_id':rid,'name':item[0],'description':item[1],'price':item[2],'category':item[3],'image_url':item[4],'available':True,'created_at':datetime.now()})
        print(f"✅ Seeded 40 restaurants + menus")

    # Coupons
    if coupons_col.count_documents({}) == 0:
        coupons_col.insert_many([
            {'code':'WELCOME50','discount_type':'percent','discount_value':50,'min_order':200,'max_discount':100,'active':True,'uses_left':1000,'description':'50% off on your first order!'},
            {'code':'ZAAQ20','discount_type':'percent','discount_value':20,'min_order':150,'max_discount':80,'active':True,'uses_left':500,'description':'20% off on all orders'},
            {'code':'FLAT100','discount_type':'flat','discount_value':100,'min_order':400,'max_discount':100,'active':True,'uses_left':200,'description':'Flat ₹100 off on orders above ₹400'},
            {'code':'KULCHA30','discount_type':'percent','discount_value':30,'min_order':100,'max_discount':60,'active':True,'uses_left':300,'description':'30% off on kulcha orders'},
            {'code':'LASSI15','discount_type':'flat','discount_value':15,'min_order':50,'max_discount':15,'active':True,'uses_left':999,'description':'₹15 off on any order'},
        ])
        print("✅ Coupons seeded")

# ═══════════════════════════════════════════════════════════════════════════════
#  DECORATORS
# ═══════════════════════════════════════════════════════════════════════════════
def login_required(f):
    @wraps(f)
    def d(*a,**k):
        if 'user_id' not in session: flash('Please login first.','warning'); return redirect(url_for('login'))
        return f(*a,**k)
    return d

def admin_required(f):
    @wraps(f)
    def d(*a,**k):
        if 'admin_id' not in session: flash('Admin access required.','danger'); return redirect(url_for('admin_login'))
        return f(*a,**k)
    return d

# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/')
def index(): return render_template('landing.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        if users_col.find_one({'email': request.form['email'].strip()}):
            flash('Email already registered.','danger')
        else:
            users_col.insert_one({'name':request.form['name'].strip(),'email':request.form['email'].strip(),'password':generate_password_hash(request.form['password']),'phone':request.form['phone'].strip(),'address':request.form['address'].strip(),'created_at':datetime.now()})
            # Auto-login after registration
            new_user = users_col.find_one({'email': request.form['email'].strip()})
            session['user_id'] = str(new_user['_id']); session['user_name'] = new_user['name']
            flash(f"Welcome to ZaaQa, {new_user['name']}! 🎉",'success')
            return redirect(url_for('restaurants'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = users_col.find_one({'email': request.form['email'].strip()})
        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id']); session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!",'success')
            return redirect(url_for('restaurants'))
        flash('Invalid email or password.','danger')
        return render_template('login.html')
    # GET request — show login page
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear(); flash('Logged out successfully.','info'); return redirect(url_for('login'))

@app.route('/set_language/<lang>')
def set_language(lang):
    if lang in SUPPORTED_LANGS: session['lang'] = lang
    return redirect(request.referrer or url_for('restaurants'))

# ═══════════════════════════════════════════════════════════════════════════════
#  RESTAURANTS
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/restaurants')
@login_required
def restaurants():
    search = request.args.get('search','').strip()
    area   = request.args.get('area','').strip()
    query  = {'is_open': True}
    if search:
        pat = re.compile(search, re.IGNORECASE)
        query['$or'] = [{'name':pat},{'cuisine':pat}]
    if area: query['area'] = area
    rests = fix_ids(list(restaurants_col.find(query).sort('rating', DESCENDING)))
    areas = restaurants_col.distinct('area')
    return render_template('restaurants.html', restaurants=rests, areas=areas, search=search, selected_area=area, selected_cuisine='')

@app.route('/restaurant/<restaurant_id>')
@login_required
def restaurant_menu(restaurant_id):
    oid = to_oid(restaurant_id)
    restaurant = fix_id(restaurants_col.find_one({'_id': oid}))
    if not restaurant: flash('Restaurant not found.','danger'); return redirect(url_for('restaurants'))
    items = fix_ids(list(menu_items_col.find({'restaurant_id':oid,'available':True}).sort('category',1)))
    categories = list(dict.fromkeys([i['category'] for i in items]))
    return render_template('restaurant_menu.html', restaurant=restaurant, items=items, categories=categories)

# ═══════════════════════════════════════════════════════════════════════════════
#  CART
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/cart')
@login_required
def cart():
    cart_data = session.get('cart',{})
    items, total, restaurant = [], 0, None
    for item_id, qty in cart_data.items():
        item = menu_items_col.find_one({'_id': to_oid(item_id)})
        if item:
            rest = restaurants_col.find_one({'_id': item['restaurant_id']})
            item = fix_id(item); item['qty']=qty; item['subtotal']=item['price']*qty
            item['restaurant_name'] = rest['name'] if rest else ''
            total += item['subtotal']; items.append(item)
            if not restaurant and rest: restaurant = {'id':str(rest['_id']),'name':rest['name']}
    return render_template('cart.html', items=items, total=total, restaurant=restaurant)

@app.route('/cart/add/<item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    item = menu_items_col.find_one({'_id': to_oid(item_id)})
    if not item: flash('Item not found.','danger'); return redirect(request.referrer or url_for('restaurants'))
    cart = session.get('cart',{})
    if cart:
        first = menu_items_col.find_one({'_id': to_oid(list(cart.keys())[0])})
        if first and str(first['restaurant_id']) != str(item['restaurant_id']):
            flash('Cart cleared! Only one restaurant at a time.','warning'); cart = {}
    cart[item_id] = cart.get(item_id,0)+1; session['cart'] = cart
    flash('Item added to cart!','success')
    return redirect(request.referrer or url_for('restaurants'))

@app.route('/cart/remove/<item_id>')
@login_required
def remove_from_cart(item_id):
    cart = session.get('cart',{}); cart.pop(item_id,None); session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    item_id=request.form['item_id']; qty=int(request.form['qty'])
    cart=session.get('cart',{})
    if qty<=0: cart.pop(item_id,None)
    else: cart[item_id]=qty
    session['cart']=cart; return redirect(url_for('cart'))

@app.route('/cart/clear')
@login_required
def clear_cart():
    session.pop('cart',None); return redirect(url_for('restaurants'))

# ═══════════════════════════════════════════════════════════════════════════════
#  COUPON API
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/api/apply_coupon', methods=['POST'])
@login_required
def apply_coupon():
    data   = request.get_json()
    code   = data.get('code','').strip().upper()
    total  = float(data.get('total',0))
    coupon = coupons_col.find_one({'code':code,'active':True})
    if not coupon: return jsonify({'success':False,'message':'Invalid coupon code'})
    if coupon.get('uses_left',0) <= 0: return jsonify({'success':False,'message':'Coupon expired'})
    if total < coupon.get('min_order',0): return jsonify({'success':False,'message':f"Min order ₹{coupon['min_order']} required"})
    if coupon['discount_type']=='percent':
        discount = min(total*coupon['discount_value']/100, coupon.get('max_discount',9999))
    else:
        discount = coupon['discount_value']
    session['coupon'] = {'code':code,'discount':round(discount,2)}
    return jsonify({'success':True,'discount':round(discount,2),'message':f"Coupon applied! ₹{round(discount,2)} off 🎉"})

@app.route('/api/remove_coupon')
@login_required
def remove_coupon():
    session.pop('coupon',None); return jsonify({'success':True})

@app.route('/offers')
@login_required
def offers():
    return render_template('offers.html', coupons=list(coupons_col.find({'active':True})))

# ═══════════════════════════════════════════════════════════════════════════════
#  CHECKOUT — with email notification
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/checkout', methods=['GET','POST'])
@login_required
def checkout():
    cart_data = session.get('cart',{})
    if not cart_data: flash('Cart is empty.','warning'); return redirect(url_for('cart'))
    items, total, restaurant_oid = [], 0, None
    for item_id, qty in cart_data.items():
        item = fix_id(menu_items_col.find_one({'_id': to_oid(item_id)}))
        if item:
            item['qty']=qty; item['subtotal']=item['price']*qty
            total+=item['subtotal']; restaurant_oid=item['restaurant_id']; items.append(item)
    restaurant  = fix_id(restaurants_col.find_one({'_id':restaurant_oid})) if restaurant_oid else None
    coupon_data = session.get('coupon',{})
    discount    = coupon_data.get('discount',0)
    final_total = max(0, total-discount)
    if request.method == 'POST':
        order_id = orders_col.insert_one({
            'user_id':          session['user_id'],
            'restaurant_id':    str(restaurant_oid),
            'restaurant_name':  restaurant['name'] if restaurant else '',
            'items':            [{'menu_item_id':i['id'],'name':i['name'],'quantity':i['qty'],'price':i['price']} for i in items],
            'total_amount':     final_total,
            'original_amount':  total,
            'discount':         discount,
            'coupon_code':      coupon_data.get('code',''),
            'payment_method':   request.form['payment_method'],
            'delivery_address': request.form['delivery_address'].strip(),
            'status':           'Pending',
            'created_at':       datetime.now()
        }).inserted_id
        if coupon_data.get('code'):
            coupons_col.update_one({'code':coupon_data['code']},{'$inc':{'uses_left':-1}})
        session.pop('cart',None); session.pop('coupon',None)
        # Notification + Email
        notify_user(
            session['user_id'],
            '🎉 Order Placed!',
            f"Your order from {restaurant['name'] if restaurant else ''} has been placed successfully!",
            'order', str(order_id),
            restaurant_name = restaurant['name'] if restaurant else '',
            amount          = final_total,
            payment         = request.form['payment_method'],
            status          = 'placed'
        )
        flash('Order placed successfully! 🎉','success')
        return redirect(url_for('order_tracking', order_id=str(order_id)))
    return render_template('checkout.html', items=items, total=total, discount=discount,
                           final_total=final_total, restaurant=restaurant, coupon=coupon_data)

# ═══════════════════════════════════════════════════════════════════════════════
#  ORDERS & TRACKING
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/orders')
@login_required
def my_orders():
    orders = fix_ids(list(orders_col.find({'user_id':session['user_id']}).sort('created_at',DESCENDING)))
    return render_template('orders.html', orders=orders)

@app.route('/order/track/<order_id>')
@login_required
def order_tracking(order_id):
    order = fix_id(orders_col.find_one({'_id':to_oid(order_id),'user_id':session['user_id']}))
    if not order: flash('Order not found.','danger'); return redirect(url_for('my_orders'))
    return render_template('tracking.html', order=order, order_items=order.get('items',[]))

# ═══════════════════════════════════════════════════════════════════════════════
#  NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/notifications')
@login_required
def notifications():
    notifs = fix_ids(list(notifications_col.find({'user_id':session['user_id']}).sort('created_at',DESCENDING).limit(50)))
    return render_template('notifications.html', notifications=notifs)

@app.route('/notifications/read/<nid>')
@login_required
def mark_read(nid):
    notifications_col.update_one({'_id':to_oid(nid)},{'$set':{'read':True}})
    return redirect(request.referrer or url_for('notifications'))

@app.route('/notifications/read_all')
@login_required
def mark_all_read():
    notifications_col.update_many({'user_id':session['user_id']},{'$set':{'read':True}})
    return redirect(url_for('notifications'))

@app.route('/api/notifications/count')
@login_required
def notif_count():
    count = notifications_col.count_documents({'user_id':session['user_id'],'read':False})
    return jsonify({'count':count})

# ═══════════════════════════════════════════════════════════════════════════════
#  REVIEWS
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/review/<order_id>', methods=['GET','POST'])
@login_required
def add_review(order_id):
    order = fix_id(orders_col.find_one({'_id':to_oid(order_id),'user_id':session['user_id']}))
    if not order or order.get('status') != 'Delivered':
        flash('You can only review delivered orders.','warning'); return redirect(url_for('my_orders'))
    if reviews_col.find_one({'order_id':order_id,'user_id':session['user_id']}):
        flash('Already reviewed this order.','info'); return redirect(url_for('my_orders'))
    if request.method == 'POST':
        rating = int(request.form.get('rating',5))
        reviews_col.insert_one({'order_id':order_id,'user_id':session['user_id'],'user_name':session['user_name'],'restaurant_id':order.get('restaurant_id',''),'restaurant_name':order.get('restaurant_name',''),'rating':rating,'comment':request.form.get('comment','').strip(),'created_at':datetime.now()})
        rest_reviews = list(reviews_col.find({'restaurant_id':order.get('restaurant_id','')}))
        if rest_reviews:
            avg = round(sum(r['rating'] for r in rest_reviews)/len(rest_reviews),1)
            restaurants_col.update_one({'_id':to_oid(order.get('restaurant_id',''))},{'$set':{'rating':avg}})
        flash('Thank you for your review! ⭐','success')
        return redirect(url_for('my_orders'))
    restaurant = fix_id(restaurants_col.find_one({'_id':to_oid(order.get('restaurant_id',''))}))
    return render_template('add_review.html', order=order, restaurant=restaurant)

@app.route('/reviews/<restaurant_id>')
@login_required
def restaurant_reviews(restaurant_id):
    restaurant = fix_id(restaurants_col.find_one({'_id':to_oid(restaurant_id)}))
    reviews    = fix_ids(list(reviews_col.find({'restaurant_id':restaurant_id}).sort('created_at',DESCENDING)))
    avg        = round(sum(r['rating'] for r in reviews)/len(reviews),1) if reviews else 0
    return render_template('reviews.html', restaurant=restaurant, reviews=reviews, avg=avg)

# ═══════════════════════════════════════════════════════════════════════════════
#  USER PROFILE
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/profile', methods=['GET','POST'])
@login_required
def user_profile():
    user = fix_id(users_col.find_one({'_id':to_oid(session['user_id'])}))
    if request.method == 'POST':
        update = {'name':request.form['name'].strip(),'phone':request.form['phone'].strip(),'address':request.form['address'].strip()}
        if request.form.get('new_password'):
            if check_password_hash(user['password'],request.form['current_password']):
                update['password'] = generate_password_hash(request.form['new_password'])
            else:
                flash('Current password is incorrect.','danger'); return render_template('profile.html',user=user,order_count=0,total_spent=0)
        users_col.update_one({'_id':to_oid(session['user_id'])},{'$set':update})
        session['user_name'] = update['name']
        flash('Profile updated! ✅','success'); return redirect(url_for('user_profile'))
    order_count = orders_col.count_documents({'user_id':session['user_id']})
    total_spent_agg = list(orders_col.aggregate([{'$match':{'user_id':session['user_id'],'status':'Delivered'}},{'$group':{'_id':None,'total':{'$sum':'$total_amount'}}}]))
    spent = total_spent_agg[0]['total'] if total_spent_agg else 0
    return render_template('profile.html', user=user, order_count=order_count, total_spent=spent)

# ═══════════════════════════════════════════════════════════════════════════════
#  ADVANCED SEARCH
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/search')
@login_required
def advanced_search():
    query    = request.args.get('q','').strip()
    cuisine  = request.args.get('cuisine','').strip()
    min_r    = request.args.get('min_rating','').strip()
    sort_by  = request.args.get('sort','rating')
    rest_results, item_results = [], []
    if query or cuisine or min_r:
        rq = {'is_open':True}
        if query:
            pat = re.compile(query,re.IGNORECASE)
            rq['$or'] = [{'name':pat},{'cuisine':pat},{'area':pat}]
        if cuisine: rq['cuisine'] = re.compile(cuisine,re.IGNORECASE)
        if min_r:   rq['rating']  = {'$gte':float(min_r)}
        rest_results = fix_ids(list(restaurants_col.find(rq).sort(sort_by if sort_by=='rating' else 'delivery_time',DESCENDING)))
        if query:
            ip  = re.compile(query,re.IGNORECASE)
            iq  = {'$or':[{'name':ip},{'description':ip},{'category':ip}],'available':True}
            rmap = {str(r['_id']):r for r in restaurants_col.find({})}
            for item in fix_ids(list(menu_items_col.find(iq).limit(20))):
                rest = rmap.get(str(item.get('restaurant_id','')))
                if rest:
                    item['restaurant_name'] = rest['name']
                    item['restaurant_id_str'] = str(rest['_id'])
                    item_results.append(item)
    cuisines = list(set(c.strip() for cs in restaurants_col.distinct('cuisine') for c in cs.split(',')))
    return render_template('search.html', rest_results=rest_results, item_results=item_results,
                           query=query, cuisine=cuisine, min_r=min_r, sort_by=sort_by, cuisines=sorted(cuisines))

# ═══════════════════════════════════════════════════════════════════════════════
#  HEALTH
# ═══════════════════════════════════════════════════════════════════════════════
def load_health_foods():
    foods, path = [], os.path.join(app.root_path,'data','health_foods.csv')
    if os.path.exists(path):
        with open(path,newline='',encoding='utf-8') as f:
            for row in csv.DictReader(f): foods.append(row)
    return foods

def get_recommendations(bp,sugar):
    foods,rec = load_health_foods(),[]
    for food in foods:
        tags = food.get('tags','').lower()
        if bp=='High BP' and 'low_sodium' in tags: rec.append(food)
        elif bp=='Low BP' and 'iron_rich' in tags: rec.append(food)
        if sugar=='Diabetes' and 'low_sugar' in tags:
            if food not in rec: rec.append(food)
        elif sugar=='High Sugar' and 'low_gi' in tags:
            if food not in rec: rec.append(food)
    return rec if rec else foods[:8]

@app.route('/health', methods=['GET','POST'])
@login_required
def health_check():
    rec,bp,sugar = [],'',''
    if request.method == 'POST':
        bp=request.form.get('bp_condition',''); sugar=request.form.get('sugar_condition','')
        rec=get_recommendations(bp,sugar)
    return render_template('health.html', recommendations=rec, bp_condition=bp, sugar_condition=sugar)

# ═══════════════════════════════════════════════════════════════════════════════
#  ADMIN
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        admin = admins_col.find_one({'username':request.form['username']})
        if admin and check_password_hash(admin['password'],request.form['password']):
            session['admin_id']=str(admin['_id']); session['admin_name']=admin['username']
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.','danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id',None); session.pop('admin_name',None); return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    rev = list(orders_col.aggregate([{'$match':{'status':'Delivered'}},{'$group':{'_id':None,'total':{'$sum':'$total_amount'}}}]))
    recent = fix_ids(list(orders_col.find().sort('created_at',DESCENDING).limit(10)))
    for o in recent:
        u = users_col.find_one({'_id':to_oid(o.get('user_id',''))})
        o['user_name'] = u['name'] if u else 'Unknown'
    return render_template('admin_dashboard.html',
        total_users=users_col.count_documents({}),
        total_orders=orders_col.count_documents({}),
        revenue=rev[0]['total'] if rev else 0,
        total_items=restaurants_col.count_documents({}),
        recent_orders=recent)

@app.route('/admin/restaurants')
@admin_required
def admin_restaurants():
    return render_template('admin_restaurants.html', restaurants=fix_ids(list(restaurants_col.find().sort('name',1))))

@app.route('/admin/restaurants/toggle/<rid>')
@admin_required
def admin_toggle_restaurant(rid):
    oid=to_oid(rid); rest=restaurants_col.find_one({'_id':oid})
    if rest: restaurants_col.update_one({'_id':oid},{'$set':{'is_open':not rest.get('is_open',True)}})
    flash('Restaurant status updated.','success'); return redirect(url_for('admin_restaurants'))

@app.route('/admin/menu')
@admin_required
def admin_menu():
    items = fix_ids(list(menu_items_col.find().sort('name',1)))
    rmap  = {str(r['_id']):r['name'] for r in restaurants_col.find({},{'name':1})}
    for i in items: i['restaurant_name'] = rmap.get(str(i.get('restaurant_id','')),'Unknown')
    return render_template('admin_menu.html', items=items)

@app.route('/admin/menu/add', methods=['GET','POST'])
@admin_required
def admin_add_item():
    rests = fix_ids(list(restaurants_col.find({},{'name':1}).sort('name',1)))
    if request.method == 'POST':
        menu_items_col.insert_one({'restaurant_id':to_oid(request.form['restaurant_id']),'name':request.form['name'].strip(),'description':request.form['description'].strip(),'price':float(request.form['price']),'category':request.form['category'].strip(),'available':bool(request.form.get('available')),'image_url':request.form.get('image_url','').strip(),'created_at':datetime.now()})
        flash('Menu item added!','success'); return redirect(url_for('admin_menu'))
    return render_template('admin_add_item.html', restaurants=rests)

@app.route('/admin/menu/edit/<item_id>', methods=['GET','POST'])
@admin_required
def admin_edit_item(item_id):
    rests = fix_ids(list(restaurants_col.find({},{'name':1}).sort('name',1)))
    oid   = to_oid(item_id)
    if request.method == 'POST':
        menu_items_col.update_one({'_id':oid},{'$set':{'restaurant_id':to_oid(request.form['restaurant_id']),'name':request.form['name'].strip(),'description':request.form['description'].strip(),'price':float(request.form['price']),'category':request.form['category'].strip(),'available':bool(request.form.get('available')),'image_url':request.form.get('image_url','').strip()}})
        flash('Item updated!','success'); return redirect(url_for('admin_menu'))
    item = fix_id(menu_items_col.find_one({'_id':oid}))
    if item: item['restaurant_id'] = str(item.get('restaurant_id',''))
    return render_template('admin_edit_item.html', item=item, restaurants=rests)

@app.route('/admin/menu/delete/<item_id>')
@admin_required
def admin_delete_item(item_id):
    menu_items_col.delete_one({'_id':to_oid(item_id)}); flash('Item deleted.','info')
    return redirect(url_for('admin_menu'))

@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = fix_ids(list(orders_col.find().sort('created_at',DESCENDING)))
    for o in orders:
        u = users_col.find_one({'_id':to_oid(o.get('user_id',''))})
        o['user_name'] = u['name'] if u else 'Unknown'
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/orders/update/<order_id>', methods=['POST'])
@admin_required
def admin_update_order(order_id):
    new_status = request.form['status']
    order = orders_col.find_one({'_id':to_oid(order_id)})
    if order:
        orders_col.update_one({'_id':to_oid(order_id)},{'$set':{'status':new_status}})
        status_msgs = {
            'Confirmed':        ('✅ Order Confirmed!',    'Your order has been confirmed by the restaurant.'),
            'Preparing':        ('👨‍🍳 Being Prepared!',   'The restaurant is preparing your food.'),
            'Out for Delivery': ('🛵 On the Way!',         'Your order is out for delivery! Be ready!'),
            'Delivered':        ('🏠 Order Delivered!',    'Your order has been delivered. Enjoy your meal!'),
            'Cancelled':        ('❌ Order Cancelled',     'Your order has been cancelled.'),
        }
        if new_status in status_msgs:
            title, msg = status_msgs[new_status]
            notify_user(
                order['user_id'], title, msg, 'order', order_id,
                restaurant_name = order.get('restaurant_name',''),
                amount          = order.get('total_amount',0),
                payment         = order.get('payment_method',''),
                status          = new_status
            )
    flash('Order status updated.','success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/users')
@admin_required
def admin_users():
    return render_template('admin_users.html', users=fix_ids(list(users_col.find({},{'password':0}).sort('created_at',DESCENDING))))

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    daily  = list(orders_col.aggregate([{'$match':{'status':'Delivered'}},{'$group':{'_id':{'$dateToString':{'format':'%Y-%m-%d','date':'$created_at'}},'revenue':{'$sum':'$total_amount'},'orders':{'$sum':1}}},{'$sort':{'_id':1}},{'$limit':30}]))
    top_r  = list(orders_col.aggregate([{'$group':{'_id':'$restaurant_name','orders':{'$sum':1},'revenue':{'$sum':'$total_amount'}}},{'$sort':{'orders':-1}},{'$limit':10}]))
    status = list(orders_col.aggregate([{'$group':{'_id':'$status','count':{'$sum':1}}}]))
    pay    = list(orders_col.aggregate([{'$group':{'_id':'$payment_method','count':{'$sum':1}}}]))
    rev    = list(orders_col.aggregate([{'$match':{'status':'Delivered'}},{'$group':{'_id':None,'total':{'$sum':'$total_amount'}}}]))
    avg    = list(orders_col.aggregate([{'$group':{'_id':None,'avg':{'$avg':'$total_amount'}}}]))
    return render_template('admin_analytics.html', daily_data=daily, top_rests=top_r, status_data=status, pay_data=pay,
        total_revenue=rev[0]['total'] if rev else 0, avg_order=round(avg[0]['avg'],2) if avg else 0,
        total_users=users_col.count_documents({}), total_orders=orders_col.count_documents({}),
        total_restaurants=restaurants_col.count_documents({}))

@app.route('/api/order_status/<order_id>')
@login_required
def api_order_status(order_id):
    order = orders_col.find_one({'_id':to_oid(order_id),'user_id':session['user_id']})
    return jsonify({'status':order['status']}) if order else (jsonify({'error':'Not found'}),404)

# Server startup moved to bottom of file

# ═══════════════════════════════════════════════════════════════════════════════
#  LIVE DATA SIMULATOR — Background Thread
# ═══════════════════════════════════════════════════════════════════════════════

def order_simulator():
    restaurants = [
        ("Kesar Da Dhaba","Chowk Passian"),("Brothers Dhaba","Lawrence Road"),
        ("Surjit Food Plaza","Nehru Shopping"),("Bharawan Da Dhaba","Town Hall"),
        ("Beera Chicken Corner","Majitha Road"),("Crystal Restaurant","Queens Road"),
        ("Amritsari Kulcha Wala","Hall Bazaar"),("Gurdas Ram Jalebi","Katra Jaimal Singh"),
        ("Moti Mahal","Mall Road"),("KFC Amritsar","GT Road"),
        ("Dominos Pizza","Lawrence Road"),("Burger King","Alpha One Mall"),
        ("Pizza Hub Amritsar","Ranjit Avenue"),("Cafe Coffee Day","Mall Road"),
        ("Punjabi Rasoi","Green Avenue"),
    ]
    items_data = [
        ("Dal Makhani",139),("Butter Chicken",199),("Amritsari Kulcha",60),
        ("Chole",49),("Paneer Tikka",199),("Chicken Tikka",229),("Lassi",59),
        ("Jalebi",80),("Whopper",199),("Zinger Burger",179),("Margherita Pizza",199),
        ("Farmhouse Pizza",299),("Cappuccino",149),("Rajma Chawal",129),
        ("Sarson Da Saag",199),("Tandoori Chicken",399),("Kulfi",79),
        ("Garlic Naan",45),("Seekh Kebab",199),("Fish Tikka",219),
    ]
    payment_methods = ["Online","Cash on Delivery","Online","Online"]
    statuses = ["Pending","Confirmed","Preparing","Out for Delivery","Delivered"]

    print("🤖 Live Order Simulator started!")
    time.sleep(5)  # wait for app to fully start

    while True:
        try:
            rest, area = random.choice(restaurants)
            num_items  = random.randint(1, 3)
            order_items, total = [], 0
            for _ in range(num_items):
                item_name, price = random.choice(items_data)
                qty      = random.randint(1, 2)
                subtotal = price * qty
                total   += subtotal
                order_items.append({'name':item_name,'quantity':qty,'price':price})

            # Apply random coupon sometimes
            discount = 0
            if random.random() < 0.3:
                discount = random.choice([20, 50, 100])
                total    = max(0, total - discount)

            status = random.choices(statuses, weights=[10,20,20,20,30])[0]

            orders_col.insert_one({
                'user_id':          'simulator',
                'restaurant_name':  rest,
                'restaurant_id':    'sim',
                'area':             area,
                'items':            order_items,
                'total_amount':     total,
                'original_amount':  total + discount,
                'discount':         discount,
                'payment_method':   random.choice(payment_methods),
                'delivery_address': f'{random.randint(1,500)}, {area}, Amritsar',
                'status':           status,
                'is_simulated':     True,
                'created_at':       datetime.now(),
            })
        except Exception as e:
            print(f"Simulator error: {e}")
        time.sleep(random.randint(6, 14))

# Start simulator thread
_sim_thread = threading.Thread(target=order_simulator, daemon=True)
_sim_thread.start()

# ═══════════════════════════════════════════════════════════════════════════════
#  SPOONACULAR API
# ═══════════════════════════════════════════════════════════════════════════════

SPOONACULAR_KEY = os.environ.get('SPOONACULAR_KEY', 'YOUR_API_KEY_HERE')
_food_cache = {'data': None, 'time': None}

def get_food_trends():
    global _food_cache
    now = datetime.now()
    # Cache for 1 hour to save API calls
    if _food_cache['data'] and _food_cache['time']:
        diff = (now - _food_cache['time']).seconds
        if diff < 3600:
            return _food_cache['data']
    try:
        url    = 'https://api.spoonacular.com/recipes/random'
        params = {'apiKey': SPOONACULAR_KEY, 'number': 8, 'tags': 'indian'}
        resp   = req_lib.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            recipes = resp.json().get('recipes', [])
            result  = [{
                'title':    r.get('title',''),
                'image':    r.get('image',''),
                'calories': next((n['amount'] for n in r.get('nutrition',{}).get('nutrients',[]) if n['name']=='Calories'), 0),
                'protein':  next((n['amount'] for n in r.get('nutrition',{}).get('nutrients',[]) if n['name']=='Protein'), 0),
                'ready_in': r.get('readyInMinutes', 30),
                'servings': r.get('servings', 2),
            } for r in recipes]
            _food_cache = {'data': result, 'time': now}
            return result
    except Exception as e:
        print(f"Spoonacular error: {e}")
    # Fallback data if API not available
    return [
        {'title':'Butter Chicken','image':'','calories':320,'protein':28,'ready_in':30,'servings':4},
        {'title':'Dal Makhani','image':'','calories':250,'protein':12,'ready_in':45,'servings':4},
        {'title':'Paneer Tikka','image':'','calories':280,'protein':18,'ready_in':25,'servings':2},
        {'title':'Amritsari Kulcha','image':'','calories':380,'protein':10,'ready_in':20,'servings':2},
        {'title':'Sarson Da Saag','image':'','calories':190,'protein':8,'ready_in':60,'servings':4},
        {'title':'Chicken Tikka Masala','image':'','calories':350,'protein':32,'ready_in':35,'servings':4},
        {'title':'Rajma Chawal','image':'','calories':420,'protein':15,'ready_in':40,'servings':3},
        {'title':'Lassi','image':'','calories':150,'protein':6,'ready_in':5,'servings':1},
    ]

# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD ROUTES
# ═══════════════════════════════════════════════════════════════════════════════
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/live-stats')
@login_required
def live_stats():
    from collections import Counter
    # Basic counts
    total_orders   = orders_col.count_documents({})
    total_users    = users_col.count_documents({})
    total_rests    = restaurants_col.count_documents({})

    # Revenue
    rev_pipe = [{'$group':{'_id':None,'total':{'$sum':'$total_amount'}}}]
    rev      = list(orders_col.aggregate(rev_pipe))
    revenue  = round(rev[0]['total'], 2) if rev else 0

    # Today stats
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders  = orders_col.count_documents({'created_at':{'$gte':today_start}})
    today_rev_p   = [{'$match':{'created_at':{'$gte':today_start}}},{'$group':{'_id':None,'t':{'$sum':'$total_amount'}}}]
    today_rev_r   = list(orders_col.aggregate(today_rev_p))
    today_revenue = round(today_rev_r[0]['t'], 2) if today_rev_r else 0

    # Latest order
    latest = orders_col.find_one(sort=[('created_at',-1)])
    latest_info = {}
    if latest:
        latest_info = {
            'restaurant': latest.get('restaurant_name',''),
            'amount':     latest.get('total_amount',0),
            'area':       latest.get('area',''),
            'status':     latest.get('status',''),
            'time':       latest['created_at'].strftime('%H:%M:%S') if isinstance(latest.get('created_at'), datetime) else '',
        }

    # Status breakdown
    status_pipe  = [{'$group':{'_id':'$status','count':{'$sum':1}}}]
    status_data  = {s['_id']: s['count'] for s in orders_col.aggregate(status_pipe)}

    # Revenue by day (last 7 days)
    rev7_pipe = [
        {'$group':{'_id':{'$dateToString':{'format':'%Y-%m-%d','date':'$created_at'}},'rev':{'$sum':'$total_amount'},'cnt':{'$sum':1}}},
        {'$sort':{'_id':-1}},{'$limit':7}
    ]
    rev7 = list(orders_col.aggregate(rev7_pipe))
    rev7.reverse()

    # Top restaurants
    top_rest_pipe = [{'$group':{'_id':'$restaurant_name','orders':{'$sum':1},'revenue':{'$sum':'$total_amount'}}},{'$sort':{'orders':-1}},{'$limit':6}]
    top_rests = list(orders_col.aggregate(top_rest_pipe))

    # Area distribution
    area_pipe = [{'$group':{'_id':'$area','orders':{'$sum':1}}},{'$sort':{'orders':-1}},{'$limit':8}]
    area_data = list(orders_col.aggregate(area_pipe))

    # Payment methods
    pay_pipe  = [{'$group':{'_id':'$payment_method','count':{'$sum':1}}}]
    pay_data  = list(orders_col.aggregate(pay_pipe))

    # Hourly orders (today)
    hour_pipe = [
        {'$match':{'created_at':{'$gte':today_start}}},
        {'$group':{'_id':{'$hour':'$created_at'},'count':{'$sum':1}}},
        {'$sort':{'_id':1}}
    ]
    hour_data = list(orders_col.aggregate(hour_pipe))

    # Average order value
    avg_pipe = [{'$group':{'_id':None,'avg':{'$avg':'$total_amount'}}}]
    avg_r    = list(orders_col.aggregate(avg_pipe))
    avg_val  = round(avg_r[0]['avg'], 2) if avg_r else 0

    # Recent 10 orders for live feed
    recent = list(orders_col.find().sort('created_at',-1).limit(10))
    live_feed = [{
        'restaurant': o.get('restaurant_name',''),
        'amount':     o.get('total_amount',0),
        'status':     o.get('status',''),
        'area':       o.get('area',''),
        'time':       o['created_at'].strftime('%H:%M:%S') if isinstance(o.get('created_at'),datetime) else '',
        'simulated':  o.get('is_simulated', False),
    } for o in recent]

    return jsonify({
        'total_orders':   total_orders,
        'total_users':    total_users,
        'total_rests':    total_rests,
        'revenue':        revenue,
        'today_orders':   today_orders,
        'today_revenue':  today_revenue,
        'avg_order':      avg_val,
        'latest':         latest_info,
        'status_data':    status_data,
        'rev7':           [{'date':r['_id'],'revenue':r['rev'],'orders':r['cnt']} for r in rev7],
        'top_rests':      [{'name':r['_id'],'orders':r['orders'],'revenue':r['revenue']} for r in top_rests],
        'area_data':      [{'area':a['_id'],'orders':a['orders']} for a in area_data],
        'pay_data':       [{'method':p['_id'],'count':p['count']} for p in pay_data],
        'hour_data':      [{'hour':h['_id'],'count':h['count']} for h in hour_data],
        'live_feed':      live_feed,
    })

@app.route('/api/food-trends')
@login_required
def food_trends_api():
    data = get_food_trends()
    return jsonify({'trends': data})

if __name__ == '__main__':
    init_db()
    print("=" * 55)
    print("  ZaaQa — Amritsar Food Delivery System")
    print("=" * 55)
    print("✅ MongoDB Connected   → zaaq_food database")
    print("✅ Admin credentials  → admin / admin123")
    print("✅ Admin URL          → http://localhost:5000/admin/login")
    print("📧 Email config       → Edit EMAIL_USER & EMAIL_PASSWORD in app.py")
    print("🚀 App running at    → http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, port=5000)
