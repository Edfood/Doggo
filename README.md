# Doggo
ゲームの長時間プレイを取り締まるためのDiscord Botです。


一応公開しています: **[DiscordサーバにBotを招待](https://discord.com/api/oauth2/authorize?client_id=750754316326928495&permissions=1073925120&scope=bot)**

Botが落ちていたらごめんなさい。

---------------------------------------
# 使い方
1. サーバーにBotを招待
2. Botを招待したサーバーのチャットもしくはDMで`$register`を送信
3. Botを招待したサーバーのチャットもしくはDMで`$show`を送信し、自分のゲームプレイ時間の履歴を確認

`$register`コマンドを送信してから十分な時間が経つまでは
プレイ時間のデータが蓄積されないのでご留意を。

# コマンド
データベースに自分を登録 (ステータスのトラッキング開始)
```
$register
```

最近のプレイ時間の履歴をグラフで表示
```
$show
```

データベースから自分のデータを削除 (ステータスのトラッキング停止)
```
$delete
```

---------------------------------------

# Doggoの起動方法
自分でDoggoを起動する場合は下記の手順を行ってください(Docker必須):
1. [DEVELOPER PORTAL](https://discordapp.com/developers/applications/)でアプリを作成して、Bot用のトークンを取得
2. `.env.example`の`TOKEN`に取得したBotのトークンを入力
3. `.env.example`の`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`に適当な値を入力
4. `.env.example`を`.env`にリネーム
4. 以下のコマンドを実行してBotを起動
```
$ docker-compose up
```