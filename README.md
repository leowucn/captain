# Awesome Tool for Learning English

## What it is

Captain is a smart clipboard recorder, a dictionary and a vocabulary builder which was created for learning English.

## Features

### Smart Clipboard Recorder

Captain monitor the clipboard and extract the vocabulary and the sentence wisely. Why? Because it is essential to record the vocabulary and the sentence in which you stuck and can't recognise the word when you read English articles or English novels. If you can learn words from a vivid or meaningful sentence in which you stuck other than a trivial example from a dictionary, you would gain much efficiency when learning English.

### Automatic pronunciation

Want to listen to word pronunciation but too lazy to open other app and click pronunciation button? Or less you have to open a web browser and search the certain word? How can you bear the so much low efficiency? Now,  Captain would release you from the annoying dilemma. The only thing you need to do is to copy the word! Programming should make life easier. That's it.ʘ‿ʘ.

### Automatic notification

Just like automatic pronunciation, when you finished the step of copying a word, after a short time, the word definition would pop up with the form of notification.![](src/learn_english/asset/images/screenshot1.png)

### Dictionary

Captain, of course, can look up words. As a matter of fact, Captain requests and gets word definition from website http://dict.youdao.com/, then it will record the definition in a local dictionary file.

### Vocabulary Builder

Captain is originally designed as an assistant partner of Kindle E-reader.Frankly, I think Kindle is awesome to learning English. When we look up words on Kindle, they are automatically added to the Vocabulary Builder on the device. With Vocabulary Builder, we can use flashcards to learn the definitions and usage of words. But as a long term user, I think Kindle has a serious shortcoming which is a lack of excellent management functionary of vocabulary builder, and this is why I created this project originally.

![](src/learn_english/asset/images/screenshot2.png)

![](src/learn_english/asset/images/screenshot3.png)

### Kindle Exporter

For convenience, Captain can automatically export the words in 'mastered' category on Kindle vocabulary builder, it will delete those them on Kindle and synchronise to Kindle. But currently, you need manually reboot Kindle after exporting to make synchronisation valid.

## Install requirements

##### Install third-party library for python.

```
pip install -r requirements.txt
```

##### Install mpg123 for words pronunciation via third-party packaging tool.

[**Homebrew** ](http://brew.sh/)

```
brew install mpg123
```

## Requirements

OS: OSX

## Running the app

    sh run.sh

Open your browser, enter the url http://localhost:5000/. 

## How to use

Once you have done the above steps. You can use now.

For recording the vocabulary and the sentence where you stuck, first you should copy the word and then the sentence in which the word reside. That's all you need to do. Now the word has been stored properly associated with its definition, you can access and review at http://localhost:5000/

For exporting the vocabulary which in category 'mastered' on Kindle, you just need to plug in you Kindle and issue the command `sh run.sh` or if you have executed that command, you should issue `sh rerun.sh` instead.

For listening to word pronunciation, copy the word outright. Then the pronunciation would continually ring out for three times.

## Feedback

This is an early project and there will be breaking changes. However, discussions and contributions are welcome. Please feel free to experiment and come back with suggestions/issues to make this project more useful and more powerful. Thanks.

## Contributing

Contributions are welcome!

## License

Copyright 2017 leowucom

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



