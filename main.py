import email
import imaplib
import os
import re
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ----------------- Credentials -----------------------
credentials = {
    'first_name': '',
    'last_name': '',

    'e_mail': '',
    'e_mail_password': '',

    'twitch_username': '',
    'twitch_password': '',
    'twitch_signed_in': False,

    'twitter_username': '',
    'twitter_password': '',
    'twitter_signed_in': False,

    'discord_username': '',
    'discord_email': '',
    'discord_password': '',
    'discord_signed_in': False,
    'discord_app_open': True,

    'steam_username': '',
    'steam_password': '',
    'steam_sign_in': False,

    'pinterest_username': '',
    'pinterest_password': '',

    'giveaway_completed': True,
}

timeout = 60
opts = Options()
opts.add_argument('--incognito')
driver = Chrome('C:/WebDriver/bin/chromedriver.exe', options=opts)

driver.get('https://vast.gg/')
element = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="home"]/div/div/div/div[4]/div/span')))
pages = re.findall(r'\d+', element.text)[-1]

links = []

# collect all the links to all the draws
for i in range(int(pages)):
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.title.main-title.gradient-effect')))
    draws = driver.find_elements_by_css_selector('.title.main-title.gradient-effect')
    for draw in draws:
        link = draw.find_element_by_css_selector('a').get_attribute('href')
        links.append(link)
    driver.get('https://vast.gg/page/' + str(i+2) + '/')

for link in links:
    # navigate to the gleam.io page
    driver.get(link)
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, "//iframe[contains(@id,'GleamEmbed')]")))
    driver.switch_to.frame(driver.find_element_by_xpath("//iframe[contains(@id,'GleamEmbed')]"))
    try:
        element = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[1]/div[1]/div[6]/div[3]/div/p[3]/a')
    except NoSuchElementException:
        continue

    driver.execute_script("arguments[0].scrollIntoView();", element)
    element.click()
    time.sleep(0.5)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # enter in name and email
    if not credentials['giveaway_completed']:
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div[1]/div[1]/div[6]/div[2]/div[2]/div/form/div/span[1]/button/span[2]')))
        driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[1]/div[1]/div[6]/div[2]/div[2]/div/form/fieldset[2]/div[2]/div/div/div[1]/label/div[2]/input')\
            .send_keys(credentials['first_name'])
        driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[1]/div[1]/div[6]/div[2]/div[2]/div/form/fieldset[2]/div[2]/div/div/div[2]/label/div[2]/input')\
            .send_keys(credentials['last_name'])
        driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[1]/div[1]/div[6]/div[2]/div[2]/div/form/fieldset[2]/div[2]/div/div/div[3]/label/div[2]/input')\
            .send_keys(credentials['e_mail'])

    try:
        driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/div/div[1]/div[1]/div[6]/div[2]/div[2]/div/form/div/span[1]/button/span[2]')\
            .click()
    except:
        pass

    if not credentials['giveaway_completed']:
        # verify login with twitch login
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, ".//a[contains(@class,'twitchtv-border')]//span[@class='text capitalize ng-binding']")))
        driver.find_element_by_xpath(".//a[contains(@class,'twitchtv-border')]//span[@class='text capitalize ng-binding']")\
            .click()
        driver.switch_to.window(driver.window_handles[1])
        WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="login-username"]')))
        driver.find_element_by_xpath('//*[@id="login-username"]').send_keys(credentials['twitch_username'])
        driver.find_element_by_xpath('//*[@id="password-input"]').send_keys(credentials['twitch_password'])
        driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/div[3]/div/div/div/div[3]/form/div/div[3]/button').click()

        # check email for security code
        input('Complete Twitch captcha and verify that an email with a code has been received before continuing!')
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(credentials['e_mail'], credentials['e_mail_password'])
        imap.select("INBOX", True)
        while True:
            status, email_ids = imap.search(None, '(FROM "no-reply@twitch.tv")')

            for mail_id in email_ids:
                if mail_id != b'':
                    typ, data = imap.fetch(mail_id, '(RFC822)')
                    raw_email_string = data[0][1].decode('utf-8')
                    email_message = email.message_from_string(raw_email_string)
                    code = re.findall(r'>(\d{6})<', email_message.as_string())

                    # delete the email
                    for num in email_ids[0].split():
                        imap.store(num, '+X-GM-LABELS', '\\Trash')
                    imap.expunge()  # TODO: emails not being deleted

                    if len(code) == 1:
                        code = code[0]
                        driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/div[3]/div/div/div/div[3]/div[2]/div/div[1]/div/input') \
                            .send_keys(code)
                        break
            if len(email_ids) > 0:
                break
        imap.close()
        imap.logout()

        credentials['twitch_signed_in'] = True
        driver.switch_to.window(driver.window_handles[0])

    # process each of the entry methods
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.entry-method')))
    entries = driver.find_elements_by_css_selector('.entry-method')
    error_occurred = False
    for entry in entries:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", entry)
            entry_text = entry.text
            if 'completed' in entry.get_attribute('class'):
                continue
            elif 'Friend You Refer' in entry.text:
                if 'expanded' in entry.get_attribute('class'):
                    entry.click()
            # visiting a page
            elif 'visit' in entry.get_attribute('class') \
                    or 'Like' in entry.text \
                    or 'Instagram' in entry.text \
                    or 'Facebook' in entry.text \
                    or 'Tag' in entry.text \
                    or 'TikTok' in entry.text and 'Follow' in entry.text \
                    or 'ASUS' in entry.text \
                    or 'YouTube' in entry.text:
                entry.click()
                entry.find_element_by_xpath(".//a[contains(@class,'btn')]").click()
                driver.switch_to.window(driver.window_handles[1])

                # stay on a page for certain amount of time
                time.sleep(5)

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                if 'YouTube' in entry_text and len(entry.find_elements_by_xpath(".//textarea[@name='data']")) > 0:
                    entry.find_element_by_xpath(".//textarea[@name='data']").send_keys('No')

                try:
                    entry.find_element_by_xpath(".//a[@class='btn btn-primary']").click()
                except:
                    pass
            elif 'Entering this Giveaway' in entry.text:
                entry.click()
                entry.find_element_by_xpath(".//a[contains(@class,'btn')]").click()
                driver.switch_to.window(driver.window_handles[1])
                WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, '//main[@id="single"]')))
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                entry.find_element_by_xpath(".//button[@class='btn btn-primary']").click()
                time.sleep(0.5)
                if 'exoanded' in entry.get_attribute('class'):
                    entry.click()
            elif 'Pinterest' in entry.text:
                entry.click()
                if len(entry.find_elements_by_xpath(".//a[contains(@class,'btn')]")) > 0:
                    entry.find_element_by_xpath(".//a[contains(@class,'btn')]").click()
                    driver.switch_to.window(driver.window_handles[1])

                    time.sleep(5)

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    if len(entry.find_elements_by_xpath(".//a[@class='btn btn-primary']")) > 0:
                        entry.find_element_by_xpath(".//a[@class='btn btn-primary']").click()
                else:
                    entry.find_element_by_xpath('.//input[@name="data"]').send_keys(credentials['pinterest_username'])
                    entry.find_element_by_xpath(".//button[@class='btn btn-primary']").click()
                    entry.find_element_by_xpath(".//button[@class='btn btn-primary']").click()

                    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.entry-method')))
                    entries = driver.find_elements_by_css_selector('.entry-method')
            # login to twitter
            elif 'Twitter' in entry.text and 'Share ' not in entry.text:
                pass
                # entry.click()
                # entry.find_element_by_xpath(".//a[contains(@class,'twitter-button')]").click()
                # driver.switch_to.window(driver.window_handles[1])
                #
                # # sign in if not already
                # # if not credentials['twitter_signed_in']:
                # #     driver.find_element_by_xpath('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/form/div/div[1]/label/div/div[2]/div/input')\
                # #         .send_keys(credentials['twitter_username'])
                # #     driver.find_element_by_xpath('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[1]/div[2]/form/div/div[2]/label/div/div[2]/div/input')\
                # #         .send_keys(credentials['twitter_password'])
                # #     driver.find_element_by_xpath('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div[2]/div[2]/div/span/span/span')\
                # #         .click()
                # #     credentials['twitter_signed_in'] = True
                #
                # WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[3]/div[2]/div/span/span')))
                # time.sleep(3)
                # driver.find_element_by_xpath('//*[@id="layers"]/div[2]/div/div/div/div/div/div[2]/div[2]/div[3]/div[2]/div/span/span')\
                #     .click()
                # time.sleep(2)
                #
                # driver.close()
                # driver.switch_to.window(driver.window_handles[0])
                # WebDriverWait(entry, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//div[@class='input-append']//input[contains(@class,'twitter-username__field')]")))
                # entry.find_element_by_xpath(".//div[@class='input-append']//input[contains(@class,'twitter-username__field')]") \
                #     .send_keys(Keys.CONTROL + 'a')
                # entry.find_element_by_xpath(".//div[@class='input-append']//input[contains(@class,'twitter-username__field')]")\
                #     .send_keys(credentials['twitter_username'])
                #
                # WebDriverWait(entry, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//div[@class='input-append']//a[contains(@class,'btn btn-primary')]")))
                # entry.find_element_by_xpath(".//div[@class='input-append']//a[contains(@class,'btn btn-primary')]").click()
            # login to twitch and follow
            elif 'Twitch.tv' in entry.text and 'Follow' in entry.text:
                entry.click()
                if not credentials['twitch_signed_in']:
                    driver.switch_to.window(driver.window_handles[1])
                    driver.find_element_by_xpath('//*[@id="login-username"]').send_keys(credentials['twitch_username'])
                    driver.find_element_by_xpath('//*[@id="password-input"]').send_keys(credentials['twitch_password'])
                    driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/div[3]/div/div/div/div[3]/form/div/div[3]/button')\
                        .click()

                    # check email for security code
                    imap = imaplib.IMAP4_SSL('imap.gmail.com')
                    imap.login(credentials['e_mail'], credentials['e_mail_password'])
                    imap.select("INBOX", True)
                    while True:
                        status, email_ids = imap.search(None, '(FROM "no-reply@twitch.tv")')

                        for mail_id in email_ids:
                            typ, data = imap.fetch(mail_id, '(RFC822)')
                            raw_email_string = data[0][1].decode('utf-8')
                            email_message = email.message_from_string(raw_email_string)
                            code = re.findall(r'>(\d{6})<', email_message.as_string())

                            # delete the email
                            for num in mail_id.split():
                                imap.store(num, '+FLAGS', '\\Deleted')
                            imap.expunge()

                            if len(code) == 1:
                                code = code[0]
                                driver.find_element_by_xpath('//*[@id="root"]/div/div[1]/div[3]/div/div/div/div[3]/div[2]/div/div[1]/div/input')\
                                    .send_keys(code)
                                break
                        if len(email_ids) > 0:
                            break
                    driver.find_element_by_xpath('//*[@id="authorize_form"]/fieldset/button[1]').click()
                    credentials['twitch_signed_in'] = True
                    driver.switch_to.window(driver.window_handles[0])
            # Discord memes
            elif 'Discord' in entry.text and 'Join' in entry.text:
                # make sure discord isn't running since browser links will be caught by the desktop app instead of opening a
                # browser window
                if credentials['discord_app_open']:
                    try:
                        os.system('TASKKILL /F /IM discord.exe')
                    except:
                        pass

                entry.click()

                # sign in if not already
                if not credentials['discord_signed_in']:
                    entry.find_element_by_xpath(".//a[contains(@class,'btn')]").click()
                    driver.switch_to.window(driver.window_handles[1])
                    driver.find_element_by_xpath('//*[@id="app-mount"]/div[2]/div/div/div/form/div/div[2]/button/div')\
                        .click()
                    driver.find_element_by_xpath('//input[@name="email"]').send_keys(credentials['discord_email'])
                    driver.find_element_by_xpath('//input[@name="password"]').send_keys(credentials['discord_password'])
                    driver.find_element_by_xpath('//button[@type="submit"]').click()
                    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app-mount"]')))
                    time.sleep(3)
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    credentials['discord_signed_in'] = True

                entry.find_element_by_xpath('.//button[@class="btn btn-primary"]').click()
            # login in to Steam and join group
            elif 'Steam' in entry_text:
                pass
                # entry.click()
                #
                # if not credentials['steam_sign_in']:
                #     entry.find_element_by_xpath(".//button[contains(@class,'btn btn-primary')]").click()
                #     driver.switch_to.window(driver.window_handles[1])
                #     driver.find_element_by_xpath('//input[@name="username"]').send_keys(credentials['steam_username'])
                #     driver.find_element_by_xpath('//input[@name="password"]').send_keys(credentials['steam_password'])
                #     driver.find_element_by_xpath('//input[@type="submit"]').click()
                #     driver.switch_to.window(driver.window_handles[0])
                #     credentials['steam_sign_in'] = True
                #
                # entry.find_element_by_xpath(".//a[contains(@class,'btn')]").click()
                # driver.switch_to.window(driver.window_handles[1])
                # driver.find_element_by_xpath('/html/body/div[1]/div[7]/div[3]/div[1]/div[1]/div/div[1]/div[2]/div[4]/div/div')\
                #     .click()
                # driver.close()
                # driver.switch_to.window(driver.window_handles[0])
                # entry.find_element_by_xpath(".//button[contains(@class,'btn btn-primary')]").click()
            elif 'Complete' in entry.text and 'Actions' in entry.text and 'need to complete' not in entry.find_element_by_xpath(".//span[@class='tally']").get_attribute('uib-tooltip')\
                    or 'LinkedIn' in entry.text \
                    or 'Sign up' in entry.text:
                entry.click()
            elif 'Claim Loyalty' in entry.text:
                entry.click()
                bonuses = entry.find_elements_by_xpath('.//div[@class="expandable"]//span[@class="tally"]')
                for bonus in bonuses:
                    WebDriverWait(entry, timeout).until(EC.element_to_be_clickable((By.XPATH, './/div[@class="expandable"]//span[@class="tally"]')))
                    time.sleep(0.5)
                    if 'need' not in bonus.get_attribute('uib-tooltip') and 'Done' not in bonus.get_attribute('uib-tooltip'):
                        bonus.click()
                        time.sleep(0.5)
                entry.click()
            else:
                print('Fell through')
        except:
            error_occurred = True
            driver.switch_to.window(driver.window_handles[0])
    if error_occurred:
        input('Verify entries')
        driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    credentials['giveaway_completed'] = True

driver.close()
