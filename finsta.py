# Insta bot to like and comment on target profiles using selenium automation and Instagrapi with python

from time import sleep
from instagrapi import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser

# Read configuration
def read_config(filename="config.txt"):
    config = configparser.ConfigParser()
    config.read(filename)
    settings = {
        'username': config['Instagram']['username'],
        'password': config['Instagram']['password'],
        'target_profile': config['Instagram']['target_profile'],
        'num_posts': int(config['Instagram']['num_posts']),
        'comment': config['Instagram']['comment']
    }
    return settings

# Read settings
settings = read_config()
username = settings['username']
password = settings['password']
target_profile = settings['target_profile']
num_posts = settings['num_posts']
comment = settings['comment']

# Initialize Instagrapi client
client = Client()

# Login to Instagram API
def login_instagram_api():
    try:
        client.login(username, password)
        print(f"Logged into Instagram API as {username}")
    except Exception as e:
        print(f"Failed to login to Instagram API: {e}")

# Like posts with Instagrapi
def like_posts_with_api():
    global num_likes  # Declare the variable globally to keep track of likes
    try:
        user_id = client.user_id_from_username(target_profile)
        media = client.user_medias(user_id, amount=num_posts)
        print(f"Collected {len(media)} posts from {target_profile}.")
        for post in media:
            media_id = post.pk
            client.media_like(media_id)
            num_likes += 1  # Increment the like counter
            print(f"Liked post ID: {media_id}")
    except Exception as e:
        print(f"Error while liking posts: {e}")

# Login to Instagram using Selenium
def login_instagram_selenium():
    browser = webdriver.Firefox()
    browser.implicitly_wait(3)  # Reduced implicit wait time

    browser.get('https://www.instagram.com/accounts/login/')
    wait = WebDriverWait(browser, 10)  # Reduced WebDriverWait time

    username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_input = browser.find_element(By.NAME, "password")

    username_input.send_keys(username)
    password_input.send_keys(password)

    login_button = browser.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    print("Selenium login successful.")
    sleep(3)  # Reduced sleep after login

    return browser, wait

# Collect post links
def collect_post_links(browser, num_posts):
    links = set()
    scroll_pause_time = 1  # Reduced scroll pause time
    last_height = browser.execute_script("return document.body.scrollHeight")

    while len(links) < num_posts:
        post_elements = browser.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        for post in post_elements:
            link = post.get_attribute("href")
            if link and link not in links:
                links.add(link)

        if len(links) >= num_posts:
            break

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(scroll_pause_time)

        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return list(links)[:num_posts]

# Comment on post
def comment_on_post(browser, link, comment_text):
    global num_comments  # Declare the variable globally to keep track of comments
    try:
        browser.get(link)
        sleep(2)  # Reduced sleep before interacting with the post

        comment_area = WebDriverWait(browser, 5).until(  # Reduced WebDriverWait time
            EC.presence_of_element_located((By.XPATH, "//textarea[@placeholder='Add a comment…']"))
        )
        comment_area.click()
        sleep(1)

        comment_area = WebDriverWait(browser, 5).until(  # Reduced WebDriverWait time
            EC.element_to_be_clickable((By.XPATH, "//textarea[@placeholder='Add a comment…']"))
        )
        comment_area.clear()
        comment_area.send_keys(comment_text)
        print(f"Typed comment on: {link}")
        sleep(1)

        comment_area.send_keys(Keys.RETURN)
        print(f"Posted comment via ENTER on: {link}")
        num_comments += 1  # Increment the comment counter
        sleep(2)

    except Exception as e:
        print(f"Couldn't comment on {link}: {e}")

# Logout from API
def logout_instagram_api():
    try:
        client.logout()
        print("Logged out from Instagram API.")
    except Exception as e:
        print(f"Error during logout: {e}")

# Main program
def main():
    global num_likes, num_comments
    num_likes = 0  # Initialize like counter
    num_comments = 0  # Initialize comment counter

    login_instagram_api()
    like_posts_with_api()

    browser, wait = login_instagram_selenium()

    # Navigate to target profile
    browser.get(f"https://www.instagram.com/{target_profile}/")
    sleep(2)  # Reduced sleep before collecting links

    # Collect links
    post_links = collect_post_links(browser, num_posts)
    print(f"Collected {len(post_links)} post links.")

    # Comment on each post
    for link in post_links:
        comment_on_post(browser, link, comment)

    browser.quit()
    logout_instagram_api()
    
    # Display results
    print(f"Finished liking and commenting! Total likes: {num_likes}, Total comments: {num_comments}")

# Run
if __name__ == "__main__":
    main()
