"""
מערכת תמחור מתכונים - קורל ביטון
© 2024 כל הזכויות שמורות
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
import base64
import io

# הגדרות עמוד
st.set_page_config(
    page_title="תמחור מתכונים",
    page_icon="🎂",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS מותאם למובייל
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;700&display=swap');
    
    .stApp {
        direction: rtl !important;
        font-family: 'Rubik', sans-serif !important;
        text-align: right !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stButton > button {
        width: 100%;
        background-color: #FF6B6B;
        color: white;
        border-radius: 25px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 16px;
        border: none;
    }
    
    .stTextInput > div > div > input {
        text-align: right;
        direction: rtl;
        font-size: 16px;
    }
    
    .stSelectbox > div > div > div {
        text-align: right;
        direction: rtl;
    }
    
    h1 {
        text-align: center;
        font-size: 24px;
        color: #2C3E50;
        margin: 10px 0;
    }
    
    h3 {
        font-size: 18px;
        color: #34495e;
    }
    
    .price-highlight {
        font-size: 28px;
        font-weight: bold;
        color: #27ae60;
        text-align: center;
        padding: 10px;
        background: #e8f8f5;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .dataframe {
        font-size: 14px;
    }
    
    /* הסתרת כפתורי מינוס פלוס */
    button[title="decrement"], button[title="increment"] {
        display: none !important;
    }
    
    /* תיקון RTL */
    div[data-testid="stHorizontalBlock"] > div {
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

# מאגר חומרי גלם מלא - 102 פריטים
INGREDIENTS_DB = {
    'פצפוצי אורז': {'price': 18.9, 'package': 500, 'unit': 'גרם'},
    'שמנת מתוקה 38%': {'price': 7.07, 'package': 250, 'unit': 'גרם'},
    'שוקולד מריר מהדרין': {'price': 325.0, 'package': 10000, 'unit': 'גרם'},
    'שוקולד חלב מהדרין': {'price': 375.0, 'package': 10000, 'unit': 'גרם'},
    'שוקולד לבן מהדרין': {'price': 375.0, 'package': 10000, 'unit': 'גרם'},
    'מחית קינדר בואנו': {'price': 45.0, 'package': 1000, 'unit': 'גרם'},
    'נוטלה': {'price': 40.0, 'package': 1000, 'unit': 'גרם'},
    'פררו רושה': {'price': 24.9, 'package': 16, 'unit': 'יחידות'},
    'אוריאו רגיל': {'price': 9.9, 'package': 176, 'unit': 'גרם'},
    'אוריאו דאבל': {'price': 9.9, 'package': 170, 'unit': 'גרם'},
    'לוטוס ביסקוויט': {'price': 11.9, 'package': 250, 'unit': 'גרם'},
    'קינדר בואנו לבן וחום(שלישייה)39*3': {'price': 12.9, 'package': 6, 'unit': 'יחידות'},
    'צמקאו לבן פרווה': {'price': 92.0, 'package': 5000, 'unit': 'גרם'},
    'צמקאו חום פרווה': {'price': 92.0, 'package': 5000, 'unit': 'גרם'},
    'ג׳לטין': {'price': 170.0, 'package': 1000, 'unit': 'גרם'},
    'קמח לבן מנופה': {'price': 8.6, 'package': 1000, 'unit': 'גרם'},
    'קמח שקדים': {'price': 25.9, 'package': 250, 'unit': 'גרם'},
    'קמח כוסמין': {'price': 17.9, 'package': 1000, 'unit': 'גרם'},
    'קמח חיטה מלאה': {'price': 10.9, 'package': 1000, 'unit': 'גרם'},
    'קמח תופח': {'price': 7.9, 'package': 1000, 'unit': 'גרם'},
    'סוכר לבן': {'price': 5.2, 'package': 1000, 'unit': 'גרם'},
    'סוכר חום גולדן': {'price': 12.9, 'package': 1000, 'unit': 'גרם'},
    'סוכר חום דמררה': {'price': 12.9, 'package': 1000, 'unit': 'גרם'},
    'סוכר חום כהה': {'price': 14.9, 'package': 1000, 'unit': 'גרם'},
    'מלח': {'price': 1.3, 'package': 1000, 'unit': 'גרם'},
    'מלח גס': {'price': 1.3, 'package': 1000, 'unit': 'גרם'},
    'קקאו': {'price': 23.9, 'package': 550, 'unit': 'גרם'},
    'תמצית וניל': {'price': 4.9, 'package': 50, 'unit': 'מיליליטר'},
    'אבקת אפייה': {'price': 1.9, 'package': 100, 'unit': 'גרם'},
    'סוכר וניל': {'price': 1.9, 'package': 100, 'unit': 'גרם'},
    'אבקת סוכר': {'price': 10.0, 'package': 1000, 'unit': 'גרם'},
    'סודה לשתייה': {'price': 4.7, 'package': 80, 'unit': 'גרם'},
    'גלידן': {'price': 100.0, 'package': 5000, 'unit': 'גרם'},
    'שמנת צמחית 21%': {'price': 8.2, 'package': 250, 'unit': 'גרם'},
    'איסטנט פודינט': {'price': 20.0, 'package': 1000, 'unit': 'גרם'},
    'שמן': {'price': 14.9, 'package': 1000, 'unit': 'מיליליטר'},
    'שוקולד צ׳יפס לבן': {'price': 11.9, 'package': 260, 'unit': 'גרם'},
    'שוקולד צ׳יפס חום': {'price': 11.9, 'package': 260, 'unit': 'גרם'},
    'חלב רגיל 3%': {'price': 6.81, 'package': 1000, 'unit': 'מיליליטר'},
    'חלב נטול לקטוז': {'price': 8.9, 'package': 1000, 'unit': 'מיליליטר'},
    'חלב סויה': {'price': 11.9, 'package': 1000, 'unit': 'מיליליטר'},
    'קרם קוקוס': {'price': 7.9, 'package': 400, 'unit': 'גרם'},
    'שמרים יבשים': {'price': 6.9, 'package': 500, 'unit': 'גרם'},
    'שמרים טריים': {'price': 3.6, 'package': 50, 'unit': 'גרם'},
    'שמרים טריים ומשפר אפייה': {'price': 8.9, 'package': 100, 'unit': 'גרם'},
    'חמאה תנובה': {'price': 9.0, 'package': 200, 'unit': 'גרם'},
    'חמאה מפינלנד': {'price': 13.9, 'package': 200, 'unit': 'גרם'},
    'אצבעות קינדר': {'price': 14.9, 'package': 16, 'unit': 'יחידות'},
    'ממרח קינדר(סופר)': {'price': 16.9, 'package': 300, 'unit': 'גרם'},
    'ביצים M': {'price': 12.89, 'package': 12, 'unit': 'יחידות'},
    'ביצים L': {'price': 13.97, 'package': 12, 'unit': 'יחידות'},
    'גלוקוזה': {'price': 15.0, 'package': 500, 'unit': 'גרם'},
    'מחית וניל': {'price': 129.0, 'package': 120, 'unit': 'גרם'},
    'צבע מאכל קולור מיל': {'price': 35.0, 'package': 1, 'unit': 'יחידות'},
    'צבע מאכל מג׳יק קולורס': {'price': 18.0, 'package': 1, 'unit': 'יחידות'},
    'צבע מאכל מנדלברג': {'price': 8.0, 'package': 1, 'unit': 'יחידות'},
    'מדבקות כיתוב': {'price': 3.0, 'package': 1, 'unit': 'יחידות'},
    'טופר ימי הולדת': {'price': 3.0, 'package': 1, 'unit': 'יחידות'},
    'סוכריות ארוכות בצבעים': {'price': 12.0, 'package': 150, 'unit': 'גרם'},
    'סוכריות מיקס צבעים מיוחדות': {'price': 38.0, 'package': 350, 'unit': 'גרם'},
    'סוכריות פנינים': {'price': 10.0, 'package': 100, 'unit': 'גרם'},
    'סוכריות שלג צבעוני': {'price': 18.0, 'package': 100, 'unit': 'גרם'},
    'סוכריות צורות מיוחדות': {'price': 15.0, 'package': 100, 'unit': 'גרם'},
    'אבקת נצנצים': {'price': 115.0, 'package': 100, 'unit': 'גרם'},
    'צבע מאכל לאייבראש': {'price': 26.0, 'package': 1, 'unit': 'יחידות'},
    'נרות מיני 7.5': {'price': 7.0, 'package': 10, 'unit': 'יחידות'},
    'כפיות מיני': {'price': 18.0, 'package': 100, 'unit': 'יחידות'},
    'דפים אכילים בצבעים': {'price': 44.0, 'package': 10, 'unit': 'יחידות'},
    'ממרח spread it': {'price': 60.0, 'package': 1000, 'unit': 'גרם'},
    'ביסקוויטים פתיבר': {'price': 11.5, 'package': 500, 'unit': 'גרם'},
    'פרלין שוקולד': {'price': 40.0, 'package': 500, 'unit': 'גרם'},
    'קורנפלקס מצופה שוקולד': {'price': 35.0, 'package': 400, 'unit': 'גרם'},
    'פניני קראנץ׳ חלבי': {'price': 30.0, 'package': 400, 'unit': 'גרם'},
    'סוכריות עדשי שוקולד פרווה': {'price': 55.0, 'package': 1000, 'unit': 'גרם'},
    'קורנפלור': {'price': 6.9, 'package': 500, 'unit': 'גרם'},
    'במבה': {'price': 4.0, 'package': 100, 'unit': 'גרם'},
    'קורנפלקס אלופים': {'price': 20.0, 'package': 850, 'unit': 'גרם'},
    'חמאת בוטנים': {'price': 24.0, 'package': 1000, 'unit': 'גרם'},
    'לואקר': {'price': 15.3, 'package': 250, 'unit': 'גרם'},
    'חמאת קקאו': {'price': 20.9, 'package': 200, 'unit': 'גרם'},
    'פיסטוק': {'price': 140.0, 'package': 1000, 'unit': 'גרם'},
    'אגוזי מלך': {'price': 60.0, 'package': 1000, 'unit': 'גרם'},
    'קשיו': {'price': 85.0, 'package': 1000, 'unit': 'גרם'},
    'בצק עלים': {'price': 25.9, 'package': 1, 'unit': 'יחידות'},
    'בצק פילו': {'price': 19.9, 'package': 1, 'unit': 'יחידות'},
    'אבקת הפלא': {'price': 40.0, 'package': 150, 'unit': 'גרם'},
    'נטורינה': {'price': 7.9, 'package': 200, 'unit': 'גרם'},
    'מחמאה': {'price': 4.8, 'package': 200, 'unit': 'גרם'},
    'אפיפיות עלית': {'price': 9.6, 'package': 200, 'unit': 'גרם'},
    'קוקוס': {'price': 28.0, 'package': 1000, 'unit': 'גרם'},
    'טחינה גולמית': {'price': 14.9, 'package': 500, 'unit': 'גרם'},
    'מייפל': {'price': 15.0, 'package': 580, 'unit': 'גרם'},
    'היפו קינדר': {'price': 14.0, 'package': 5, 'unit': 'יחידות'},
    'חלב מרוכז': {'price': 9.9, 'package': 397, 'unit': 'מיליליטר'},
    'חומץ': {'price': 6.9, 'package': 1000, 'unit': 'מיליליטר'},
    'כללי קטן': {'price': 15.0, 'package': 1, 'unit': 'יחידות'},
    'כללי בינוני': {'price': 20.0, 'package': 1, 'unit': 'יחידות'},
    'כללי גדול': {'price': 30.0, 'package': 1, 'unit': 'יחידות'},
    'שוקולית': {'price': 12.0, 'package': 400, 'unit': 'גרם'},
    'ריבת חלב קומידה': {'price': 15.9, 'package': 500, 'unit': 'גרם'},
    'אגוזי לוז קצוצים': {'price': 59.9, 'package': 1000, 'unit': 'גרם'},
    'דפי טרנספר': {'price': 25.0, 'package': 1, 'unit': 'יחידות'},
}

# מאגר אריזות - 35 פריטים
PACKAGING_DB = {
    'קופסאות 40/30/8': {'price': 80, 'quantity': 10},
    'קופסא לאינגליש מכסה גבוה': {'price': 45, 'quantity': 10},
    'קופסא מלבנית מחולקת 20/11/5': {'price': 45, 'quantity': 10},
    'חלוקה פנימית לקופסא 20/20/5': {'price': 20, 'quantity': 10},
    'קופסא ל6 קאפקייקס כולל במה': {'price': 65, 'quantity': 10},
    'קופסא 30/30/11 כולל תחתית פנימית': {'price': 80, 'quantity': 10},
    'מנג׳טים לקאפקייקס צבעים -קוטר 7': {'price': 10, 'quantity': 40},
    'קריסטליות עיגול - 10 ס״מ': {'price': 25, 'quantity': 10},
    'קריסטליות עיגול - 16 ס״מ': {'price': 115, 'quantity': 50},
    'קופסא 24/24/13': {'price': 45, 'quantity': 5},
    'קופסא 25/35/7 עם מכסה גבוה 8.5 ס״מ': {'price': 45, 'quantity': 10},
    'קופסא 25/35/7 עם מכסה גבוה + 5 במות 20 קינוחים': {'price': 40, 'quantity': 5},
    'מארז 20/20/5': {'price': 100, 'quantity': 20},
    'מארז חלוקה מכסה': {'price': 50, 'quantity': 10},
    'כיבודיות': {'price': 110, 'quantity': 100},
    'ברולה -לב אישי': {'price': 110, 'quantity': 100},
    'קריסטל לב קוטר 16': {'price': 105, 'quantity': 30},
    'קרטון בנטו': {'price': 55, 'quantity': 50},
    'אלומיניום מיני אינגליש קייק ומכסה 16/6': {'price': 85, 'quantity': 50},
    'קריסטליות פלסטיק למארז+מכסה 16': {'price': 40, 'quantity': 10},
    'קופסת פרלינים 16 תאים': {'price': 65, 'quantity': 20},
    'קופסת קאפקייקס 4 תאים': {'price': 150, 'quantity': 50},
    'מיכל פרוסת עוגה זהב בודד': {'price': 30, 'quantity': 50},
    'קופסת קאפקייקס 6 תאים': {'price': 75, 'quantity': 15},
    'קופסת עוגת בנטו עם חלון וידית': {'price': 45, 'quantity': 10},
    'קופסת עוגה 25/20/25 או 20/20/6': {'price': 220, 'quantity': 40},
    'מארז עוגה 25/20/25': {'price': 85, 'quantity': 10},
    'קופסת מקרון 30/5/5': {'price': 70, 'quantity': 20},
    'מארז קאפקייקס 6 תאים מכסה שקוף': {'price': 130, 'quantity': 24},
    'קופסה לעוגיות עם חלון שקוף': {'price': 20, 'quantity': 10},
    'נייר אפייה ריבוע 60*40': {'price': 198, 'quantity': 1000},
    'ניירר אפייה עגול - 20': {'price': 15, 'quantity': 50},
    'נייר אפייה - סופגניות': {'price': 15, 'quantity': 100},
    'נייר אפייה בנטו 18*18': {'price': 15, 'quantity': 50},
    'מסכות': {'price': 15, 'quantity': 10},
}

# Initialize session state
if 'saved_recipes' not in st.session_state:
    st.session_state.saved_recipes = {}

if 'current_recipe' not in st.session_state:
    st.session_state.current_recipe = []

# כותרת
st.markdown("<h1>🎂 תמחור מתכונים</h1>", unsafe_allow_html=True)
st.markdown("<center>© כל הזכויות שמורות לקורל ביטון 2024</center>", unsafe_allow_html=True)
st.markdown("---")

# טאבים
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧮 תמחור",
    "💾 שמורים",
    "🥘 חומרים",
    "📦 אריזות",
    "📥 ייצוא"
])

# טאב 1: תמחור
with tab1:
    # שם המתכון
    recipe_name = st.text_input("📝 שם המתכון", placeholder="עוגת שוקולד")
    
    st.markdown("### הוסף חומרים")
    
    # רשימה משולבת
    all_items = (
        [(f"🥘 {name}", name, 'ing') for name in INGREDIENTS_DB.keys()] +
        [(f"📦 {name}", name, 'pkg') for name in PACKAGING_DB.keys()]
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected = st.selectbox(
            "בחר פריט",
            [""] + [item[0] for item in all_items],
            key="select"
        )
    
    with col2:
        quantity = st.number_input("כמות", min_value=0.0, value=0.0, step=1.0, key="qty")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ הוסף", type="primary"):
            if selected and quantity > 0:
                for display, name, type_ in all_items:
                    if display == selected:
                        st.session_state.current_recipe.append({
                            'name': name,
                            'quantity': quantity,
                            'type': type_
                        })
                        st.success(f"נוסף: {name}")
                        break
    
    with col2:
        if st.button("🗑️ נקה הכל"):
            st.session_state.current_recipe = []
            st.rerun()
    
    # הצגת המתכון
    if st.session_state.current_recipe:
        st.markdown("### 📋 רשימת חומרים")
        
        # הצגת כל פריט עם אפשרות מחיקה
        for i, item in enumerate(st.session_state.current_recipe):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                icon = "🥘" if item['type'] == 'ing' else "📦"
                st.write(f"{icon} {item['name']}")
            with col2:
                st.write(f"{item['quantity']}")
            with col3:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.current_recipe.pop(i)
                    st.rerun()
        
        st.markdown("---")
        
        # חישוב עלויות
        total_ing = 0
        total_pkg = 0
        
        for item in st.session_state.current_recipe:
            if item['type'] == 'ing' and item['name'] in INGREDIENTS_DB:
                ing = INGREDIENTS_DB[item['name']]
                cost = item['quantity'] * (ing['price'] / ing['package'])
                total_ing += cost
            elif item['type'] == 'pkg' and item['name'] in PACKAGING_DB:
                pkg = PACKAGING_DB[item['name']]
                cost = item['quantity'] * (pkg['price'] / pkg['quantity'])
                total_pkg += cost
        
        # הגדרות נוספות
        col1, col2 = st.columns(2)
        with col1:
            hours = st.number_input("⏰ שעות עבודה", value=0.5, step=0.25)
            rate = st.number_input("💰 מחיר לשעה", value=75.0, step=5.0)
        with col2:
            overhead = st.number_input("⚡ תקורות", value=5.0, step=1.0)
            margin = st.slider("📈 רווח %", 20, 50, 35)
        
        labor = hours * rate
        total = total_ing + total_pkg + labor + overhead
        
        # תצוגת עלויות
        st.markdown("### 💰 סיכום עלויות")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("חומרי גלם", f"{total_ing:.2f} ₪")
            st.metric("אריזות", f"{total_pkg:.2f} ₪")
        with col2:
            st.metric("עבודה", f"{labor:.2f} ₪")
            st.metric("תקורות", f"{overhead:.2f} ₪")
        
        st.markdown(f"<div class='price-highlight'>עלות כוללת: {total:.2f} ₪</div>", unsafe_allow_html=True)
        
        # מחירי מכירה
        st.markdown("### 💎 מחירי מכירה")
        
        margins = [25, margin, 40, 50]
        cols = st.columns(len(set(margins)))
        
        for i, m in enumerate(set(margins)):
            with cols[i]:
                price = total * (1 + m/100)
                if m == margin:
                    st.success(f"**{m}%**\n\n**{price:.0f} ₪**")
                else:
                    st.info(f"{m}%\n\n{price:.0f} ₪")
        
        # שמירה
        if recipe_name and st.button("💾 שמור מתכון", type="primary"):
            st.session_state.saved_recipes[recipe_name] = {
                'date': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'recipe': st.session_state.current_recipe.copy(),
                'cost': total,
                'hours': hours,
                'rate': rate,
                'overhead': overhead
            }
            st.success(f"✅ נשמר: {recipe_name}")
            st.balloons()

# טאב 2: מתכונים שמורים
with tab2:
    st.markdown("### 📋 מתכונים שמורים")
    
    if st.session_state.saved_recipes:
        for name, data in st.session_state.saved_recipes.items():
            with st.expander(f"📄 {name} - {data['date']}"):
                st.write(f"**עלות:** {data['cost']:.2f} ₪")
                
                for item in data['recipe']:
                    icon = "🥘" if item['type'] == 'ing' else "📦"
                    st.write(f"{icon} {item['name']}: {item['quantity']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📋 טען", key=f"load_{name}"):
                        st.session_state.current_recipe = data['recipe'].copy()
                        st.success("נטען!")
                with col2:
                    if st.button(f"🗑️ מחק", key=f"delete_{name}"):
                        del st.session_state.saved_recipes[name]
                        st.rerun()
    else:
        st.info("אין מתכונים שמורים")

# טאב 3: חומרי גלם
with tab3:
    st.markdown("### 🥘 רשימת חומרי גלם")
    st.info(f"סה״כ: {len(INGREDIENTS_DB)} חומרים")
    
    search = st.text_input("🔍 חיפוש")
    
    # סינון
    filtered = INGREDIENTS_DB
    if search:
        filtered = {k: v for k, v in INGREDIENTS_DB.items() if search in k}
    
    # הצגה
    data = []
    for name, details in filtered.items():
        unit_price = details['price'] / details['package']
        data.append({
            'שם': name,
            'מחיר': f"{details['price']} ₪",
            'אריזה': f"{details['package']} {details['unit']}",
            'ליחידה': f"{unit_price:.4f} ₪"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# טאב 4: אריזות
with tab4:
    st.markdown("### 📦 רשימת אריזות")
    st.info(f"סה״כ: {len(PACKAGING_DB)} אריזות")
    
    data = []
    for name, details in PACKAGING_DB.items():
        unit_price = details['price'] / details['quantity']
        data.append({
            'שם': name,
            'מחיר': f"{details['price']} ₪",
            'כמות': details['quantity'],
            'ליחידה': f"{unit_price:.2f} ₪"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# טאב 5: ייצוא
with tab5:
    st.markdown("### 📥 ייצוא לאקסל")
    
    if st.button("💾 הורד הכל לאקסל", type="primary"):
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # חומרי גלם
            df_ing = pd.DataFrame.from_dict(INGREDIENTS_DB, orient='index')
            df_ing.to_excel(writer, sheet_name='חומרי גלם')
            
            # אריזות
            df_pkg = pd.DataFrame.from_dict(PACKAGING_DB, orient='index')
            df_pkg.to_excel(writer, sheet_name='אריזות')
            
            # מתכונים שמורים
            if st.session_state.saved_recipes:
                recipes_data = []
                for name, data in st.session_state.saved_recipes.items():
                    recipes_data.append({
                        'שם': name,
                        'תאריך': data['date'],
                        'עלות': data['cost']
                    })
                df_saved = pd.DataFrame(recipes_data)
                df_saved.to_excel(writer, sheet_name='מתכונים', index=False)
        
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="תמחור_{datetime.now().strftime("%Y%m%d")}.xlsx">📥 לחץ להורדה</a>'
        st.markdown(href, unsafe_allow_html=True)

# פוטר
st.markdown("---")
st.markdown("""
<center>
© 2024 כל הזכויות שמורות לקורל ביטון<br>
אין להעתיק או להפיץ ללא אישור
</center>
""", unsafe_allow_html=True)
