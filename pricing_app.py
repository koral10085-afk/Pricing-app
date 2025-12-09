"""
🎂 מערכת תמחור מתכונים מקצועית
© 2024 כל הזכויות שמורות לקורל ביטון
אין להעתיק, להפיץ או לעשות כל שימוש ללא אישור בכתב
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
import base64
import io
import openpyxl

# הגדרות אפליקציה
st.set_page_config(
    page_title="תמחור מתכונים - קורל ביטון",
    page_icon="🎂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS מותאם למובייל ועברית
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;700&display=swap');
    
    /* RTL וגופן עברי */
    .stApp {
        direction: rtl !important;
        font-family: 'Assistant', sans-serif !important;
    }
    
    /* כפתורים */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 8px 16px;
        font-weight: bold;
        border: none;
    }
    
    /* כותרות */
    h1, h2, h3 {
        text-align: center;
        direction: rtl;
    }
    
    /* טבלאות */
    .dataframe {
        direction: rtl;
        text-align: right;
    }
    
    /* תיבות תוצאה */
    .result-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-right: 4px solid #667eea;
    }
    
    /* זכויות יוצרים */
    .copyright {
        text-align: center;
        color: #666;
        font-size: 12px;
        margin-top: 20px;
        padding: 10px;
        background: #f0f0f0;
        border-radius: 5px;
    }
    
    /* הסתרת אלמנטים */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# אתחול Session State
if 'recipes_db' not in st.session_state:
    st.session_state.recipes_db = {}

if 'current_recipe' not in st.session_state:
    st.session_state.current_recipe = []

if 'saved_recipes' not in st.session_state:
    st.session_state.saved_recipes = {}

# פונקציה לטעינת נתוני האקסל
@st.cache_data
def load_excel_data():
    """טעינת כל הנתונים מקובץ האקסל"""
    try:
        # נסה לטעון מהקובץ המקורי
        excel_path = 'חישוב_עלויות_-_מחירון_עדכני.xlsx'
        if not os.path.exists(excel_path):
            # אם לא קיים, נסה מהתיקייה
            excel_path = '/mnt/user-data/uploads/חישוב_עלויות_-_מחירון_עדכני.xlsx'
        
        if not os.path.exists(excel_path):
            # יצירת נתוני ברירת מחדל
            return create_default_data()
        
        # טעינת כל הגיליונות
        all_sheets = pd.read_excel(excel_path, sheet_name=None)
        
        # עיבוד חומרי גלם
        ingredients = {}
        if 'חומרי גלם' in all_sheets:
            df = all_sheets['חומרי גלם'].dropna(subset=['חומר גלם'])
            for _, row in df.iterrows():
                name = row['חומר גלם']
                ingredients[name] = {
                    'price': row.get('עלות רכישה', 0),
                    'package': row.get('כמות באריזה', 1),
                    'unit': row.get('יחידת מידה', 'יחידה')
                }
        
        # עיבוד אריזות
        packaging = {}
        if 'אריזות' in all_sheets:
            df = all_sheets['אריזות'].dropna(subset=['מוצר'])
            for _, row in df.iterrows():
                name = row['מוצר']
                packaging[name] = {
                    'price': row.get('עלות', 0),
                    'quantity': row.get('כמות באריזה', 1),
                    'source': row.get('מאיפה נקנה', '')
                }
        
        # עיבוד מוצרים
        products = {}
        if 'מוצרים' in all_sheets:
            df = all_sheets['מוצרים'].dropna(subset=['מוצר'])
            for _, row in df.iterrows():
                name = row['מוצר']
                products[name] = row.get('עלות ליחידה', 0)
        
        # עיבוד מתכונים קיימים
        recipes = {}
        for sheet_name in all_sheets:
            if sheet_name not in ['ראשי', 'חומרי גלם', 'אריזות', 'מוצרים', 'עלות ליחידה']:
                df = all_sheets[sheet_name]
                if 'מרכיבים' in df.columns or 'מוצרים' in df.columns:
                    recipes[sheet_name] = df
        
        return {
            'ingredients': ingredients,
            'packaging': packaging,
            'products': products,
            'recipes': recipes
        }
        
    except Exception as e:
        st.error(f"שגיאה בטעינת הקובץ: {e}")
        return create_default_data()

def create_default_data():
    """יצירת נתוני ברירת מחדל"""
    return {
        'ingredients': {
            'קמח': {'price': 8.5, 'package': 1000, 'unit': 'גרם'},
            'סוכר': {'price': 5.2, 'package': 1000, 'unit': 'גרם'},
            'ביצים': {'price': 14, 'package': 12, 'unit': 'יחידות'},
            'חמאה': {'price': 9, 'package': 200, 'unit': 'גרם'},
            'שמן': {'price': 14.9, 'package': 1000, 'unit': 'מ״ל'}
        },
        'packaging': {
            'קופסא קטנה': {'price': 2, 'quantity': 1, 'source': 'חנות'},
            'קופסא גדולה': {'price': 5, 'quantity': 1, 'source': 'חנות'}
        },
        'products': {
            'עוגיות': 5.5,
            'עוגה': 35
        },
        'recipes': {}
    }

# טעינת הנתונים
data = load_excel_data()

# כותרת ראשית
st.markdown("# 🎂 מערכת תמחור מתכונים מקצועית")
st.markdown("### © כל הזכויות שמורות לקורל ביטון 2024")
st.markdown("---")

# סרגל צד
with st.sidebar:
    st.markdown("### ⚙️ הגדרות")
    
    labor_rate = st.number_input("💰 מחיר שעת עבודה", value=75.0, step=5.0)
    default_margin = st.slider("📈 רווח מומלץ %", 20, 50, 35)
    
    st.markdown("---")
    st.markdown("### 📊 סטטיסטיקות")
    st.info(f"חומרי גלם: {len(data['ingredients'])}")
    st.info(f"אריזות: {len(data['packaging'])}")
    st.info(f"מוצרים: {len(data['products'])}")
    st.info(f"מתכונים: {len(data['recipes'])}")
    
    st.markdown("---")
    st.markdown("### 💾 ייצוא נתונים")
    if st.button("📥 הורד הכל לאקסל"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # חומרי גלם
            df_ing = pd.DataFrame.from_dict(data['ingredients'], orient='index')
            df_ing.to_excel(writer, sheet_name='חומרי גלם')
            
            # אריזות
            df_pack = pd.DataFrame.from_dict(data['packaging'], orient='index')
            df_pack.to_excel(writer, sheet_name='אריזות')
            
            # מוצרים
            df_prod = pd.DataFrame.from_dict(data['products'], orient='index', columns=['מחיר'])
            df_prod.to_excel(writer, sheet_name='מוצרים')
            
            # מתכונים שמורים
            if st.session_state.saved_recipes:
                df_saved = pd.DataFrame.from_dict(st.session_state.saved_recipes, orient='index')
                df_saved.to_excel(writer, sheet_name='מתכונים שמורים')
        
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="תמחור_מתכונים.xlsx">📥 לחץ להורדה</a>'
        st.markdown(href, unsafe_allow_html=True)

# טאבים
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧮 תמחור חדש",
    "📋 מתכונים שמורים",
    "🥘 חומרי גלם",
    "📦 אריזות",
    "🛍️ מוצרים",
    "📊 מתכונים מהאקסל"
])

# טאב 1: תמחור חדש
with tab1:
    st.markdown("## 🆕 יצירת תמחור חדש")
    
    # שם המתכון
    recipe_name = st.text_input("📝 שם המתכון", placeholder="עוגת שוקולד מושלמת")
    
    # הוספת חומרים
    st.markdown("### הוספת חומרים")
    
    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
    
    with col1:
        # רשימה משולבת של כל הפריטים
        all_items = list(data['ingredients'].keys()) + list(data['packaging'].keys())
        selected = st.selectbox(
            "בחר פריט",
            [""] + sorted(all_items),
            key="select_item"
        )
    
    with col2:
        quantity = st.number_input("כמות", min_value=0.0, step=1.0, key="qty")
    
    with col3:
        st.write("")
        st.write("")
        if st.button("➕ הוסף"):
            if selected and quantity > 0:
                st.session_state.current_recipe.append({
                    'name': selected,
                    'quantity': quantity,
                    'type': 'ingredient' if selected in data['ingredients'] else 'packaging'
                })
    
    with col4:
        st.write("")
        st.write("")
        if st.button("🗑️ נקה"):
            st.session_state.current_recipe = []
    
    # הצגת המתכון הנוכחי
    if st.session_state.current_recipe:
        st.markdown("### 📝 פירוט המתכון")
        
        total_ingredients = 0
        total_packaging = 0
        details = []
        
        for i, item in enumerate(st.session_state.current_recipe):
            if item['type'] == 'ingredient' and item['name'] in data['ingredients']:
                ing = data['ingredients'][item['name']]
                unit_price = ing['price'] / ing['package']
                cost = item['quantity'] * unit_price
                total_ingredients += cost
                
                details.append({
                    'סוג': '🥘',
                    'פריט': item['name'],
                    'כמות': f"{item['quantity']} {ing['unit']}",
                    'עלות': f"{cost:.2f} ₪"
                })
                
            elif item['type'] == 'packaging' and item['name'] in data['packaging']:
                pack = data['packaging'][item['name']]
                cost = item['quantity'] * pack['price']
                total_packaging += cost
                
                details.append({
                    'סוג': '📦',
                    'פריט': item['name'],
                    'כמות': f"{item['quantity']} יח'",
                    'עלות': f"{cost:.2f} ₪"
                })
        
        # טבלה
        if details:
            df = pd.DataFrame(details)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # חישוב עלויות
        st.markdown("### 💰 חישוב עלויות")
        
        col1, col2 = st.columns(2)
        
        with col1:
            labor_hours = st.number_input("⏰ שעות עבודה", value=0.5, step=0.25)
            overhead = st.number_input("⚡ תקורות", value=5.0, step=1.0)
        
        with col2:
            labor_cost = labor_hours * labor_rate
            total_cost = total_ingredients + total_packaging + labor_cost + overhead
            
            st.metric("חומרי גלם", f"{total_ingredients:.2f} ₪")
            st.metric("אריזות", f"{total_packaging:.2f} ₪")
            st.metric("עבודה", f"{labor_cost:.2f} ₪")
            st.metric("תקורות", f"{overhead:.2f} ₪")
        
        # סיכום
        st.markdown("---")
        st.markdown(f"### 🎯 עלות כוללת: {total_cost:.2f} ₪")
        
        # מחירי מכירה
        st.markdown("### 💎 המלצות מחיר מכירה")
        
        margins = [25, default_margin, 40, 50]
        cols = st.columns(len(margins))
        
        for i, margin in enumerate(margins):
            with cols[i]:
                price = total_cost * (1 + margin/100)
                profit = price - total_cost
                
                if margin == default_margin:
                    st.success(f"**מומלץ**\n\n**{margin}%**\n\n{price:.0f} ₪\n\nרווח: {profit:.0f} ₪")
                else:
                    st.info(f"{margin}%\n\n{price:.0f} ₪\n\nרווח: {profit:.0f} ₪")
        
        # שמירה
        st.markdown("---")
        if recipe_name:
            if st.button("💾 שמור מתכון", type="primary"):
                st.session_state.saved_recipes[recipe_name] = {
                    'date': datetime.now().strftime("%d/%m/%Y %H:%M"),
                    'recipe': st.session_state.current_recipe,
                    'cost': total_cost,
                    'details': details,
                    'labor_hours': labor_hours,
                    'overhead': overhead
                }
                st.success(f"✅ המתכון '{recipe_name}' נשמר בהצלחה!")
                st.balloons()
        else:
            st.warning("⚠️ הכנס שם למתכון כדי לשמור")

# טאב 2: מתכונים שמורים
with tab2:
    st.markdown("## 📋 המתכונים השמורים שלך")
    
    if st.session_state.saved_recipes:
        for name, recipe_data in st.session_state.saved_recipes.items():
            with st.expander(f"📄 {name} - {recipe_data['date']}"):
                st.write(f"**עלות כוללת:** {recipe_data['cost']:.2f} ₪")
                
                if 'details' in recipe_data:
                    df = pd.DataFrame(recipe_data['details'])
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✏️ ערוך", key=f"edit_{name}"):
                        st.session_state.current_recipe = recipe_data['recipe']
                        st.info("המתכון נטען לעריכה")
                
                with col2:
                    if st.button(f"🗑️ מחק", key=f"del_{name}"):
                        del st.session_state.saved_recipes[name]
                        st.rerun()
    else:
        st.info("אין מתכונים שמורים עדיין")

# טאב 3: חומרי גלם
with tab3:
    st.markdown("## 🥘 רשימת חומרי גלם")
    
    # חיפוש
    search = st.text_input("🔍 חיפוש חומר גלם")
    
    # סינון
    filtered = data['ingredients']
    if search:
        filtered = {k: v for k, v in data['ingredients'].items() if search.lower() in k.lower()}
    
    # הצגה
    if filtered:
        df_data = []
        for name, details in filtered.items():
            unit_price = details['price'] / details['package']
            df_data.append({
                'שם': name,
                'מחיר אריזה': f"{details['price']} ₪",
                'כמות': f"{details['package']} {details['unit']}",
                'מחיר ליחידה': f"{unit_price:.4f} ₪"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("לא נמצאו תוצאות")

# טאב 4: אריזות
with tab4:
    st.markdown("## 📦 רשימת אריזות")
    
    if data['packaging']:
        df_data = []
        for name, details in data['packaging'].items():
            df_data.append({
                'שם': name,
                'מחיר': f"{details['price']} ₪",
                'כמות': details['quantity'],
                'מקור': details.get('source', '')
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("אין אריזות במערכת")

# טאב 5: מוצרים
with tab5:
    st.markdown("## 🛍️ רשימת מוצרים")
    
    if data['products']:
        df_data = []
        for name, price in data['products'].items():
            df_data.append({
                'מוצר': name,
                'מחיר': f"{price} ₪"
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("אין מוצרים במערכת")

# טאב 6: מתכונים מהאקסל
with tab6:
    st.markdown("## 📊 מתכונים מקובץ האקסל")
    
    if data['recipes']:
        recipe_list = list(data['recipes'].keys())
        selected_recipe = st.selectbox("בחר מתכון", recipe_list)
        
        if selected_recipe:
            st.markdown(f"### {selected_recipe}")
            df = data['recipes'][selected_recipe]
            st.dataframe(df, use_container_width=True)
            
            if st.button("📋 העתק לתמחור חדש"):
                st.info("המתכון הועתק - עבור לטאב 'תמחור חדש'")
    else:
        st.info("לא נמצאו מתכונים בקובץ")

# פוטר עם זכויות יוצרים
st.markdown("---")
st.markdown("""
<div class='copyright'>
    <strong>© 2024 כל הזכויות שמורות לקורל ביטון</strong><br>
    מערכת תמחור מתכונים מקצועית - גרסה 3.0<br>
    אין להעתיק, להפיץ או לעשות כל שימוש מסחרי ללא אישור בכתב<br>
    לפניות: 052-751-3002
</div>
""", unsafe_allow_html=True)
