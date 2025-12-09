"""
מערכת תמחור מתכונים - קורל ביטון
© 2024 כל הזכויות שמורות
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import base64

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
</style>
""", unsafe_allow_html=True)

# מאגר חומרי גלם - 102 פריטים
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
    'חמאה תנובה': {'price': 9.0, 'package': 200, 'unit': 'גרם'},
    'חמאה מפינלנד': {'price': 13.9, 'package': 200, 'unit': 'גרם'},
    'אצבעות קינדר': {'price': 14.9, 'package': 16, 'unit': 'יחידות'},
    'ממרח קינדר': {'price': 16.9, 'package': 300, 'unit': 'גרם'},
    'ביצים M': {'price': 12.89, 'package': 12, 'unit': 'יחידות'},
    'ביצים L': {'price': 13.97, 'package': 12, 'unit': 'יחידות'},
    'גלוקוזה': {'price': 15.0, 'package': 500, 'unit': 'גרם'},
    'מחית וניל': {'price': 129.0, 'package': 120, 'unit': 'גרם'},
    'צבע מאכל': {'price': 18.0, 'package': 1, 'unit': 'יחידות'},
    'טופר יום הולדת': {'price': 3.0, 'package': 1, 'unit': 'יחידות'},
    'סוכריות צבעוניות': {'price': 12.0, 'package': 150, 'unit': 'גרם'},
    'ממרח spread it': {'price': 60.0, 'package': 1000, 'unit': 'גרם'},
    'ביסקוויטים פתיבר': {'price': 11.5, 'package': 500, 'unit': 'גרם'},
    'פרלין שוקולד': {'price': 40.0, 'package': 500, 'unit': 'גרם'},
    'קורנפלקס שוקולד': {'price': 35.0, 'package': 400, 'unit': 'גרם'},
    'קורנפלור': {'price': 6.9, 'package': 500, 'unit': 'גרם'},
    'במבה': {'price': 4.0, 'package': 100, 'unit': 'גרם'},
    'חמאת בוטנים': {'price': 24.0, 'package': 1000, 'unit': 'גרם'},
    'לואקר': {'price': 15.3, 'package': 250, 'unit': 'גרם'},
    'פיסטוק': {'price': 140.0, 'package': 1000, 'unit': 'גרם'},
    'אגוזי מלך': {'price': 60.0, 'package': 1000, 'unit': 'גרם'},
    'קשיו': {'price': 85.0, 'package': 1000, 'unit': 'גרם'},
    'בצק עלים': {'price': 25.9, 'package': 1, 'unit': 'יחידות'},
    'בצק פילו': {'price': 19.9, 'package': 1, 'unit': 'יחידות'},
    'נטורינה': {'price': 7.9, 'package': 200, 'unit': 'גרם'},
    'מחמאה': {'price': 4.8, 'package': 200, 'unit': 'גרם'},
    'קוקוס': {'price': 28.0, 'package': 1000, 'unit': 'גרם'},
    'טחינה גולמית': {'price': 14.9, 'package': 500, 'unit': 'גרם'},
    'מייפל': {'price': 15.0, 'package': 580, 'unit': 'גרם'},
    'חלב מרוכז': {'price': 9.9, 'package': 397, 'unit': 'מ״ל'},
    'חומץ': {'price': 6.9, 'package': 1000, 'unit': 'מ״ל'},
    'שוקולית': {'price': 12.0, 'package': 400, 'unit': 'גרם'},
    'ריבת חלב': {'price': 15.9, 'package': 500, 'unit': 'גרם'},
    'אגוזי לוז': {'price': 59.9, 'package': 1000, 'unit': 'גרם'},
}

# מאגר אריזות
PACKAGING_DB = {
    'קופסא 40/30/8': {'price': 8.0, 'package': 1, 'unit': 'יחידות'},
    'קופסא אינגליש': {'price': 4.5, 'package': 1, 'unit': 'יחידות'},
    'קופסא מחולקת': {'price': 4.5, 'package': 1, 'unit': 'יחידות'},
    'קופסא קאפקייקס': {'price': 6.5, 'package': 1, 'unit': 'יחידות'},
    'מנג׳טים': {'price': 0.25, 'package': 1, 'unit': 'יחידות'},
    'קריסטליות 10': {'price': 2.5, 'package': 1, 'unit': 'יחידות'},
    'קריסטליות 16': {'price': 2.3, 'package': 1, 'unit': 'יחידות'},
    'כיבודיות': {'price': 1.1, 'package': 1, 'unit': 'יחידות'},
    'קופסת פרלינים': {'price': 3.25, 'package': 1, 'unit': 'יחידות'},
    'נייר אפייה': {'price': 0.2, 'package': 1, 'unit': 'יחידות'},
}

# Initialize session state
if 'custom_ingredients' not in st.session_state:
    st.session_state.custom_ingredients = {}

if 'custom_packaging' not in st.session_state:
    st.session_state.custom_packaging = {}

if 'saved_recipes' not in st.session_state:
    st.session_state.saved_recipes = {}

if 'current_recipe' not in st.session_state:
    st.session_state.current_recipe = []

# כותרת
st.markdown("<h1>🎂 תמחור מתכונים</h1>", unsafe_allow_html=True)
st.markdown("<center>© כל הזכויות שמורות לקורל ביטון 2024</center>", unsafe_allow_html=True)
st.markdown("---")

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
    
    st.markdown("### הוסף חומרים")
    
    # איחוד כל המאגרים
    all_ingredients = {**INGREDIENTS_DB, **st.session_state.custom_ingredients}
    all_packaging = {**PACKAGING_DB, **st.session_state.custom_packaging}
    
    # בחירת סוג
    item_type = st.radio("בחר סוג:", ["🥘 חומר גלם", "📦 אריזה"], horizontal=True)
    
    if item_type == "🥘 חומר גלם":
        selected = st.selectbox("בחר חומר:", [""] + list(all_ingredients.keys()))
        items_dict = all_ingredients
        type_key = 'ing'
    else:
        selected = st.selectbox("בחר אריזה:", [""] + list(all_packaging.keys()))
        items_dict = all_packaging
        type_key = 'pkg'
    
    quantity = st.number_input("כמות:", min_value=0.0, value=1.0, step=1.0)
    
    # כפתור הוספה
    if st.button("➕ הוסף לרשימה", type="primary"):
        if selected and quantity > 0:
            st.session_state.current_recipe.append({
                'name': selected,
                'quantity': quantity,
                'type': type_key
            })
            st.success(f"✅ נוסף: {selected}")
            st.rerun()
    
    # הצגת הרשימה הנוכחית
    if st.session_state.current_recipe:
        st.markdown("### 📋 רשימת חומרים")
        
        # טבלה עם מחיקה
        for i, item in enumerate(st.session_state.current_recipe):
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            with col1:
                st.write("🥘" if item['type'] == 'ing' else "📦")
            with col2:
                st.write(item['name'])
            with col3:
                st.write(f"{item['quantity']}")
            with col4:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.current_recipe.pop(i)
                    st.rerun()
        
        # כפתור ניקוי
        if st.button("🗑️ נקה הכל"):
            st.session_state.current_recipe = []
            st.rerun()
        
        st.markdown("---")
        
        # חישוב עלויות
        total_ing = 0
        total_pkg = 0
        
        for item in st.session_state.current_recipe:
            if item['type'] == 'ing' and item['name'] in all_ingredients:
                ing = all_ingredients[item['name']]
                cost = item['quantity'] * (ing['price'] / ing['package'])
                total_ing += cost
            elif item['type'] == 'pkg' and item['name'] in all_packaging:
                pkg = all_packaging[item['name']]
                cost = item['quantity'] * (pkg['price'] / pkg['package'])
                total_pkg += cost
        
        # הגדרות
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
        st.markdown("### 💰 סיכום")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("חומרים", f"{total_ing:.2f} ₪")
            st.metric("אריזות", f"{total_pkg:.2f} ₪")
        with col2:
            st.metric("עבודה", f"{labor:.2f} ₪")
            st.metric("תקורות", f"{overhead:.2f} ₪")
        
        st.markdown(f"<div class='price-highlight'>עלות: {total:.2f} ₪</div>", unsafe_allow_html=True)
        
        # מחירי מכירה
        price = total * (1 + margin/100)
        st.success(f"**מחיר מכירה מומלץ ({margin}%): {price:.0f} ₪**")
        
        # שמירה
        if recipe_name:
            if st.button("💾 שמור מתכון", type="primary"):
                st.session_state.saved_recipes[recipe_name] = {
                    'date': datetime.now().strftime("%d/%m %H:%M"),
                    'recipe': st.session_state.current_recipe.copy(),
                    'cost': total,
                    'price': price
                }
                st.success(f"✅ נשמר!")
                st.balloons()
        else:
            st.warning("⚠️ הכנס שם למתכון כדי לשמור")

# טאב 2: מתכונים שמורים
with tab2:
    st.markdown("### 📋 מתכונים שמורים")
    
    if st.session_state.saved_recipes:
        for name, data in st.session_state.saved_recipes.items():
            with st.expander(f"📄 {name} - {data['date']}"):
                st.write(f"**עלות:** {data['cost']:.2f} ₪")
                st.write(f"**מחיר:** {data.get('price', 0):.0f} ₪")
                
                for item in data['recipe']:
                    icon = "🥘" if item['type'] == 'ing' else "📦"
                    st.write(f"{icon} {item['name']}: {item['quantity']}")
                
                if st.button(f"🗑️ מחק", key=f"del_saved_{name}"):
                    del st.session_state.saved_recipes[name]
                    st.rerun()
    else:
        st.info("אין מתכונים שמורים")

# טאב 3: חומרי גלם
with tab3:
    st.markdown("### 🥘 רשימת חומרי גלם")
    
    all_ing = {**INGREDIENTS_DB, **st.session_state.custom_ingredients}
    st.info(f"סה״כ: {len(all_ing)} חומרים")
    
    search = st.text_input("🔍 חיפוש חומר")
    
    filtered = all_ing
    if search:
        filtered = {k: v for k, v in all_ing.items() if search in k}
    
    if filtered:
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
    
    all_pkg = {**PACKAGING_DB, **st.session_state.custom_packaging}
    st.info(f"סה״כ: {len(all_pkg)} אריזות")
    
    data = []
    for name, details in all_pkg.items():
        unit_price = details['price'] / details['package']
        data.append({
            'שם': name,
            'מחיר': f"{details['price']} ₪",
            'ליחידה': f"{unit_price:.2f} ₪"
        })
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

# טאב 5: הוספת חומרים חדשים
with tab5:
    st.markdown("### ➕ הוספת פריט חדש למאגר")
    
    add_type = st.radio("סוג פריט:", ["חומר גלם", "אריזה"])
    
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
                st.success(f"✅ נוסף חומר גלם: {new_name}")
            else:
                st.session_state.custom_packaging[new_name] = new_item
                st.success(f"✅ נוספה אריזה: {new_name}")
            
            st.balloons()

# טאב 6: ייצוא
with tab6:
    st.markdown("### 📥 ייצוא לאקסל")
    
    if st.button("💾 הורד הכל לאקסל", type="primary"):
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
                for name, data in st.session_state.saved_recipes.items():
                    recipes_data.append({
                        'שם': name,
                        'תאריך': data['date'],
                        'עלות': data['cost'],
                        'מחיר': data.get('price', 0)
                    })
                df_recipes = pd.DataFrame(recipes_data)
                df_recipes.to_excel(writer, sheet_name='מתכונים', index=False)
        
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        
        st.download_button(
            label="📥 הורד קובץ אקסל",
            data=base64.b64decode(b64),
            file_name=f"תמחור_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("✅ הקובץ מוכן להורדה!")

# פוטר
st.markdown("---")
st.markdown("""
<center>
© 2024 כל הזכויות שמורות לקורל ביטון<br>
אין להעתיק או להפיץ ללא אישור
</center>
""", unsafe_allow_html=True)
