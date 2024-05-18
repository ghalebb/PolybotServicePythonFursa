
# The Polybot Service: Python Project [![][autotest_badge]][autotest_workflow]

## Background

This project is a Python implementations of a chatbot application which applies filters to images send by users to a Telegram bot. 

Here is a short demonstration:

![app demo](.github/python_project_demo.gif)

## Preliminaries

1. Fork this repo by clicking **Fork** in the top-right corner of the page. 
2. Clone your forked repository by:
   ```bash
   git clone https://github.com/<your-username>/<your-project-repo-name>
   ```
   Change `<your-username>` and `<your-project-repo-name>` according to your GitHub username and the name you gave to your fork. E.g. `git clone https://github.com/johndoe/PolybotServicePython`.
3. Open the repo as a code project in your favorite IDE (Pycharm, VSCode, etc..).
   It is also a good practice to create an isolated Python virtual environment specifically for your project ([see here how to do it in PyCharm](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html)).
4. To install the requirements for the project, you can execute the following command:
``` pip install -r requirements.txt```

## The `Img` class

Under `polybot/img_proc.py`, the `Img` class is designed for image filtering on grayscale images.
Here is a detailed usage instruction for the class:

1. Creating an instance of `Img`:

   Provide the path to the image file as a parameter when creating an instance of the `Img` class, for example:
   
   ```python
   my_img = Img('path/to/image.jpg')
   ```

2. Saving the modified image:
   After performing operations on the image, you can save the modified image using the `save_img()` method, for example:
   
   ```python
   my_img.save_img()
   ```
   
   This will save the modified grayscale image to a new path with an appended `_filtered` suffix, and uses the same file extension.

### Filters in the class

In the project I implemented the following filters: `concat()`, `rotate()`, `salt_n_pepper()`, `segment()` and `flip_horizontal()`.

On every error (E.g. image path doesn't exist, input image is not an RGB) the program raises a `RuntimeError` exception.


#### Concatenating images

The `concat()` method is meant to concatenate two images together horizontally (side by side).

```python
my_img = Img('path/to/image.jpg')
another_img = Img('path/to/image2.jpg')
my_img.concat(another_img) 
my_img.save_img()   # concatenated image was saved in 'path/to/image_filtered.jpg'
```

Note: The `direction` argument is set `vertical` concatenation by default.

#### Adding "salt and pepper" noise to the image

The `salt_n_pepper()` noise method applies a type of image distortion that randomly adds isolated pixels with value of either 255 (maximum white intensity) or 0 (minimum black intensity).
The name "salt and pepper" reflects the appearance of these randomly scattered bright and dark pixels, resembling grains of salt and pepper sprinkled on an image.

```python
my_img = Img('path/to/image.jpg')
my_img.salt_n_pepper() 
my_img.save_img()  # noisy image was saved in 'path/to/image_filtered.jpg'
```

#### Rotating the image

The `rotate()` method rotates an image around its center in a clockwise direction.

```python
my_img = Img('path/to/image.jpg')
my_img.rotate() 
my_img.rotate()  # rotate again for a 180 degrees rotation
my_img.save_img()   # rotated image was saved in 'path/to/image_filtered.jpg'
```

#### Segmenting the image

The `segment()` method partitions the image into regions where the pixels have similar attributes, so the image is represented in a more simplified manner, and so we can then identify objects and boundaries more easily.

```python
my_img = Img('path/to/image.jpg')
my_img.segment() 
my_img.save_img()
```

#### Blurring the image

The `blur()` method blurs the image by replacing the value of each pixel by the average of the 16 pixels around him (or any other value, controlled by the `blur_level` argument. The bigger the value, the stronger the blurring level).
You can control the blurring level `blur_level` argument (default is 16).


```python
my_img = Img('path/to/image.jpg')
my_img.blur()   # or my_img.blur(blur_level=32) for stronger blurring effect
my_img.save_img()
```

#### Creating a contour of the image

The `contour()` method applies a contour effect to the image by calculating the **differences between neighbor pixels** along each row of the image matrix.

```python
my_img = Img('path/to/image.jpg')
my_img.contour() 
my_img.save_img()
```

#### Flipping the Image Horizontally

The `flip_horizontal()` method flips the image horizontally, effectively reversing the order of pixels in each row of the image matrix. This operation mirrors the image along a vertical axis passing through its center.

Here's an example of how to use the `flip_horizontal()` method:

```python
my_img = Img('path/to/image.jpg')
my_img.flip_horizontal() 
my_img.save_img()   # flipped image was saved in 'path/to/image_filtered.jpg'
```

## Test your filters locally

Under `polybot/test` you'll find unittests for each filter.

For example, to execute the test suite for the `concat()` filter, run the below command from the root dir of your repo:

```bash
python -m polybot.test.test_concat
```

An alternative way is to run tests from the Pycharm UI. 

## Create a Telegram Bot

1. <a href="https://desktop.telegram.org/" target="_blank">Download</a> and install Telegram Desktop (you can use your phone app as well).
2. Once installed, create your own Telegram Bot by following <a href="https://core.telegram.org/bots/features#botfather">this section</a> to create a bot. Once you have your telegram token you can move to the next step.

**Never** commit your telegram token in Git repo, even if the repo is private.
For now, we will provide the token as an environment variable to your chat app. 
Later on in the course we will learn better approaches to store sensitive data.

## Running the Telegram bot locally

The Telegram app is a flask-based service that responsible for providing a chat-based interface for users to interact with your image processing functionality. 
It utilizes the Telegram Bot API to receive user images and respond with processed images. 

The code skeleton for the bot app is already given to you under `polybot/app.py`.
In order to run the server, you have to [provide 2 environment variables](https://www.jetbrains.com/help/objc/add-environment-variables-and-program-arguments.html#add-environment-variables):

1. `TELEGRAM_TOKEN` which is your bot token.
2. `TELEGRAM_APP_URL` which is your app public URL provided by Ngrok (will be discussed soon).

Implementing bot logic involves running a local Python script that listens for updates from Telegram servers.
When a user sends a message to the bot, Telegram servers forward the message to the Python app using a method called **webhook** (**long-polling** and **websocket** are other possible methods which wouldn't be used in this project).
The Python app processes the message, executes the desired logic, and may send a response back to Telegram servers, which then delivers the response to the user.

The webhook method consists of simple two steps:

Setting your chat app URL in Telegram Servers:

![][python_project_webhook1]

Once the webhook URL is set, Telegram servers start sending HTTPS POST requests to the specified webhook URL whenever there are updates, such as new messages or events, for the bot. 

![][python_project_webhook2]


You've probably noticed that setting `localhost` URL as the webhook for a Telegram bot can be problematic because Telegram servers need to access the webhook URL over the internet to send updates.
As `localhost` is not accessible externally, Telegram servers won't be able to reach the webhook, and the bot won't receive any updates.

[Ngrok](https://ngrok.com/) can solve this problem by creating a secure tunnel between the local machine (where the bot is running) and a public URL provided by Ngrok.
It exposes the local server to the internet, allowing Telegram servers to reach the webhook URL and send updates to the bot.

Sign-up for the Ngrok service (or any another tunneling service to your choice), then install the `ngrok` agent as [described here](https://ngrok.com/docs/getting-started/#step-2-install-the-ngrok-agent). 

Authenticate your ngrok agent. You only have to do this once:

```bash
ngrok config add-authtoken <your-authtoken>
```

Since the telegram bot service will be listening on port `8443`, start ngrok by running the following command:

```bash
ngrok http 8443
```

Your bot public URL is the URL specified in the `Forwarding` line (e.g. `https://16ae-2a06-c701-4501-3a00-ecce-30e9-3e61-3069.ngrok-free.app`).
Don't forget to set the `TELEGRAM_APP_URL` env var to your URL. 

In the next step you'll finally run your bot app.

## Running a simple "echo" Bot - the `Bot` class

Under `polybot/bot.py` you are given a class called `Bot`. This class implements a simple telegram bot, as follows.

The constructor `__init__` receives the `token` and `telegram_chat_url` arguments.
The constructor creates an instance of the `TeleBot` object, which is a pythonic interface to Telegram API. You can use this instance to conveniently communicate with the Telegram servers.
Later, the constructor sets the webhook URL to be the `telegram_chat_url`. 

The `polybot/app.py` is the main app entrypoint. It's nothing but a simple flask webserver that uses a `Bot` instance to handle incoming messages, caught in the `webhook` endpoint function.

The default behavior of the `Bot` class is to "echo" the incoming messages. Try it out!

## Extending the echo bot - the `QuoteBot` class

In `bot.py` you are given a class called `QuoteBot` which **inherits** from `Bot`.
Upon incoming messages, this bot echoing the message while quoting the original message, unless the user is asking politely not to quote.

In `app.py`, change the instantiated instance to the `QuoteBot`:

```diff
- Bot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
+ QuoteBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)
```

Run this bot and check its behavior.

## Build your image processing bot - the `ImageProcessingBot` class

In `bot.py` you are given a class called `ImageProcessingBot` which **inherits** from `Bot`, again.
Upon incoming **photo messages**, this bot downloads the photos and processes them according to the **`caption`** field provided with the message.
The bot will then send the processed image to the user.

A few notes:

- Inside the `ImageProcessingBot` class, override `handle_message` method and implement the needed functionality.
- Remember that by inheriting the `Bot` class, you can use all of its methods (such as `send_text`, `download_user_photo`, `send_photo`...). 
- Possible `caption` values are: `['Blur', 'Contour', 'Rotate', 'Segment', 'Salt and pepper', 'Concat']`.
- Handle potential errors using `try... except... `. Send an appropriate message to the user (E.g. "something went wrong... please try again").
- Set a timeout when sending a message to Telegram.
- Use `logger` to log important information in your app.
- Your bot should support the `Blur` and `Contour` filters (those filters have already implemented for you). 

Test your bot on real photos and make sure it's functioning properly.

> [!TIP]
> When working with Telegram's API, you might encounter situations where your code encounters errors while processing incoming messages. In such cases, Telegram's server will automatically retry sending messages that were not responded to with a status code of 200. This retry mechanism is designed to ensure the reliable delivery of messages.
> If you find that your bot is receiving repeated messages due to this retry mechanism, just review your code and identify any errors or issues that might be causing the message processing failures. 

## Test your bot locally

You can test your bot logic locally by:

```bash
python -m polybot.test.test_telegram_bot
```

Or via the Pycharm UI. 

## Exporting TELEGRAM_TOKEN and TELEGRAM_APP_URL

### Windows:

To export environment variables in Windows, you can use the `set` command. Open Command Prompt and execute the following commands:

```cmd
set TELEGRAM_TOKEN=your_telegram_token
set TELEGRAM_APP_URL=your_telegram_app_url
```

### Linux/ Mac:
In Linux/Mac, you can export environment variables using the export command. Open Terminal and execute the following commands:

```cmd
export TELEGRAM_TOKEN=your_telegram_token
export TELEGRAM_APP_URL=your_telegram_app_url
```
## Running the App from the Command Line

To run the app from the command line, execute the following command:


```bash
python3 polyplot.app
```



[DevOpsTheHardWay]: https://github.com/alonitac/DevOpsTheHardWay
[autotest_badge]: ../../actions/workflows/project_auto_testing.yaml/badge.svg?event=push
[autotest_workflow]: ../../actions/workflows/project_auto_testing.yaml/
[github_actions]: ../../actions

[python_project_demo]: https://alonitac.github.io/DevOpsTheHardWay/img/python_project_demo.gif
[python_project_pixel]: https://alonitac.github.io/DevOpsTheHardWay/img/python_project_pixel.gif
[python_project_imagematrix]: https://alonitac.github.io/DevOpsTheHardWay/img/python_project_imagematrix.png
[python_project_pythonimage]: https://alonitac.github.io/DevOpsTheHardWay/img/python_project_pythonimage.png
[python_project_webhook1]: https://alonitac.github.io/DevOpsTheHardWay/img/python_project_webhook1.png
[python_project_webhook2]: https://alonitac.github.io/DevOpsTheHardWay/img/python_project_webhook2.png


