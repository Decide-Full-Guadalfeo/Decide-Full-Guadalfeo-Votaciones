from base.tests import BaseTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class PrimaryVotingTestCase(StaticLiveServerTestCase):

    def setUp(self):
        self.base=BaseTestCase()
        self.base.setUp()

        options=webdriver.ChromeOptions()
        options.headless=True
        self.driver=webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def test_view_createPrimaryVotingOneCandiancyCorrect(self):

        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura con representantes elegidos")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()

        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Crear votación primaria con las candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".success").text == "¡La elección primaria se ha creado!"

        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        assert self.driver.find_element(By.LINK_TEXT, 'Votaciones de la candidatura "Candidatura con representantes elegidos"').text == 'Votaciones de la candidatura "Candidatura con representantes elegidos"'
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"'
        
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de master de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de master de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"

        self.driver.find_element(By.ID, "id_options-0-option").click()

    def test_view_createPrimaryVotingMoreThanOneCandiancyCorrect(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()

        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura con representantes elegidos")   
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()

        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()

        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura 2 con representantes elegidos")   
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('noadmin')
        self.driver.find_element(By.NAME, "_save").click()

        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Crear votación primaria con las candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".success").text == "¡La elección primaria se ha creado!"

        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        assert self.driver.find_element(By.LINK_TEXT, 'Votaciones de la candidatura "Candidatura con representantes elegidos"').text == 'Votaciones de la candidatura "Candidatura con representantes elegidos"'
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"'

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname+" "+admin_lastname'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de master de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de master de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname+" "+admin_lastname'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname+" "+admin_lastname'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname+" "+admin_lastname'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname+" "+admin_lastname'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname+" "+admin_lastname'
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname+" "+admin_lastname'
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"