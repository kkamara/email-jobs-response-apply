from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

import os
import json
import time
import logging
import phonenumbers

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class Command(BaseCommand):
    help = 'help text'

    def add_arguments(self, parser):
        # parser.add_argument("--email", type=str, help='Your Gmail address.')
        pass
    
    def handle(self, *args, **options):
        '''
        The Selenium Python Documentation:
            https://www.selenium.dev/documentation/
        '''
        config_file = open(
            os.path.join(settings.BASE_DIR, 'config.json'),'r')
        config = json.loads(config_file.read())

        if True is not self.validate_url(config['email_page_link']):
            raise ValidationError('The email_page_link config value must be a valid url.')
        
        if True is not self.validate_email(config['email']):
            raise ValidationError('The email config value must be a email.')
        
        if True is not self.validate_phonenumber(config['phone_number']):
            raise ValidationError('The phone_number config value must be a phone number.')
        
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            userAgent = 'Mozilla/5.0 (BB10; Touch) AppleWebKit/537.1+ (KHTML, like Gecko) Version/10.0.0.1337 Mobile Safari/537.1+'
            chrome_options.add_argument('--user-agent='+userAgent)
            # Use SELENIUM_HEADLESS in .env to remove GUI.
            if settings.SELENIUM_HEADLESS == True or settings.APP_ENV == 'testing':
                chrome_options.add_argument('--headless')
            if settings.APP_ENV == 'testing':
                chrome_options.add_argument('--disable-dev-shm-usage')
            browser = webdriver.Chrome(options=chrome_options)
            
            browser.get(config['email_page_link'])

            el = browser.find_element(
                By.XPATH, "//input[@id='identifierId']")
            
            el.send_keys(config['email']+Keys.ENTER)

            del el
            time.sleep(3)

            browser.find_element(
                By.XPATH, "//input[@type='password']").send_keys(
                config['password']+Keys.ENTER)

            # "//input[@id='phoneNumber']"

            time.sleep(60)
            self.screenshot(browser, name='debug')
            # if 'Thisisnotinpagesource.' in browser.page_source:
            #     raise RuntimeError('We were detected.')            

            browser.quit()
            self.stdout.write(self.style.SUCCESS('Success'))
        except Exception as e:
            try:
                browser.quit()
            except:
                pass
            raise CommandError(str(e))

    def screenshot(self, browser, el=None, name='example'):
        browser.save_screenshot(f'./screenshots/{name}.png')
        if el:
            el_text = browser.execute_script('return arguments[0].innerText', el)
            logging.info(el_text)
    
    def validate_url(self, subject):
        validat_url = URLValidator()
        try:
            validat_url(subject)
            return True
        except ValidationError as exception:
            logging.info(str(exception))
            return False
    
    def validate_email(self, subject):
        try:
            validate_email(subject)
            return True
        except ValidationError as exception:
            logging.info(str(exception))
            return False
    
    def validate_phonenumber(self, subject):
        return True if phonenumbers.parse(
            subject, None) is not None else False
