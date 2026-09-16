<div align="right">
  <a href="README_en.md">English</a> | <b>日本語</b>
</div>

# Turtle Pico - 配線いらずで、本格的な電子工作を -

![Turtle Pico](pic/TurtlePico_Thumbnail.png)

こんにちは！皆さんは、**電子工作でのお困りごと**を、どのように解決しますか？

煩雑な配線、難しいプログラミングと困難な環境構築、毎回確認が面倒なピン配置...などなど、電子工作を楽しんでいると、いくつもの壁に突き当たります。

そんな課題を克服できるようにと開発したのが、このTurtle Pico マイコンボード。ブレッドボードすら不要で、**コネクタに直接部品を接続するだけ**で回路が完成します。内部には**Raspberry Pi Pico W**を搭載しているので、プログラミングには**MicroPython**を使用でき、更にリソースにも困りません！

コネクタに超音波センサを指すと、その容姿はまるで亀のようで、その容姿から「**Turtle Pico**」とボードを名付けました。

ボードの詳細仕様は、 [Turtle Pico 仕様書](https://jinproduction.work/wp-content/uploads/2024/07/specific_ja.pdf)をご覧ください！

**本PJは現在、製品化に向けて準備中です。**

## Turtle Pico 製品パッケージ

![alt text](pic/Package.jpg)

Turtle Picoは、画像のような**パッケージ**に収納されています。

![alt text](pic/InCase.png)

中を開けるとこのようになっていて、本体と外箱の寸法は画像に記載のとおりです。黄色が外箱、ピンクが本体の寸法です。

パッケージの中に、更にTurtle Pico本体がありますが、本体は基板を**オリジナル3Dプリンタ製カバー**で覆うような形状をしています。USBやMicroSDカードなどのコネクタポートがロゴで表示されています。

それぞれの意味は、[Turtle Pico 仕様書](https://jinproduction.work/wp-content/uploads/2024/07/specific_ja.pdf) にてご確認ください。

![alt text](pic/Color.jpg)

Turtle Picoは本体カバーの色で**カラーバリエーション**が4色あり、**ピンク色、緑色、グレー、空色**となっています。

## Turtle Pico ワクワク作例ブック

![Recipes](pic/TP_recipes.jpg)

製品化モデルでは、上記の作例集が付属します。ソースコードを [example](./example/)に掲載している、TurtlePico作例の数々の作り方を掲載しています。

ここでは、作例集に掲載している、いくつかの**Turtle Picoの仲間たち**をご紹介しましょう。

![alt text](pic/Friends.png)

画像左上は4脚でよちよちと歩くロボット「**Turtle Pico Robot**」で、サーボモータの回転で歩きます。その右側にあるのはドローン「**Turtle Pico Drone**」、更にその下にはマイコンカー「**Turtle Pico Car**」があります。

これらは、上に乗せるものを変えたり、様々な制御を追加することで、**いろいろな応用**が効きそうです。ぜひ、作例集を参考に、**自分専用のアプリケーション**に仕上げてください！

画像左下には、Turtle Picoを**サウンドカード**にしてスピーカーで音楽を流している作例です。Turtle Picoに搭載されているPCM5102AというオーディオDACは、**32bit / 192kHz**にも対応しているため、ハイレゾ音源も流せるパワフルなオーディオDACとなります。

従って、TurtlePicoは、公式にある**サウンドカード**のファームウェアを使用すれば、周囲にアンプやスピーカーをつないで、**クラフトオーディオ**を楽しむことができるボードにもなります。

作例集では、これら作例の作り方を始めとし、**応用の仕方を設計からデバッグまで**、最近の「**バイブコーディング**」でかんたんに行う**製作方法**を解説しています。Turtle Picoをお買い上げいただければ、セット担っているので、ぜひお買い求めください！

<!-- 

## Case

![case](board/main/pic/Case2.PNG)

Turtle Pico Package is available in [**board/main/Case**](https://github.com/Jin-Neuron/Turtle-Pico/tree/master/board/main/Case).

## Purchase your board

![image](https://github.com/user-attachments/assets/7ed59ffb-0fa4-4088-b02c-0e429f06822e)

Turtle Pico boards can currently only be purchased from [PCBWay's Shared Project Page](https://www.pcbway.com/project/shareproject/Turtle_Pico_Board_c183b11f.html). Once officially released, we plan to make it available for purchase at various online stores. 

-->

## License

本公式リポジトリは、複数のライセンスにて構成されています。

[LICENSE File](License.txt)にてご確認ください。
