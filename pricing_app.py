import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
import base64
from PIL import Image
import io

# הגדרות עמוד
st.set_page_config(
    page_title="🎂 סוכן תמחור מתכונים",
    page_icon="🎂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS לתמיכה בעברית
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;700&display=swap');
    
    * {
        font-family: 'Heebo', sans-serif !important;
        direction: rtl !important;
    }
    
    .stApp {
        direction: rtl;
    }
    
    h1, h2, h3 {
        text-align: center;
        color: #2C3E50;
    }
    
    .ingredient-box {
        background: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    .price-display {
        font-size: 24px;
        font-weight: bold;
        color: #28A745;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# יצירת רשימת חומרי גלם קבועה
DEFAULT_INGREDIENTS = {
    'קמח לבן מנופה': {'price': 8.5, 'package': 1000, 'unit': 'גרם'},
    'קמח תופח': {'price': 8, 'package': 1000, 'unit': 'גרם'},
    'קמח מלא': {'price': 9, 'package': 1000, 'unit': 'גרם'},
    'קמח כוסמין': {'price': 12, 'package': 1000, 'unit': 'גרם'},
    
    'סוכר לבן': {'price': 5.2, 'package': 1000, 'unit': 'גרם'},
    'סוכר חום בהיר': {'price': 14.9, 'package': 1000, 'unit': 'גרם'},
    'סוכר חום כהה': {'price': 14.9, 'package': 1000, 'unit': 'גרם'},
    'אבקת סוכר': {'price': 7.5, 'package': 500, 'unit': 'גרם'},
    'סוכר וניל': {'price': 3, 'package': 10, 'unit': 'יחידות'},
    
    'חמאה תנובה': {'price': 9, 'package': 200, 'unit': 'גרם'},
    'חמאה עם מלח': {'price': 9, 'package': 200, 'unit': 'גרם'},
    'מרגרינה': {'price': 7, 'package': 200, 'unit': 'גרם'},
    'מחמאה': {'price': 4.8, 'package': 200, 'unit': 'גרם'},
    
    'ביצים L': {'price': 14, 'package': 12, 'unit': 'יחידות'},
    'ביצים M': {'price': 12, 'package': 12, 'unit': 'יחידות'},
    'ביצים S': {'price': 10, 'package': 12, 'unit': 'יחידות'},
    'ביצים אורגניות': {'price': 18, 'package': 12, 'unit': 'יחידות'},
    
    'שמן קנולה': {'price': 14.9, 'package': 1000, 'unit': 'מ״ל'},
    'שמן זית': {'price': 35, 'package': 750, 'unit': 'מ״ל'},
    'שמן קוקוס': {'price': 25, 'package': 500, 'unit': 'מ״ל'},
    
    'שמנת מתוקה 38%': {'price': 6.8, 'package': 250, 'unit': 'מ״ל'},
    'שמנת מתוקה 32%': {'price': 5.5, 'package': 250, 'unit': 'מ״ל'},
    'שמנת חמוצה': {'price': 5.5, 'package': 200, 'unit': 'גרם'},
    'שמנת צמחית': {'price': 8, 'package': 250, 'unit': 'מ״ל'},
    
    'חלב 3%': {'price': 6.5, 'package': 1000, 'unit': 'מ״ל'},
    'חלב 1%': {'price': 6, 'package': 1000, 'unit': 'מ״ל'},
    'חלב מרוכז': {'price': 8, 'package': 397, 'unit': 'גרם'},
    
    'שוקולד מריר': {'price': 32.5, 'package': 1000, 'unit': 'גרם'},
    'שוקולד מריר מהדרין': {'price': 32.5, 'package': 1000, 'unit': 'גרם'},
    'שוקולד חלב': {'price': 37.5, 'package': 1000, 'unit': 'גרם'},
    'שוקולד חלב מהדרין': {'price': 37.5, 'package': 1000, 'unit': 'גרם'},
    'שוקולד לבן': {'price': 37.5, 'package': 1000, 'unit': 'גרם'},
    'שוקולד לבן מהדרין': {'price': 37.5, 'package': 1000, 'unit': 'גרם'},
    'שוקולד צ׳יפס': {'price': 23, 'package': 500, 'unit': 'גרם'},
    'קקאו': {'price': 45, 'package': 500, 'unit': 'גרם'},
    
    'אבקת אפייה': {'price': 11.5, 'package': 100, 'unit': 'גרם'},
    'סודה לשתייה': {'price': 3.5, 'package': 500, 'unit': 'גרם'},
    'קורנפלור': {'price': 7, 'package': 500, 'unit': 'גרם'},
    
    'וניל נוזלי': {'price': 53.8, 'package': 50, 'unit': 'מ״ל'},
    'תמצית וניל': {'price': 15, 'package': 30, 'unit': 'מ״ל'},
    'מחית וניל': {'price': 53.8, 'package': 50, 'unit': 'גרם'},
    
    'מלח': {'price': 2.5, 'package': 1000, 'unit': 'גרם'},
    'דבש': {'price': 25, 'package': 500, 'unit': 'גרם'},
    'ריבה': {'price': 12, 'package': 350, 'unit': 'גרם'},
    'שמרים יבשים': {'price': 8, 'package': 50, 'unit': 'גרם'},
    'שמרים טריים': {'price': 3, 'package': 50, 'unit': 'גרם'},
    
    'אגוזי מלך': {'price': 60, 'package': 500, 'unit': 'גרם'},
    'שקדים': {'price': 45, 'package': 500, 'unit': 'גרם'},
    'פיסטוקים': {'price': 150, 'package': 500, 'unit': 'גרם'},
    'קוקוס טחון': {'price': 20, 'package': 200, 'unit': 'גרם'},
}

# Initialize session state
if 'ingredients_db' not in st.session_state:
    st.session_state.ingredients_db = DEFAULT_INGREDIENTS.copy()

if 'recipes_history' not in st.session_state:
    st.session_state.recipes_history = []

# כותרת
st.markdown("<h1>🎂 סוכן תמחור מתכונים חכם 🎂</h1>", unsafe_allow_html=True)
st.markdown("<h3>המערכת המקצועית שלך לתמחור מדויק</h3>", unsafe_allow_html=True)
st.markdown("---")

# פונקציות עזר
def find_ingredient_smart(query):
    """חיפוש חכם של חומר גלם"""
    query = query.strip().lower()
    exact_matches = []
    partial_matches = []
    
    for name, details in st.session_state.ingredients_db.items():
        name_lower = name.lower()
        if name_lower == query:
            return name, details
        elif query in name_lower:
            partial_matches.append((name, details))
        elif all(word in name_lower for word in query.split()):
            partial_matches.append((name, details))
    
    if partial_matches:
        return partial_matches[0]
    
    return None, None

def calculate_ingredient_cost(name, quantity):
    """חישוב עלות חומר גלם"""
    ingredient_name, details = find_ingredient_smart(name)
    
    if details:
        unit_price = details['price'] / details['package']
        cost = quantity * unit_price
        return {
            'name': ingredient_name,
            'quantity': quantity,
            'unit': details['unit'],
            'unit_price': unit_price,
            'cost': round(cost, 2)
        }
    return None

def parse_recipe_text(text):
    """פענוח טקסט של מתכון"""
    recipe = {}
    lines = text.replace(',', '\n').replace('،', '\n').split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # ניסיון למצוא כמות
        parts = line.split()
        if len(parts) >= 2:
            try:
                # חיפוש מספר
                for i, part in enumerate(parts):
                    try:
                        quantity = float(part.replace(',',''))
                        # מציאת שם החומר
                        rest = parts[i+1:]
                        
                        # הסרת יחידות מידה
                        units = ['גרם', 'ג', 'מ״ל', 'מל', 'כוסות', 'כוס', 'כפות', 'כפית', 'יחידות', 'יח']
                        if rest and rest[0] in units:
                            rest = rest[1:]
                        
                        if rest:
                            ingredient_name = ' '.join(rest)
                            found_name, _ = find_ingredient_smart(ingredient_name)
                            if found_name:
                                recipe[found_name] = quantity
                                break
                    except:
                        continue
            except:
                pass
    
    return recipe

# סרגל צד
with st.sidebar:
    st.markdown("### ⚙️ הגדרות תמחור")
    
    labor_rate = st.number_input("💰 מחיר שעת עבודה", value=75, min_value=0, step=5)
    default_margin = st.slider("📈 אחוז רווח מומלץ", 15, 60, 35, 5)
    
    st.markdown("---")
    st.markdown("### 📊 מאגר חומרי גלם")
    st.info(f"סה״כ חומרים: {len(st.session_state.ingredients_db)}")
    
    # כפתור לצפייה במאגר
    if st.button("📋 הצג רשימה מלאה"):
        st.session_state.show_db = True

# טאבים
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚡ תמחור מהיר",
    "📸 תמחור מתמונה",
    "🔍 חיפוש חומרים",
    "➕ ניהול מאגר",
    "📊 מאגר החומרים"
])

# טאב 1: תמחור מהיר
with tab1:
    st.markdown("### 📝 בחר חומרים מהרשימה או הקלד חופשי")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # אפשרות 1: בחירה מרשימה עם חיפוש
        st.markdown("#### בחירה מרשימה")
        
        num_ingredients = st.number_input("כמה חומרים במתכון?", 1, 20, 5, key="num_ing")
        
        recipe_items = {}
        for i in range(num_ingredients):
            cols = st.columns([2, 1])
            with cols[0]:
                # חיפוש עם השלמה אוטומטית
                ingredient = st.selectbox(
                    f"חומר {i+1}",
                    options=[""] + list(st.session_state.ingredients_db.keys()),
                    key=f"select_{i}"
                )
            with cols[1]:
                if ingredient:
                    quantity = st.number_input(
                        "כמות",
                        min_value=0.0,
                        step=1.0,
                        key=f"qty_{i}"
                    )
                    if quantity > 0:
                        recipe_items[ingredient] = quantity
        
        # אפשרות 2: הקלדה חופשית
        st.markdown("#### או הקלד טקסט חופשי")
        free_text = st.text_area(
            "דוגמה: 200 גרם קמח, 100 גרם סוכר, 3 ביצים",
            height=100
        )
        
        if st.button("🧮 חשב עלות", type="primary"):
            # איחוד המתכון
            final_recipe = recipe_items.copy()
            
            if free_text:
                parsed = parse_recipe_text(free_text)
                final_recipe.update(parsed)
            
            if final_recipe:
                # חישוב עלויות
                total_ingredients = 0
                results = []
                missing = []
                
                st.markdown("### 📊 תוצאות התמחור")
                
                for ing, qty in final_recipe.items():
                    cost_data = calculate_ingredient_cost(ing, qty)
                    if cost_data:
                        results.append(cost_data)
                        total_ingredients += cost_data['cost']
                    else:
                        missing.append(ing)
                
                # הצגת תוצאות
                if results:
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                
                if missing:
                    st.warning(f"חומרים לא מזוהים: {', '.join(missing)}")
                    if st.button("➕ הוסף חומרים חסרים"):
                        st.session_state.add_missing = missing
                
                # חישוב סופי
                labor_hours = st.number_input("שעות עבודה", value=0.5, step=0.25)
                labor_cost = labor_hours * labor_rate
                overhead = 5
                packaging = 5
                
                total_cost = total_ingredients + labor_cost + overhead + packaging
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("חומרי גלם", f"{total_ingredients:.2f} ש״ח")
                with col2:
                    st.metric("עבודה", f"{labor_cost:.2f} ש״ח")
                with col3:
                    st.metric("תקורות", f"{overhead + packaging:.2f} ש״ח")
                
                st.markdown(f"<div class='price-display'>עלות כוללת: {total_cost:.2f} ש״ח</div>", unsafe_allow_html=True)
                
                # מחירי מכירה
                st.markdown("### 💰 מחירי מכירה מומלצים")
                margins = [0.25, default_margin/100, 0.40, 0.50]
                
                cols = st.columns(len(margins))
                for i, margin in enumerate(margins):
                    price = total_cost * (1 + margin)
                    profit = price - total_cost
                    with cols[i]:
                        if margin == default_margin/100:
                            st.success(f"**{int(margin*100)}%**\n\n{price:.0f} ש״ח\n\nרווח: {profit:.0f} ש״ח")
                        else:
                            st.info(f"**{int(margin*100)}%**\n\n{price:.0f} ש״ח\n\nרווח: {profit:.0f} ש״ח")

# טאב 2: תמחור מתמונה
with tab2:
    st.markdown("### 📸 העלה תמונה של מתכון")
    st.info("העלה תמונה של מתכון והמערכת תזהה את החומרים")
    
    uploaded_file = st.file_uploader("בחר תמונה", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        # הצגת התמונה
        image = Image.open(uploaded_file)
        st.image(image, caption="התמונה שהועלתה", use_column_width=True)
        
        st.warning("⚠️ זיהוי אוטומטי של טקסט מתמונה דורש חיבור ל-OCR API")
        st.info("💡 בינתיים, העתק את הטקסט מהתמונה לתיבה למטה:")
        
        manual_text = st.text_area("הקלד את המתכון מהתמונה:", height=150)
        
        if manual_text and st.button("🔍 זהה וחשב"):
            recipe = parse_recipe_text(manual_text)
            if recipe:
                st.success(f"זוהו {len(recipe)} חומרים")
                for ing, qty in recipe.items():
                    st.write(f"• {ing}: {qty}")

# טאב 3: חיפוש חומרים
with tab3:
    st.markdown("### 🔍 חיפוש במאגר חומרי הגלם")
    
    search_term = st.text_input("הקלד שם חומר גלם:")
    
    if search_term:
        results = []
        for name, details in st.session_state.ingredients_db.items():
            if search_term.lower() in name.lower():
                unit_price = details['price'] / details['package']
                results.append({
                    'שם': name,
                    'מחיר לאריזה': f"{details['price']} ש״ח",
                    'כמות באריזה': f"{details['package']} {details['unit']}",
                    'מחיר ליחידה': f"{unit_price:.4f} ש״ח/{details['unit']}"
                })
        
        if results:
            st.success(f"נמצאו {len(results)} תוצאות:")
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("לא נמצאו תוצאות")
            if st.button("➕ הוסף חומר חדש"):
                st.session_state.add_new = search_term

# טאב 4: ניהול מאגר
with tab4:
    st.markdown("### ➕ הוספת חומר גלם חדש")
    
    # אם יש חומר להוספה מחיפוש
    if hasattr(st.session_state, 'add_new'):
        st.info(f"מוסיף את: {st.session_state.add_new}")
    
    new_name = st.text_input("שם החומר:", value=getattr(st.session_state, 'add_new', ''))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        new_price = st.number_input("מחיר אריזה (ש״ח)", min_value=0.0, step=0.5)
    with col2:
        new_package = st.number_input("כמות באריזה", min_value=0.0, step=1.0)
    with col3:
        new_unit = st.selectbox("יחידת מידה", ["גרם", "מ״ל", "יחידות"])
    
    if st.button("➕ הוסף למאגר", type="primary"):
        if new_name and new_price > 0 and new_package > 0:
            st.session_state.ingredients_db[new_name] = {
                'price': new_price,
                'package': new_package,
                'unit': new_unit
            }
            st.success(f"✅ נוסף בהצלחה: {new_name}")
            st.balloons()
            
            # ניקוי
            if hasattr(st.session_state, 'add_new'):
                del st.session_state.add_new
    
    st.markdown("---")
    
    # עריכת חומר קיים
    st.markdown("### ✏️ עריכת חומר קיים")
    
    edit_item = st.selectbox(
        "בחר חומר לעריכה:",
        options=[""] + list(st.session_state.ingredients_db.keys())
    )
    
    if edit_item:
        current = st.session_state.ingredients_db[edit_item]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            edit_price = st.number_input("מחיר חדש", value=current['price'], key="edit_p")
        with col2:
            edit_package = st.number_input("כמות חדשה", value=float(current['package']), key="edit_q")
        with col3:
            st.write(f"יחידה: {current['unit']}")
        
        if st.button("💾 שמור שינויים"):
            st.session_state.ingredients_db[edit_item] = {
                'price': edit_price,
                'package': edit_package,
                'unit': current['unit']
            }
            st.success("✅ עודכן בהצלחה!")

# טאב 5: מאגר החומרים
with tab5:
    st.markdown("### 📊 רשימת כל חומרי הגלם במערכת")
    
    # יצירת DataFrame
    data = []
    for name, details in st.session_state.ingredients_db.items():
        unit_price = details['price'] / details['package']
        data.append({
            'שם החומר': name,
            'מחיר אריזה': f"{details['price']} ש״ח",
            'כמות': f"{details['package']} {details['unit']}",
            'מחיר ליחידה': f"{unit_price:.4f} ש״ח"
        })
    
    df = pd.DataFrame(data)
    
    # חיפוש וסינון
    filter_text = st.text_input("🔍 סנן לפי שם:", key="filter_db")
    if filter_text:
        df = df[df['שם החומר'].str.contains(filter_text, case=False)]
    
    # הצגה
    st.dataframe(df, use_container_width=True, height=500)
    
    # ייצוא
    if st.button("💾 הורד כקובץ Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='חומרי גלם')
        
        output.seek(0)
        b64 = base64.b64encode(output.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="ingredients.xlsx">📥 לחץ להורדה</a>'
        st.markdown(href, unsafe_allow_html=True)

# פוטר
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🎂 סוכן תמחור מתכונים - גרסה 2.0 🎂</p>
    <p>כל הזכויות שמורות © 2024</p>
</div>
""", unsafe_allow_html=True)
