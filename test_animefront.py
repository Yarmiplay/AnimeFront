import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from app import Anime, User, UserReview, db, app


class TestAnimeFront:

    @pytest.mark.usefixtures("setup_signup")
    def test_signup(self, setup_signup):
        driver, username = setup_signup
        driver.find_element(By.LINK_TEXT, "Sign Up").click()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("not_admin")
        driver.find_element(By.TAG_NAME, "button").click()
        with app.app_context():
            assert User.query.filter_by(username=username).first(), "Failed to create user"
        assert driver.find_element(By.ID, "welcome_user").text == "Welcome, " + username, "Failed to welcome user"
        assert driver.find_element(By.LINK_TEXT, "Logout"), "Failed to find logout button"
    
    @pytest.mark.usefixtures("setup_signup")
    def test_login(self, setup_signup):
        driver, username = setup_signup
        # In sign up page
        driver.find_element(By.LINK_TEXT, "Sign Up").click()
        driver.find_element(By.ID, "username").send_keys(username)
        password = "not_admin"
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.TAG_NAME, "button").click()
        driver.find_element(By.LINK_TEXT, "Logout").click()
        # In login page
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.TAG_NAME, "button").click()
        assert driver.find_element(By.ID, "welcome_user").text == "Welcome, " + username, "Failed to welcome user"
        assert driver.find_element(By.LINK_TEXT, "Logout"), "Failed to find logout button"

    @pytest.mark.usefixtures("get_driver")
    def test_hover(self, get_driver):
        driver = get_driver
        action = ActionChains(driver)
        action.move_to_element(driver.find_element(By.XPATH, "//body/div[@class='anime-container']/div[15]/a[1]")).perform()
        assert driver.find_element(By.ID, "anime_name").text == "Komi Can't Communicate", "Failed to show anime name on hover"

    @pytest.mark.usefixtures("get_driver")
    def test_badlogin(self, get_driver):
        driver = get_driver
        # In login page
        driver.find_element(By.LINK_TEXT, "Login").click()
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("wrongpassword")
        driver.find_element(By.TAG_NAME, "button").click()
        assert driver.find_element(By.ID, "error-message").text == "Error: Login failed.", "Failed to show error on bad login attempt"

    @pytest.mark.usefixtures("get_driver")
    def test_badsignup(self, get_driver):
        driver = get_driver
        # In login page
        driver.find_element(By.LINK_TEXT, "Sign Up").click()
        driver.find_element(By.ID, "username").send_keys("admin")
        driver.find_element(By.ID, "password").send_keys("wrongpassword")
        driver.find_element(By.TAG_NAME, "button").click()
        assert driver.find_element(By.ID, "error-message").text == "Error: Username already exists.", "Failed to block bad sign up"

    @pytest.mark.usefixtures("get_driver")
    def test_404(self, get_driver):
        driver = get_driver
        driver.get("http://127.0.0.1:5000/anime/0")
        assert driver.find_element(By.TAG_NAME, "h1").text == "404 Not Found", "Failed to reach 404 page"

    @pytest.mark.usefixtures("get_driver")
    def test_admin403(self, get_driver):
        driver = get_driver
        driver.get("http://127.0.0.1:5000/add_anime")
        assert driver.find_element(By.TAG_NAME, "h1").text == "403 Forbidden", "Failed to reach 403 page"

    @pytest.mark.usefixtures("get_driver")
    def test_403(self, get_driver):
        driver = get_driver
        driver.get("http://127.0.0.1:5000/review/5")
        assert driver.find_element(By.TAG_NAME, "h1").text == "403 Forbidden", "Failed to reach 403 page"

    @pytest.mark.usefixtures("setup_signup")
    def test_signup_into_review(self, setup_review):
        driver, username = setup_review
        driver.find_element(By.LINK_TEXT, "Sign Up").click()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("not_admin")
        driver.find_element(By.TAG_NAME, "button").click()
        driver.get("http://127.0.0.1:5000/anime/1")
        driver.find_element(By.LINK_TEXT, "Add Review").click()
        review_text = "This is a reviewing test"
        review_stars = "10"
        driver.find_element(By.ID, "review-text").send_keys(review_text)
        driver.find_element(By.ID, "star-rating").clear()
        driver.find_element(By.ID, "star-rating").send_keys(review_stars)
        driver.find_element(By.TAG_NAME, "button").click()
        assert driver.find_element(By.LINK_TEXT, "Edit Review"), "Failed to find edit review button"
        found_review = False
        for review in driver.find_elements(By.CLASS_NAME, "single-review"):
            if review.find_element(By.TAG_NAME, "p").text == review_text:
                if review.find_elements(By.TAG_NAME, "h4")[1].text == f"{username} gave it {review_stars} stars.":
                    found_review = True
                break
        assert found_review, "Test review not found"

    @pytest.mark.usefixtures("setup_signup")
    def test_signup_into_edit_review(self, setup_review):
        driver, username = setup_review
        driver.find_element(By.LINK_TEXT, "Sign Up").click()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("not_admin")
        driver.find_element(By.TAG_NAME, "button").click()
        driver.get("http://127.0.0.1:5000/anime/1")
        driver.find_element(By.LINK_TEXT, "Add Review").click()
        review_text = "This is a reviewing test"
        review_stars = "10"
        driver.find_element(By.ID, "review-text").send_keys(review_text)
        driver.find_element(By.ID, "star-rating").clear()
        driver.find_element(By.ID, "star-rating").send_keys(review_stars)
        driver.find_element(By.TAG_NAME, "button").click()

        # Editting Review
        driver.find_element(By.LINK_TEXT, "Edit Review").click()
        review_text = "Trying to test editting a review now"
        review_stars = "8"
        driver.find_element(By.ID, "review-text").clear()
        driver.find_element(By.ID, "review-text").send_keys(review_text)
        driver.find_element(By.ID, "star-rating").clear()
        driver.find_element(By.ID, "star-rating").send_keys(review_stars)
        driver.find_element(By.TAG_NAME, "button").click()

        assert driver.find_element(By.LINK_TEXT, "Edit Review"), "Failed to find edit review button"
        found_review = False
        for review in driver.find_elements(By.CLASS_NAME, "single-review"):
            if review.find_element(By.TAG_NAME, "p").text == review_text:
                if review.find_elements(By.TAG_NAME, "h4")[1].text == f"{username} gave it {review_stars} stars.":
                    found_review = True
                break
        assert found_review, "Test review not found"

    @pytest.mark.usefixtures("setup_signup")
    def test_add_review_button(self, setup_signup):
        driver, username = setup_signup
        driver.find_element(By.LINK_TEXT, "Sign Up").click()
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("not_admin")
        driver.find_element(By.TAG_NAME, "button").click()
        driver.get("http://127.0.0.1:5000/anime/1")
        assert driver.find_element(By.LINK_TEXT, "Add Review")

    @pytest.mark.usefixtures("get_driver")
    def test_search(self, get_driver):
        driver = get_driver
        driver.find_element(By.ID, "search").send_keys("[Oshi No Ko]")
        driver.find_element(By.CLASS_NAME, "search-icon").click()
        action = ActionChains(driver)
        action.move_to_element(driver.find_element(By.XPATH, "(//a[@class='image-link'])[1]")).perform()
        assert driver.find_element(By.ID, "anime_name").text == "[Oshi No Ko]", "Failed find expected result in search"

    @pytest.mark.usefixtures("get_driver")
    def test_animeclick(self, get_driver):
        driver = get_driver
        anime_element = driver.find_element(By.XPATH, "//body/div[@class='anime-container']/div[10]/a[1]")
        action = ActionChains(driver)
        action.move_to_element(anime_element).perform()
        anime_name = driver.find_element(By.ID, "anime_name").text
        anime_element.click()
        assert driver.find_element(By.ID, "anime_name").text == anime_name, "Failed, Anime clicked is not the same as anime showing"
        assert driver.find_element(By.TAG_NAME, "h1").text == anime_name, "Failed, Anime title is not the same as anime showing"

    @pytest.mark.usefixtures("get_driver")
    def test_animefront(self, get_driver):
        driver = get_driver
        driver.get("http://127.0.0.1:5000/anime/1")
        driver.find_element(By.LINK_TEXT, "AnimeFront").click()
        assert driver.current_url == "http://127.0.0.1:5000/", "AnimeFront button not working"

    @pytest.mark.usefixtures("get_driver")
    def test_existinganime(self, get_driver):
        driver = get_driver
        anime_id = 2
        driver.get(f"http://127.0.0.1:5000/anime/{anime_id}")
        with app.app_context():
            anime = Anime.query.filter_by(id=anime_id).first()
            assert driver.find_element(By.TAG_NAME, "h1").text == anime.title, "Wrong anime title"
            full_details = driver.find_element(By.CLASS_NAME, "anime-details-left")
            minor_details = full_details.find_elements(By.TAG_NAME, "b")
            expected_details = [anime.studio, anime.release_year, anime.characters, str(anime.average_stars) + " stars"]
            curr_detail = 0
            for detail in minor_details:
                assert detail.text == str(expected_details[curr_detail]), "Mismatching detail"
                curr_detail += 1

        
    @pytest.mark.usefixtures("get_driver")
    def test_existingreview(self, get_driver):
        driver = get_driver
        driver.get("http://127.0.0.1:5000/anime/7")
        username = "admin" # user_id 1
        with app.app_context():
            admin_review = UserReview.query.filter_by(anime_id=7, user_id=1).first()
            found_review = False
            for review in driver.find_elements(By.CLASS_NAME, "single-review"):
                if review.find_element(By.TAG_NAME, "p").text == admin_review.review:
                    if review.find_elements(By.TAG_NAME, "h4")[1].text == f"{username} gave it {admin_review.stars} stars.":
                        found_review = True
                    break
            assert found_review, "Test review not found"