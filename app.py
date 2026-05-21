# Подключаем необходимые библиотеки для работы приложения:
import streamlit as st          # Главная библиотека для создания веб-интерфейса
import numpy as np              # Библиотека для быстрых математических операций и работы с массивами
import scipy.stats as stats     # Научная библиотека, берем отсюда нормальное распределение (norm) для Лапласа
import matplotlib.pyplot as plt # Библиотека для рисования графиков (точек и линий)

# ==========================================
# 1. НАСТРОЙКИ СТРАНИЦЫ И ДИЗАЙН (REFERENCE STYLE)
# ==========================================
# Задаем базовые настройки страницы: заголовок во вкладке браузера и широкий формат (layout="wide")
st.set_page_config(page_title="Проект 23 | DGTU", layout="wide", initial_sidebar_state="expanded")

# Внедряем пользовательский CSS для стилизации под "Neo-brutalism"
# Используем unsafe_allow_html=True, чтобы Streamlit отрендерил этот блок как реальный код стилей веб-страницы
st.markdown("""
    <style>
    /* 1. ЖЕСТКИЙ ФИКС ЦВЕТОВ (Против белого текста на белом фоне) */
    /* Принудительно задаем черный цвет для всего текста, даже если у пользователя темная тема в браузере */
    .stApp, [data-testid="stSidebar"], .stMarkdown p, h1, h2, h3, h4, h5, h6, span, div, label, li, .stRadio label {
        color: #000000 !important;
    }
    
    /* Форсируем черный цвет специально для математических формул LaTeX */
    .katex { color: #000000 !important; }

    /* 2. ГРАДИЕНТНЫЙ ФОН */
    /* Делаем красивый перелив от теплого желтого к белому и светло-розовому */
    .stApp { 
        background: linear-gradient(135deg, #FFF9D2 0%, #FFFFFF 50%, #FFE1E6 100%) !important; 
    }
    
    /* 3. ОФОРМЛЕНИЕ БОКОВОЙ ПАНЕЛИ */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 4px solid #000000 !important; /* Жирная черная линия отсечения */
    }

    /* 4. ТИПОГРАФИКА */
    /* Делаем заголовки крупными, жирными (900) и заглавными буквами */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        font-weight: 900 !important;
        letter-spacing: -1.5px !important;
        text-transform: uppercase;
        line-height: 1.1 !important;
    }
    
    /* Акцентный красно-оранжевый цвет для важных слов */
    .highlight {
        color: #F04A26 !important;
    }

    /* 5. КНОПКИ В СТИЛЕ NEO-BRUTALISM */
    /* Кнопки с жесткой черной тенью без размытия, которая смещается при нажатии */
    .stButton>button { 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        border: 3px solid #000000 !important;
        border-radius: 12px !important; 
        box-shadow: 4px 4px 0px #000000 !important; /* Та самая жесткая тень */
        font-weight: 900 !important;
        text-transform: uppercase;
        padding: 10px 24px !important;
        transition: all 0.1s ease;
    }
    /* Эффект при наведении курсора */
    .stButton>button:hover {
        background-color: #F04A26 !important;
        color: #FFFFFF !important;
    }
    /* Эффект при клике: кнопка "продавливается" вниз и вправо */
    .stButton>button:active { 
        transform: translate(4px, 4px) !important; 
        box-shadow: 0px 0px 0px #000000 !important; 
    }

    /* Метрики (карточки с крупными итоговыми цифрами a, b, r_xy) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 3px solid #000000 !important;
        border-radius: 12px !important;
        box-shadow: 4px 4px 0px #F04A26 !important; /* Тень акцентного цвета */
        padding: 20px !important;
    }
    
    /* Оформление редактируемой таблицы данных */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border: 3px solid #000000 !important;
        border-radius: 12px !important;
    }
    
    /* Карточка для блока с ролями команды в боковом меню */
    .info-box {
        background-color: #FFFFFF;
        border: 3px solid #000000;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 4px 4px 0px #000000;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ИНИЦИАЛИЗАЦИЯ ДАННЫХ
# ==========================================
# Функция возвращает эталонные данные 23 варианта в виде простого словаря (dict) со списками (list)
def get_default_data():
    return {
        'X (Объем, тыс.шт)': [1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.2, 1.1, 0.9, 0.8, 0.7, 0.6, 0.5],
        'Y (Себестоимость, тыс.руб)': [0.94, 1.33, 1.73, 2.12, 2.2, 3.5, 3.7, 3.8, 4.5, 5.7, 5.68, 6.07, 6.47]
    }

# Сохраняем данные в "состояние сессии" (session_state). 
# Это нужно, чтобы при каждом обновлении страницы данные в таблице не сбрасывались до дефолтных
if 'data' not in st.session_state:
    st.session_state.data = get_default_data()

# Функция генерации "случайных" реалистичных данных вокруг нашего тренда
def randomize_data():
    x_vals = st.session_state.data['X (Объем, тыс.шт)'] # Берем текущий столбец иксов
    new_y_vals = [] # Пустой список для новых игреков
    
    # Проходим циклом по каждому значению X
    for x in x_vals:
        # np.random.normal(0, 0.5) генерирует случайный шум со средним 0 и разбросом 0.5
        noise = np.random.normal(0, 0.5)
        # Подставляем X в базовую формулу (примерно -3.5x + 8.5) и добавляем шум
        new_y = round(-3.5 * x + 8.5 + noise, 2)
        # Защита от отрицательных цен: берем максимальное между 0.5 и сгенерированным числом
        final_y = max(0.5, new_y)
        new_y_vals.append(final_y) # Добавляем в список
        
    # Записываем сгенерированный список обратно в словарь
    st.session_state.data['Y (Себестоимость, тыс.руб)'] = new_y_vals

# Функция сброса таблицы в нули
def clear_data():
    st.session_state.data = {
        'X (Объем, тыс.шт)': [0.0] * 13, 
        'Y (Себестоимость, тыс.руб)': [0.0] * 13
    }

# Функция возврата к изначальным данным 23 варианта
def default_data():
    st.session_state.data = get_default_data()

# ==========================================
# 3. МАТЕМАТИЧЕСКИЕ ФУНКЦИИ
# ==========================================
# Функция для вычисления всех базовых сумм МНК
def calculate_sums(data):
    # Достаем списки по ключам словаря и переводим в numpy массивы (np.array) 
    # для быстрых матричных расчетов и возведения в квадрат
    x = np.array(data['X (Объем, тыс.шт)'], dtype=float)
    y = np.array(data['Y (Себестоимость, тыс.руб)'], dtype=float)
    
    # np.sum автоматически суммирует все элементы массива
    return np.sum(x), np.sum(y), np.sum(x**2), np.sum(x*y), len(x), x, y

# Решение системы методом Гаусса (исключение переменных)
def solve_gauss_steps(sum_x, sum_y, sum_x2, sum_xy, n):
    # Ищем коэффициент k, чтобы уравнять a в обоих уравнениях
    k = sum_x2 / sum_x if sum_x != 0 else 0
    
    # Умножаем первое уравнение на k
    new_b1, new_y1 = n * k, sum_y * k
    
    # Вычитаем первое (умноженное) уравнение из второго (исключаем a)
    diff_b, diff_y = sum_x - new_b1, sum_xy - new_y1
    
    # Находим b и a
    b = diff_y / diff_b if diff_b != 0 else 0
    a = (sum_y - n * b) / sum_x if sum_x != 0 else 0
    
    # Возвращаем не только корни, но и промежуточные шаги для красивого вывода
    return a, b, k, diff_b, diff_y

# Решение системы методом Крамера (через определители)
def solve_cramer_steps(sum_x, sum_y, sum_x2, sum_xy, n):
    # Главный определитель
    delta = (sum_x2 * n) - (sum_x * sum_x)
    # Побочные определители (заменяем столбцы столбцом свободных членов)
    delta_a = (sum_xy * n) - (sum_x * sum_y)
    delta_b = (sum_x2 * sum_y) - (sum_x * sum_xy)
    
    # Корни - это отношение побочного к главному
    a = delta_a / delta if delta != 0 else 0
    b = delta_b / delta if delta != 0 else 0
    return a, b, delta, delta_a, delta_b

# Решение матричным методом: B = (X^T * X)^-1 * X^T * Y
def solve_matrix_steps(x, y):
    n = len(x)
    # np.ones(n) создает столбец из единиц (для коэффициента b)
    # column_stack склеивает столбец иксов и столбец единиц в матрицу X
    X_mat = np.column_stack((x, np.ones(n)))
    # Делаем из массива Y вектор-столбец
    Y_mat = y.reshape(-1, 1)
    
    # X_mat.T — это транспонированная матрица. .dot() — матричное умножение
    XT_X = X_mat.T.dot(X_mat)
    try:
        # np.linalg.inv() находит обратную матрицу
        XT_X_inv = np.linalg.inv(XT_X)
        XT_Y = X_mat.T.dot(Y_mat)
        # Финальное перемножение для получения вектора параметров B
        B = XT_X_inv.dot(XT_Y)
        return B[0][0], B[1][0], XT_X, XT_X_inv, XT_Y
    except:
        # Если определитель ноль, обратной матрицы нет — вернем пустые значения
        return 0, 0, None, None, None

# ==========================================
# 4. БОКОВАЯ ПАНЕЛЬ (SIDEBAR)
# ==========================================
# with st.sidebar означает, что все виджеты внутри этого блока пойдут в боковое меню
with st.sidebar:
    st.markdown("<h2>СЛАВА ДГТУ</h2>", unsafe_allow_html=True)
    
    # Пытаемся загрузить картинку. Если файла logo.png в папке нет, выводим заглушку-рамку
    try:
        st.image("logo.png", use_container_width=True)
    except FileNotFoundError:
        st.markdown("""
        <div>
        🖼️ LOGO.PNG
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---") # Разделительная линия
    
    st.markdown("<h3>РОЛИ В КОМАНДЕ</h3>", unsafe_allow_html=True)
    # Пытаемся загрузить картинку. Если файла logo.png в папке нет, выводим заглушку-рамку
    try:
        st.image("image.png", use_container_width=True)
    except FileNotFoundError:
        st.markdown("""
        <div>
        🖼️ IMAGE.PNG
        </div>
        """, unsafe_allow_html=True)


# ==========================================
# 5. СЕКЦИЯ 1: ВВОД ДАННЫХ И ПЕРВИЧНЫЙ ГРАФИК
# ==========================================
st.markdown("<h1>ПРОГНОЗИРОВАНИЕ ЭКОНОМИЧЕСКИХ ПОКАЗАТЕЛЕЙ ПРОИЗВОДСТВА ЛИНЕЙНОЙ РЕГРЕССИИ</h1>", unsafe_allow_html=True)
st.markdown("---")

# Вывод главного заголовка с акцентным словом (class='highlight')
st.markdown("<h1>1. DATA <span class='highlight'>INPUT.</span></h1>", unsafe_allow_html=True)
st.write("Отредактируйте таблицу. График обновится автоматически.")

# Разбиваем пространство под кнопки на 3 равные колонки
col_btn1, col_btn2, col_btn3 = st.columns(3)
with col_btn1:
    if st.button("СЛУЧАЙНЫЕ ЗНАЧЕНИЯ"): randomize_data() # Кнопка привязывается к нашей функции рандома
with col_btn2:
    if st.button("ОЧИСТИТЬ ТАБЛИЦУ"): clear_data()
with col_btn3:
    if st.button("ВАРИАНТ 23"): default_data()

st.write("") # Пустая строка для визульного отступа

# Делим экран на две колонки: узкую для таблицы (1) и широкую для графика (1.5)
col_tab, col_plot = st.columns([1, 1.5])

with col_tab:
    # st.data_editor создает интерактивную таблицу. Данные привязываются к session_state
    # height=550 гарантирует, что таблица не схлопнется и скролл не понадобится
    st.session_state.data = st.data_editor(st.session_state.data, num_rows="dynamic", height=550)
    # Сразу пересчитываем суммы по измененным в таблице данным
    sum_x, sum_y, sum_x2, sum_xy, n, x, y = calculate_sums(st.session_state.data)

with col_plot:
    # Инициализируем график Matplotlib
    fig0, ax0 = plt.subplots(figsize=(8, 5.5))

    # Рисуем точки: 'bo' означает Blue (синий) Circle (кружок)
    ax0.plot(x, y, 'bo', label=f'Опытные данные ({n} точек)')
    
    # Настройки подписей осей и заголовка
    ax0.set_title('Первичное облако точек (Корреляционное поле)', fontweight='bold')
    ax0.set_xlabel('Объем производства X (тыс. шт.)', fontweight='bold')
    ax0.set_ylabel('Себестоимость Y (тыс. руб.)', fontweight='bold')
    
    # Включаем пунктирную сетку ('--')
    ax0.grid(True, linestyle='--', color='grey', alpha=0.5)
    ax0.legend() # Показываем легенду
    
    # Выводим график в интерфейс Streamlit
    st.pyplot(fig0)

st.markdown("<h3>ПОКАЗАТЕЛИ:</h3>", unsafe_allow_html=True)
# Используем st.latex для красивого математического вывода.
# Символ `r` говорит питону "не трогай обратные слэши", а `f` позволяет вставлять переменные
st.latex(rf"\sum x_i = {sum_x:.4f} \quad\quad \sum y_i = {sum_y:.4f}")
st.latex(rf"\sum x_i^2 = {sum_x2:.4f} \quad\quad \sum x_i y_i = {sum_xy:.4f} \quad\quad n = {n}")

st.markdown("---")

# ==========================================
# 6. СЕКЦИЯ 2: РЕГРЕССИЯ
# ==========================================
st.markdown("<h1>2. BUILD THE <span class='highlight'>MODEL.</span></h1>", unsafe_allow_html=True)
st.write("Нахождение коэффициентов a и b производится двумя методами: Методом наименьших квадратов (МНК) и Матричным методом. В рамках МНК решение системы линейных алгебраических уравнений (СЛАУ) выполняется методами Гаусса и Крамера.")

st.markdown("<h2>МЕТОД НАИМЕНЬШИХ КВАДРАТОВ (МНК)</h2>", unsafe_allow_html=True)

# ---------------- ГАУСС ----------------
st.markdown("<h3>1. МЕТОД ГАУССА</h3>", unsafe_allow_html=True)
# Распаковываем все шаги Гаусса, полученные из нашей функции
a_g, b_g, k, diff_b, diff_y = solve_gauss_steps(sum_x, sum_y, sum_x2, sum_xy, n)

st.write("РАСШИРЕННАЯ МАТРИЦА СИСТЕМЫ")
# Двойные {{ }} нужны, чтобы f-строка Питона не пыталась распарсить команду LaTeX
st.latex(rf"\left(\begin{{array}}{{cc|c}} {sum_x:.2f} & {n} & {sum_y:.2f} \\ {sum_x2:.2f} & {sum_x:.2f} & {sum_xy:.2f} \end{{array}}\right)")
st.write(f"ШАГ 1: УРАВНИВАЕМ КОЭФФИЦИЕНТЫ ПЕРВОГО СТОЛБЦА")
st.latex(rf"\left(\begin{{array}}{{cc|c}} {sum_x2:.2f} & {n*k:.2f} & {sum_y*k:.2f} \\ {sum_x2:.2f} & {sum_x:.2f} & {sum_xy:.2f} \end{{array}}\right)")
st.write("ШАГ 2: ВЫЧИТАЕМ ИЗ ВТОРОЙ СТРОКИ ПЕРВУЮ И НАХОДИМ $b$")
st.latex(rf"\left(\begin{{array}}{{cc|c}} {sum_x2:.2f} & {n*k:.2f} & {sum_y*k:.2f} \\ 0 & {diff_b:.4f} & {diff_y:.4f} \end{{array}}\right)")
st.latex(rf"{diff_b:.4f}b = {diff_y:.4f} \implies \mathbf{{b = {b_g:.4f}}}")
st.write("ШАГ 3: ПОДСТАВЛЯЕМ В ПЕРВУЮ СТРОКУ И НАХОДИМ $a$")
st.latex(rf"\mathbf{{a = {a_g:.4f}}}")

# ---------------- КРАМЕР ----------------
st.write("")
st.markdown("<h3>2. МЕТОД КРАМЕРА</h3>", unsafe_allow_html=True)
a_c, b_c, delta, delta_a, delta_b = solve_cramer_steps(sum_x, sum_y, sum_x2, sum_xy, n)

st.write("ОПРЕДЕЛИТЕЛИ СИСТЕМЫ")
st.latex(rf"\Delta = \begin{{vmatrix}} {sum_x2:.2f} & {sum_x:.2f} \\ {sum_x:.2f} & {n} \end{{vmatrix}} = {sum_x2:.2f} \cdot {n} - {sum_x:.2f} \cdot {sum_x:.2f} = {delta:.4f}")
st.latex(rf"\Delta_a = \begin{{vmatrix}} {sum_xy:.2f} & {sum_x:.2f} \\ {sum_y:.2f} & {n} \end{{vmatrix}} = {sum_xy:.2f} \cdot {n} - {sum_x:.2f} \cdot {sum_y:.2f} = {delta_a:.4f}")
st.latex(rf"\Delta_b = \begin{{vmatrix}} {sum_x2:.2f} & {sum_xy:.2f} \\ {sum_x:.2f} & {sum_y:.2f} \end{{vmatrix}} = {sum_x2:.2f} \cdot {sum_y:.2f} - {sum_xy:.2f} \cdot {sum_x:.2f} = {delta_b:.4f}")
st.write("КОРНИ")
st.latex(rf"a = \frac{{\Delta_a}}{{\Delta}} = \mathbf{{{a_c:.4f}}}, \quad b = \frac{{\Delta_b}}{{\Delta}} = \mathbf{{{b_c:.4f}}}")

# ---------------- МАТРИЦЫ ----------------
st.write("")
st.markdown("<h2>МАТРИЧНЫЙ МЕТОД</h2>", unsafe_allow_html=True)
a_m, b_m, XT_X, XT_X_inv, XT_Y = solve_matrix_steps(x, y)
if XT_X is not None:
    st.write("МАТРИЦА $X^T X$")
    # Достаем ячейки матрицы по их индексам [строка][столбец] и округляем до 2 знаков (.2f)
    st.latex(rf"\begin{{pmatrix}} {XT_X[0][0]:.2f} & {XT_X[0][1]:.2f} \\ {XT_X[1][0]:.2f} & {XT_X[1][1]:.2f} \end{{pmatrix}}")
    st.write("ОБРАТНАЯ МАТРИЦА $(X^T X)^{{-1}}$")
    st.latex(rf"\begin{{pmatrix}} {XT_X_inv[0][0]:.4f} & {XT_X_inv[0][1]:.4f} \\ {XT_X_inv[1][0]:.4f} & {XT_X_inv[1][1]:.4f} \end{{pmatrix}}")
    st.write("РЕЗУЛЬТАТ $\\vec{{\\beta}} = (X^T X)^{{-1}} X^T Y$")
    st.latex(rf"a = \mathbf{{{a_m:.4f}}}, \quad b = \mathbf{{{b_m:.4f}}}")

# ---------------- ИТОГ И ГРАФИК ----------------
a_final, b_final = a_m, b_m # Берем коэффициенты из матричного метода как итоговые
st.write("")
st.markdown(f"<h2>ИТОГ: <span class='highlight'>y = {a_final:.4f}x + {b_final:.4f}</span></h2>", unsafe_allow_html=True)

# Формула расчета коэффициента корреляции Пирсона r_xy через дисперсии
# np.std вычисляет среднеквадратическое отклонение массива

# --- ПОШАГОВЫЙ РАСЧЕТ КОЭФФИЦИЕНТА КОРРЕЛЯЦИИ ---
avg_x = sum_x / n          # Среднее выборочное X
avg_y = sum_y / n          # Среднее выборочное Y
avg_xy = sum_xy / n        # Среднее произведение XY

# Ковариация (корреляционный момент)
covariance = avg_xy - (avg_x * avg_y)

# Среднеквадратические отклонения (через дисперсию)
std_x = np.std(x)
std_y = np.std(y)

# Итоговый коэффициент корреляции r_xy
if std_x * std_y != 0:
    r_xy = covariance / (std_x * std_y)
else:
    r_xy = 0

# --- РАСЧЕТ ОШИБОК АППРОКСИМАЦИИ ---
y_theoretical = a_final * x + b_final
# Сумма квадратов ошибок (sum e_i^2)
sum_e2 = np.sum((y - y_theoretical)**2)
# Среднеквадратическая ошибка (RMSE)
rmse = np.sqrt(sum_e2 / n)

st.write("ОЦЕНКА ТОЧНОСТИ МОДЕЛИ")
st.latex(r"RMSE = \sqrt{\frac{\sum e_i^2}{n}}")
st.latex(rf"RMSE = \sqrt{{\frac{{\sum e_i^2}}{{n}}}} = \sqrt{{\frac{{{sum_e2:.5f}}}{{{n}}}}} \approx \mathbf{{{rmse:.3f}}} \text{{ тыс. руб.}}")

# Выводим 4 плашки метрик в один ряд
m1, m2, m3, m4 = st.columns(4)
m1.metric("Параметр a (Наклон)", round(a_final, 4))
m2.metric("Параметр b (Сдвиг)", round(b_final, 4))
m3.metric("Корреляция (r_xy)", round(r_xy, 4))
m4.metric("RMSE", round(rmse, 3))

st.write("")

# Итоговый график с линией тренда (регрессии)
fig, ax = plt.subplots()

ax.plot(x, y, 'bo', label=f'Данные ({n} точек)')

# Рисуем саму линию тренда
# np.linspace генерирует 100 точек на отрезке [min, max] для идеальной гладкости линии
x_line = np.linspace(min(x)-0.1, max(x)+0.1, 100)
# Подставляем этот массив X в наше уравнение y = ax + b 
ax.plot(x_line, a_final * x_line + b_final, 'r-', label=f'Уравнение: y = {a_final:.4f}x + {b_final:.4f}')

ax.set_title('Линейная регрессионная модель зависимости Y от X', fontweight='bold')
ax.set_xlabel('Объем производства X (тыс. шт.)', fontweight='bold')
ax.set_ylabel('Себестоимость Y (тыс. руб.)', fontweight='bold')
ax.grid(True, linestyle='--', color='grey', alpha=0.5)

# Код для добавления текстового бокса (r_xy = ...) прямо на координатную плоскость графика
x_min, x_max = ax.get_xlim()
y_min, y_max = ax.get_ylim()
ax.text(x_min + (x_max - x_min) * 0.05,  # Сдвигаем на 5% вправо от левого края
        y_min + (y_max - y_min) * 0.1,   # Сдвигаем на 10% вверх от нижнего края
        f"r_xy = {r_xy:.3f}", 
        fontsize=14, color='#F04A26', fontweight='bold',
        bbox=dict(facecolor='white', edgecolor='black', linewidth=2))

# Стилизуем легенду (рамку со списком линий)
legend = ax.legend(prop={'weight': 'bold'})
legend.get_frame().set_linewidth(2)
# Центрируем и уменьшаем график (создаем пустые колонки по бокам)
col_left, col_center, col_right = st.columns([1, 2, 1])
with col_center:
    st.pyplot(fig)

st.markdown("---")

# ==========================================
# 7. СЕКЦИЯ 3: ВЕРОЯТНОСТИ
# ==========================================
st.markdown("<h1>3. RISK <span class='highlight'>ANALYSIS.</span></h1>", unsafe_allow_html=True)
st.write("Оценка рисков через нормальное распределение и функцию Лапласа.")

# Наследуем коэффициенты a и b из предыдущего блока (чтобы тервер опирался на нашу же линию)
a = a_final
b = b_final

col_sigma, _ = st.columns([1, 2])
with col_sigma:
    # Поле ввода для СКО. По умолчанию равно 0.4 (по условию варианта)
    sigma = st.number_input("ВВЕДИТЕ СРЕДНЕКВАДРАТИЧЕСКОЕ ОТКЛОНЕНИЕ (σ):", value=0.4, step=0.1)

st.write("")
col1, col2 = st.columns(2) # Две колонки для двух задач

with col1:
    st.markdown("<h3>ЗАДАЧА 1: ИНТЕРВАЛ</h3>", unsafe_allow_html=True)
    st.write("ОБЩАЯ ФОРМУЛА:")
    st.latex(r"P(y_{min} \le Y \le y_{max}) = \Phi\left(\frac{y_{max} - M[Y]}{\sigma}\right) - \Phi\left(\frac{y_{min} - M[Y]}{\sigma}\right)")
    # Поля для ввода исходных данных первой задачи
    x_val_1 = st.number_input("Объем (X):", value=1.0)
    min_y = st.number_input("От (Y):", value=3.5)
    max_y = st.number_input("До (Y):", value=4.5)
    
    # Находим математическое ожидание (подставляем X в нашу формулу регрессии)
    expected_y1 = a * x_val_1 + b
    
    # Принудительно округляем z до 3 знаков, чтобы имитировать работу с классическими "бумажными" таблицами Лапласа
    # Z-преобразование переводит наши рубли в стандартное отклонение
    z1 = round((min_y - expected_y1)/sigma, 3)
    z2 = round((max_y - expected_y1)/sigma, 3)
    
    # stats.norm.cdf(z) считает интеграл вероятности от минус бесконечности до z.
    # Разница cdf(z2) - cdf(z1) дает площадь нормального колокола ровно между z1 и z2
    prob = stats.norm.cdf(z2) - stats.norm.cdf(z1)
    
    st.write("ШАГ 1: МАТ. ОЖИДАНИЕ")
    st.latex(rf"M[Y] = {a:.4f} \cdot {x_val_1} + {b:.4f} = \mathbf{{{expected_y1:.4f}}}")
    st.write("ШАГ 2: НОРМИРОВАНИЕ ГРАНИЦ")
    st.latex(rf"z_1 = \frac{{{min_y} - {expected_y1:.4f}}}{{{sigma}}} = {z1:.3f}")
    st.latex(rf"z_2 = \frac{{{max_y} - {expected_y1:.4f}}}{{{sigma}}} = {z2:.3f}")
    st.write("ШАГ 3: ФОРМУЛА ЛАПЛАСА")
    st.latex(rf"P = \Phi({z2:.3f}) - \Phi({z1:.3f}) = \mathbf{{{prob:.4f}}}")
    
    # Выводим финальный успех (зеленая плашка)
    st.success(f"ВЕРОЯТНОСТЬ: {prob*100:.2f}%")

with col2:
    st.markdown("<h3>ЗАДАЧА 2: ОТКЛОНЕНИЕ</h3>", unsafe_allow_html=True)
    st.write("ОБЩАЯ ФОРМУЛА:")
    st.latex(r"P(|Y - M[Y]| \le \delta) = 2 \cdot \Phi\left(\frac{\delta}{\sigma}\right)")
    # Поля для ввода данных второй задачи
    x_val_2 = st.number_input("Объем (X) 2:", value=1.2)
    delta = st.number_input("Макс. отклонение (δ):", value=0.6)
    
    # Мат. ожидание для второго объема
    expected_y2 = a * x_val_2 + b
    
    # Z для отклонения. Поскольку отклонение симметрично в обе стороны, нам нужен только один Z
    z = round(delta / sigma, 3)
    
    # 2 * Ф(z). Так как norm.cdf включает левую половину колокола (0.5), 
    # мы вычитаем ее, чтобы получить классическую функцию Лапласа от нуля, и умножаем на 2
    prob_dev = 2 * (stats.norm.cdf(z) - 0.5)
    
    st.write("ШАГ 1: МАТ. ОЖИДАНИЕ")
    st.latex(rf"M[Y] = {a:.4f} \cdot {x_val_2} + {b:.4f} = \mathbf{{{expected_y2:.4f}}}")
    st.write("ШАГ 2: НОРМИРОВАНИЕ")
    st.latex(rf"z = \frac{{{delta}}}{{{sigma}}} = {z:.3f}")
    st.write("ШАГ 3: ФОРМУЛА ЛАПЛАСА")
    st.latex(rf"P = 2 \cdot \Phi({z:.3f}) = \mathbf{{{prob_dev:.4f}}}")
    
    st.success(f"ВЕРОЯТНОСТЬ: {prob_dev*100:.2f}%")