import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img


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
            if self.is_current_msg_photo(msg):
                photo_path = self.download_user_photo(msg)

                if 'caption' in msg:
                    caption = msg['caption'].lower()
                    img = Img(photo_path)

                    if caption == 'concat':
                        # if self.first_image_path:
                        #     other_img = Img(self.first_image_path)
                        #     img.concat(other_img)
                        #     processed_img_path = img.save_img()
                        #     self.send_photo(chat_id, processed_img_path)
                        #     self.first_image_path = None
                        # else:
                        self.first_image_path = photo_path
                        # self.send_text(chat_id, 'First image received. Please send the second image with the caption "concat".')

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
                        else:
                            self.send_text(chat_id,
                                           'Unknown command. Please use one of the following: Blur, Contour, Rotate, Segment, Salt and pepper, Concat')
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


class ImageProcessingBot2(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        chat_id = msg['chat']['id']
        for photo in range(len(msg['photo'])):
            self.send_photo(chat_id, self.download_user_photo(msg, photo_index=photo))
        # try:
        #     if self.is_current_msg_photo(msg):
        #         caption = msg['caption'].lower() if 'caption' in msg else ''
        #
        #         if caption == 'concat' and len(msg['photo']) >= 2:
        #             # Download both photos
        #             photo_path1 = self.download_user_photo(msg, photo_index=-1)
        #             photo_path2 = self.download_user_photo(msg, photo_index=-2)
        #             for photo in range(len(msg['photo'])):
        #
        #                 self.send_photo(chat_id,self.download_user_photo(msg,photo_index=photo))
        #             # self.send_photo(chat_id,photo_path1)
        #             # self.send_photo(chat_id,photo_path2)
        #             # Process the images
        #             img1 = Img(photo_path1)
        #             img2 = Img(photo_path2)
        #
        #             # Concatenate images
        #             img1.concat(img2)
        #             processed_img_path = img1.save_img()
        #             self.send_photo(chat_id, processed_img_path)
        #         else:
        #             # Download the photo
        #             photo_path = self.download_user_photo(msg)
        #             img = Img(photo_path)
        #
        #             if caption == 'blur':
        #                 img.blur()
        #             elif caption == 'contour':
        #                 img.contour()
        #             elif caption == 'rotate':
        #                 img.rotate()
        #             elif caption == 'segment':
        #                 img.segment()
        #             elif caption == 'salt and pepper':
        #                 img.salt_n_pepper()
        #             else:
        #                 self.send_text(chat_id,
        #                                'Unknown command. Please use one of the following: Blur, Contour, Rotate, Segment, Salt and pepper, Concat')
        #                 return
        #
        #             processed_img_path = img.save_img()
        #             self.send_photo(chat_id, processed_img_path)
        #     else:
        #         self.send_text(chat_id, 'Please send a photo with a valid command as the caption.')
        # except Exception as e:
        #     logger.error(f"Error processing image: {e}")
        #     self.send_text(chat_id, 'Something went wrong... please try again.')

    def download_user_photo(self, msg, photo_index=0):
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][photo_index]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = 'photos'

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        file_path = os.path.join(folder_name, os.path.basename(file_info.file_path))
        with open(file_path, 'wb') as photo:
            photo.write(data)

        return file_path


class ImageProcessingBot1(Bot):

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        chat_id = msg['chat']['id']

        try:
            if self.is_current_msg_photo(msg):
                photo_path = self.download_user_photo(msg)
                img = Img(photo_path)

                caption = msg['caption'] if 'caption' in msg else ''
                caption = caption.lower()

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
                else:
                    self.send_text(chat_id,
                                   'Unknown command. Please use one of the following: Blur, Contour, Rotate, Segment, Salt and pepper, Concat')
                    return

                processed_img_path = img.save_img()
                self.send_photo(chat_id, processed_img_path)
            else:
                self.send_text(chat_id, 'Please send a photo with a valid command as the caption.')
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.send_text(chat_id, 'Something went wrong... please try again.')

    # def handle_message(self, msg):

    # logger.info(f'Incoming message: {msg}')
    # chat_id = msg['chat']['id']

    # try:
    #     if self.is_current_msg_photo(msg):
    #         caption = msg['caption'].lower() if 'caption' in msg else ''
    #
    #         if caption == 'concat' and len(msg['photo']) >= 2:
    #             # Download both photos
    #             photo_path1 = self.download_user_photo(msg)
    #             photo_path2 = self.download_user_photo(msg)
    #
    #             # Process the images
    #             img1 = Img(photo_path1)
    #             img2 = Img(photo_path2)
    #
    #             img1.concat(img2)
    #             processed_img_path = img1.save_img()
    #             self.send_photo(chat_id, processed_img_path)
    #         else:
    #             photo_path = self.download_user_photo(msg)
    #             img = Img(photo_path)
    #
    #             if caption == 'blur':
    #                 img.blur()
    #             elif caption == 'contour':
    #                 img.contour()
    #             elif caption == 'rotate':
    #                 img.rotate()
    #             elif caption == 'segment':
    #                 img.segment()
    #             elif caption == 'salt and pepper':
    #                 img.salt_n_pepper()
    #             else:
    #                 self.send_text(chat_id,
    #                                'Unknown command. Please use one of the following: Blur, Contour, Rotate, Segment, Salt and pepper, Concat')
    #                 return
    #
    #             processed_img_path = img.save_img()
    #             self.send_photo(chat_id, processed_img_path)
    #     else:
    #         self.send_text(chat_id, 'Please send a photo with a valid command as the caption.')
    # except Exception as e:
    #     logger.error(f"Error processing image: {e}")
    #     self.send_text(chat_id, 'Something went wrong... please try again.')
