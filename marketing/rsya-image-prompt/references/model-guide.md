# Шпаргалка по моделям и типам сцен для РСЯ / ЕПК

## Адаптация под популярные модели

### Gemini / Nano Banana (Image) и GPT Image
- **Стиль промпта**: развёрнутый естественный язык (как ТЗ фотографу), полные предложения вместо списка тегов через запятую.
- **Сильные стороны**: точно понимают пространственные инструкции («оставь чистый фон по краям для обрезки», «объект строго по центру»), хорошо держат реалистичный свет и бытовую естественность.
- **Важно**: избегать длинных списков `no X, no Y`; лучше описывать желаемое состояние позитивно (*clean smooth wall in the background, unobstructed frame*).

### Flux (Dev / Pro / Schnell)
- **Стиль промпта**: чёткое описательное предложение с акцентом на камеру, объектив, свет и текстуры; не требует «магических слов» вроде *8k, masterpiece*.
- **Сильные стороны**: фотореализм, естественная кожа, отличная предметная съёмка и оптика (глубина резкости `shallow depth of field`, `85mm lens`, `soft window light`).
- **Важно**: явно указывать точное соотношение сторон в параметрах генерации (для `WIDE` ЕПК — строго `16:9`, например `1344×768` не подойдёт как `WIDE` — нужен ресайз/кроп до `1920×1080` или `1280×720`).

### Midjourney (v6 / v6.1+)
- **Стиль промпта**: более компактный, структурный, с явными параметрами в конце (`--ar 16:9`, `--ar 1:1`, `--ar 3:4`, `--style raw` для снижения «нейросетевого глянца»).
- **Сильные стороны**: высокий визуальный стоп-эффект, выразительный свет и цвет.
- **Важно**: обязательно добавлять `--style raw` для медицинских, сервисных и B2B-креативов, иначе картинка выглядит слишком «киношно-рекламной».

### Ideogram / Recraft
- **Стиль промпта**: чёткое описание композиции + если всё-таки нужен минимальный брендовый знак или крупная короткая надпись на русском (строго < 15–20% площади), эти модели лучше остальных справляются с типографикой.
- **Для РСЯ**: даже здесь по умолчанию лучше генерировать чистую картинку без текста, а тексты отдавать в поля ЕПК.

---

## 4 проверенные формулы сцен для РСЯ

### 1. Чистая предметная / продуктовая съёмка (E-commerce, товары, оборудование)
- **Суть**: один крупный объект в центре, чистый контрастный фон, мягкий направленный свет, лёгкая естественная тень.
- **Паттерн**:
  `Studio product photograph of [объект] placed in the exact center on a [поверхность], surrounded by generous clean [цвет] negative space for cropping. Soft directional daylight from the left, crisp textures, subtle natural shadow, high contrast between subject and background, shot on 85mm lens, clean uncluttered frame without text or logos.`

### 2. Спокойный результат услуги / комфорт (Медицина, стоматология, красота, сервисы)
- **Суть**: фокус на позитивном результате и доверии — никакой «боли», инструментов, крови и коллажей «до/после».
- **Паттерн**:
  `Candid natural-light portrait of a [описание человека/ЦА] smiling calmly in a bright modern interior, framed from chest up in the center with ample clean blurred background around the edges. Warm natural window light, authentic skin texture, relaxed confident expression, photorealistic editorial photography, 50mm lens, shallow depth of field, no text, no watermarks.`

### 3. Живая нативная сцена (Анти-баннерная слепота)
- **Суть**: выглядит как живой кадр из жизни, а не стоковая реклама — отлично пробивает баннерную слепоту в лентах РСЯ.
- **Паттерн**:
  `Authentic lifestyle photograph of [1 человек в понятной бытовой ситуации с продуктом/результатом], centered subject with breathing room on all sides. Soft natural daylight, slightly warm tones, realistic candid moment, shot on 35mm lens, clean background without visual clutter, no overlays or text.`

### 4. Пространство и экспертность (Клиники, офисы, локальный бизнес)
- **Суть**: чистое современное помещение или уверенный специалист в светлом интерьере — снимает страх перед первым визитом.
- **Паттерн**:
  `Editorial interior photograph of a bright modern [тип помещения] with [1 ключевой визуальный акцент] in the center, balanced composition with open clean space along the margins for square and widescreen cropping. Soft natural daylight, clean architectural lines, welcoming calm atmosphere, realistic photography, no signage text or watermarks.`

---

## Быстрые правки типовых проблем

| Проблема на генерации | Что добавить / изменить в промпте |
|---|---|
| Объект обрезается в `1:1` или `16:9` | `centered composition, generous clean negative space on all four sides, medium shot` |
| В тизере `120×90` всё сливается в кашу | Убрать второстепенные предметы, приблизить план (`close-up` / `medium close-up`), усилить контраст объекта и фона |
| «Пластиковые» лица / стоковый глянец | `authentic skin texture, candid natural lighting, unretouched editorial photography` (в MJ: `--style raw`) |
| Нейросеть дорисовывает мусорный текст | `clean seamless background, plain surfaces without any letters, signs, labels, or watermarks` |
| Коллаж «до/после» в медицине | `single continuous undivided photograph` + описывать только конечный позитивный результат |
