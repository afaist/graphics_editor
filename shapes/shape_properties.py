"""База данных свойств геометрических фигур для образовательного вывода."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PropertyItem:
    """Один пункт свойства фигуры."""

    title: str
    description: str
    formula: str = ""


@dataclass
class ShapeProperties:
    """Свойства фигуры — список пунктов + заголовок."""

    name: str
    properties: list[PropertyItem] = field(default_factory=list)


# ====================================================================
# База данных свойств
# ====================================================================

SHAPE_PROPERTIES_DB: dict[str, ShapeProperties] = {}


def register_properties(shape_type: str, props: ShapeProperties):
    """Регистрирует свойства фигуры."""
    SHAPE_PROPERTIES_DB[shape_type] = props


def get_properties(shape_type: str) -> ShapeProperties | None:
    """Возвращает свойства фигуры по типу, или None если не найдено."""
    return SHAPE_PROPERTIES_DB.get(shape_type)


# ====================================================================
# Квадрат
# ====================================================================

register_properties(
    "square",
    ShapeProperties(
        name="Квадрат",
        properties=[
            PropertyItem(
                title="Все стороны равны",
                description="Все четыре стороны квадрата равны между собой",
                formula="a = b = c = d",
            ),
            PropertyItem(
                title="Все углы прямые",
                description="Все четыре угла квадрата равны 90°",
                formula="α = β = γ = δ = 90°",
            ),
            PropertyItem(
                title="Диагонали равны и перпендикулярны",
                description="Диагонали квадрата равны, перпендикулярны и делятся точкой пересечения пополам",
                formula="d₁ = d₂ ⊥",
            ),
            PropertyItem(
                title="Диагонали делят углы пополам",
                description="Каждая диагональ делит углы квадрата пополам (на 45°)",
                formula="45°",
            ),
            PropertyItem(
                title="Площадь квадрата",
                description="Квадрат стороны или половина квадрата диагонали",
                formula="S = a² = d²/2",
            ),
            PropertyItem(
                title="Радиусы окружностей",
                description="R — радиус описанной, r — радиус вписанной окружности",
                formula="R = d/2, r = a/2",
            ),
        ],
    ),
)


# ====================================================================
# Ромб
# ====================================================================

register_properties(
    "rhombus",
    ShapeProperties(
        name="Ромб",
        properties=[
            PropertyItem(
                title="Все стороны равны",
                description="Все четыре стороны ромба равны между собой",
                formula="a = b = c = d",
            ),
            PropertyItem(
                title="Противоположные углы попарно равны",
                description="Углы, лежащие напротив друг друга, равны",
                formula="α = γ, β = δ",
            ),
            PropertyItem(
                title="Диагонали перпендикулярны",
                description="Диагонали ромба перпендикулярны и делят углы ромба пополам",
                formula="d₁ ⊥ d₂",
            ),
            PropertyItem(
                title="Диагонали делят углы пополам",
                description="Каждая диагональ делит углы ромба пополам",
                formula="d₁: α/2, γ/2  |  d₂: β/2, δ/2",
            ),
            PropertyItem(
                title="Сумма квадратов диагоналей",
                description="Сумма квадратов диагоналей равна сумме квадратов всех сторон",
                formula="d₁² + d₂² = 4a²",
            ),
            PropertyItem(
                title="Площадь ромба",
                description="Полупроизведение диагоналей, произведение стороны на высоту или произведение стороны на синус угла",
                formula="S = ½·d₁·d₂ = a·h = a²·sin(α)",
            ),
        ],
    ),
)


# ====================================================================
# Параллелограмм
# ====================================================================

register_properties(
    "parallelogram",
    ShapeProperties(
        name="Параллелограмм",
        properties=[
            PropertyItem(
                title="Противоположные стороны попарно равны",
                description="Стороны, лежащие напротив друг друга, равны",
                formula="a = c, b = d",
            ),
            PropertyItem(
                title="Противоположные стороны параллельны",
                description="Противоположные стороны параллелограмма параллельны",
                formula="a ∥ c, b ∥ d",
            ),
            PropertyItem(
                title="Противоположные углы попарно равны",
                description="Углы, лежащие напротив друг друга, равны",
                formula="α = γ, β = δ",
            ),
            PropertyItem(
                title="Сумма прилежащих углов",
                description="Сумма углов, прилежащих к любой стороне, равна 180°",
                formula="α + β = 180°",
            ),
            PropertyItem(
                title="Диагонали делятся точкой пересечения пополам",
                description="Точка пересечения диагоналей делит каждую из них пополам",
                formula="AO = OC, BO = OD",
            ),
            PropertyItem(
                title="Сумма квадратов диагоналей",
                description="Сумма квадратов диагоналей равна сумме квадратов всех сторон",
                formula="d₁² + d₂² = a² + b² + c² + d²",
            ),
            PropertyItem(
                title="Каждая диагональ делит на два равных треугольника",
                description="Каждая диагональ делит параллелограмм на два равных треугольника",
                formula="△ABC = △CDA",
            ),
            PropertyItem(
                title="Обе диагонали делят на четыре равновеликих треугольника",
                description="Диагонали делят параллелограмм на четыре треугольника равной площади",
                formula="S₁ = S₂ = S₃ = S₄",
            ),
            PropertyItem(
                title="Площадь параллелограмма",
                description="Произведение стороны на высоту или произведение двух сторон на синус угла между ними",
                formula="S = a·h = a·b·sin(α)",
            ),
        ],
    ),
)


# ====================================================================
# Прямоугольник
# ====================================================================

register_properties(
    "rectangle",
    ShapeProperties(
        name="Прямоугольник",
        properties=[
            PropertyItem(
                title="Противоположные стороны попарно равны",
                description="Стороны, лежащие напротив друг друга, равны",
                formula="a = c, b = d",
            ),
            PropertyItem(
                title="Противоположные стороны параллельны",
                description="Противоположные стороны прямоугольника параллельны",
                formula="a ∥ c, b ∥ d",
            ),
            PropertyItem(
                title="Все углы прямые",
                description="Все четыре угла прямоугольника равны 90°",
                formula="α = β = γ = δ = 90°",
            ),
            PropertyItem(
                title="Диагонали равны",
                description="Диагонали прямоугольника равны между собой",
                formula="d₁ = d₂",
            ),
            PropertyItem(
                title="Диагонали делятся точкой пересечения пополам",
                description="Точка пересечения диагоналей делит каждую из них пополам",
                formula="AO = OC, BO = OD",
            ),
            PropertyItem(
                title="Сумма квадратов диагоналей",
                description="Сумма квадратов диагоналей равна сумме квадратов всех сторон",
                formula="d₁² + d₂² = a² + b² + c² + d²",
            ),
            PropertyItem(
                title="Каждая диагональ делит на два равных треугольника",
                description="Каждая диагональ делит прямоугольник на два равных прямоугольных треугольника",
                formula="△ABC = △CDA",
            ),
            PropertyItem(
                title="Площадь прямоугольника",
                description="Произведение двух смежных сторон",
                formula="S = a·b",
            ),
        ],
    ),
)


# ====================================================================
# Трапеция
# ====================================================================

register_properties(
    "trapezoid",
    ShapeProperties(
        name="Трапеция",
        properties=[
            PropertyItem(
                title="Основания параллельны",
                description="Две противоположные стороны (основания) параллельны, две другие — нет",
                formula="AD ∥ BC",
            ),
            PropertyItem(
                title="Сумма углов при боковой стороне",
                description="Сумма углов, прилежащих к любой боковой стороне, равна 180°",
                formula="α + β = 180°, γ + δ = 180°",
            ),
            PropertyItem(
                title="Средняя линия",
                description="Средняя линия параллельна основаниям и равна их полусумме",
                formula="m = (a + b) / 2",
            ),
            PropertyItem(
                title="Диагонали делят трапецию на 4 треугольника",
                description="Диагонали делят трапецию на 4 треугольника: при основаниях — подобны, при боковых сторонах — равновелики",
                formula="△AOD ~ △BOC, S△AOB = S△COD",
            ),
            PropertyItem(
                title="Площадь трапеции",
                description="Произведение средней линии на высоту или полусумма оснований на высоту",
                formula="S = m·h = (a + b)/2 · h",
            ),
        ],
    ),
)


# ====================================================================
# Равнобедренная трапеция
# ====================================================================

register_properties(
    "trapezoid_isosceles",
    ShapeProperties(
        name="Равнобедренная трапеция",
        properties=[
            PropertyItem(
                title="Основания параллельны",
                description="Две противоположные стороны (основания) параллельны",
                formula="AD ∥ BC",
            ),
            PropertyItem(
                title="Боковые стороны равны",
                description="Две непараллельные стороны (боковые) равны между собой",
                formula="AB = CD",
            ),
            PropertyItem(
                title="Углы при основании равны",
                description="Углы, прилежащие к каждому основанию, равны между собой",
                formula="∠A = ∠D, ∠B = ∠C",
            ),
            PropertyItem(
                title="Диагонали равны",
                description="Диагонали равнобедренной трапеции равны между собой",
                formula="AC = BD",
            ),
            PropertyItem(
                title="Диагонали делят трапецию на 4 треугольника",
                description="При основаниях — подобны, при боковых сторонах — равновелики",
                formula="△AOD ~ △BOC, S△AOB = S△COD",
            ),
            PropertyItem(
                title="Около равнобедренной трапеции можно описать окружность",
                description="Сумма противоположных углов равна 180°",
                formula="α + γ = 180°",
            ),
            PropertyItem(
                title="Площадь трапеции",
                description="Произведение средней линии на высоту",
                formula="S = (a + b)/2 · h",
            ),
        ],
    ),
)


# ====================================================================
# Равносторонний треугольник
# ====================================================================

register_properties(
    "regular_triangle",
    ShapeProperties(
        name="Равносторонний треугольник",
        properties=[
            PropertyItem(
                title="Все стороны равны",
                description="Все три стороны треугольника равны между собой",
                formula="a = b = c",
            ),
            PropertyItem(
                title="Все углы равны 60°",
                description="Все три угла треугольника равны 60°",
                formula="α = β = γ = 60°",
            ),
            PropertyItem(
                title="Средние, медианы и биссектрисы равны",
                description="Все медианы, биссектрисы и высоты равны между собой",
                formula="m_a = m_b = m_c = h_a = h_b = h_c",
            ),
            PropertyItem(
                title="Центры описанной и вписанной окружностей совпадают",
                description="Центр описанной и вписанной окружностей — одна и та же точка",
                formula="O = I",
            ),
            PropertyItem(
                title="Площадь",
                description="Квадрат стороны, умноженный на корень из трёх, делённый на четыре",
                formula="S = a²·√3 / 4",
            ),
        ],
    ),
)


# ====================================================================
# Равнобедренный треугольник
# ====================================================================

register_properties(
    "triangle_isosceles",
    ShapeProperties(
        name="Равнобедренный треугольник",
        properties=[
            PropertyItem(
                title="Две стороны равны",
                description="Две стороны треугольника (боковые) равны между собой",
                formula="AB = AC",
            ),
            PropertyItem(
                title="Углы при основании равны",
                description="Углы, лежащие при основании, равны между собой",
                formula="∠B = ∠C",
            ),
            PropertyItem(
                title="Медиана к основанию — высота и биссектриса",
                description="Медиана, проведённая к основанию, является высотой и биссектрисой",
                formula="BM = MC  →  AM ⊥ BC, AM — биссектриса",
            ),
            PropertyItem(
                title="Высота, проведённая к основанию",
                description="Является осью симметрии треугольника",
                formula="对称轴: AM",
            ),
            PropertyItem(
                title="Около равнобедренного треугольника можно описать окружность",
                description="Центр описанной окружности лежит на медиане к основанию",
                formula="R = a² / √(4a² - b²)",
            ),
            PropertyItem(
                title="Площадь",
                description="Полупроизведение боковой стороны на основание и синус угла между ними",
                formula="S = ½·b·c·sin(α)",
            ),
        ],
    ),
)


# ====================================================================
# Прямоугольный треугольник
# ====================================================================

register_properties(
    "triangle_right",
    ShapeProperties(
        name="Прямоугольный треугольник",
        properties=[
            PropertyItem(
                title="Прямой угол",
                description="Один из углов треугольника равен 90°",
                formula="γ = 90°",
            ),
            PropertyItem(
                title="Сумма острых углов",
                description="Сумма двух острых углов прямоугольного треугольника равна 90°",
                formula="α + β = 90°",
            ),
            PropertyItem(
                title="Катет против угла 30°",
                description="Катет, лежащий против угла в 30°, равен половине гипотенузы",
                formula="a = c/2  (при α = 30°)",
            ),
            PropertyItem(
                title="Средняя к гипотенузе",
                description="Медиана, проведённая к гипотенузе, равна её половине",
                formula="m_c = c/2 = R",
            ),
            PropertyItem(
                title="Теорема Пифагора",
                description="Квадрат гипотенузы равен сумме квадратов катетов",
                formula="c² = a² + b²",
            ),
            PropertyItem(
                title="Гипотенуза",
                description="Гипотенуза больше любого катета",
                formula="c > a, c > b",
            ),
            PropertyItem(
                title="Площадь",
                description="Полупроизведение катетов",
                formula="S = a·b / 2",
            ),
        ],
    ),
)


# ====================================================================
# Треугольник (общий)
# ====================================================================

register_properties(
    "triangle_equilateral",
    ShapeProperties(
        name="Правильный треугольник",
        properties=[
            PropertyItem(
                title="Все стороны равны",
                description="Все три стороны треугольника равны между собой",
                formula="a = b = c",
            ),
            PropertyItem(
                title="Все углы равны 60°",
                description="Все три угла треугольника равны 60°",
                formula="α = β = γ = 60°",
            ),
            PropertyItem(
                title="Средние, медианы и биссектрисы равны",
                description="Все медианы, биссектрисы и высоты равны между собой",
                formula="m_a = m_b = m_c = h_a = h_b = h_c",
            ),
            PropertyItem(
                title="Площадь",
                description="Квадрат стороны, умноженный на корень из трёх, делённый на четыре",
                formula="S = a²·√3 / 4",
            ),
        ],
    ),
)


# ====================================================================
# Окружность
# ====================================================================

register_properties(
    "circle",
    ShapeProperties(
        name="Окружность",
        properties=[
            PropertyItem(
                title="Радиус",
                description="Все точки окружности равноудалены от центра",
                formula="OA = OB = OC = R",
            ),
            PropertyItem(
                title="Диаметр",
                description="Диаметр равен удвоенному радиусу и проходит через центр",
                formula="d = 2R",
            ),
            PropertyItem(
                title="Длина окружности",
                description="Произведение числа π на диаметр",
                formula="L = 2πR = πd",
            ),
            PropertyItem(
                title="Площадь круга",
                description="Произведение числа π на квадрат радиуса",
                formula="S = πR²",
            ),
            PropertyItem(
                title="Хорда",
                description="Хорда, проходящая через центр, является диаметром",
                formula="AB — хорда, O ∈ AB  →  AB = d",
            ),
            PropertyItem(
                title="Касательная",
                description="Касательная перпендикулярна радиусу, проведённому в точку касания",
                formula="l ⊥ OA",
            ),
        ],
    ),
)


# ====================================================================
# Прямоугольник (дополнительно)
# ====================================================================

register_properties(
    "rectangle",
    ShapeProperties(
        name="Прямоугольник",
        properties=[
            PropertyItem(
                title="Противоположные стороны попарно равны и параллельны",
                description="a = c, b = d; a ∥ c, b ∥ d",
                formula="a = c, b = d",
            ),
            PropertyItem(
                title="Все углы прямые",
                description="Все четыре угла равны 90°",
                formula="α = β = γ = δ = 90°",
            ),
            PropertyItem(
                title="Диагонали равны и делятся пополам",
                description="d₁ = d₂; AO = OC, BO = OD",
                formula="d₁ = d₂",
            ),
            PropertyItem(
                title="Сумма квадратов диагоналей",
                description="Равна сумме квадратов всех сторон",
                formula="d₁² + d₂² = 2a² + 2b²",
            ),
            PropertyItem(
                title="Площадь",
                description="Произведение смежных сторон",
                formula="S = a·b",
            ),
            PropertyItem(
                title="Периметр",
                description="Удвоенная сумма смежных сторон",
                formula="P = 2(a + b)",
            ),
        ],
    ),
)


# ====================================================================
# Эллипс
# ====================================================================

register_properties(
    "ellipse",
    ShapeProperties(
        name="Эллипс",
        properties=[
            PropertyItem(
                title="Большая и малая полуоси",
                description="a — большая полуось, b — малая полуось",
                formula="a ≥ b",
            ),
            PropertyItem(
                title="Фокусы",
                description="Эллипс — геометрическое место точек, сумма расстояний от которых до двух фокусов постоянна",
                formula="F₁A + F₂A = 2a",
            ),
            PropertyItem(
                title="Фокусное расстояние",
                description="Расстояние от центра до каждого фокуса",
                formula="c = √(a² - b²)",
            ),
            PropertyItem(
                title="Эксцентриситет",
                description="Отношение фокусного расстояния к большой полуоси",
                formula="ε = c/a < 1",
            ),
            PropertyItem(
                title="Площадь",
                description="Произведение полуосей на число π",
                formula="S = πab",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Параллелепипед
# ====================================================================

register_properties(
    "parallelepiped",
    ShapeProperties(
        name="Параллелепипед",
        properties=[
            PropertyItem(
                title="Противоположные грани равны и параллельны",
                description="Все грани — параллелограммы",
                formula="ABCD = A₁B₁C₁D₁",
            ),
            PropertyItem(
                title="12 рёбер, 8 вершин, 6 граней",
                description="Эйлерова формула: V - E + F = 2",
                formula="8 - 12 + 6 = 2",
            ),
            PropertyItem(
                title="Диагонали",
                description="Диагонали пересекаются в одной точке и делятся пополам",
                formula="AC₁ = BD₁ = CA₁ = DB₁",
            ),
            PropertyItem(
                title="Объём",
                description="Произведение трёх измерений или площадь основания на высоту",
                formula="V = a·b·c = S_осн · H",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Сумма площадей всех граней",
                formula="S = 2(ab + bc + ac)",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Куб
# ====================================================================

register_properties(
    "cube",
    ShapeProperties(
        name="Куб",
        properties=[
            PropertyItem(
                title="Все рёбра равны",
                description="Все 12 рёбер куба равны между собой",
                formula="a = b = c",
            ),
            PropertyItem(
                title="Все грани — квадраты",
                description="Все 6 граней куба — равные квадраты",
                formula="ABCD = A₁B₁C₁D₁ = ...",
            ),
            PropertyItem(
                title="Диагональ грани",
                description="Диагональ любой грани равна a√2",
                formula="d_гр = a√2",
            ),
            PropertyItem(
                title="Пространственная диагональ",
                description="Диагональ куба равна a√3",
                formula="d = a√3",
            ),
            PropertyItem(
                title="Объём",
                description="Куб ребра",
                formula="V = a³",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Утроенная площадь грани",
                formula="S = 6a²",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Цилиндр
# ====================================================================

register_properties(
    "cylinder",
    ShapeProperties(
        name="Цилиндр",
        properties=[
            PropertyItem(
                title="Основания",
                description="Основания — равные окружности радиуса R",
                formula="R₁ = R₂ = R",
            ),
            PropertyItem(
                title="Образующая",
                description="Образующая равна высоте (для прямого цилиндра)",
                formula="l = h",
            ),
            PropertyItem(
                title="Объём",
                description="Площадь основания на высоту",
                formula="V = πR²h",
            ),
            PropertyItem(
                title="Площадь боковой поверхности",
                description="2πRl",
                formula="S_бок = 2πRh",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Сумма площадей двух оснований и боковой поверхности",
                formula="S = 2πR(R + h)",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Конус
# ====================================================================

register_properties(
    "cone",
    ShapeProperties(
        name="Конус",
        properties=[
            PropertyItem(
                title="Основание",
                description="Основание — окружность радиуса R",
                formula="R — радиус основания",
            ),
            PropertyItem(
                title="Образующая",
                description="Образующая l соединяет вершину с окружностью основания",
                formula="l² = R² + h²",
            ),
            PropertyItem(
                title="Объём",
                description="Треть произведения площади основания на высоту",
                formula="V = ⅓πR²h",
            ),
            PropertyItem(
                title="Площадь боковой поверхности",
                description="Полупроизведение длины окружности основания на образующую",
                formula="S_бок = πRl",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Сумма площади основания и боковой поверхности",
                formula="S = πR(R + l)",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Пирамида
# ====================================================================

register_properties(
    "pyramid",
    ShapeProperties(
        name="Пирамида",
        properties=[
            PropertyItem(
                title="Основание и боковые грани",
                description="Основание — многоугольник, боковые грани — треугольники",
                formula="n — сторон основания",
            ),
            PropertyItem(
                title="Объём",
                description="Треть произведения площади основания на высоту",
                formula="V = ⅓S_осн · h",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Сумма площади основания и площади боковых граней",
                formula="S = S_осн + S_бок",
            ),
            PropertyItem(
                title="Правильная пирамида",
                description="Основание — правильный многоугольник, вершина проецируется в центр основания",
                formula="S_бок = ½P·apofema",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Призма
# ====================================================================

register_properties(
    "prism",
    ShapeProperties(
        name="Призма",
        properties=[
            PropertyItem(
                title="Основания",
                description="Основания — равные многоугольники, лежащие в параллельных плоскостях",
                formula="ABC... = A₁B₁C₁...",
            ),
            PropertyItem(
                title="Боковые грани",
                description="Параллелограммы",
                formula="AB B₁A₁, BC C₁B₁, ...",
            ),
            PropertyItem(
                title="Объём",
                description="Площадь основания на высоту",
                formula="V = S_осн · h",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Сумма площадей двух оснований и боковых граней",
                formula="S = 2S_осн + S_бок",
            ),
            PropertyItem(
                title="Прямая призма",
                description="Боковые рёбра перпендикулярны основанию",
                formula="S_бок = P_осн · h",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Усечённый конус
# ====================================================================

register_properties(
    "truncated_cone",
    ShapeProperties(
        name="Усечённый конус",
        properties=[
            PropertyItem(
                title="Основания",
                description="Два параллельных круга радиусов R и r",
                formula="R > r",
            ),
            PropertyItem(
                title="Объём",
                description="Треть высоты на сумму площадей оснований и среднего геометрического",
                formula="V = ⅓πh(R² + Rr + r²)",
            ),
            PropertyItem(
                title="Площадь боковой поверхности",
                description="Полусумма длин окружностей оснований на образующую",
                formula="S_бок = πl(R + r)",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Сумма площадей оснований и боковой поверхности",
                formula="S = πR² + πr² + πl(R + r)",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Усечённая пирамида
# ====================================================================

register_properties(
    "truncated_pyramid",
    ShapeProperties(
        name="Усечённая пирамида",
        properties=[
            PropertyItem(
                title="Основания",
                description="Два параллельных подобных многоугольника",
                formula="S₁, S₂ — площади оснований",
            ),
            PropertyItem(
                title="Объём",
                description="Треть высоты на сумму площадей оснований и среднего геометрического",
                formula="V = ⅓h(S₁ + S₂ + √(S₁S₂))",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Сумма площадей оснований и боковых граней",
                formula="S = S₁ + S₂ + S_бок",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Сфера
# ====================================================================

register_properties(
    "sphere",
    ShapeProperties(
        name="Сфера",
        properties=[
            PropertyItem(
                title="Радиус",
                description="Все точки сферы равноудалены от центра",
                formula="OA = OB = OC = R",
            ),
            PropertyItem(
                title="Объём шара",
                description="Четыре третьих π на куб радиуса",
                formula="V = 4/3πR³",
            ),
            PropertyItem(
                title="Площадь поверхности",
                description="Четыре π на квадрат радиуса",
                formula="S = 4πR²",
            ),
            PropertyItem(
                title="Сечение",
                description="Любое сечение сферы плоскостью — окружность",
                formula="r = √(R² - d²)",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Тетраэдр
# ====================================================================

register_properties(
    "tetrahedron",
    ShapeProperties(
        name="Тетраэдр",
        properties=[
            PropertyItem(
                title="Грани",
                description="Четыре треугольные грани",
                formula="4 грани, 6 рёбер, 4 вершины",
            ),
            PropertyItem(
                title="Правильный тетраэдр",
                description="Все грани — равносторонние треугольники",
                formula="a = b = c = ...",
            ),
            PropertyItem(
                title="Объём",
                description="Куб ребра, делённый на 6√2",
                formula="V = a³ / (6√2)",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Утроенная площадь грани",
                formula="S = √3 · a²",
            ),
            PropertyItem(
                title="Высота",
                description="Расстояние от вершины до противоположной грани",
                formula="h = a√(2/3)",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Октаэдр
# ====================================================================

register_properties(
    "octahedron",
    ShapeProperties(
        name="Октаэдр",
        properties=[
            PropertyItem(
                title="Грани",
                description="Восемь равносторонних треугольников",
                formula="8 граней, 12 рёбер, 6 вершин",
            ),
            PropertyItem(
                title="Правильный октаэдр",
                description="Все грани — равносторонние треугольники",
                formula="a = b = c = ...",
            ),
            PropertyItem(
                title="Объём",
                description="Корень из двух, делённый на три, на куб ребра",
                formula="V = √2/3 · a³",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="Удвоенная площадь четырёх равносторонних треугольников",
                formula="S = 2√3 · a²",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Додекаэдр
# ====================================================================

register_properties(
    "dodecahedron",
    ShapeProperties(
        name="Додекаэдр",
        properties=[
            PropertyItem(
                title="Грани",
                description="Двенадцать правильных пятиугольников",
                formula="12 граней, 30 рёбер, 20 вершин",
            ),
            PropertyItem(
                title="Правильный додекаэдр",
                description="Все грани — равные правильные пятиугольники",
                formula="a = b = c = ...",
            ),
            PropertyItem(
                title="Объём",
                description="(15 + 7√5) / 4 на куб ребра",
                formula="V = (15 + 7√5) / 4 · a³",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="3√(25 + 10√5) на квадрат ребра",
                formula="S = 3√(25 + 10√5) · a²",
            ),
            PropertyItem(
                title="Золотое сечение",
                description="Отношение диагонали пятиугольника к стороне — золотое сечение",
                formula="φ = (1 + √5) / 2",
            ),
        ],
    ),
)


# ====================================================================
# 3D: Икосаэдр
# ====================================================================

register_properties(
    "icosahedron",
    ShapeProperties(
        name="Икосаэдр",
        properties=[
            PropertyItem(
                title="Грани",
                description="Двадцать равносторонних треугольников",
                formula="20 граней, 30 рёбер, 12 вершин",
            ),
            PropertyItem(
                title="Правильный икосаэдр",
                description="Все грани — равносторонние треугольники",
                formula="a = b = c = ...",
            ),
            PropertyItem(
                title="Объём",
                description="5(3 + √5) / 12 на куб ребра",
                formula="V = 5(3 + √5) / 12 · a³",
            ),
            PropertyItem(
                title="Полная поверхность",
                description="5√3 на квадрат ребра",
                formula="S = 5√3 · a²",
            ),
        ],
    ),
)


# ====================================================================
# Вписанный угол на диаметре
# ====================================================================

register_properties(
    "inscribed_angle_diameter",
    ShapeProperties(
        name="Вписанный угол на диаметре",
        properties=[
            PropertyItem(
                title="Вписанный угол на диаметре",
                description="Вписанный угол, опирающийся на диаметр, всегда прямой",
                formula="∠ = 90°",
            ),
            PropertyItem(
                title="Следствие",
                description="Любой угол, вершина которого лежит на окружности, а стороны проходят через концы диаметра, равен 90°",
                formula="∠ACB = 90°  (AB — диаметр)",
            ),
        ],
    ),
)


# ====================================================================
# Вписанный угол на хорде
# ====================================================================

register_properties(
    "inscribed_angle_chord",
    ShapeProperties(
        name="Вписанный угол на хорде",
        properties=[
            PropertyItem(
                title="Вписанный угол",
                description="Вписанный угол равен половине дуги, на которую опирается",
                formula="∠ = ½ · дуга",
            ),
            PropertyItem(
                title="Вписанные углы на одной дуге",
                description="Все вписанные углы, опирающиеся на одну дугу, равны",
                formula="∠₁ = ∠₂ = ∠₃",
            ),
            PropertyItem(
                title="Вписанные углы на противоположных дугах",
                description="Сумма вписанных углов, опирающихся на противоположные дуги, равна 180°",
                formula="∠₁ + ∠₂ = 180°",
            ),
        ],
    ),
)


# ====================================================================
# Тригонометрическая окружность
# ====================================================================

register_properties(
    "trigonometric_circle",
    ShapeProperties(
        name="Тригонометрическая окружность",
        properties=[
            PropertyItem(
                title="Единичная окружность",
                description="Радиус окружности равен 1, центр в начале координат",
                formula="x² + y² = 1",
            ),
            PropertyItem(
                title="sin(α)",
                description="Синус — ордината точки на окружности",
                formula="sin(α) = y",
            ),
            PropertyItem(
                title="cos(α)",
                description="Косинус — абсцисса точки на окружности",
                formula="cos(α) = x",
            ),
            PropertyItem(
                title="tg(α)",
                description="Тангенс — отрезок на касательной",
                formula="tg(α) = sin(α) / cos(α)",
            ),
            PropertyItem(
                title="ctg(α)",
                description="Котангенс — отрезок на касательной",
                formula="ctg(α) = cos(α) / sin(α)",
            ),
            PropertyItem(
                title="Основное тождество",
                description="Сумма квадратов синуса и косинуса равна 1",
                formula="sin²(α) + cos²(α) = 1",
            ),
        ],
    ),
)


# ====================================================================
# Единичная окружность
# ====================================================================

register_properties(
    "unit_circle",
    ShapeProperties(
        name="Единичная окружность",
        properties=[
            PropertyItem(
                title="Радиус",
                description="Радиус единичной окружности равен 1",
                formula="R = 1",
            ),
            PropertyItem(
                title="Уравнение",
                description="Уравнение единичной окружности с центром в начале координат",
                formula="x² + y² = 1",
            ),
            PropertyItem(
                title="Координаты точки",
                description="Любая точка на окружности задаётся углом α",
                formula="M(cos α, sin α)",
            ),
        ],
    ),
)


# ====================================================================
# Фрактал: Снежинка Коха
# ====================================================================

register_properties(
    "fractal_koch",
    ShapeProperties(
        name="Снежинка Коха",
        properties=[
            PropertyItem(
                title="Рекурсия",
                description="Каждая сторона заменяется на 4 отрезка, каждый в 3 раза короче",
                formula="N = 4ⁿ",
            ),
            PropertyItem(
                title="Размерность",
                description="Фрактальная размерность снежинки Коха",
                formula="D = lg(4) / lg(3) ≈ 1.262",
            ),
            PropertyItem(
                title="Периметр",
                description="Периметр стремится к бесконечности при n → ∞",
                formula="P → ∞",
            ),
            PropertyItem(
                title="Площадь",
                description="Площадь конечна и равна 8/5 площади начального треугольника",
                formula="S = 8/5 · S₀",
            ),
        ],
    ),
)


# ====================================================================
# Фрактал: Треугольник Серпинского
# ====================================================================

register_properties(
    "fractal_sierpinski_triangle",
    ShapeProperties(
        name="Треугольник Серпинского",
        properties=[
            PropertyItem(
                title="Рекурсия",
                description="Треугольник делится на 4 равных, средний удаляется",
                formula="N = 3ⁿ",
            ),
            PropertyItem(
                title="Размерность",
                description="Фрактальная размерность треугольника Серпинского",
                formula="D = lg(3) / lg(2) ≈ 1.585",
            ),
            PropertyItem(
                title="Площадь",
                description="Площадь стремится к нулю при n → ∞",
                formula="S → 0",
            ),
        ],
    ),
)


# ====================================================================
# Фрактал: Ковёр Серпинского
# ====================================================================

register_properties(
    "fractal_sierpinski_carpet",
    ShapeProperties(
        name="Ковёр Серпинского",
        properties=[
            PropertyItem(
                title="Рекурсия",
                description="Квадрат делится на 9, средний удаляется",
                formula="N = 8ⁿ",
            ),
            PropertyItem(
                title="Размерность",
                description="Фрактальная размерность ковра Серпинского",
                formula="D = lg(8) / lg(3) ≈ 1.893",
            ),
            PropertyItem(
                title="Площадь",
                description="Площадь стремится к нулю при n → ∞",
                formula="S → 0",
            ),
        ],
    ),
)


# ====================================================================
# Фрактал: Дерево Пифагора
# ====================================================================

register_properties(
    "fractal_pythagorean_tree",
    ShapeProperties(
        name="Дерево Пифагора",
        properties=[
            PropertyItem(
                title="Рекурсия",
                description="На вершине квадрата строятся два меньших квадрата по теореме Пифагора",
                formula="a² = b² + c²",
            ),
            PropertyItem(
                title="Размерность",
                description="Фрактальная размерность дерева Пифагора",
                formula="D ≈ 1.528",
            ),
            PropertyItem(
                title="Площадь",
                description="Площадь конечна при угле 45°",
                formula="S < ∞",
            ),
        ],
    ),
)


# ====================================================================
# Фрактал: Множество Кантора
# ====================================================================

register_properties(
    "fractal_cantor_set",
    ShapeProperties(
        name="Множество Кантора",
        properties=[
            PropertyItem(
                title="Рекурсия",
                description="Отрезок делится на 3, средняя треть удаляется",
                formula="N = 2ⁿ",
            ),
            PropertyItem(
                title="Размерность",
                description="Фрактальная размерность множества Кантора",
                formula="D = lg(2) / lg(3) ≈ 0.631",
            ),
            PropertyItem(
                title="Мера",
                description="Мера множества Кантора равна нулю",
                formula="μ = 0",
            ),
        ],
    ),
)


# ====================================================================
# Фрактал: Множество Мандельброта
# ====================================================================

register_properties(
    "fractal_mandelbrot",
    ShapeProperties(
        name="Множество Мандельброта",
        properties=[
            PropertyItem(
                title="Рекурсия",
                description="zₙ₊₁ = zₙ² + c",
                formula="z₀ = 0, |zₙ| ≤ 2",
            ),
            PropertyItem(
                title="Множество",
                description="Множество точек c, для которых последовательность не уходит в бесконечность",
                formula="c ∈ ℂ",
            ),
            PropertyItem(
                title="Размерность границы",
                description="Фрактальная размерность границы множества Мандельброта",
                formula="D = 2",
            ),
        ],
    ),
)


# ====================================================================
# Фрактал: Множество Жюлиа
# ====================================================================

register_properties(
    "fractal_julia",
    ShapeProperties(
        name="Множество Жюлиа",
        properties=[
            PropertyItem(
                title="Рекурсия",
                description="zₙ₊₁ = zₙ² + c (c — постоянная)",
                formula="z₀ ∈ ℂ",
            ),
            PropertyItem(
                title="Множество",
                description="Множество точек z₀, для которых последовательность не уходит в бесконечность",
                formula="|zₙ| ≤ 2",
            ),
            PropertyItem(
                title="Связность",
                description="Множество Жюлиа связно тогда и только тогда, когда c принадлежит множеству Мандельброта",
                formula="c ∈ M  →  J_c связно",
            ),
        ],
    ),
)


# ====================================================================
# Фрактал: Бассейны Ньютона
# ====================================================================

register_properties(
    "fractal_newton",
    ShapeProperties(
        name="Бассейны Ньютона",
        properties=[
            PropertyItem(
                title="Метод Ньютона",
                description="Итерационный метод нахождения корней: zₙ₊₁ = zₙ - f(zₙ)/f'(zₙ)",
                formula="zₙ₊₁ = zₙ - f(zₙ)/f'(zₙ)",
            ),
            PropertyItem(
                title="Бассейны притяжения",
                description="Каждая точка плоскости окрашивается в цвет корня, к которому сходится метод Ньютона",
                formula="zₙ → z*  (корень)",
            ),
            PropertyItem(
                title="Границы бассейнов",
                description="Границы бассейнов имеют фрактальную структуру",
                formula="D > 1",
            ),
        ],
    ),
)


# ====================================================================
# Угол
# ====================================================================

register_properties(
    "angle",
    ShapeProperties(
        name="Угол",
        properties=[
            PropertyItem(
                title="Измерение",
                description="Угол измеряется в градусах или радианах",
                formula="180° = π рад",
            ),
            PropertyItem(
                title="Виды углов",
                description="Острый (< 90°), прямой (90°), тупой (> 90°), развёрнутый (180°)",
                formula="0° < α < 180°",
            ),
            PropertyItem(
                title="Смежные углы",
                description="Сумма смежных углов равна 180°",
                formula="α + β = 180°",
            ),
            PropertyItem(
                title="Вертикальные углы",
                description="Вертикальные углы равны",
                formula="α = γ",
            ),
        ],
    ),
)


# ====================================================================
# Описанный четырёхугольник
# ====================================================================

register_properties(
    "circumscribed_quadrilateral",
    ShapeProperties(
        name="Описанный четырёхугольник",
        properties=[
            PropertyItem(
                title="Окружность",
                description="Около четырёхугольника можно описать окружность, если суммы противоположных сторон равны",
                formula="a + c = b + d",
            ),
            PropertyItem(
                title="Сумма противоположных углов",
                description="Сумма противоположных углов вписанного четырёхугольника равна 180°",
                formula="α + γ = 180°, β + δ = 180°",
            ),
            PropertyItem(
                title="Теорема Птолемея",
                description="Произведение диагоналей равно сумме произведений противоположных сторон",
                formula="AC · BD = a·c + b·d",
            ),
            PropertyItem(
                title="Площадь (Брахмагупта)",
                description="Площадь вписанного четырёхугольника",
                formula="S = √((s-a)(s-b)(s-c)(s-d))",
            ),
        ],
    ),
)


# ====================================================================
# Неправильный четырёхугольник
# ====================================================================

register_properties(
    "quadrilateral_irregular",
    ShapeProperties(
        name="Неправильный четырёхугольник",
        properties=[
            PropertyItem(
                title="Сумма углов",
                description="Сумма внутренних углов любого четырёхугольника равна 360°",
                formula="α + β + γ + δ = 360°",
            ),
            PropertyItem(
                title="Диагонали",
                description="Диагонали делят четырёхугольник на четыре треугольника",
                formula="S = S₁ + S₂ + S₃ + S₄",
            ),
            PropertyItem(
                title="Средняя линия",
                description="Средняя линия соединяет середины противоположных сторон",
                formula="m = (a + c) / 2  (для трапеции)",
            ),
            PropertyItem(
                title="Площадь (Бретшнейдер)",
                description="Площадь произвольного четырёхугольника",
                formula="S = √((s-a)(s-b)(s-c)(s-d) - abcd·cos²((α+γ)/2))",
            ),
        ],
    ),
)


# ====================================================================
# Равные треугольники
# ====================================================================

register_properties(
    "triangle_congruent",
    ShapeProperties(
        name="Равные треугольники",
        properties=[
            PropertyItem(
                title="Признаки равенства (1)",
                description="По двум сторонам и углу между ними",
                formula="a = a₁, b = b₁, γ = γ₁  →  △ = △₁",
            ),
            PropertyItem(
                title="Признаки равенства (2)",
                description="По стороне и двум прилежащим углам",
                formula="c = c₁, α = α₁, β = β₁  →  △ = △₁",
            ),
            PropertyItem(
                title="Признаки равенства (3)",
                description="По трём сторонам",
                formula="a = a₁, b = b₁, c = c₁  →  △ = △₁",
            ),
            PropertyItem(
                title="Свойства равных фигур",
                description="Соответствующие элементы равных треугольников равны",
                formula="h₁ = h₂, m₁ = m₂, b₁ = b₂",
            ),
        ],
    ),
)


# ====================================================================
# Подобные треугольники
# ====================================================================

register_properties(
    "triangle_similar",
    ShapeProperties(
        name="Подобные треугольники",
        properties=[
            PropertyItem(
                title="Признаки подобия (1)",
                description="По двум сторонам и углу между ними",
                formula="a/a₁ = b/b₁, γ = γ₁  →  △ ~ △₁",
            ),
            PropertyItem(
                title="Признаки подобия (2)",
                description="По стороне и двум прилежащим углам",
                formula="α = α₁, β = β₁  →  △ ~ △₁",
            ),
            PropertyItem(
                title="Признаки подобия (3)",
                description="По трём сторонам",
                formula="a/a₁ = b/b₁ = c/c₁  →  △ ~ △₁",
            ),
            PropertyItem(
                title="Свойства подобных фигур",
                description="Коэффициент подобия k, площади относятся как k²",
                formula="S/S₁ = k²",
            ),
        ],
    ),
)


# ====================================================================
# Треугольник Шарыгина
# ====================================================================

register_properties(
    "triangle_sharygin",
    ShapeProperties(
        name="Треугольник Шарыгина",
        properties=[
            PropertyItem(
                title="Определение",
                description="Задача Шарыгина — геометрическая задача на построение треугольника по заданным элементам",
                formula="Построение по заданным параметрам",
            ),
            PropertyItem(
                title="Свойства",
                description="Связь между медианами, биссектрисами и высотами треугольника",
                formula="m_a, m_b, m_c — медианы",
            ),
        ],
    ),
)


# ====================================================================
# Контур (Polygon)
# ====================================================================

register_properties(
    "polygon",
    ShapeProperties(
        name="Многоугольник",
        properties=[
            PropertyItem(
                title="Сумма углов",
                description="Сумма внутренних углов n-угольника",
                formula="S = (n-2) · 180°",
            ),
            PropertyItem(
                title="Число диагоналей",
                description="Число диагоналей n-угольника",
                formula="D = n(n-3)/2",
            ),
            PropertyItem(
                title="Правильный n-угольник",
                description="Все стороны и углы равны",
                formula="α = (n-2) · 180° / n",
            ),
        ],
    ),
)


# ====================================================================
# Линии (Line, Ray, InfiniteLine)
# ====================================================================

register_properties(
    "line",
    ShapeProperties(
        name="Отрезок",
        properties=[
            PropertyItem(
                title="Длина отрезка",
                description="Расстояние между двумя точками",
                formula="d = √((x₂-x₁)² + (y₂-y₁)²)",
            ),
        ],
    ),
)

register_properties(
    "ray",
    ShapeProperties(
        name="Луч",
        properties=[
            PropertyItem(
                title="Луч",
                description="Часть прямой, ограниченная с одной стороны точкой",
                formula="Начало: A, направление: v",
            ),
        ],
    ),
)

register_properties(
    "infinite_line",
    ShapeProperties(
        name="Прямая",
        properties=[
            PropertyItem(
                title="Уравнение прямой",
                description="Общий вид уравнения прямой на плоскости",
                formula="Ax + By + C = 0",
            ),
            PropertyItem(
                title="Две точки",
                description="Прямая однозначно определяется двумя точками",
                formula="(y-y₁)/(y₂-y₁) = (x-x₁)/(x₂-x₁)",
            ),
        ],
    ),
)


# ====================================================================
# Окружность (Circle)
# ====================================================================

register_properties(
    "circle",
    ShapeProperties(
        name="Окружность",
        properties=[
            PropertyItem(
                title="Радиус и диаметр",
                description="Все точки окружности равноудалены от центра",
                formula="R — радиус, d = 2R — диаметр",
            ),
            PropertyItem(
                title="Длина окружности",
                description="Произведение числа π на диаметр",
                formula="L = 2πR = πd",
            ),
            PropertyItem(
                title="Площадь круга",
                description="Произведение числа π на квадрат радиуса",
                formula="S = πR²",
            ),
            PropertyItem(
                title="Касательная",
                description="Касательная перпендикулярна радиусу в точке касания",
                formula="l ⊥ R",
            ),
        ],
    ),
)


# ====================================================================
# Эллипс (Ellipse)
# ====================================================================

register_properties(
    "ellipse",
    ShapeProperties(
        name="Эллипс",
        properties=[
            PropertyItem(
                title="Большая и малая полуоси",
                description="a — большая полуось, b — малая полуось",
                formula="a ≥ b",
            ),
            PropertyItem(
                title="Фокусы",
                description="Сумма расстояний от любой точки эллипса до фокусов постоянна",
                formula="F₁M + F₂M = 2a",
            ),
            PropertyItem(
                title="Площадь",
                description="Произведение полуосей на число π",
                formula="S = πab",
            ),
        ],
    ),
)


# ====================================================================
# Дуга (Arc)
# ====================================================================

register_properties(
    "arc",
    ShapeProperties(
        name="Дуга",
        properties=[
            PropertyItem(
                title="Длина дуги",
                description="Часть длины окружности, соответствующая центральному углу",
                formula="L = 2πR · α/360°",
            ),
            PropertyItem(
                title="Центральный угол",
                description="Угол, опирающийся на дугу",
                formula="∠ = дуга",
            ),
        ],
    ),
)


# ====================================================================
# Парабола (Parabola)
# ====================================================================

register_properties(
    "parabola",
    ShapeProperties(
        name="Парабола",
        properties=[
            PropertyItem(
                title="Уравнение",
                description="Каноническое уравнение параболы",
                formula="y = ax² + bx + c",
            ),
            PropertyItem(
                title="Ось симметрии",
                description="Парабола симметрична относительно своей оси",
                formula="x = -b/(2a)",
            ),
            PropertyItem(
                title="Вершина",
                description="Координаты вершины параболы",
                formula="V(-b/(2a), f(-b/(2a)))",
            ),
            PropertyItem(
                title="Фокус и директриса",
                description="Парабола — геометрическое место точек, равноудаленных от фокуса и директрисы",
                formula="|MF| = |Md|",
            ),
        ],
    ),
)


# ====================================================================
# Гипербола (Hyperbola)
# ====================================================================

register_properties(
    "hyperbola",
    ShapeProperties(
        name="Гипербола",
        properties=[
            PropertyItem(
                title="Уравнение",
                description="Каноническое уравнение гиперболы",
                formula="x²/a² - y²/b² = 1",
            ),
            PropertyItem(
                title="Фокусы",
                description="Гипербола — геометрическое место точек, разность расстояний до которых постоянна",
                formula="|F₁M - F₂M| = 2a",
            ),
            PropertyItem(
                title="Асимптоты",
                description="Гипербола асимптотически приближается к прямым",
                formula="y = ±(b/a)·x",
            ),
            PropertyItem(
                title="Эксцентриситет",
                description="Эксцентриситет гиперболы больше 1",
                formula="ε = c/a > 1",
            ),
        ],
    ),
)


# ====================================================================
# Ломаная (Polyline)
# ====================================================================

register_properties(
    "polyline",
    ShapeProperties(
        name="Ломаная",
        properties=[
            PropertyItem(
                title="Длина ломаной",
                description="Сумма длин всех звеньев",
                formula="L = Σ |PᵢPᵢ₊₁|",
            ),
            PropertyItem(
                title="Звенья и вершины",
                description="Ломаная состоит из звеньев и вершин",
                formula="n звеньев, n+1 вершина",
            ),
        ],
    ),
)


# ====================================================================
# Карандаш (Pencil)
# ====================================================================

register_properties(
    "pencil",
    ShapeProperties(
        name="Карандаш",
        properties=[
            PropertyItem(
                title="Свободный рисунок",
                description="Кривая, построенная по точкам следования курсора",
                formula="Параметрическая кривая",
            ),
        ],
    ),
)


# ====================================================================
# Текст (Text)
# ====================================================================

register_properties(
    "text",
    ShapeProperties(
        name="Текст",
        properties=[
            PropertyItem(
                title="Шрифт",
                description="Параметры шрифта: семейство, размер, начертание",
                formula="font-family, font-size, font-weight",
            ),
            PropertyItem(
                title="Позиция",
                description="Координаты начала текста",
                formula="(x, y)",
            ),
        ],
    ),
)


# ====================================================================
# Формула (Formula)
# ====================================================================

register_properties(
    "formula",
    ShapeProperties(
        name="Формула",
        properties=[
            PropertyItem(
                title="LaTeX-формула",
                description="Формула, отрисованная с использованием LaTeX-рендеринга",
                formula="Формат: \\frac{a}{b}",
            ),
            PropertyItem(
                title="Позиция",
                description="Координаты размещения формулы",
                formula="(x, y)",
            ),
        ],
    ),
)


# ====================================================================
# График функции (Graph)
# ====================================================================

register_properties(
    "graph",
    ShapeProperties(
        name="График функции",
        properties=[
            PropertyItem(
                title="Функция",
                description="Аналитическое выражение функции",
                formula="y = f(x)",
            ),
            PropertyItem(
                title="Область определения",
                description="Множество значений x, для которых функция определена",
                formula="D(f)",
            ),
            PropertyItem(
                title="Область значений",
                description="Множество значений y, которые принимает функция",
                formula="E(f)",
            ),
        ],
    ),
)
