# import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import datetime
import json
import requests
import os
import whisper
import warnings
import ssl
import subprocess
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")
model = whisper.load_model("base")


def send_email(subject, body, to_email, from_email, from_password, image_path):
    # Set up the server
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    # Image attachment
    try:
        with open(image_path, 'rb') as img:
            img_data = img.read()
            image = MIMEImage(img_data, name=image_path.split('/')[-1])
            msg.attach(image)
    except Exception as e:
        print(f"Failed to attach image: {e}")
    
    try:
        # Connect to the server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        
        # Log in to the server
        server.login(from_email, from_password)
        
        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        
    finally:
        server.quit()


def transcribe(url):
    with open('.temp', 'wb') as f:
        f.write(requests.get(url).content)
        time.sleep(2)
    result = model.transcribe('.temp')
    return result["text"].strip()

def click_checkbox(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='reCAPTCHA']"))
    driver.find_element(By.ID, "recaptcha-anchor-label").click()
    driver.switch_to.default_content()

def request_audio_version(driver):
    driver.implicitly_wait(10)
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.XPATH, ".//iframe[@title='hình ảnh xác thực reCAPTCHA sẽ hết hạn sau 2 phút nữa']"))
    driver.find_element(By.ID, "recaptcha-audio-button").click()

def solve_audio_captcha(driver):
    driver.implicitly_wait(10)
    text = transcribe(driver.find_element(By.ID, "audio-source").get_attribute('src'))
    driver.find_element(By.ID, "audio-response").send_keys(text)
    driver.find_element(By.ID, "recaptcha-verify-button").click()

def run_script(user,cccd):
    # Email info
        subject = f"SJC - {user}"
        to_email = "xxxx@gmail.com"
        from_email = "xxxx@gmail.com"
        from_password = "xxx"

    # Note setup
        current_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        with open("./result.txt", "a") as result:
            result.write(f"========= SJC {current_date}========= \n")

    # Purchase
        while True:
            try:
                # Icognito
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.add_argument("--incognito")
                    driver = webdriver.Chrome(options=chrome_options)
                    driver.get("https://tructuyen.sjc.com.vn/dang-nhap")

                # login + need to add network error and re-try + cannot press sign-in butt
                    while True:
                        try:
                            driver.implicitly_wait(5)
                            name = driver.find_element(By.ID,"id_name")
                            id = driver.find_element(By.ID,"id_cccd")
                            sign_in_but = driver.find_element(By.ID, "sign_in_submit")
                            # send keys
                            name.send_keys(user)
                            id.send_keys(cccd)
                            driver.implicitly_wait(2)
                            sign_in_but.click()
                            break
                        except NoSuchElementException:
                            driver.refresh()
                        
                # Already bought
                    try:
                        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'swal2-html-container')))
                        with open("./result.txt", "a") as result:
                            result.write(f"{user} Already bought \n")
                        print("Already bought")
                        body = f"{user} Already bought"
                        send_email(subject, body, to_email, from_email, from_password)
                        driver.quit()
                        return
                    except:
                        pass

                # Loop for keep buying
                    while True:
                        # Info
                            wait = WebDriverWait(driver, 3)
                            # khu vuc
                            select2_container_khuvuc = wait.until(EC.element_to_be_clickable((By.ID, 'select2-id_area-container')))
                            select2_container_khuvuc.click()
                            dropdown_option_khuvuc = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[text()='Thành phố Hồ Chí Minh']")))
                            dropdown_option_khuvuc.click()
                            # chi nhanh
                            select2_container_chinhanh = wait.until(EC.element_to_be_clickable((By.ID, 'select2-id_store-container')))
                            select2_container_chinhanh.click()
                            # dropdown_option_chinhanh = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[text()='TRỤ SỞ - TRUNG TÂM VÀNG BẠC ĐÁ QUÝ SJC  ']")))
                            dropdown_option_chinhanh = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[text()='TRUNG TÂM VÀNG BẠC ĐÁ QUÝ SJC QUANG TRUNG  ']")))
                            dropdown_option_chinhanh.click()
                            # so luong
                            soluong = wait.until(EC.presence_of_element_located((By.ID, 'id_qty')))
                            soluong.clear()  # Clear the existing value
                            soluong.send_keys('1')  # Set the value to 1
                            # tien mat
                            select2_container_cash = wait.until(EC.element_to_be_clickable((By.ID, 'select2-id_hinhthuc-container')))
                            select2_container_cash.click()
                            dropdown_option_cash = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[text()='Tiền mặt']")))
                            dropdown_option_cash.click()

                        # WAITING TIME 
                            now = datetime.datetime.now()
                            # target_time = (now + datetime.timedelta(seconds=5)).replace(microsecond=1)
                            # target_time = (now + datetime.timedelta(minutes=1)).replace(second=0, microsecond=0)
                            # target_time = (now + datetime.timedelta(hours=1)).replace(hour=0, second=0, microsecond=1)
                            target_time = now + datetime.timedelta(seconds=5)
                            wait_time = (target_time - now).total_seconds()
                            # with open("./result.txt", "a") as result:
                            #     result.write(f"wait time: {wait_time} \ntarget time: {target_time}\ncheck time: {wait_time/1.5}\n")

                        # Authorization
                            time.sleep(wait_time/2)
                            try:
                                try:
                                    click_checkbox(driver)
                                    sound_check = driver.find_element(By.XPATH, ".//iframe[@title='hình ảnh xác thực reCAPTCHA sẽ hết hạn sau 2 phút nữa']")
                                    sound_verify = True
                                except:
                                    sound_verify = False
                                if sound_verify == True:
                                    request_audio_version(driver)
                                    solve_audio_captcha(driver)
                                else: pass
                            except:
                                driver.refresh()
                                continue
                            else:
                                driver.switch_to.default_content() 
                                pass


                        # Wait for the purchase button
                            while (target_time - datetime.datetime.now()).total_seconds() > 1:
                                time.sleep(1)
                            
                            # Busy wait for the remaining time to ensure precision
                            while datetime.datetime.now() < target_time:
                                pass

                            purchased_butt = driver.find_element(By.ID, 'register_form_submit')
                            purchased_butt.click()
                            time.sleep(3)  # Wait for the page to update

                        # Out of stock
                            try:
                                # Wait for the element to be present and visible
                                element = WebDriverWait(driver, 2).until(
                                    EC.visibility_of_element_located((By.ID, "swal2-html-container"))
                                )
                                if element.text.strip() == "Cửa hàng đã hết lượt giao dịch, xin vui lòng chọn cửa hàng khác.":
                                    close_button = wait.until(
                                        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.swal2-confirm"))
                                    )
                                    close_button.click()
                            except: pass
                            else:
                                # time.sleep(30)
                                continue

                        # Loading for soo long
                            try:
                                # time.sleep(20)
                                # Find the span element with class "indicator-label"
                                element = driver.find_element(By.CLASS_NAME, 'indicator-label')
                                if element.text.strip() != "Đăng ký":
                                    driver.refresh()
                                    time.sleep(1)
                                    continue
                            except:
                                break       
                        
                # Scroll the element and screenshot
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
                    screenshot_path = f"./image/sjc/{user}_{current_date}.png"
                    driver.save_screenshot(screenshot_path)
                    body = f"{user} Success"
                    send_email(subject, body, to_email, from_email, from_password, screenshot_path)
                    print("Email sent successfully!")
                    os.remove(screenshot_path)
                    with open("./result.txt", "a") as result:
                        result.write(f"Success!! \nimage: {user} - {current_date}\n")
                    driver.quit() 
                    continue
            except Exception as e:
                print(f"error: {e}")
                body = f"{user} Error {e}\nExit!!"
                send_email(subject, body, to_email, from_email, from_password, screenshot_path)
                driver.quit()   

if __name__ == "__main__":
    # User credentials
    user1 = "Name1"
    password1 = "xxxxxx"
    user2 = "Name2"
    password2 = "xxxxxx"
    with ThreadPoolExecutor(max_workers=1) as executor:
        # Run logins in parallel
        executor.submit(run_script, user1, password1)
        # executor.submit(run_script, user2, password2)
