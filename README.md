# Pixel Operator

画像を縮小・減色して、LibreSpriteへマウス操作でドット絵を描くGUI。
元画像とは別の、透明キャンバスと色見本を持つ新規PNGを使用します。
画面は **English / 日本語 / 中文 / русский / 조선말** に対応しており、起動時のOS言語を自動検出します。
GUI右上の「言語 / Language / 语言 / Язык / 언어」でいつでも切り替えられます（再起動不要）。

> 注: このリポジトリは開発用です。ローカルで動かす場合は下の「起動」を、
> 配布用のAppImageビルドは「AppImage 配布」を参照してください。

## 起動

```sh
python3 /home/yomiplush/Projects/pixel-operator/app.py
```

依存: Python 3、PySide6、Pillow、python-xlib、LibreSprite。現在のPCには導入済み。
実行中のデスクトップセッションから起動してください。

## 使い方

1. 「画像を開く」で元画像を選び、幅・高さ・色数を調整。まず32×32・16色がおすすめ。
2. 「転写用画像をLibreSpriteで開く」。この画像の上部が描画領域、下端が色見本です。
3. LibreSpriteで転写用画像を整数倍率で表示します。**おすすめは約3200%**（キー6で切替、Ctrl++ / Ctrl+- で調整）で、全体が画面内に収まるようにします。鉛筆（B）を1px、通常インク、不透明度255にし、対称描画をOFFにしてください。選択範囲も解除します。
4. GUIの左上・右下指定ボタンをそれぞれ押し、5秒以内にLibreSpriteをクリックしてから、画像全体の該当ピクセル中心へマウスを置きます。右下は**色見本より右の空きピクセルを含む画像全体の右下端**です。
5. 確認欄をチェックし開始。5秒以内にLibreSpriteの転写用画像へフォーカスを移します。
6. スポイト（I）で色見本を拾い、鉛筆（B）で各ピクセルを実際にクリックします。
7. 完了後、LibreSpriteで別名保存。下の色見本が不要ならキャンバスを指定した元の幅・高さに切り詰めてください。「変換PNGを保存」では色見本のない完成画像を直接保存できます。

## 停止

- ESCを1秒以内に2回押す。押しっぱなしは二度押しになりません。
- 別のウィンドウへ切り替えると停止します。
- GUIの停止ボタン、またはGUIを閉じる操作でも停止します。
- 中断した描画は残ります。再開機能はありません。新しい転写用画像でやり直せます。

自動操作中は表示倍率・スクロール・ツール・レイヤー・タブを変更しないでください。
ウィンドウ移動・サイズ変更・フォーカス変更を検知すると停止します。
ショートカットを変更している場合、LibreSpriteのI＝スポイト、B＝鉛筆へ戻してください。
透明度128未満は省略、それ以外は不透明色になります。画像の縦横比は保持し、余白は透明になります。
約3200%前後がバランス良く、ピクセル中心を正確にクリックできます。画像が大きい場合は全体が収まる範囲で調整してください。
mozc/fcitxが全角入力のままだとB・Iなどのキーが奪われて動作しません。自動操作の直前・各キー送信前にIME状態を確認し、activeの場合は半角（直接入力）へ自動で切り替えます。
処理中に元画像を保存・上書きする操作は行いません。

## AppImage 配布（設計）

Pixel-Operator本体（Python + PySide6 + Pillow + python-xlib + evdev）を
1つのAppImageに同梱し、**実行環境を自動検出してセットアップ**します。

### 同梱 / 非同梱の割り切り

| 対象 | 扱い |
|---|---|
| Python 3、PySide6、Pillow、python-xlib、evdev、i18n データ | **AppImageへ同梱**（推定150〜250MB） |
| LibreSprite 本体 | 同梱せず、**システムに導入済みのもの**を使う（AUR/ソースでのみ配布のため） |
| X11/Wayland・`niri`・`fcitx5`・`/dev/uinput` 権限 | 起動時の自動検出で確認し、不足時は対処方法を表示 |

### 自動検出（`packaging/AppRun`）

AppImage起動時に以下を検出し、GUI起動前/起動後に案内します。

1. 表示サーバ — `$WAYLAND_DISPLAY` / `$DISPLAY`
2. `libresprite` の有無（無ければインストール手順を案内）
3. IME (`fcitx5-remote`) の有無 — あれば全角対策を自動適用
4. `/dev/uinput` の書き込み権限（仮想キーボード用。無ければ `uinput` グループ加入を案内）
5. Qt のプラットフォーム選択（Wayland があれば `wayland`、無ければ `xcb`）

### GitHub Actions 自動ビルド（`.github/workflows/appimage.yml`）

- トリガー: `v*` タグのpush、および workflow_dispatch（手動）
- Ubuntu上で `pydist` + PySide6等をAppDirへ展開し、`appimagetool` でAppImage化
- 成果物を GitHub Release の `assets` へ自動アップロード

手動リリース例:
```sh
git tag v1.0.0 && git push origin v1.0.0
```

## 開発と検証

```sh
cd /home/yomiplush/Projects/pixel-operator
python3 -m unittest -v
```

`core.py`: 画像処理と座標、`automation.py`: 入力・停止監視、`app.py`: GUI、`i18n.py`: 多言語翻訳。
`desktop_check.py`: integration-transferという名前の新規テスト画像だけを操作する検証用。
サンプルは本プロジェクトで作成したオリジナルのテスト用スプライトです。
利用するOSS: [Pillow](https://github.com/python-pillow/Pillow)、[PySide6](https://doc.qt.io/qtforpython-6/)、[python-xlib](https://github.com/python-xlib/python-xlib)、[LibreSprite](https://github.com/LibreSprite/LibreSprite)。ライブラリ自体は再配布せず、インストール済みのものを利用します。
