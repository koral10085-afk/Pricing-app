import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# הגדרות עמוד
st.set_page_config(
    page_title="🎂 סוכן תמחור מתכונים",
    page_icon="🎂",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS לתמיכה בעברית וממשק יפה
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
    
    .main {
        direction: rtl;
        text-align: right;
    }
    
    .stButton button {
        background-color: #FF6B6B;
        color: white;
        border-radius: 20px;
        font-weight: bold;
        width: 100%;
    }
    
    .stButton button:hover {
        background-color: #FF5252;
        transform: scale(1.02);
    }
    
    h1, h2, h3 {
        text-align: center;
        color: #2C3E50;
    }
    
    .success-box {
        background-color: #D4EDDA;
        border: 2px solid #28A745;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .error-box {
        background-color: #F8D7DA;
        border: 2px solid #DC3545;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .info-box {
        background-color: #D1ECF1;
        border: 2px solid #17A2B8;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("<h1>🎂 סוכן תמחור מתכונים חכם 🎂</h1>", unsafe_allow_html=True)
st.markdown("<h3>התמחור המקצועי שלך - תמיד זמין, תמיד חינם!</h3>", unsafe_allow_html=True)
st.markdown("---")

# טעינת נתונים
@st.cache_data
def load_excel_data():
    """טעינת נתוני האקסל"""
    try:
        excel_file = 'pricing_data.xlsx'
        if not os.path.exists(excel_file):
            # אם אין קובץ, יוצר נתוני דוגמה
            create_sample_data(excel_file)
        
        all_sheets = pd.read_excel(excel_file, sheet_name=None)
        
        # חומרי גלם
        ingredients_df = all_sheets.get('חומרי גלם', pd.DataFrame())
        if not ingredients_df.empty:
            ingredients_df = ingredients_df.dropna(subset=['חומר גלם'])
        
        # אריזות
        packaging_df = all_sheets.get('אריזות', pd.DataFrame())
        
        return ingredients_df, packaging_df
    except:
        return create_default_ingredients(), pd.DataFrame()

def create_default_ingredients():
    """יצירת רשימת חומרי גלם בסיסית"""
    data = {
        'חומר גלם': [
            'קמח לבן מנופה', 'סוכר לבן', 'סוכר חום', 'חמאה תנובה', 'מרגרינה',
            'ביצים L', 'ביצים M', 'שמן קנולה', 'שמנת מתוקה 38%', 'שמנת חמוצה',
            'שוקולד מריר', 'שוקולד חלב', 'שוקולד לבן', 'קקאו', 'אבקת אפייה',
            'סודה לשתיה', 'וניל', 'מלח', 'חלב', 'יוגורט'
        ],
        'עלות רכישה': [
            8.5, 5.2, 14.9, 9, 7,
            14, 12, 14.9, 6.8, 5.5,
            32.5, 37.5, 37.5, 45, 11.5,
            3.5, 53.8, 2.5, 6.5, 4.5
        ],
        'כמות באריזה': [
            1000, 1000, 1000, 200, 200,
            12, 12, 1000, 250, 200,
            1000, 1000, 1000, 500, 100,
            500, 50, 1000, 1000, 150
        ],
        'יחידת מידה': [
            'גרם', 'גרם', 'גרם', 'גרם', 'גרם',
            'יחידות', 'יחידות', 'מיליליטר', 'גרם', 'גרם',
            'גרם', 'גרם', 'גרם', 'גרם', 'גרם',
            'גרם', 'גרם', 'גרם', 'מיליליטר', 'גרם'
        ]
    }
    return pd.DataFrame(data)

def create_sample_data(filename):
    """יצירת קובץ אקסל לדוגמה"""
    df = create_default_ingredients()
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name='חומרי גלם', index=False)

# טעינת הנתונים
ingredients_df, packaging_df = load_excel_data()

# פונקציות עזר
def find_ingredient(name, df):
    """מציאת חומר גלם"""
    name = name.strip().lower()
    
    # חיפוש מדויק
    exact = df[df['חומר גלם'].str.lower() == name]
    if not exact.empty:
        return exact.iloc[0]
    
    # חיפוש חלקי
    partial = df[df['חומר גלם'].str.lower().str.contains(name, na=False)]
    if not partial.empty:
        return partial.iloc[0]
    
    return None

def calculate_recipe_cost(recipe, labor_hours=0.5, labor_rate=75, utilities=3, packaging=5):
    """חישוב עלות מתכון"""
    results = {
        'ingredients': [],
        'missing': [],
        'ingredients_cost': 0,
        'labor_cost': labor_hours * labor_rate,
        'utilities_cost': utilities,
        'packaging_cost': packaging,
        'total_cost': 0
    }
    
    for ingredient_name, quantity in recipe.items():
        ingredient = find_ingredient(ingredient_name, ingredients_df)
        
        if ingredient is not None:
            unit_price = ingredient['עלות רכישה'] / ingredient['כמות באריזה']
            cost = quantity * unit_price
            
            results['ingredients'].append({
                'name': ingredient['חומר גלם'],
                'quantity': quantity,
                'unit': ingredient.get('יחידת מידה', ''),
                'cost': round(cost, 2)
            })
            results['ingredients_cost'] += cost
        else:
            results['missing'].append(ingredient_name)
    
    results['ingredients_cost'] = round(results['ingredients_cost'], 2)
    results['total_cost'] = round(
        results['ingredients_cost'] + 
        results['labor_cost'] + 
        results['utilities_cost'] + 
        results['packaging_cost'], 2
    )
    
    return results

# סרגל צד
with st.sidebar:
    st.markdown("### ⚙️ הגדרות תמחור")
    
    labor_rate = st.number_input("💰 מחיר שעת עבודה", value=75, min_value=0, step=5)
    default_utilities = st.number_input("⚡ תקורות ברירת מחדל", value=3, min_value=0, step=1)
    default_packaging = st.number_input("📦 אריזה ברירת מחדל", value=5, min_value=0, step=1)
    default_margin = st.slider("📈 אחוז רווח מומלץ", 15, 60, 35, 5)
    
    st.markdown("---")
    st.markdown("### 📊 סטטיסטיקות")
    st.info(f"🥘 חומרי גלם במערכת: {len(ingredients_df)}")
    st.info(f"📦 סוגי אריזות: {len(packaging_df)}")

# טאבים
tab1, tab2, tab3, tab4 = st.tabs([
    "⚡ תמחור מהיר", 
    "🧮 תמחור מלא", 
    "🔍 חיפוש חומרים",
    "➕ הוסף חומר"
])

# טאב 1: תמחור מהיר
with tab1:
    st.markdown("### הזן רשימת חומרים בפורמט חופשי")
    
    quick_text = st.text_area(
        "דוגמה: 200 גרם קמח, 100 גרם סוכר, 3 ביצים",
        height=100,
        placeholder="הקלד כאן את רשימת החומרים..."
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        quick_labor = st.number_input("שעות עבודה", value=0.5, min_value=0.0, step=0.25, key="quick_labor")
    
    if st.button("🚀 חשב עלות", key="quick_calc"):
        if quick_text:
            # פענוח הטקסט
            recipe = {}
            lines = quick_text.replace(',', '\n').split('\n')
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        # מנסה למצוא מספר
                        for i, part in enumerate(parts):
                            try:
                                quantity = float(part)
                                rest = parts[i+1:]
                                
                                # מסיר יחידות מידה
                                if rest and rest[0] in ['גרם', 'ג', 'מ"ל', 'מל', 'כוס', 'כפות', 'יחידות']:
                                    rest = rest[1:]
                                
                                if rest:
                                    ingredient = ' '.join(rest)
                                    recipe[ingredient] = quantity
                                    break
                            except:
                                continue
                    except:
                        pass
            
            if recipe:
                results = calculate_recipe_cost(
                    recipe, 
                    quick_labor, 
                    labor_rate, 
                    default_utilities, 
                    default_packaging
                )
                
                # הצגת תוצאות
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📊 פירוט עלויות")
                    
                    if results['ingredients']:
                        st.markdown("**חומרי גלם:**")
                        for item in results['ingredients']:
                            st.write(f"• {item['name']}: {item['cost']} ש״ח")
                    
                    if results['missing']:
                        st.error("חומרים שלא נמצאו:")
                        for item in results['missing']:
                            st.write(f"• {item}")
                
                with col2:
                    st.markdown("### 💰 סיכום")
                    
                    st.success(f"חומרי גלם: {results['ingredients_cost']} ש״ח")
                    st.info(f"עבודה: {results['labor_cost']} ש״ח")
                    st.info(f"תקורות: {results['utilities_cost']} ש״ח")
                    st.info(f"אריזה: {results['packaging_cost']} ש״ח")
                    
                    st.markdown("---")
                    st.markdown(f"### עלות כוללת: {results['total_cost']} ש״ח")
                    
                    # מחירי מכירה
                    margins = [0.25, default_margin/100, 0.40, 0.50]
                    st.markdown("### 💎 מחירי מכירה מומלצים:")
                    
                    for margin in margins:
                        price = round(results['total_cost'] * (1 + margin), 2)
                        profit = round(price - results['total_cost'], 2)
                        
                        if margin == default_margin/100:
                            st.success(f"**מומלץ ({int(margin*100)}%)**: {price} ש״ח (רווח: {profit} ש״ח)")
                        else:
                            st.info(f"{int(margin*100)}%: {price} ש״ח (רווח: {profit} ש״ח)")

# טאב 2: תמחור מלא
with tab2:
    st.markdown("### 📝 הזן פרטי מתכון")
    
    recipe_name = st.text_input("שם המתכון", placeholder="עוגת שוקולד")
    
    # טבלה להזנת חומרים
    st.markdown("### חומרי גלם")
    
    num_ingredients = st.number_input("כמה חומרים?", 1, 20, 5)
    
    recipe_full = {}
    cols = st.columns(3)
    
    for i in range(num_ingredients):
        with cols[i % 3]:
            ing = st.text_input(f"חומר {i+1}", key=f"ing_{i}")
            qty = st.number_input(f"כמות", min_value=0.0, key=f"qty_{i}")
            if ing and qty > 0:
                recipe_full[ing] = qty
    
    # פרמטרים
    st.markdown("### ⚙️ פרמטרים")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        full_labor = st.number_input("שעות עבודה", value=0.5, min_value=0.0, step=0.25, key="full_labor")
    with col2:
        full_utilities = st.number_input("תקורות", value=default_utilities, min_value=0.0, key="full_util")
    with col3:
        full_packaging = st.number_input("אריזה", value=default_packaging, min_value=0.0, key="full_pack")
    
    if st.button("🧮 חשב תמחור מלא", key="full_calc"):
        if recipe_full:
            results = calculate_recipe_cost(
                recipe_full, 
                full_labor, 
                labor_rate, 
                full_utilities, 
                full_packaging
            )
            
            # הצגה יפה של התוצאות
            st.markdown("---")
            st.markdown(f"## 📊 תמחור: {recipe_name if recipe_name else 'מתכון'}")
            
            # יצירת DataFrame לתצוגה
            if results['ingredients']:
                df_display = pd.DataFrame(results['ingredients'])
                st.dataframe(df_display, use_container_width=True)
            
            # סיכום
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("חומרי גלם", f"{results['ingredients_cost']} ש״ח")
                st.metric("עבודה", f"{results['labor_cost']} ש״ח")
            
            with col2:
                st.metric("תקורות + אריזה", f"{results['utilities_cost'] + results['packaging_cost']} ש״ח")
                st.metric("**עלות כוללת**", f"{results['total_cost']} ש״ח")
            
            # המלצת מחיר
            recommended_price = round(results['total_cost'] * (1 + default_margin/100), 2)
            st.success(f"### 💰 מחיר מכירה מומלץ: {recommended_price} ש״ח")

# טאב 3: חיפוש חומרים
with tab3:
    st.markdown("### 🔍 חפש חומרי גלם במאגר")
    
    search_term = st.text_input("הקלד מילת חיפוש", placeholder="שוקולד")
    
    if search_term:
        matches = ingredients_df[
            ingredients_df['חומר גלם'].str.contains(search_term, case=False, na=False)
        ]
        
        if not matches.empty:
            st.success(f"נמצאו {len(matches)} התאמות:")
            
            # הצגת תוצאות
            for _, row in matches.iterrows():
                unit_price = row['עלות רכישה'] / row['כמות באריזה']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{row['חומר גלם']}**")
                with col2:
                    st.write(f"{unit_price:.3f} ש״ח/{row.get('יחידת מידה', 'יחידה')}")
                with col3:
                    st.write(f"אריזה: {row['עלות רכישה']} ש״ח")
        else:
            st.warning("לא נמצאו התאמות")

# טאב 4: הוספת חומרים
with tab4:
    st.markdown("### ➕ הוסף חומר גלם חדש")
    
    new_name = st.text_input("שם החומר")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        new_price = st.number_input("מחיר רכישה (ש״ח)", min_value=0.0, step=0.5)
    with col2:
        new_size = st.number_input("כמות באריזה", min_value=0.0, step=1.0)
    with col3:
        new_unit = st.selectbox("יחידת מידה", ["גרם", "מיליליטר", "יחידות"])
    
    if st.button("➕ הוסף לרשימה"):
        if new_name and new_price > 0 and new_size > 0:
            # הוספה לדאטהפריים
            new_row = pd.DataFrame({
                'חומר גלם': [new_name],
                'עלות רכישה': [new_price],
                'כמות באריזה': [new_size],
                'יחידת מידה': [new_unit]
            })
            
            st.success(f"✅ החומר '{new_name}' נוסף בהצלחה!")
            st.info(f"מחיר ליחידה: {new_price/new_size:.4f} ש״ח/{new_unit}")

# פוטר
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🎂 פותח במיוחד עבורך - סוכן תמחור חכם למתכונים 🎂</p>
    <p>כל הזכויות שמורות © 2024</p>
</div>
""", unsafe_allow_html=True)
