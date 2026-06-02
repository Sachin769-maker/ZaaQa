# ZaaQa — B.Tech Final Year Project
## Online Food Delivery System with Live Data Analysis Dashboard

### Features
- 25 Amritsar Restaurants + 125+ Menu Items
- Complete Order Management System
- LIVE Analytics Dashboard (updates every 5 seconds)
- Background Order Simulator (auto-generates orders)
- Spoonacular API Integration (real food trends)
- Email Notifications via Gmail
- In-app Real-time Notifications
- Ratings & Reviews System
- User Profile Management
- Offers & Coupons System
- Health-based Food Recommendations
- 4 Language Support (EN/HI/PA/UR)
- Admin Panel + Analytics

### Dashboard Features
- Revenue charts (7-day trend)
- Live order feed (real-time)
- Top restaurants ranking
- Order status breakdown (donut chart)
- Area-wise distribution (Amritsar)
- Payment method analysis
- Hourly order patterns
- Food trends from Spoonacular API

### Setup

Step 1 — Install MongoDB
https://www.mongodb.com/try/download/community

Step 2 — Install packages
pip install flask werkzeug pymongo dnspython requests

Step 3 — Configure Email (app.py line 20-21)
EMAIL_USER     = 'your@gmail.com'
EMAIL_PASSWORD = 'xxxx xxxx xxxx xxxx'

Step 4 — Get Spoonacular API Key (FREE)
1. Go to: https://spoonacular.com/food-api
2. Sign up free
3. Copy your API key
4. In app.py find: SPOONACULAR_KEY = 'YOUR_API_KEY_HERE'
5. Replace with your key

Step 5 — Run
python app.py

Open: http://localhost:5000
Dashboard: http://localhost:5000/dashboard
Admin: http://localhost:5000/admin/login (admin/admin123)

### Dashboard Access
Login as user → Click "Analytics" in navbar

### Coupon Codes for Demo
WELCOME50, ZAAQ20, FLAT100, KULCHA30, LASSI15
