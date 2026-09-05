"""Lightweight client-side i18n. English is the source language and the
fallback; GUI/status/error strings pass through tr() before being shown."""
import os

LANGUAGES = {
    'en': 'English',
    'ja': '日本語',
    'zh': '中文',
    'ru': 'Русский',
    'ko': '조선말',
}

_current = 'en'


def detect():
    text = os.environ.get('LC_ALL', '') or os.environ.get('LC_MESSAGES', '') or os.environ.get('LANG', '')
    tag = text.split('.')[0].split('_')[0].lower()
    if tag == 'ja':
        return 'ja'
    if tag in ('zh', 'zh_cn', 'zh_tw', 'zh_hk'):
        return 'zh'
    if tag == 'ru':
        return 'ru'
    if tag == 'ko':
        return 'ko'
    return 'en'


def current():
    return _current


def set_language(code):
    global _current
    if code in LANGUAGES:
        _current = code


T = {
 # -- app.py ----------------------------------------------
 'Convert an image to pixel art and draw it into LibreSprite': {
   'ja': '画像をドット絵に変換 → LibreSpriteへマウスで転写',
   'zh': '将图片转换为像素画，并用鼠标绘制到 LibreSprite',
   'ru': 'Преобразование в пиксель-арт и перенос в LibreSprite мышью',
   'ko': '이미지를 픽셀아트로 변환해 LibreSprite에 마우스로 그리기'},
 'Choose an image (PNG / JPEG / WebP / BMP / GIF)': {
   'ja': '画像を選択してください（PNG / JPEG / WebP / BMP / GIF）',
   'zh': '请选择图片（PNG / JPEG / WebP / BMP / GIF）',
   'ru': 'Выберите изображение (PNG / JPEG / WebP / BMP / GIF)',
   'ko': '이미지를 선택하세요 (PNG / JPEG / WebP / BMP / GIF)'},
 'Open image': {'ja': '画像を開く', 'zh': '打开图片', 'ru': 'Открыть изображение', 'ko': '이미지 열기'},
 'Sample': {'ja': 'サンプル', 'zh': '示例', 'ru': 'Образец', 'ko': '샘플'},
 'Width': {'ja': '幅', 'zh': '宽度', 'ru': 'Ширина', 'ko': '너비'},
 'Height': {'ja': '高さ', 'zh': '高度', 'ru': 'Высота', 'ko': '높이'},
 'Colors': {'ja': '色数', 'zh': '颜色数', 'ru': 'Цвета', 'ko': '색상 수'},
 'Dither': {'ja': 'ディザ', 'zh': '抖动', 'ru': 'Дизеринг', 'ko': '디더'},
 'Preview': {'ja': 'プレビュー', 'zh': '预览', 'ru': 'Предпросмотр', 'ko': '미리보기'},
 'Save PNG art': {'ja': '変換PNGを保存', 'zh': '保存转换后的PNG', 'ru': 'Сохранить PNG-арт', 'ko': '변환 PNG 저장'},
 'Open transfer image in LibreSprite': {
   'ja': '転写用画像をLibreSpriteで開く', 'zh': '在LibreSprite中打开转写用图片',
   'ru': 'Открыть изображение-шаблон в LibreSprite', 'ko': '전사용 이미지를 LibreSprite에서 열기'},
 'Instructions': {
   'en': ('1. Open the transfer image and show the whole image (including the color swatch row below) '
          'at an integer zoom.\n'
          '   About 3200% is recommended (press key 6; fine-tune with Ctrl++ / Ctrl+-).\n'
          '2. Press B to pick the pencil: 1 px brush, opacity 255, normal ink, mirroring OFF.\n'
          '3. Press a coordinate button below, then within 5 s click LibreSprite\'s title bar and place '
          'the mouse on the pixel center of the image\'s top-left / bottom-right\n'
          '   (the bottom-right includes the empty pixel to the right of the swatches).\n'
          '4. Within 5 s after it starts, click the transfer image. Do not move the mouse or zoom afterwards.\n'
          'Stop: press ESC twice within 1 s ／ switch to another window ／ the Stop button below.'),
   'ja': ('① 転写用画像を開き、全体（下の色見本を含む）が収まる整数倍率で表示。\n'
          '   おすすめは約3200%（キー6で切替、Ctrl++で微調整）で、見やすくバランスが良い。\n'
          '② Bキーで鉛筆を選び、ブラシ1px・不透明度255・通常インク・左右対称OFF。\n'
          '③ 下の座標ボタンを押し、5秒以内にLibreSpriteのタイトルバーをクリックしてから、\n'
          '   画像全体の左上／右下のピクセル中心にマウスを置く（右下は色見本より右の空き含む）。\n'
          '④ 開始後5秒以内に転写用画像をクリック。以降はマウス・ズームを動かさない。\n'
          '停止：ESCを1秒以内に2回 ／ 別ウィンドウへ移動 ／ 下の停止ボタン。'),
   'zh': ('1. 打开转写用图片，以整数倍率显示整体（含下方的色样行）。\n'
          '   推荐约 3200%（按数字键 6 切换，Ctrl++ / Ctrl+- 微调），清晰且均衡。\n'
          '2. 按 B 选择铅笔：1px 画笔、不透明度 255、普通墨水、左右对称关闭。\n'
          '3. 按下方坐标按钮，5 秒内点击 LibreSprite 的标题栏，然后把鼠标放到\n'
          '   整张图片左上角 / 右下角的像素中心（右下含色样右侧的空像素）。\n'
          '4. 开始后 5 秒内点击转写用图片。之后不要移动鼠标或改变缩放。\n'
          '停止：1 秒内按两次 ESC ／ 切换到其他窗口 ／ 按下方的停止按钮。'),
   'ru': ('1. Откройте изображение-шаблон и покажите его целиком (включая нижний ряд образцов) '
          'в целочисленном масштабе.\n'
          '   Рекомендуется около 3200% (клавиша 6; Ctrl++ / Ctrl+- для точной настройки).\n'
          '2. Нажмите B — карандаш: кисть 1px, непрозрачность 255, обычные чернила, симметрия выкл.\n'
          '3. Нажмите кнопку координат ниже и в течение 5 с кликните заголовок LibreSprite, затем '
          'наведите мышь на центр верхнего левого / нижнего правого пикселя всего изображения '
          '(нижний правый включает пустой пиксель справа от образцов).\n'
          '4. В течение 5 с после старта кликните изображение-шаблон. Далее не двигайте мышь и не меняйте масштаб.\n'
          'Стоп: ESC дважды за 1 с ／ переключиться в другое окно ／ кнопка «Стоп» ниже.'),
   'ko': ('1. 전사용 이미지를 열고 전체(아래 색상 견본 포함)가 보이도록 정수 배율로 표시합니다.\n'
          '   권장: 약 3200%(숫자 6 키로 전환, Ctrl++/Ctrl+- 미세 조정) — 보기 좋고 균형 잡힘.\n'
          '2. B 키로 연필 선택: 브러시 1px, 불투명도 255, 일반 잉크, 좌우 대칭 끄기.\n'
          '3. 아래 좌표 버튼을 누른 뒤 5초 안에 LibreSprite 제목 표시줄을 클릭하고,\n'
          '   전체 이미지의 왼쪽 위/오른쪽 아래 픽셀 중심에 마우스를 둡니다(오른쪽 아래는 견본 오른쪽 빈 픽셀 포함).\n'
          '4. 시작 후 5초 안에 전사용 이미지를 클릭합니다. 이후 마우스·확대는 움직이지 마세요.\n'
          '중지: 1초 안에 ESC 두 번 ／ 다른 창으로 전환 ／ 아래 중지 버튼.')},
 'Specify top-left center (5 s)': {'ja': '左上の中心を指定（5秒）', 'zh': '指定左上角中心（5秒）',
   'ru': 'Задать центр левого верхнего (5 с)', 'ko': '왼쪽 위 중심 지정(5초)'},
 'Specify bottom-right center (5 s)': {'ja': '右下の中心を指定（5秒）', 'zh': '指定右下角中心（5秒）',
   'ru': 'Задать центр правого нижнего (5 с)', 'ko': '오른쪽 아래 중심 지정(5초)'},
 'Coordinates not set': {'ja': '座標未設定', 'zh': '坐标未设置', 'ru': 'Координаты не заданы', 'ko': '좌표 미설정'},
 'Delay per operation (s)': {'ja': '1操作の待機時間（秒）', 'zh': '每次操作的等待时间（秒）',
   'ru': 'Пауза на операцию (с)', 'ko': '작업 사이 대기 시간(초)'},
 'Confirmed transfer image, 1 px pencil and zoom': {
   'ja': '転写用画像・1px鉛筆・表示倍率を確認した', 'zh': '已确认转写用图片、1px 铅笔和缩放倍率',
   'ru': 'Подтверждаю: шаблон, карандаш 1px и масштаб', 'ko': '전사용 이미지·1px 연필·배율 확인함'},
 'Start automatic transfer in 5 s': {'ja': '5秒後に自動転写を開始', 'zh': '5 秒后开始自动转写',
   'ru': 'Начать автоперенос через 5 с', 'ko': '5초 후 자동 전사 시작'},
 'Idle - the source image is never modified.': {
   'ja': '待機中 — 元画像は変更しません。', 'zh': '空闲 — 原始图片不会被修改。',
   'ru': 'Ожидание — исходное изображение не изменяется.', 'ko': '대기 중 — 원본 이미지는 변경되지 않습니다.'},
 'Stop automatic operation': {'ja': '■ 自動操作を停止', 'zh': '■ 停止自动操作',
   'ru': '■ Остановить автоперенос', 'ko': '■ 자동 작업 중지'},
 'Source image': {'ja': '元画像', 'zh': '原始图片', 'ru': 'Исходное изображение', 'ko': '원본 이미지'},
 'Images (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;All files (*)': {
   'ja': '画像 (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;すべて (*)',
   'zh': '图片 (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;所有文件 (*)',
   'ru': 'Изображения (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;Все файлы (*)',
   'ko': '이미지 (*.png *.jpg *.jpeg *.webp *.bmp *.gif);;모든 파일 (*)'},
 'Save pixel-art PNG': {'ja': 'ドット絵PNGを保存', 'zh': '保存像素画PNG', 'ru': 'Сохранить пиксель-арт PNG',
   'ko': '픽셀아트 PNG 저장'},
 'Saved: {path}': {'ja': '保存しました: {path}', 'zh': '已保存: {path}', 'ru': 'Сохранено: {path}',
   'ko': '저장했습니다: {path}'},
 'Choose a source image first.': {'ja': '先に元画像を選択してください。', 'zh': '请先选择原始图片。',
   'ru': 'Сначала выберите исходное изображение.', 'ko': '먼저 원본 이미지를 선택하세요.'},
 'Coordinates not set (re-specify after changing the image)': {
   'ja': '座標未設定（画像変更後は再指定）', 'zh': '坐标未设置（更换图片后需重新指定）',
   'ru': 'Координаты не заданы (задайте снова после смены изображения)',
   'ko': '좌표 미설정(이미지 변경 후 재지정)'},
 'Specify coordinates on the new transfer image.': {
   'ja': '新しい転写用画像の座標を指定してください。', 'zh': '请在新的转写用图片上指定坐标。',
   'ru': 'Задайте координаты на новом изображении-шаблоне.', 'ko': '새 전사용 이미지에서 좌표를 지정하세요.'},
 'Transfer image {w} x {h} px. The bottom row holds the color swatches.': {
   'ja': '転写用画像 {w} × {h} px。下端は色見本です。', 'zh': '转写用图片 {w} × {h} px。下方一行是色样。',
   'ru': 'Изображение-шаблон {w} × {h} px. В нижнем ряду — образцы цветов.',
   'ko': '전사용 이미지 {w} × {h} px. 아래쪽 행이 색상 견본입니다.'},
 'Within 5 s click LibreSprite, then place the mouse on the requested position.': {
   'ja': '5秒以内にLibreSpriteをクリックし、指定位置へマウスを移動してください。',
   'zh': '请在 5 秒内点击 LibreSprite，然后把鼠标移动到指定位置。',
   'ru': 'В течение 5 с кликните LibreSprite и наведите мышь на нужное место.',
   'ko': '5초 안에 LibreSprite를 클릭하고, 지정한 위치로 마우스를 옮기세요.'},
 'Coordinates recorded.': {'ja': '座標を記録しました。', 'zh': '坐标已记录。', 'ru': 'Координаты записаны.',
   'ko': '좌표를 기록했습니다.'},
 'Specify the two points in the same LibreSprite window.': {
   'ja': '同じLibreSpriteウィンドウの2点を指定してください。', 'zh': '请在同一个 LibreSprite 窗口中指定两个点。',
   'ru': 'Задайте обе точки в одном окне LibreSprite.', 'ko': '같은 LibreSprite 창에서 두 점을 지정하세요.'},
 'A source image, two coordinate points and the ready checkbox are required.': {
   'ja': '元画像・座標2点・準備確認のチェックが必要です。', 'zh': '需要原始图片、两个坐标点和准备确认勾选。',
   'ru': 'Нужны исходное изображение, две точки и отметка готовности.',
   'ko': '원본 이미지·좌표 2점·준비 확인 체크가 필요합니다.'},
 'Operation stopped: {exc}': {'ja': '操作を停止しました: {exc}', 'zh': '操作已停止: {exc}',
   'ru': 'Операция остановлена: {exc}', 'ko': '작업을 중지했습니다: {exc}'},
 ' Partial drawing stays in LibreSprite.': {
   'ja': ' 途中の描画はLibreSpriteに残っています。', 'zh': ' 已画出的部分保留在 LibreSprite 中。',
   'ru': ' Частично нарисованное остаётся в LibreSprite.', 'ko': ' 그린 일부는 LibreSprite에 남아 있습니다.'},
 'top-left': {'ja': '左上', 'zh': '左上', 'ru': 'верх-лево', 'ko': '왼쪽 위'},
 'bottom-right': {'ja': '右下', 'zh': '右下', 'ru': 'низ-право', 'ko': '오른쪽 아래'},
 '{w} x {h} px ・ {n} colors ・ {clicks:,} clicks + picks ・ alpha<128 skipped': {
   'ja': '{w} × {h} px ・ {n}色 ・ {clicks:,}クリック + 色選択 ・ 透明度128未満は描画省略',
   'zh': '{w} × {h} px ・ {n} 色 ・ {clicks:,} 次点击 + 取色 ・ 透明度低于128的像素跳过',
   'ru': '{w} × {h} px ・ {n} цветов ・ {clicks:,} кликов + выбор цветов ・ прозрачность <128 пропускается',
   'ko': '{w} × {h} px ・ {n}색 ・ {clicks:,}클릭 + 색 선택 ・ 투명도 128 미만은 생략'},
 'Language': {'ja': '言語', 'zh': '语言', 'ru': 'Язык', 'ko': '언어'},
 'Tone': {'ja': '色調', 'zh': '色调', 'ru': 'Тон', 'ko': '색조'},
 'Brightness': {'ja': '明度', 'zh': '亮度', 'ru': 'Яркость', 'ko': '밝기'},
 'Contrast': {'ja': 'コントラスト', 'zh': '对比度', 'ru': 'Контраст', 'ko': '대비'},
 'Saturation': {'ja': '彩度', 'zh': '饱和度', 'ru': 'Насыщенность', 'ko': '채도'},
 'Hue': {'ja': '色相', 'zh': '色相', 'ru': 'Тон (оттенок)', 'ko': '색상'},
 'Palette': {'ja': 'パレット', 'zh': '调色板', 'ru': 'Палитра', 'ko': '팔레트'},
 'Auto': {'ja': '自動（画像の色）', 'zh': '自动（图片颜色）', 'ru': 'Авто (цвета изображения)', 'ko': '자동(이미지 색상)'},
 'Unknown palette preset.': {'ja': '不明なパレットです。', 'zh': '未知的调色板。', 'ru': 'Неизвестная палитра.', 'ko': '알 수 없는 팔레트입니다.'},
 'Environment check': {'ja': '環境チェック', 'zh': '环境检查', 'ru': 'Проверка окружения', 'ko': '환경 확인'},
 'Checking environment...': {'ja': '環境をチェックしています…', 'zh': '正在检查环境…', 'ru': 'Проверка окружения…', 'ko': '환경을 확인하는 중…'},
 'DONE': {'ja': 'DONE', 'zh': '完成', 'ru': 'ГОТОВО', 'ko': '완료'},
 'All environment checks passed.': {
   'ja': 'すべての環境チェックに合格しました。', 'zh': '所有环境检查均已通过。',
   'ru': 'Все проверки окружения пройдены.', 'ko': '모든 환경 확인을 통과했습니다.'},
 'Warnings found:': {'ja': '警告があります:', 'zh': '存在警告:', 'ru': 'Обнаружены предупреждения:', 'ko': '경고가 있습니다:'},
 'Display server found (Wayland/X11)': {'ja': '表示サーバを検出（Wayland/X11）', 'zh': '已检测到显示服务器（Wayland/X11）',
   'ru': 'Сервер отображения найден (Wayland/X11)', 'ko': '디스플레이 서버 감지됨 (Wayland/X11)'},
 'No display server found (need Wayland or X11).': {
   'ja': '表示サーバが見つかりません（WaylandかX11が必要）。',
   'zh': '未检测到显示服务器（需要 Wayland 或 X11）。',
   'ru': 'Сервер отображения не найден (нужен Wayland или X11).',
   'ko': '디스플레이 서버를 찾을 수 없습니다 (Wayland 또는 X11 필요).'},
 'LibreSprite found': {'ja': 'LibreSprite を検出', 'zh': '已检测到 LibreSprite', 'ru': 'LibreSprite найден', 'ko': 'LibreSprite 감지됨'},
 'LibreSprite not found. Install it to use the transfer feature.': {
   'ja': 'LibreSprite が見つかりません。転写機能にはインストールが必要です。',
   'zh': '未检测到 LibreSprite。使用转写功能需要安装。',
   'ru': 'LibreSprite не найден. Установите его для функции переноса.',
   'ko': 'LibreSprite를 찾을 수 없습니다. 전사 기능에 설치가 필요합니다.'},
 'Input method (IME) available': {'ja': '入力メソッド(IME)を利用可能', 'zh': '输入法(IME)可用',
   'ru': 'Метод ввода (IME) доступен', 'ko': '입력기(IME) 사용 가능'},
 'No IME found; keyboard shortcuts may behave differently.': {
   'ja': 'IMEが見つかりません。キーボード操作が通常と異なる場合があります。',
   'zh': '未检测到输入法；快捷键行为可能不同。',
   'ru': 'Метод ввода не найден; сочетания клавиш могут работать иначе.',
   'ko': '입력기를 찾을 수 없습니다. 단축키 동작이 다를 수 있습니다.'},
 '/dev/uinput writable': {'ja': '/dev/uinput に書き込み可能', 'zh': '/dev/uinput 可写',
   'ru': '/dev/uinput доступен для записи', 'ko': '/dev/uinput 쓰기 가능'},
 'No write access to /dev/uinput. Join the uinput group or add a udev rule.': {
   'ja': '/dev/uinput に書き込めません。uinputグループへ加入するかudevルールを追加してください。',
   'zh': '无法写入 /dev/uinput。请加入 uinput 组或添加 udev 规则。',
   'ru': 'Нет доступа к /dev/uinput. Войдите в группу uinput или добавьте правило udev.',
   'ko': '/dev/uinput에 쓸 수 없습니다. uinput 그룹에 가입하거나 udev 규칙을 추가하세요.'},
 'Done. Transferred {count} pixels.': {
   'ja': '完了。{count} ピクセルを転写しました。',
   'zh': '完成。已转写 {count} 个像素。',
   'ru': 'Готово. Перенесено {count} пикселей.',
   'ko': '완료. {count} 픽셀을 전사했습니다.'},

 # -- automation.py ---------------------------------------
 'Stopped because focus, window position or the document changed.': {
   'ja': 'フォーカス・ウィンドウ位置・ドキュメントが変わったため停止しました。',
   'zh': '焦点、窗口位置或文档发生变化，已停止。',
   'ru': 'Остановлено: изменились фокус, положение окна или документ.',
   'ko': '포커스·창 위치·문서가 바뀌어 중지했습니다.'},
 'Stopped.': {'ja': '停止しました。', 'zh': '已停止。', 'ru': 'Остановлено.', 'ko': '중지했습니다.'},
 'Stopped: ESC pressed twice.': {'ja': 'ESCを2回検出したため停止しました。',
   'zh': '检测到 ESC 按了两次，已停止。', 'ru': 'Остановлено: ESC нажат дважды.',
   'ko': 'ESC 두 번 입력으로 중지했습니다.'},
 'Stop-key monitor failed: {exc}': {'ja': '停止キーの監視が失敗しました: {exc}',
   'zh': '停止键监视失败: {exc}', 'ru': 'Сбой монитора клавиши стопа: {exc}',
   'ko': '중지 키 감시 실패: {exc}'},
 'XTEST extension is not available.': {'ja': 'XTEST拡張が利用できません。',
   'zh': '无法使用 XTEST 扩展。', 'ru': 'Расширение XTEST недоступно.', 'ko': 'XTEST 확장을 사용할 수 없습니다.'},
 'Click LibreSprite first, then put the mouse on the image.': {
   'ja': 'LibreSpriteをクリックしてから、その画像上にマウスを置いてください。',
   'zh': '请先点击 LibreSprite，再把鼠标放到该图片上。',
   'ru': 'Сначала кликните LibreSprite, затем наведите мышь на его изображение.',
   'ko': 'LibreSprite를 클릭한 다음 이미지 위에 마우스를 두세요.'},
 '{second} s to start. Click the LibreSprite transfer image.': {
   'ja': '{second}秒後に開始。LibreSpriteの転写用画像をクリックしてください。',
   'zh': '{second} 秒后开始。请点击 LibreSprite 中的转写用图片。',
   'ru': '{second} с до старта. Кликните изображение-шаблон в LibreSprite.',
   'ko': '{second}초 후 시작. LibreSprite의 전사용 이미지를 클릭하세요.'},
 'The specified coordinates are outside the LibreSprite window.': {
   'ja': '指定した座標がLibreSpriteウィンドウの外にあります。',
   'zh': '指定的坐标在 LibreSprite 窗口之外。',
   'ru': 'Заданные координаты вне окна LibreSprite.',
   'ko': '지정한 좌표가 LibreSprite 창 밖에 있습니다.'},
 'Drawing {done:,} / {total:,} px': {'ja': '描画中 {done:,} / {total:,} px',
   'zh': '绘制中 {done:,} / {total:,} px', 'ru': 'Рисование {done:,} / {total:,} px',
   'ko': '그리는 중 {done:,} / {total:,} px'},
 'Done: transferred {done:,} pixels by clicking.': {
   'ja': '完了: {done:,}ピクセルをクリックして転写しました。',
   'zh': '完成: 已通过 {done:,} 次点击完成转写。',
   'ru': 'Готово: перенесено {done:,} пикселей кликами.',
   'ko': '완료: {done:,}픽셀을 클릭해 전사했습니다.'},

 # -- core.py ---------------------------------------------
 'Width/height must be 2-256 and colors 2-64.': {
   'ja': 'サイズは2〜256、色数は2〜64にしてください。',
   'zh': '宽高需为 2–256，颜色数需为 2–64。',
   'ru': 'Размер 2–256, количество цветов 2–64.',
   'ko': '크기는 2~256, 색상 수는 2~64로 하세요.'},
 'No opaque pixel to draw.': {'ja': '描画できる不透明ピクセルがありません。',
   'zh': '没有可绘制的不透明像素。', 'ru': 'Нет непрозрачных пикселей для рисования.',
   'ko': '그릴 수 있는 불투명 픽셀이 없습니다.'},
 'Show the whole image (incl. the empty pixel on the bottom-right) at about 3200% or another integer zoom, then specify the top-left and bottom-right pixel centers again.': {
   'ja': '全画像（右下の空きピクセルまで）を約3200%など整数倍率で表示し、左上と右下のピクセル中心を再指定してください。',
   'zh': '请以约 3200% 等整数倍率显示整张图片（含右下角的空像素），然后重新指定左上和右下像素的中心。',
   'ru': 'Покажите всё изображение (включая пустой пиксель в правом нижнем углу) примерно в 3200% или другом целом масштабе и задайте центры верхнего левого и нижнего правого пикселей заново.',
   'ko': '전체 이미지(오른쪽 아래 빈 픽셀 포함)를 약 3200% 등 정수 배율로 표시하고, 왼쪽 위/오른쪽 아래 픽셀 중심을 다시 지정하세요.'},
}


def tr(template):
    """Translate an English template to the current language.
    Unknown strings are returned unchanged."""
    entry = T.get(template)
    if not entry:
        return template
    return entry.get(_current, template)


def set_language_from_env():
    set_language(detect())
