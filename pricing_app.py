"""
מערכת תמחור מתכונים - קורל ביטון
© 2024 כל הזכויות שמורות
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64
import json
import os

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
    
    h1 {
        text-align: center;
        font-size: 24px;
        color: #2C3E50;
        margin: 10px 0;
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
    
    .ingredient-row {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    
    .success-message {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# נתיב לקובץ השמירה
RECIPES_FILE = "saved_recipes.json"
CUSTOM_ITEMS_FILE = "custom_items.json"

# פונקציות לשמירה וטעינה
def save_recipes(recipes):
    """שומר מתכונים לקובץ JSON"""
    try:
        with open(RECIPES_FILE, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"שגיאה בשמירה: {e}")
        return False

def load_recipes():
    """טוען מתכונים מקובץ JSON"""
    if os.path.exists(RECIPES_FILE):
        try:
            with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_custom_items(ingredients, packaging):
    """שומר פריטים מותאמים אישית"""
    try:
        data = {
            'ingredients': ingredients,
            'packaging': packaging
        }
        with open(CUSTOM_ITEMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_custom_items():
    """טוען פריטים מותאמים אישית"""
    if os.path.exists(CUSTOM_ITEMS_FILE):
        try:
            with open(CUSTOM_ITEMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('ingredients', {}), data.get('packaging', {})
        except:
            return {}, {}
    return {}, {}

# מאגר חומרי גלם - כל 102 הפריטים מהאקסל
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
    'קינדר בואנו': {'price': 12.9, 'package': 6, 'unit': 'יחידות'},
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
    'תמצית וניל': {'price': 4.9, 'package': 50, 'unit': 'מ״ל'},
    'אבקת אפייה': {'price': 1.9, 'package': 100, 'unit': 'גרם'},
    'סוכר וניל': {'price': 1.9, 'package': 100, 'unit': 'גרם'},
    'אבקת סוכר': {'price': 10.0, 'package': 1000, 'unit': 'גרם'},
    'סודה לשתייה': {'price': 4.7, 'package': 80, 'unit': 'גרם'},
    'גלידן': {'price': 100.0, 'package': 5000, 'unit': 'גרם'},
    'שמנת צמחית 21%': {'price': 8.2, 'package': 250, 'unit': 'גרם'},
    'איסטנט פודינג': {'price': 20.0, 'package': 1000, 'unit': 'גרם'},
    'שמן': {'price': 14.9, 'package': 1000, 'unit': 'מ״ל'},
    'שוקולד צ׳יפס לבן': {'price': 11.9, 'package': 260, 'unit': 'גרם'},
    'שוקולד צ׳יפס חום': {'price': 11.9, 'package': 260, 'unit': 'גרם'},
    'חלב רגיל 3%': {'price': 6.81, 'package': 1000, 'unit': 'מ״ל'},
    'חלב נטול לקטוז': {'price': 8.9, 'package': 1000, 'unit': 'מ״ל'},
    'חלב סויה': {'price': 11.9, 'package': 1000, 'unit': 'מ״ל'},
    'קרם קוקוס': {'price': 7.9, 'package': 400, 'unit': 'גרם'},
    'שמרים יבשים': {'price': 6.9, 'package': 500, 'unit': 'גרם'},
    'שמרים טריים': {'price': 3.6, 'package': 50, 'unit': 'גרם'},
    'שמרים טריים ומשפר אפייה': {'price': 8.9, 'package': 100, 'unit': 'גרם'},
    'חמאה תנובה': {'price': 9.0, 'package': 200, 'unit': 'גרם'},
    'חמאה מפינלנד': {'price': 13.9, 'package': 200, 'unit': 'גרם'},
    'אצבעות קינדר': {'price': 14.9, 'package': 16, 'unit': 'יחידות'},
    'ממרח קינדר': {'price': 16.9, 'package': 300, 'unit': 'גרם'},
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
    'חלב מרוכז': {'price': 9.9, 'package': 397, 'unit': 'מ״ל'},
    'חומץ': {'price': 6.9, 'package': 1000, 'unit': 'מ״ל'},
    'כללי קטן': {'price': 15.0, 'package': 1, 'unit': 'יחידות'},
    'כללי בינוני': {'price': 20.0, 'package': 1, 'unit': 'יחידות'},
    'כללי גדול': {'price': 30.0, 'package': 1, 'unit': 'יחידות'},
    'שוקולית': {'price': 12.0, 'package': 400, 'unit': 'גרם'},
    'ריבת חלב קומידה': {'price': 15.9, 'package': 500, 'unit': 'גרם'},
    'אגוזי לוז קצוצים': {'price': 59.9, 'package': 1000, 'unit': 'גרם'},
    'דפי טרנספר': {'price': 25.0, 'package': 1, 'unit': 'יחידות'},
}

# מאגר אריזות - כל 35 הפריטים מהאקסל
PACKAGING_DB = {
    'קופסאות 40/30/8': {'price': 80, 'package': 10, 'unit': 'יחידות'},
    'קופסא לאינגליש מכסה גבוה': {'price': 45, 'package': 10, 'unit': 'יחידות'},
    'קופסא מלבנית מחולקת 20/11/5': {'price': 45, 'package': 10, 'unit': 'יחידות'},
    'חלוקה פנימית לקופסא 20/20/5': {'price': 20, 'package': 10, 'unit': 'יחידות'},
    'קופסא ל6 קאפקייקס כולל במה': {'price': 65, 'package': 10, 'unit': 'יחידות'},
    'קופסא 30/30/11 כולל תחתית פנימית': {'price': 80, 'package': 10, 'unit': 'יחידות'},
    'מנג׳טים לקאפקייקס צבעים -קוטר 7': {'price': 10, 'package': 40, 'unit': 'יחידות'},
    'קריסטליות עיגול - 10 ס״מ': {'price': 25, 'package': 10, 'unit': 'יחידות'},
    'קריסטליות עיגול - 16 ס״מ': {'price': 115, 'package': 50, 'unit': 'יחידות'},
    'קופסא 24/24/13': {'price': 45, 'package': 5, 'unit': 'יחידות'},
    'קופסא 25/35/7 עם מכסה גבוה 8.5 ס״מ': {'price': 45, 'package': 10, 'unit': 'יחידות'},
    'קופסא 25/35/7 עם מכסה גבוה + 5 במות 20 קינוחים': {'price': 40, 'package': 5, 'unit': 'יחידות'},
    'מארז 20/20/5': {'price': 100, 'package': 20, 'unit': 'יחידות'},
    'מארז חלוקה מכסה': {'price': 50, 'package': 10, 'unit': 'יחידות'},
    'כיבודיות': {'price': 110, 'package': 100, 'unit': 'יחידות'},
    'ברולה -לב אישי': {'price': 110, 'package': 100, 'unit': 'יחידות'},
    'קריסטל לב קוטר 16': {'price': 105, 'package': 30, 'unit': 'יחידות'},
    'קרטון בנטו': {'price': 55, 'package': 50, 'unit': 'יחידות'},
    'אלומיניום מיני אינגליש קייק ומכסה 16/6': {'price': 85, 'package': 50, 'unit': 'יחידות'},
    'קריסטליות פלסטיק למארז+מכסה 16': {'price': 40, 'package': 10, 'unit': 'יחידות'},
    'קופסת פרלינים 16 תאים': {'price': 65, 'package': 20, 'unit': 'יחידות'},
    'קופסת קאפקייקס 4 תאים': {'price': 150, 'package': 50, 'unit': 'יחידות'},
    'מיכל פרוסת עוגה זהב בודד': {'price': 30, 'package': 50, 'unit': 'יחידות'},
    'קופסת קאפקייקס 6 תאים': {'price': 75, 'package': 15, 'unit': 'יחידות'},
    'קופסת עוגת בנטו עם חלון וידית': {'price': 45, 'package': 10, 'unit': 'יחידות'},
    'קופסת עוגה 25/20/25 או 20/20/6': {'price': 220, 'package': 40, 'unit': 'יחידות'},
    'מארז עוגה 25/20/25': {'price': 85, 'package': 10, 'unit': 'יחידות'},
    'קופסת מקרון 30/5/5': {'price': 70, 'package': 20, 'unit': 'יחידות'},
    'מארז קאפקייקס 6 תאים מכסה שקוף': {'price': 130, 'package': 24, 'unit': 'יחידות'},
    'קופסה לעוגיות עם חלון שקוף': {'price': 20, 'package': 10, 'unit': 'יחידות'},
    'נייר אפייה ריבוע 60*40': {'price': 198, 'package': 1000, 'unit': 'יחידות'},
    'ניירר אפייה עגול - 20': {'price': 15, 'package': 50, 'unit': 'יחידות'},
    'נייר אפייה - סופגניות': {'price': 15, 'package': 100, 'unit': 'יחידות'},
    'נייר אפייה בנטו 18*18': {'price': 15, 'package': 50, 'unit': 'יחידות'},
    'מסכות': {'price': 15, 'package': 10, 'unit': 'יחידות'},
}

# Initialize session state
if 'num_ingredients' not in st.session_state:
    st.session_state.num_ingredients = 5

if 'num_packaging' not in st.session_state:
    st.session_state.num_packaging = 2

# טעינת נתונים שמורים
if 'saved_recipes' not in st.session_state:
    st.session_state.saved_recipes = load_recipes()

if 'custom_ingredients' not in st.session_state:
    ingredients, packaging = load_custom_items()
    st.session_state.custom_ingredients = ingredients
    st.session_state.custom_packaging = packaging

# כותרת
st.markdown("<h1>🎂 תמחור מתכונים</h1>", unsafe_allow_html=True)
st.markdown("<center>© כל הזכויות שמורות לקורל ביטון 2024</center>", unsafe_allow_html=True)
st.markdown("---")

# הודעת מצב שמירה
if os.path.exists(RECIPES_FILE):
    st.success(f"✅ נטענו {len(st.session_state.saved_recipes)} מתכונים שמורים")

# טאבים
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧮 תמחור",
    "💾 שמורים",
    "🥘 חומרים",
    "📦 אריזות",
    "➕ הוספה",
    "📥 ייצוא"
])

# טאב 1: תמחור
with tab1:
    # שם המתכון
    recipe_name = st.text_input("📝 שם המתכון", placeholder="עוגת שוקולד")
    
    # איחוד כל המאגרים
    all_ingredients = {**INGREDIENTS_DB, **st.session_state.custom_ingredients}
    all_packaging = {**PACKAGING_DB, **st.session_state.custom_packaging}
    
    st.markdown("### 🥘 חומרי גלם")
    
    # בחירת מספר חומרי גלם
    col1, col2 = st.columns([1, 3])
    with col1:
        st.session_state.num_ingredients = st.number_input(
            "כמה חומרים?",
            min_value=1,
            max_value=30,
            value=st.session_state.num_ingredients,
            step=1
        )
    
    # רשימת חומרי גלם
    ingredients_list = []
    st.markdown("#### הוסף חומרי גלם:")
    
    for i in range(st.session_state.num_ingredients):
        st.markdown(f"<div class='ingredient-row'>", unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            ingredient = st.selectbox(
                f"חומר {i+1}",
                [""] + sorted(list(all_ingredients.keys())),
                key=f"ing_{i}"
            )
        
        with col2:
            quantity = st.number_input(
                "כמות",
                min_value=0.0,
                value=0.0,
                step=1.0,
                key=f"ing_qty_{i}"
            )
        
        if ingredient and quantity > 0:
            ingredients_list.append({
                'name': ingredient,
                'quantity': quantity,
                'type': 'ingredient',
                'details': all_ingredients[ingredient]
            })
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📦 אריזות")
    
    # בחירת מספר אריזות
    col1, col2 = st.columns([1, 3])
    with col1:
        st.session_state.num_packaging = st.number_input(
            "כמה אריזות?",
            min_value=0,
            max_value=10,
            value=st.session_state.num_packaging,
            step=1
        )
    
    # רשימת אריזות
    packaging_list = []
    if st.session_state.num_packaging > 0:
        st.markdown("#### הוסף אריזות:")
        
        for i in range(st.session_state.num_packaging):
            st.markdown(f"<div class='ingredient-row'>", unsafe_allow_html=True)
            col1, col2 = st.columns([2, 1])
            
            with col1:
                package = st.selectbox(
                    f"אריזה {i+1}",
                    [""] + sorted(list(all_packaging.keys())),
                    key=f"pkg_{i}"
                )
            
            with col2:
                quantity = st.number_input(
                    "כמות",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key=f"pkg_qty_{i}"
                )
            
            if package and quantity > 0:
                packaging_list.append({
                    'name': package,
                    'quantity': quantity,
                    'type': 'packaging',
                    'details': all_packaging[package]
                })
            st.markdown("</div>", unsafe_allow_html=True)
    
    # איחוד הרשימות
    all_items = ingredients_list + packaging_list
    
    if all_items:
        st.markdown("---")
        st.markdown("### 💰 חישוב עלויות")
        
        # חישוב עלויות
        total_ingredients = 0
        total_packaging = 0
        items_breakdown = []
        
        for item in all_items:
            unit_price = item['details']['price'] / item['details']['package']
            item_cost = item['quantity'] * unit_price
            
            if item['type'] == 'ingredient':
                total_ingredients += item_cost
            else:
                total_packaging += item_cost
            
            items_breakdown.append({
                'פריט': item['name'],
                'כמות': f"{item['quantity']} {item['details'].get('unit', 'יח׳')}",
                'עלות': f"{item_cost:.2f} ₪"
            })
        
        # הצגת פירוט
        st.markdown("#### 📊 פירוט עלויות")
        df_breakdown = pd.DataFrame(items_breakdown)
        st.dataframe(df_breakdown, use_container_width=True, hide_index=True)
        
        # הגדרות נוספות
        st.markdown("#### ⚙️ הגדרות נוספות")
        col1, col2 = st.columns(2)
        with col1:
            hours = st.number_input("⏰ שעות עבודה", value=0.5, step=0.25)
            rate = st.number_input("💰 מחיר לשעה", value=75.0, step=5.0)
        with col2:
            overhead = st.number_input("⚡ תקורות", value=5.0, step=1.0)
            margin = st.slider("📈 רווח %", 20, 50, 35)
        
        labor_cost = hours * rate
        total_cost = total_ingredients + total_packaging + labor_cost + overhead
        
        # תצוגת סיכום
        st.markdown("#### 📈 סיכום")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("חומרי גלם", f"{total_ingredients:.2f} ₪")
            st.metric("אריזות", f"{total_packaging:.2f} ₪")
        with col2:
            st.metric("עבודה", f"{labor_cost:.2f} ₪")
            st.metric("תקורות", f"{overhead:.2f} ₪")
        
        st.markdown(f"<div class='price-highlight'>עלות כוללת: {total_cost:.2f} ₪</div>", unsafe_allow_html=True)
        
        # מחיר מכירה
        selling_price = total_cost * (1 + margin/100)
        profit = selling_price - total_cost
        
        st.success(f"""
        ### מחיר מכירה מומלץ ({margin}%)
        # {selling_price:.0f} ₪
        **רווח: {profit:.0f} ₪**
        """)
        
        # שמירה
        if recipe_name:
            if st.button("💾 שמור מתכון", type="primary"):
                # יצירת מפתח ייחודי למתכון
                recipe_key = f"{recipe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # שמירה למילון
                st.session_state.saved_recipes[recipe_key] = {
                    'name': recipe_name,
                    'date': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'items': all_items,
                    'breakdown': items_breakdown,
                    'costs': {
                        'ingredients': total_ingredients,
                        'packaging': total_packaging,
                        'labor': labor_cost,
                        'overhead': overhead,
                        'total': total_cost
                    },
                    'pricing': {
                        'margin': margin,
                        'selling_price': selling_price,
                        'profit': profit
                    }
                }
                
                # שמירה לקובץ
                if save_recipes(st.session_state.saved_recipes):
                    st.markdown(f"""
                    <div class='success-message'>
                    ✅ המתכון "{recipe_name}" נשמר בהצלחה!<br>
                    📁 השמירה קבועה ותישאר גם אחרי יציאה מהאפליקציה
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.error("❌ שגיאה בשמירת המתכון")
        else:
            st.warning("⚠️ הכנס שם למתכון כדי לשמור")

# טאב 2: מתכונים שמורים
with tab2:
    st.markdown("### 📋 מתכונים שמורים")
    st.info(f"💾 סה״כ {len(st.session_state.saved_recipes)} מתכונים שמורים בקובץ")
    
    if st.session_state.saved_recipes:
        # סידור לפי תאריך
        sorted_recipes = sorted(st.session_state.saved_recipes.items(), 
                               key=lambda x: x[1].get('date', ''), 
                               reverse=True)
        
        for key, data in sorted_recipes:
            recipe_name = data.get('name', key.split('_')[0])
            with st.expander(f"📄 {recipe_name} - {data['date']}"):
                # פירוט פריטים
                st.markdown("**פריטים:**")
                for item in data['items']:
                    icon = "🥘" if item['type'] == 'ingredient' else "📦"
                    unit = item['details'].get('unit', 'יח׳')
                    st.write(f"{icon} {item['name']}: {item['quantity']} {unit}")
                
                # עלויות
                st.markdown("---")
                costs = data['costs']
                st.write(f"חומרי גלם: {costs['ingredients']:.2f} ₪")
                st.write(f"אריזות: {costs['packaging']:.2f} ₪")
                st.write(f"עבודה: {costs['labor']:.2f} ₪")
                st.write(f"תקורות: {costs['overhead']:.2f} ₪")
                st.success(f"**עלות כוללת: {costs['total']:.2f} ₪**")
                
                # תמחור
                pricing = data['pricing']
                st.info(f"""
                **מחיר מכירה ({pricing['margin']}%): {pricing['selling_price']:.0f} ₪**
                **רווח: {pricing['profit']:.0f} ₪**
                """)
                
                # מחיקה
                if st.button(f"🗑️ מחק", key=f"del_{key}"):
                    del st.session_state.saved_recipes[key]
                    save_recipes(st.session_state.saved_recipes)
                    st.rerun()
    else:
        st.info("אין מתכונים שמורים")

# טאב 3: חומרי גלם
with tab3:
    st.markdown("### 🥘 רשימת חומרי גלם")
    
    all_ing = {**INGREDIENTS_DB, **st.session_state.custom_ingredients}
    st.info(f"סה״כ: {len(all_ing)} חומרים")
    
    search = st.text_input("🔍 חיפוש")
    
    filtered = all_ing
    if search:
        filtered = {k: v for k, v in all_ing.items() if search.lower() in k.lower()}
    
    if filtered:
        data_list = []
        for name, details in filtered.items():
            unit_price = details['price'] / details['package']
            data_list.append({
                'שם': name,
                'מחיר': f"{details['price']} ₪",
                'אריזה': f"{details['package']} {details['unit']}",
                'ליחידה': f"{unit_price:.4f} ₪"
            })
        
        df = pd.DataFrame(data_list)
        st.dataframe(df, use_container_width=True, hide_index=True)

# טאב 4: אריזות
with tab4:
    st.markdown("### 📦 רשימת אריזות")
    
    all_pkg = {**PACKAGING_DB, **st.session_state.custom_packaging}
    st.info(f"סה״כ: {len(all_pkg)} אריזות")
    
    data_list = []
    for name, details in all_pkg.items():
        unit_price = details['price'] / details['package']
        data_list.append({
            'שם': name,
            'מחיר חבילה': f"{details['price']} ₪",
            'כמות': details['package'],
            'ליחידה': f"{unit_price:.2f} ₪"
        })
    
    df = pd.DataFrame(data_list)
    st.dataframe(df, use_container_width=True, hide_index=True)

# טאב 5: הוספת פריטים חדשים
with tab5:
    st.markdown("### ➕ הוספת פריט חדש למאגר")
    
    add_type = st.radio("סוג:", ["חומר גלם", "אריזה"])
    
    new_name = st.text_input("שם הפריט:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        new_price = st.number_input("מחיר:", min_value=0.0, step=0.5)
    with col2:
        new_package = st.number_input("כמות באריזה:", min_value=1.0, step=1.0)
    with col3:
        if add_type == "חומר גלם":
            new_unit = st.selectbox("יחידה:", ["גרם", "מ״ל", "יחידות"])
        else:
            new_unit = "יחידות"
            st.write("יחידה: יחידות")
    
    if st.button("💾 הוסף למאגר", type="primary"):
        if new_name and new_price > 0:
            new_item = {
                'price': new_price,
                'package': new_package,
                'unit': new_unit
            }
            
            if add_type == "חומר גלם":
                st.session_state.custom_ingredients[new_name] = new_item
                success_msg = f"✅ נוסף חומר גלם: {new_name}"
            else:
                st.session_state.custom_packaging[new_name] = new_item
                success_msg = f"✅ נוספה אריזה: {new_name}"
            
            # שמירה לקובץ
            if save_custom_items(st.session_state.custom_ingredients, 
                               st.session_state.custom_packaging):
                st.success(success_msg)
                st.info("💾 השינויים נשמרו לקובץ")
                st.balloons()
            else:
                st.error("שגיאה בשמירה")

# טאב 6: ייצוא
with tab6:
    st.markdown("### 📥 ייצוא לאקסל")
    
    if st.button("💾 הכן קובץ אקסל", type="primary"):
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # חומרי גלם
            all_ing = {**INGREDIENTS_DB, **st.session_state.custom_ingredients}
            df_ing = pd.DataFrame.from_dict(all_ing, orient='index')
            df_ing.to_excel(writer, sheet_name='חומרי גלם')
            
            # אריזות
            all_pkg = {**PACKAGING_DB, **st.session_state.custom_packaging}
            df_pkg = pd.DataFrame.from_dict(all_pkg, orient='index')
            df_pkg.to_excel(writer, sheet_name='אריזות')
            
            # מתכונים
            if st.session_state.saved_recipes:
                recipes_data = []
                for key, data in st.session_state.saved_recipes.items():
                    recipes_data.append({
                        'שם': data.get('name', key.split('_')[0]),
                        'תאריך': data['date'],
                        'עלות': data['costs']['total'],
                        'מחיר מכירה': data['pricing']['selling_price'],
                        'רווח': data['pricing']['profit']
                    })
                df_recipes = pd.DataFrame(recipes_data)
                df_recipes.to_excel(writer, sheet_name='מתכונים', index=False)
        
        output.seek(0)
        
        st.download_button(
            label="📥 הורד קובץ אקסל",
            data=output.getvalue(),
            file_name=f"תמחור_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("✅ הקובץ מוכן להורדה!")
    
    # כפתור גיבוי
    st.markdown("---")
    st.markdown("### 🔒 גיבוי וטעינה")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 הורד גיבוי JSON"):
            backup_data = {
                'recipes': st.session_state.saved_recipes,
                'custom_ingredients': st.session_state.custom_ingredients,
                'custom_packaging': st.session_state.custom_packaging
            }
            
            backup_json = json.dumps(backup_data, ensure_ascii=False, indent=2)
            
            st.download_button(
                label="💾 הורד קובץ גיבוי",
                data=backup_json,
                file_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_file = st.file_uploader("📥 טען גיבוי", type="json")
        if uploaded_file is not None:
            try:
                backup_data = json.load(uploaded_file)
                st.session_state.saved_recipes = backup_data.get('recipes', {})
                st.session_state.custom_ingredients = backup_data.get('custom_ingredients', {})
                st.session_state.custom_packaging = backup_data.get('custom_packaging', {})
                
                save_recipes(st.session_state.saved_recipes)
                save_custom_items(st.session_state.custom_ingredients, 
                                st.session_state.custom_packaging)
                
                st.success("✅ הגיבוי נטען בהצלחה!")
                st.rerun()
            except Exception as e:
                st.error(f"שגיאה בטעינת הגיבוי: {e}")

# פוטר
st.markdown("---")
st.markdown("""
<center>
<strong>© 2024 כל הזכויות שמורות לקורל ביטון</strong><br>
אין להעתיק או להפיץ ללא אישור<br>
<small>גרסה 2.0 - שמירה קבועה</small>
</center>
""", unsafe_allow_html=True)
