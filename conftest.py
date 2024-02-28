import pytest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from app import User, UserReview, db, app

@pytest.fixture()
def get_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.\
        Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.implicitly_wait(5)
    driver.get("http://127.0.0.1:5000")
    yield driver
    driver.quit()


@pytest.fixture()
def setup_signup(get_driver):
    driver = get_driver
    username = "test_user"
    yield driver, username
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()

@pytest.fixture()
def setup_review(setup_signup):
    driver, username = setup_signup
    yield driver, username
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        user_review = UserReview.query.filter_by(user_id=user.id).first()
        if user_review:
            db.session.delete(user_review)
            db.session.commit()
        


    