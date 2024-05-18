import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img

HELP_MSG = ("You can use one of the following commands:\n"
            "- Blur: Applies a blurring effect to the image, smoothing out details.\n"
            "- Contour: Detects edges or boundaries of objects in the image.\n"
            "- Rotate: Rotates the image clockwise.\n"
            "- Segment: Divides the image into regions based on similarities.\n"
            "- Salt and pepper: Adds random noise to individual pixels in the image.\n"
            "- Concat: Combines two images either horizontally.\n"
            "- Rotate2: Rotates the image two times.\n"
            "- Flip horizontal: Flips the image horizontally, reversing the order of pixels.")


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ImageProcessingBot(Bot):
    def __init__(self, token, telegram_chat_url):
        super().__init__(token, telegram_chat_url)
        self.first_image_path = None

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        chat_id = msg['chat']['id']

        try:

            if 'text' in msg and (msg['text'] == '/start' or msg['text'].lower() == 'hi'):
                name = msg['chat']['first_name']
                self.send_text(chat_id,
                               f"Hello {name}! I am your image bot.\n")
                self.send_text(chat_id, HELP_MSG)
                return
            if 'text' in msg and msg['text'] == '/help':
                self.send_text(chat_id, HELP_MSG)
                return
            if 'text' in msg and msg['text'] == 'bye':
                self.send_text(chat_id, "Goodbye!")
                return

            if self.is_current_msg_photo(msg):
                photo_path = self.download_user_photo(msg)

                if 'caption' in msg:
                    caption = msg['caption'].lower()
                    img = Img(photo_path)

                    if caption == 'concat':
                        self.first_image_path = photo_path
                    else:
                        if caption == 'blur':
                            img.blur()
                        elif caption == 'contour':
                            img.contour()
                        elif caption == 'rotate':
                            img.rotate()
                        elif caption == 'segment':
                            img.segment()
                        elif caption == 'salt and pepper':
                            img.salt_n_pepper()
                        elif caption == 'rotate2':
                            img.rotate()
                            img.rotate()
                        elif caption == 'flip horizontal':
                            img.flip_horizontal()
                        else:
                            self.send_text(chat_id,
                                           'Unknown command. Please use one of the following: Blur, Contour, Rotate'
                                           ', Segment, Salt and pepper, Concat')
                            return

                        processed_img_path = img.save_img()
                        self.send_photo(chat_id, processed_img_path)
                elif self.first_image_path:
                    img = Img(photo_path)
                    other_img = Img(self.first_image_path)
                    img.concat(other_img)
                    processed_img_path = img.save_img()
                    self.send_photo(chat_id, processed_img_path)
                    self.first_image_path = None

                else:
                    self.send_text(chat_id, 'Please send a photo with a valid command as the caption.')
            else:

                self.send_text(chat_id, 'Please send a photo with a valid command as the caption.')
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.send_text(chat_id, 'Something went wrong... please try again.')
