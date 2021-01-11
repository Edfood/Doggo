# Doggo
ゲームのプレイ時間を可視化・警告するためのDiscord Botです。

公開しています: **[DiscordサーバにBotを招待](https://discord.com/api/oauth2/authorize?client_id=750754316326928495&permissions=1073925120&scope=bot)**

## 使い方
下記の手順でセットアップしてください。
1. サーバーにBotを招待
2. Botを招待したサーバーのチャットもしくはBotへのDMで`$register`を送信 

`$register`を送信してから、十分な時間が経つまではプレイ時間のデータが蓄積されません。

## コマンド一覧
|コマンド|内容|
|----|----|
|register|ユーザ登録|
|delete_me|ユーザ削除|
|graph|プレイデータの統計グラフを表示|
|set_alert [minutes]|長時間プレイのアラートをセット|
|show_alert|セットしたアラートの制限時間を表示|
|reset_alert|長時間プレイのアラートをリセット|
|help|コマンドの説明を表示|

デフォルトのコマンドのプレフィックス(接頭辞)は`$`です。
全てのコマンドは`$`を最初に入力してから実行してください。

具体例:
```
$graph
```

## 機能説明
### ユーザ登録・削除
Doggoの機能を使う際は、ユーザ登録を行う必要があります(プライバシー上の理由)。
登録されたユーザのゲームステータスを10分ごとに取得し、データを蓄積します。
ユーザ登録が行われていない場合、`register`コマンド以外のコマンドを利用することはできません。
- `register` - Doggoのデータベースにユーザを登録。
- `delete_me` - Doggoのデータベースからユーザデータの削除。ユーザステータスの監視は停止され、蓄積したデータは削除されます。

### 統計グラフ表示
Doggoは、ユーザのプレイ時間の統計グラフを表示する機能があります。
`register`コマンドが実行されてから、十分な時間が経つまでデータは蓄積されないので、。
- `graph` - プレイ時間の統計グラフを表示します(デフォルトは過去10日間表示)。

### プレイ時間のアラート
１日のゲームの制限時間を設定できます。制限時間を超過した場合は、Doggoからアラートが送信されます。
- `set_alert` - アラートの制限時間を設定できます。90分のアラートをセットする例:
```
$set_alert 90
```
- `show_alert` - 設定した制限時間を表示。
- `reset_alert` - アラートをリセット。

### ヘルプ
- `help` - コマンド一覧と、コマンドの実行内容を表示できます。

## Botのセットアップ
自分でBotを起動する場合は下記の手順を行ってください(Docker必須):
1. [DEVELOPER PORTAL](https://discordapp.com/developers/applications/)でアプリを作成して、Bot用のトークンを取得
2. `.env.example`内の`TOKEN`に取得したBotのトークンを入力
3. `.env.example`内の`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`に適当な値を入力
4. `.env.example`を`.env`にリネーム
4. 以下のコマンドを実行してBotを起動
```
$ docker-compose up
```