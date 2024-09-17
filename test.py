from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# EBAY LOGIN CREDENTIALS
USER_EMAIL = ''
USER_PASSWORD = ''
def ebay_login():
    print('Logging in to eBay...')
    try:
        driver.get('https://ebay.ch/')
        time.sleep(1)
        try:
            if 'signin.ebay.ch' not in driver.find_element(By.ID, 'gh-top').find_element(By.TAG_NAME, 'a').get_attribute('href') and 'captcha' not in driver.current_url:
                return True
        except:
            pass
        driver.get('https://signin.ebay.ch/')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'userid')))
        if len(driver.find_elements(By.ID, 'userid')) > 0:
            if not USER_EMAIL:
                print("Missing eBay login email, fill it manually...\n\n")
                while 'signin.ebay.ch' in driver.current_url:
                    time.sleep(1)
                return True
            else:
                try:
                    driver.find_element(By.ID, 'userid').send_keys(USER_EMAIL)
                    driver.find_element(By.ID, 'signin-continue-btn').click()
                    time.sleep(3)
                except:
                    pass
        if not USER_PASSWORD:
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, 'pass')))
        else:
            driver.find_element(By.ID, 'pass').send_keys(USER_PASSWORD)
        if len(driver.find_elements(By.ID, 'sgnBt')) > 0:
            driver.find_element(By.ID, 'sgnBt').click()
    except Exception as e:
        print(f"Error while logging in to eBay: {e}")

def check_for_template_list():
    templates = []
    main = driver.find_element(By.ID, 'mainContent')
    if len(driver.find_elements(By.CLASS_NAME, 'template-list__title')) > 0:
        return driver.find_elements(By.CLASS_NAME, 'template-list__title')
    else:
        print("GENERATING TEMPLATES FILE")
        write_to_file('templates.html', main.get_attribute('outerHTML'))
    if False:
        block = driver.find_elements(By.CLASS_NAME, 'template-list')
        if len(block) > 0:
            template_list = driver.find_element(By.CLASS_NAME, 'template-list').find_elements(By.TAG_NAME, 'ul')
            if len(template_list) > 0:
                templates = driver.find_element(By.CLASS_NAME, 'template-list').find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
        if len(templates):
            print("Templates...")
            for template in templates:
                print(template.text)
        else:
            print("No template found...")
        return templates

def add_images(product):
    print('Adding images...')
    try:
        # ADD IMAGES
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'summary__photos')))
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__photos'))
        time.sleep(1)
        if len(driver.find_elements(By.CLASS_NAME, 'uploader-thumbnails__container-empty--importFromWeb')) == 0:
            driver.find_elements(By.CLASS_NAME, 'se-expand-button__button-text')[0].click()
            driver.find_element(By.NAME, 'photoUploadWebPref').click()
            driver.find_elements(By.CLASS_NAME, 'se-expand-button__button-text')[0].click()
        driver.find_element(By.CLASS_NAME, 'uploader-thumbnails__container-empty--importFromWeb').click()
        if len(driver.find_elements(By.CLASS_NAME, 'se-panel-container')) == 0:
            print('No se-panel-container found, skipping...')
            return
        driver.find_element(By.CLASS_NAME, 'se-panel-container').click()
        for index, image_url in enumerate(product['images']):
            if index > 0:
                driver.find_element(By.NAME, 'addAdditional').click()
            input_blocks = driver.find_elements(By.CLASS_NAME, 'url-row')
            input_blocks[index].find_element(By.TAG_NAME, 'input').send_keys(image_url)
        # done
        driver.find_element(By.CLASS_NAME, 'se-panel-container__header').find_element(By.TAG_NAME, 'button').click()
    except Exception as e:
        print(f"Error while adding images: {e}")

def add_title(product):
    # ADD TITLE
    print('Adding title...')
    try:
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__title'))
        time.sleep(1)
        title_block = driver.find_element(By.CLASS_NAME, 'summary__title').find_element(By.CLASS_NAME, 'smry--section')
        title_input = title_block.find_element(By.TAG_NAME, 'input')
        title_input.clear()
        title_input.send_keys(product['name'])
    except Exception as e:
        print(f"Error while adding title: {e}")

def add_description(product):
    # ADD DESCRIPTION
    print('Adding description...')
    try:
        description_block = driver.find_element(By.CLASS_NAME, 'summary__description')
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", description_block)
        time.sleep(0.5)
        if len(driver.find_elements(By.ID, 'se-rte-frame__summary')) > 0:
            iframe = driver.find_element(By.ID, 'se-rte-frame__summary')
            driver.switch_to.frame(iframe)
            # Locate the contenteditable div inside the iframe
            editor_div = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
            # Set the HTML content directly using JavaScript
            driver.execute_script(f"arguments[0].innerHTML = `{product['description']}`;", editor_div)
            time.sleep(0.1)
            driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(0.1)
            driver.switch_to.default_content()
        else:
            print('No description editor found, skipping...')
    except Exception as e:
        print(f"Error while adding description: {e}")

def check_close_category():
    # lightbox-dialog__main
    while len(driver.find_elements(By.CLASS_NAME, 'lightbox-dialog__main')) > 0:
        for _ in range(5):
            try:
                driver.find_element(By.CLASS_NAME, 'se-panel-container__header-suffix').click()
                break
            except:
                time.sleep(1)

def list_products_in_ebay(products):
    driver.get('https://www.ebay.ch/sl/prelist/suggest?sr=cubstart')
    time.sleep(3)
    i = 1
    #templates_list = check_for_template_list()
    if False:# len(templates_list) == 0:
        try:
            print('No Templates Found, creating...')
            driver.get('https://www.ebay.ch/lstng/template?mode=AddItem')
            time.sleep(1)
            # templateName
            for _ in range(8):
                if len(driver.find_elements(By.NAME, 'templateName')) > 0:
                    break
                time.sleep(1)
            if len(driver.find_elements(By.NAME, 'templateName')) == 0:
                print('Cannot create template, create one and try again...')
                driver.get('https://www.ebay.ch/sl/prelist/suggest?sr=cubstart')
                #return
            title_input = driver.find_element(By.NAME, 'templateName')
            title_input.clear()
            title_input.send_keys("New Template")
            driver.find_element(By.CLASS_NAME, 'btn--large').click()
            time.sleep(3)
            driver.get('https://www.ebay.ch/sl/prelist/suggest?sr=cubstart')
            time.sleep(2)
        except Exception as e:
            print(f"Error while creating template, create one and try again: {e}")
    templates_list = check_for_template_list()
    if len(templates_list) == 0:
        print('No template found...')
        return []
    print("Templage found, listing products...")
    for product in products:
        print(f"{i}/{len(products)} Listing product: {product['name']}")
        driver.get('https://www.ebay.ch/sl/prelist/suggest?sr=cubstart')
        templates_list = check_for_template_list()
        time.sleep(1)
        # template-list__list
        if len(driver.find_elements(By.CLASS_NAME, 'template-list__list')) > 0:
            templates_list[0].click()
            time.sleep(1)
            add_category()
            time.sleep(2)
            check_close_category()
            add_images(product)
            time.sleep(2)
            check_close_category()
            add_title(product)
            time.sleep(2)
            check_close_category()
            add_specifics()
            time.sleep(2)
            check_close_category()
            add_description(product)
            time.sleep(2)
            check_close_category()
            add_pricing(product)
            time.sleep(2)
            check_close_category()
            driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__cta'))
            print(f"Product {product['name']} listed!\n\n")
        else:
            print('No template-list__list found, skipping...')
        i += 1

def add_pricing(product):
    # ADD PRICING
    print('Setting price...')
    try:
        while len(driver.find_elements(By.CLASS_NAME, 'summary__price')) == 0:
            time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__price'))
        time.sleep(1)
        price_block = driver.find_element(By.CLASS_NAME, 'summary__price')
        # button
        try:
            a = 0/0
            button = price_block.find_element(By.CLASS_NAME, 'summary__price-fields').find_element(By.TAG_NAME, 'button')
            button.click()
        except:
            for button in price_block.find_elements(By.TAG_NAME, 'button'):
                if button.text == 'Auktion':
                    button.click()
                    break
        if button.text != 'Sofort-Kaufen':
            # listbox__options
            for option in price_block.find_elements(By.CLASS_NAME, 'listbox__option'):
                if option.text == 'Sofort-Kaufen':
                    option.click()
                    break
        # get input with name 'price'
        while len(price_block.find_elements(By.NAME, 'price')) == 0:
            time.sleep(0.5)
        time.sleep(0.1)
        price_input = price_block.find_element(By.NAME, 'price')
        price_input.send_keys(str(product['price']))
    except Exception as e:
        print("WRITING PRICING TO FILE")
        write_to_file('pricing.html', price_block.get_attribute('outerHTML'))
        print(f"Error while adding pricing: {e}")

def write_to_file(filename, data):
    with open(filename, 'w') as file:
        file.write(data)

def shipping_policy():
    try:
        # summary__shipping
        print("A")
        shipping_block = driver.find_element(By.CLASS_NAME, 'summary__shipping')
        # business-policy-field
        print("B")
        business_policy_field = shipping_block.find_element(By.CLASS_NAME, 'business-policy-field')
        # business-policy-field__menu
        print("C")
        business_policy_field_menu = business_policy_field.find_element(By.CLASS_NAME, 'business-policy-field__menu')
        print('Setting shipping policy... Click button')
        button = business_policy_field_menu.find_element(By.CLASS_NAME, 'menu-button__button')
        print("Clicking...")
        button.click()
        time.sleep(2)
    except Exception as e:
        print("Error:", e)
    try:
        print("Get shipping policy container")
        if len(driver.find_elements(By.CLASS_NAME, 'lightbox-dialog__main')) > 0:
            main_container = driver.find_element(By.CLASS_NAME, 'lightbox-dialog__main')
            write_to_file('shipping_policy.html', main_container.get_attribute('outerHTML'))
        else:
            print("No lightbox-dialog__main found")
    except Exception as e:
        print("Error:", e)

def add_shipping():
    # ADD SHIPPING
    print('Setting shipping...')
    try:
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__shipping'))
        time.sleep(1)
        shipping_block = driver.find_element(By.CLASS_NAME, 'summary__shipping')
        try:
            print("Get summary__shipping--section (select_block)")
            select_block = shipping_block.find_element(By.CLASS_NAME, 'summary__shipping--section')
            if len(select_block.find_elements(By.CLASS_NAME, 'se-field--fluid')) > 0:
                print("Get se-field--fluid")
                select = select_block.find_element(By.CLASS_NAME, 'se-field--fluid')
                print("Clicking...")
                select.click()
                time.sleep(0.1)
                print("Get summary__shipping--field")
                options = select_block.find_elements(By.CLASS_NAME, 'listbox__option')
                print("Clicking... 2nd option")
                options[1].click()
                time.sleep(0.1)
                print("Clicking select again...")
                select.click()
        except Exception as e:
            print("WRITING SHIPPING TO FILE")
            write_to_file('shipping2.html', shipping_block.get_attribute('outerHTML'))
            print("Error:", e)
            time.sleep(1)
        try:
            preferences_block = shipping_block.find_element(By.CLASS_NAME, 'shipping-settings-container')
            button = preferences_block.find_element(By.TAG_NAME, 'button')
            button.click()
        except Exception as e:
            print("Error:", e)
        to_write = ''
        try:
            print("Get handlig-time block")
            handling_time_block = driver.find_element(By.CLASS_NAME, 'se-panel-container__body').find_element(By.TAG_NAME, 'div')
            for i in range(5):
                if len(handling_time_block.find_elements(By.TAG_NAME, 'button')) > 0:
                    print("Button found")
                    break
                time.sleep(1)
            print("Get button")
            to_write = driver.find_element(By.CLASS_NAME, 'se-panel-container__body').get_attribute('outerHTML')
            button = handling_time_block.find_element(By.TAG_NAME, 'button')
            print("Clicking...")
            for _ in range(10):
                try:
                    button.click()
                    time.sleep(0.1)
                    options = handling_time_block.find_elements(By.CLASS_NAME, 'listbox__option')
                    print("Clicking... 3th option")
                    time.sleep(1)
                    options[3].click()
                    break
                except:
                    print("Retrying...")
            button.click()
            print("Handling time set")
            driver.find_element(By.CLASS_NAME, 'textual-display').click()
            time.sleep(0.1)
        except Exception as e:
            print("WRITING PREFECENCES TO FILE")
            write_to_file('prefecences.html', to_write)
            print("Error", e)
        try:
            prefecences_settings = driver.find_element(By.CLASS_NAME, 'se-panel-container__body')
            country_input = prefecences_settings.find_element(By.NAME, 'itemLocationCountry')
            country_input.click()
            print("Ok, clicked")
            if True:
                time.sleep(0.1)
                while country_input.get_attribute('value'):
                    country_input.send_keys('\b')
                country_input.clear()
                time.sleep(0.1)
                country_input.send_keys('Germany')
                time.sleep(0.1)
                print("Ok, clicked 2")
                # combobox__option
                prefecences_settings.find_element(By.CLASS_NAME, 'combobox__option').click()
                # itemLocation
                if len(prefecences_settings.find_elements(By.NAME, 'itemLocation')) > 0:
                    location_input = prefecences_settings.find_element(By.NAME, 'itemLocation')
                    location_input.send_keys('d-59227')
                # itemLocationCityState
                location_city_state = prefecences_settings.find_element(By.NAME, 'itemLocationCityState')
                location_city_state.clear()
                location_city_state.send_keys('Ahlen')
                print("Ok, clicked 3")
                driver.find_element(By.CLASS_NAME, 'se-panel-container__header-suffix').find_element(By.TAG_NAME, 'button').click()
                time.sleep(1)
        except Exception as e:
            write_to_file('prefecences.html', prefecences_settings.get_attribute('outerHTML'))
            print("Error:", e)
        try:
            # name packageDepth
            print("Last click")
            driver.find_element(By.NAME, 'packageDepth').click()
        except Exception as e:
            print("Error:", e)
    except Exception as e:
        print(f"Error while adding shipping: {e}")

def add_category():
    print('Selecting category...')
    try:
        while len(driver.find_elements(By.CLASS_NAME, 'summary__category')) == 0:
            time.sleep(0.5)
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__category'))
        time.sleep(1)
        category_block = driver.find_element(By.CLASS_NAME, 'summary__category')
        time.sleep(0.1)
        # categoryId
        if category_block.find_element(By.NAME, 'categoryId').text == "Sonstige":
            #return
            pass
        while len(driver.find_elements(By.CLASS_NAME, 'lightbox-dialog__main')) == 0:
            try:
                category_block.find_element(By.TAG_NAME, 'button').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.1)
        time.sleep(1)
        # category-picker
        category_picker = driver.find_element(By.CLASS_NAME, 'lightbox-dialog__main')
        while len(category_picker.find_elements(By.CLASS_NAME, 'textbox__control')) == 0:
            category_picker.find_element(By.NAME, 'primaryCategory').click()
            time.sleep(3)
        category_picker.find_element(By.CLASS_NAME, 'textbox__control').send_keys('Beauty & Gesundheit > Sonstige')
        for _ in range(50):
            if len(driver.find_elements(By.NAME, 'categoryId')) > 2:
                break
            time.sleep(0.1)
        for option in driver.find_elements(By.NAME, 'categoryId'):
            if option.get_attribute('value') == '1277':
                option.click()
                break
        for _ in range(10):
            try:
                driver.find_element(By.CLASS_NAME, 'se-panel-container__header-suffix').click()
                break
            except:
                pass
            time.sleep(0.5)
        while len(driver.find_elements(By.CLASS_NAME, 'lightbox-dialog__main')) > 0:
            time.sleep(0.2)
    except Exception as e:
        print(f"Error while adding category: {e}")

def add_condition():
    # ADD CONDITION
    print('Selecting condition...')
    try:
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__condition'))
        time.sleep(1)
        condition_block = driver.find_element(By.CLASS_NAME, 'summary__condition')
        # get condition-recommendation-value btn
        options = condition_block.find_elements(By.CLASS_NAME, 'condition-recommendation-value')
        if len(options) > 0:
            options[0].click()
    except Exception as e:
        print(f"Error while adding condition: {e}")

def add_specifics():
    # ITEM SPECIFICS
    print('Adding specifics...')
    try:
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__attributes--container'))
        time.sleep(1)
        specifics_block = driver.find_element(By.CLASS_NAME, 'summary__attributes--container')
        required = specifics_block.find_elements(By.CLASS_NAME, 'summary__attributes--section-container')[0]
        required_fields = required.find_elements(By.CLASS_NAME, 'summary__attributes--fields')
        other = specifics_block.find_elements(By.CLASS_NAME, 'summary__attributes--section-container')[1]
        other_fields = other.find_elements(By.CLASS_NAME, 'summary__attributes--fields')
        for field in required_fields:
            if len(field.find_elements(By.NAME, 'attributes.Brand')) > 0:
                while True:
                    try:
                        driver.find_element(By.NAME, 'attributes.Brand').click()
                        time.sleep(0.1)
                        driver.find_element(By.NAME, 'search-box-attributesBrand').send_keys("LR World")
                        break
                    except:
                        time.sleep(0.1)
                options = field.find_elements(By.CLASS_NAME, 'se-filter-menu-button__add-custom-value')
                if len(options) > 0:
                    options[0].click()
        for field in other_fields:
            print(field.text)
            if len(field.find_elements(By.NAME, 'attributes.Country/Region of Manufacture')) > 0:
                while True:
                    try:
                        driver.find_element(By.NAME, 'attributes.Country/Region of Manufacture').click()
                        time.sleep(0.1)
                        driver.find_element(By.NAME, 'search-box-attributesCountryRegionofManufacture').send_keys("Germany")
                        # click name "searchedOptions-attributesCountryRegionofManufacture"
                        driver.find_element(By.NAME, 'searchedOptions-attributesCountryRegionofManufacture').click()
                        break
                    except:
                        time.sleep(0.1)
                options = field.find_elements(By.CLASS_NAME, 'se-filter-menu-button__add-custom-value')
                if len(options) > 0:
                    options[0].click()
    except Exception as e:
        print(f"Error while adding specifics: {e}")



def create_template():
    try:
        driver.get('https://www.ebay.ch/lstng/template?mode=AddItem')
        time.sleep(1)
        # templateName
        for _ in range(8):
            if len(driver.find_elements(By.NAME, 'templateName')) > 0:
                break
            time.sleep(1)
        if len(driver.find_elements(By.NAME, 'templateName')) == 0:
            print('Cannot create template, create one and try again...')
            driver.get('https://www.ebay.ch/sl/prelist/suggest?sr=cubstart')
            #return
        title_input = driver.find_element(By.NAME, 'templateName')
        title_input.clear()
        title_input.send_keys("Set Template")
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__shipping'))
    except Exception as e:
        print(f"Error while creating template, create one and try again: {e}")


# Automatically download and use the correct version of ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--enable-features=UseOzonePlatform")
options.add_argument("--ozone-platform=wayland")
options.add_argument("--log-level=1")
options.add_argument("--incognito")
options.add_argument("--guest")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

#html = '<div class="additional-price-info shipping-costs">plus delivery costs<span class="inactive info tooltip btn-simple light" data-tooltip="<div class="title">Delivery costs</div><div class="content"><div></div><div></div><div>Shipping costs:</br> to £ 75.00 -> £ 9.99 </br> £ 75.01 to £ 150.00 -> £ 5.99 </br> above £ 150.00 -> free of charge</div></div>">i</span></div>'
#shipping_costs_html = html.find_element(By.CLASS_NAME, 'shipping-costs').find_element(By.TAG_NAME, 'span').get_attribute('data-tooltip')
#shipping_costs_html = "<div class='title'>Delivery costs</div><div class='content'><div></div><div></div><div>Shipping costs:</br> to £ 75.00 -> £ 9.99 </br> £ 75.01 to £ 150.00 -> £ 5.99 </br> above £ 150.00 -> free of charge</div></div>"
#shipping_costs = shipping_costs_html.split('Shipping costs:')[1].split('</div>')[0].split('</br>')
#shipping_costs = list(filter(None, shipping_costs))
shipping_costs = [' to £ 75.00 -> £ 9.99 ', ' £ 75.01 to £ 150.00 -> £ 5.99 ', ' above £ 150.00 -> free of charge']



products = [{
    'shipping_policy': '',
    'name': 'LR LIFETAKT Vita Active Daily Vitamin Drink Red Fruits', 'description': '<h2> LR LIFETAKT Vita Active Daily Vitamin Drink Red Fruits </h2><p>Vitamins for the whole family - 100 % vitamin supply with just one teaspoon.</p><p>A varied and balanced diet is an important part of a healthy lifestyle. This is because we can and must take in a variety of nutrients that the body needs every day with our food. To ensure that we are always well supplied, taking Vita Active can make a meaningful contribution. Vita Active is a concentrate of 21 natural fruits and vegetables that tastes delicious and provides the body with ten important vitamins. Vitamins are true artists: for example, vitamins D and B6 contribute to a normal function of the immune system, vitamin B12 has a function in cell division, and vitamin B1 contributes to a normal heart function.</p><br><h2> Ingredients/Nutritional information </h2><p><strong>Ingredients: </strong>Fruit and vegetable concentrates (94 %, consisting of red grapes, apples, sour cherries, elderberries, black currants, rose hips, strawberries, blackberries, carrots, sloes, blueberries, aronia berries, plums, red currants, sea buckthorn berries, lemons, peaches, apricots, raspberries, boysenberries), dextrose, tomato concentrate, emulsifier (sunflower lecithin), niacin, vitamin E, pantothenic acid, vitamin B12, biotin, vitamin D, vitamin B6, thiamine, riboflavin, folic acid.</p><p>*&nbsp;of the reference quantity for daily intake (NRV)</p><br><h2> Application </h2><p>Consume 5 ml once a day during or after a meal. You can also mix Vita Active as a spritzer with water, consume it with yoghurt, as a dessert or with muesli. Long-term consumption is recommended.</p><p>Do not exceed the recommended daily intake. Food supplements are not a substitute for a varied and balanced diet, which is important together with a healthy lifestyle. Keep product out of the reach of small children.</p><p>Do not store above 25 °C. Re-seal well after opening, store in the refrigerator.<br>Shake before use.</p><br><h2> Worth knowing </h2><p><strong>Did you know that vitamin D is also called the "sun vitamin"?</strong><br>It is a special vitamin that the body can produce under the influence of sunlight. A balanced diet normally supplies the body with all relevant vitamins. Especially in the dark season, Vita Active can be a useful addition to your diet.</p><p>A balanced diet is especially important for people who are very busy at work or with their families. Also pay attention to what you eat during such phases and supplement your diet with Vita Active if necessary.</p><br>', 'category': 'Nutrition Nutrient complex', 'brand': 'LR LIFETAKT', 'type': 'None', 'color': 'None', 'price': '26.39 GBP', 'images': ['https://cdn.lrworld.com/images_cms/images/product/884x1200/80301-50/lr_lifetakt_vita_active_daily_vitamin_drink_red_fruits.jpg'], 'filled': True, 'upc': '80301-50'}]

while not ebay_login():
    pass

for product in products:
    break

#driver.get('https://www.ebay.ch/sl/prelist/suggest?sr=cubstart')

#list_products_in_ebay(products)

list_products_in_ebay(products)